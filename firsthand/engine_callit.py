"""Call it in the engine: episodes, the red and fix runs, the offer and the release.

A mixin for `engine.Engine`. An episode follows one failing test in a session from
its red run (or the prompt that pasted the failure) to its first green run. It is
kept in `Session.episode` and written to the record as `episode.red` and
`episode.green`, asked about or not, so the failure is saved for the Replay drill.

Being asked never depends on what a run found: the gates decide before the red run
starts, the red run is the control, and the fix run starts only for a question that
was locked. `release_call` is the only place a Call it result leaves the key store.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from firsthand import ask, gitwatch
from firsthand.model import REVEALED, Moment, SpoolEvent
from firsthand.moments import call_it, call_it_run
from firsthand.moments.call_it import Case, Frame
from firsthand.moments.revert_test import RunContext
from firsthand.record import new_ulid
from firsthand.state import Project, Session

if TYPE_CHECKING:
    from firsthand.engine import Engine

_LOGGER = logging.getLogger("firsthand.engine")
CALL_KIND = call_it.KIND


@dataclass(eq=False)
class CallCheck:
    case: Case
    skey: str
    phase: str  # "red" or "fix"
    cancel: threading.Event = field(default_factory=threading.Event)
    cancelled: bool = False

    @property
    def id(self) -> str:
        return self.case.check_id


def _frames(rows) -> tuple[Frame, ...]:
    return tuple(Frame(r["path"], int(r["line"]), r.get("where")) for r in rows or ())


def _frame_rows(frames) -> list[dict]:
    return [{"path": f.path, "line": f.line, "where": f.where} for f in frames]


class CallIt:
    """Mixed into Engine. `self` is always an Engine."""

    # ------------------------------------------------------------- triggers

    def _pytest_project(self: Engine, p: Project):
        proj = self.config.project(p.id)
        if proj is None or not proj.test_command:
            return None
        return proj if gitwatch.runner_token(proj.test_command) == "pytest" else None

    def _following(self: Engine, s: Session) -> dict | None:
        """The episode of this change that has not gone green yet."""
        ep = s.episode
        if ep is None or ep.get("green_tree") or ep.get("change") != s.st.change_id:
            return None
        return ep

    def callit_prompt(
        self: Engine, p: Project, s: Session, ev: SpoolEvent, tree: str | None
    ) -> None:
        """A prompt that holds a pasted traceback or FAILED line starts an episode."""
        task = s.st.task
        if (
            tree is None
            or task is None
            or not call_it.is_failure_prompt(ev.prompt)
            or self._following(s) is not None
            or self._pytest_project(p) is None
        ):
            return
        store = self.store(p.id)
        test = next(
            (
                t
                for t in call_it.failed_ids(ev.prompt)
                if store.read_file(tree, t.split("::", 1)[0]) is not None
            ),
            None,
        )
        frames = call_it.frames_from_text(ev.prompt, p.root)
        self._start_episode(p, s, ev, "prompt", test, tree, frames, None)

    def callit_failed(
        self: Engine, p: Project, s: Session, ev: SpoolEvent, body: dict
    ) -> None:
        """A failing test run: the red run of a new episode, or the test of a pasted one."""
        tree = body.get("tree")
        task = s.st.task
        if tree is None or task is None or self._pytest_project(p) is None:
            return
        failing = [str(f) for f in body.get("failing") or ()]
        ep = self._following(s)
        if ep is not None:
            if ep.get("test") is None and failing and not ep.get("fix_started"):
                ep["test"] = call_it.strip_param(failing[0])
                self._record_red(p, s, ep, ev.at, ev.command)
                self._maybe_red_check(p, s, ep)
            return
        test = call_it.qualifying_test(
            failing, self.store(p.id), task.base_tree, str(tree)
        )
        if test is not None:
            self._start_episode(p, s, ev, "test_run", test, str(tree), (), ev.command)

    def _start_episode(
        self: Engine,
        p: Project,
        s: Session,
        ev: SpoolEvent,
        trigger: str,
        test: str | None,
        tree: str,
        frames,
        command: str | None,
    ) -> None:
        task = s.st.task
        assert task is not None
        ep = {
            "id": new_ulid(),
            "task": task.id,
            "change": s.st.change_id,
            "trigger": trigger,
            "test": test,
            "red_tree": tree,
            "red_at": ev.at,
            "base_tree": task.base_tree,
            "frames": _frame_rows(frames),
            "message": None,
            "fix_started": False,
            "green_tree": None,
            "red_check": None,
            "red_status": None,
            "turn_ended": False,
            "decided": False,
            "moment": None,
            "fix_check": None,
        }
        s.episode = ep
        if test is not None:
            self._record_red(p, s, ep, ev.at, command)
            self._maybe_red_check(p, s, ep)

    def _record_red(
        self: Engine, p: Project, s: Session, ep: dict, at: str, command: str | None
    ) -> None:
        body = {
            "episode": ep["id"],
            "task": ep["task"],
            "trigger": ep["trigger"],
            "test": ep["test"],
            "tree": ep["red_tree"],
            "command": command,
        }
        self.append("episode.red", body, project=p.id, change=ep["change"], at=at)

    def _maybe_red_check(self: Engine, p: Project, s: Session, ep: dict) -> None:
        """Start the red run only if a question could be asked: selection comes first."""
        g = self.gate_input(p, s, ep["red_at"])
        reason = ask.gates(g) if self.live(p) is None else "change"
        if reason is not None:
            ep["decided"] = True
            self.log(f"episode {ep['id']} not asked: {reason}")
            return
        task = s.st.task
        assert task is not None
        case = Case(
            check_id=new_ulid(),
            project_id=p.id,
            project_root=p.root,
            task_id=task.id,
            change_id=ep["change"],
            test=ep["test"],
            red_tree=ep["red_tree"],
        )
        c = CallCheck(case, s.key, "red")
        ep["red_check"], ep["red_status"] = c.id, "control"
        self._call_launch(p, c)

    # -------------------------------------------------------------- the runs

    def _call_ctx(self: Engine, p: Project, c: CallCheck) -> RunContext:
        s = self.sessions.get(c.skey)
        settings = self.config.load()
        return RunContext(
            store=self.store(p.id),
            project=self.config.project(p.id),
            venv_hint=s.st.venv if s else None,
            time_limit_s=float(settings.check_time_limit_s),
            on_control=lambda ok: None,
            cancel=c.cancel,
        )

    def _call_launch(self: Engine, p: Project, c: CallCheck) -> None:
        self.call_checks[c.id] = c
        ctx = self._call_ctx(p, c)
        if c.phase == "red":
            self._executor(lambda: self._red_worker(p, c, ctx))
        else:
            self._executor(lambda: self._fix_worker(p, c, ctx))

    def _red_worker(self: Engine, p: Project, c: CallCheck, ctx: RunContext) -> None:
        out = call_it_run.run_red(c.case, ctx)
        with self._mutex:
            try:
                self._red_done(p, c, out)
            finally:
                self.checkpoint()

    def _fix_worker(self: Engine, p: Project, c: CallCheck, ctx: RunContext) -> None:
        out = call_it_run.run(c.case, ctx)
        with self._mutex:
            try:
                self._fix_done(p, c, out)
            finally:
                self.checkpoint()

    def _call_cancel(self: Engine, check_id: str | None) -> None:
        c = self.call_checks.pop(check_id or "", None)
        if c is not None:
            c.cancelled = True
            c.cancel.set()

    def _red_done(self: Engine, p: Project, c: CallCheck, out) -> None:
        self.call_checks.pop(c.id, None)
        s = self.sessions.get(c.skey)
        ep = s.episode if s is not None else None
        if c.cancelled or out.cancelled or ep is None or ep.get("red_check") != c.id:
            return
        if not out.ok:
            ep["red_status"], ep["decided"] = "failed", True
            self._call_unavailable(p, c, None, out.unavailable or "does not match here")
            self.answer_deferred(p, s)
            return
        # The red run's junit text is the chosen test's own trace. A pasted prompt
        # can hold the traces of other failing tests too, so it is used only when
        # the red run gave no frames.
        frames = tuple(out.frames) or _frames(ep.get("frames"))
        ep["frames"], ep["message"], ep["red_status"] = (
            _frame_rows(frames),
            out.message,
            "ok",
        )
        self._call_try_offer(p, s, None)
        self.answer_deferred(p, s)

    def _call_unavailable(
        self: Engine, p: Project, c: CallCheck, m: Moment | None, reason: str
    ) -> None:
        body = {
            "check_kind": CALL_KIND,
            "check": c.id,
            "reason": reason,
            "step": "control",
            "base_tree": c.case.red_tree,
            "head_tree": c.case.green_tree or c.case.red_tree,
            "command": None,
            "exit": None,
        }
        self.append(
            "check.unavailable",
            body,
            project=p.id,
            change=c.case.change_id,
            moment=m.id if m else None,
        )

    # ---------------------------------------------------------------- offer

    def _call_try_offer(
        self: Engine, p: Project, s: Session, ev: SpoolEvent | None
    ) -> None:
        ep = self._following(s)
        if (
            ep is None
            or ep["decided"]
            or ep["red_status"] != "ok"
            or ep["fix_started"]
            or (ep["trigger"] == "test_run" and not ep["turn_ended"])
        ):
            return
        ep["decided"] = True
        at = ev.at if ev is not None else self.now()
        task = s.st.task
        changes = self.store(p.id).diff(ep["base_tree"], ep["red_tree"])
        picks = call_it.build_picks(_frames(ep["frames"]), [c.path for c in changes])
        reason = (
            ask.gates(self.gate_input(p, s, at)) if self.live(p) is None else "change"
        )
        if not call_it.worth_asking(picks):
            reason = reason or "fewer than two files to pick"
        if reason is not None or task is None:
            self.log(f"episode {ep['id']} not asked: {reason or 'no task'}")
            return
        self._call_offer(p, s, ep, picks, at)

    def _call_offer(
        self: Engine, p: Project, s: Session, ep: dict, picks, at: str
    ) -> None:
        task = s.st.task
        assert task is not None
        m = Moment(
            id=new_ulid(),
            kind=CALL_KIND,
            state="open",
            project_id=p.id,
            change_id=ep["change"],
            task_id=task.id,
            session=s.st.session,
            task_name=task.name,
            base_at=ep["red_at"],
            base_tree=ep["red_tree"],
            head_tree=ep["red_tree"],
            tests=(),
            how="pytest",
            high_stakes=None,
            offered_at=at,
            extra={
                "episode": ep["id"],
                "test": ep["test"],
                "picks": [dict(x) for x in picks],
                "frames": list(ep["frames"]),
                "message": ep["message"],
                "trigger": ep["trigger"],
            },
        )
        self.moments[m.id] = m
        p.live, ep["moment"] = m.id, m.id
        s.st.change_asked = True
        if self.current_event:
            self.offered_in[m.id] = self.current_event
        body = {
            "moment_kind": CALL_KIND,
            "form": "pick",
            "skill": call_it.SKILL,
            "break": "failure_prompt"
            if ep["trigger"] == "prompt"
            else "failure_turn_end",
            "fading": "full",
            "task": task.id,
            "base_tree": ep["red_tree"],
            "head_tree": ep["red_tree"],
            "how": "pytest",
            "tests": [],
            "high_stakes": None,
            "replaces": None,
            "episode": ep["id"],
            "test": ep["test"],
            "picks": [
                {k: x[k] for k in ("n", "path", "traced", "changed")} for x in picks
            ],
        }
        self.append(
            "moment.offered",
            body,
            project=p.id,
            change=ep["change"],
            moment=m.id,
            at=at,
        )
        self.prune_moments()
        self.notify("inbox")

    # ------------------------------------------------- turn ends, edits, green

    def callit_turn_end(self: Engine, p: Project, s: Session, ev: SpoolEvent) -> None:
        """The turn ended with the test still failing: the break of the turn-end form."""
        ep = self._following(s)
        task = s.st.task
        if ep is None or task is None or ep["decided"] or ep["fix_started"]:
            return
        if ep["trigger"] == "test_run":
            if task.last_test_exit in (None, 0):
                return
            ep["turn_ended"] = True
        self._call_try_offer(p, s, ev)

    def call_waiting(self: Engine, s: Session) -> bool:
        """The stop should wait briefly: the red run for this turn end is still going."""
        ep = self._following(s)
        return bool(
            ep is not None
            and ep["red_status"] == "control"
            and ep["turn_ended"]
            and not ep["decided"]
        )

    def call_may_speak(self: Engine, s: Session) -> bool:
        ep = self._following(s)
        task = s.st.task
        return bool(
            ep is not None
            and task is not None
            and not ep["decided"]
            and not ep["fix_started"]
            and ep["red_status"] in ("control", "ok")
            and task.last_test_exit not in (None, 0)
        )

    def callit_edit(self: Engine, p: Project, s: Session, ev: SpoolEvent) -> None:
        """The first edit to a non-test file after the failure: the fix has begun."""
        ep = self._following(s)
        if ep is None or ep["fix_started"] or ev.tool != "edit":
            return
        root = p.root.rstrip("/") + "/"
        rel = [x.removeprefix(root) for x in ev.paths]
        if not any(not gitwatch.is_test_path(x) for x in rel):
            return
        ep["fix_started"] = True
        if not ep["decided"]:
            ep["decided"] = True
            self._call_cancel(ep.get("red_check"))
        m = self.moments.get(ep.get("moment") or "")
        if m is not None and m.state == "open":
            self.close_moment(p, m, "fix-started", ev.at)
        elif m is not None and m.state == "held":
            self.settle_held(p, m)

    def callit_green(
        self: Engine, p: Project, s: Session, ev: SpoolEvent, tree: str | None
    ) -> None:
        ep = self._following(s)
        if ep is None or tree is None or not ep.get("test"):
            return
        if not call_it.covers(ev.command, ep["test"]):
            return
        ep["green_tree"] = tree
        body = {
            "episode": ep["id"],
            "task": s.st.task.id if s.st.task else ep["task"],
            "test": ep["test"],
            "red_tree": ep["red_tree"],
            "green_tree": tree,
            "command": ev.command,
        }
        self.append("episode.green", body, project=p.id, change=ep["change"], at=ev.at)
        if not ep["decided"]:
            ep["decided"] = True
            self._call_cancel(ep.get("red_check"))
        m = self.moments.get(ep.get("moment") or "")
        if m is not None and m.state == "open":
            self.close_moment(p, m, "fix-started", ev.at)
        elif m is not None and m.state in ("held", "sealed"):
            self._fix_check(p, s, ep, m)

    def _fix_check(self: Engine, p: Project, s: Session, ep: dict, m: Moment) -> None:
        store = self.store(p.id)
        changes = store.diff(ep["red_tree"], ep["green_tree"])
        case = Case(
            check_id=m.id,
            project_id=p.id,
            project_root=p.root,
            task_id=m.task_id,
            change_id=m.change_id,
            test=ep["test"],
            red_tree=ep["red_tree"],
            green_tree=ep["green_tree"],
            picks=tuple((m.extra or {}).get("picks", ())),
            frames=_frames((m.extra or {}).get("frames")),
            fix_changes=tuple(c for c in changes if not gitwatch.is_test_path(c.path)),
            changed=tuple(c.path for c in changes),
            patterns=call_it.symptoms(store, ep["red_tree"], ep["green_tree"], changes),
        )
        ep["fix_check"] = m.id
        self._call_launch(p, CallCheck(case, s.key, "fix"))

    def _fix_done(self: Engine, p: Project, c: CallCheck, out) -> None:
        self.call_checks.pop(c.id, None)
        m = self.moments.get(c.id)
        if c.cancelled or m is None or (out.key is None and out.unavailable is None):
            return
        if out.unavailable:
            self._call_unavailable(p, c, m, out.unavailable)
            if m.state == "held":
                self.settle_held(p, m)
            if m.state == "sealed":
                self._call_unscored(p, m, "check-unavailable")
            return
        self.keys.put(out.key)
        if m.state in REVEALED:
            self.release_call(p, m)

    # --------------------------------------------------------------- release

    def _call_unscored(self: Engine, p: Project, m: Moment, reason: str) -> None:
        body = {
            "result": "unscored",
            "checked_by": "runner",
            "check": None,
            "outcome_kind": "common",
            "catch": False,
            "unscored_reason": reason,
            "supersedes": None,
        }
        self.append("call.scored", body, project=p.id, change=m.change_id, moment=m.id)
        m.state = ask.step(m.state, "settle")
        self.commit_question(m, "unscored")
        self.notify("inbox")
        self.notify("question", m.id)

    def release_call(self: Engine, p: Project, m: Moment) -> None:
        """The only place a Call it result leaves the key store."""
        k = self.keys.reveal(m.id, m)
        body = {
            "check_kind": CALL_KIND,
            "check": m.id,
            "how": k.how,
            "base_tree": k.base_tree,
            "head_tree": k.head_tree,
            "steps": [
                {
                    "step": st.step,
                    "command": st.command,
                    "exit": st.exit,
                    "failing": list(st.failing),
                    "output_sha256": st.output_sha256,
                }
                for st in k.steps
            ],
            "results": [
                {
                    "id": t.id,
                    "result": t.result,
                    "assert_line": None,
                    "fail_line": t.fail_line,
                }
                for t in k.tests
            ],
            "undone_paths": list(k.undone_paths),
            "duration_s": k.duration_s,
            "rerun_of": None,
            "reason": None,
            "extra": dict(k.extra or {}),
        }
        ran = self.append(
            "check.ran", body, project=p.id, change=m.change_id, moment=m.id
        )
        if m.state == "sealed":
            sc = call_it.score(m.answer, k)  # type: ignore[arg-type]
            if sc is not None:
                scored = {
                    "result": sc.result,
                    "checked_by": "runner",
                    "check": ran["id"],
                    "outcome_kind": sc.outcome_kind,
                    "catch": sc.catch,
                    "unscored_reason": sc.unscored_reason,
                    "supersedes": None,
                }
                self.append(
                    "call.scored", scored, project=p.id, change=m.change_id, moment=m.id
                )
            m.state = ask.step(m.state, "settle")
        self.keys.discard(m.id)
        self.commit_question(m, self.outcome_word(m))
        self.notify("inbox")
        self.notify("question", m.id)

    def callit_revealed(self: Engine, p: Project, m: Moment) -> None:
        if self.keys.has(m.id):
            self.release_call(p, m)
            return
        if m.id not in self.call_checks and m.state != "sealed":
            self.commit_question(m, self.outcome_word(m))

    def callit_end_change(self: Engine, p: Project, s: Session) -> None:
        """A commit or branch switch: a call still waiting for green is not scored."""
        ep, s.episode = s.episode, None
        if ep is None:
            return
        self._call_cancel(ep.get("red_check"))
        m = self.moments.get(ep.get("moment") or "")
        if m is None or ep.get("green_tree"):
            return
        if m.state == "held":
            self.settle_held(p, m)
        if (
            m.state == "sealed"
            and m.id not in self.call_checks
            and not self.keys.has(m.id)
        ):
            self._call_unscored(p, m, "never-green")

    def call_running(self: Engine) -> bool:
        return bool(self.call_checks)

    def resume_calls(self: Engine) -> None:
        """After a restart: rerun a red run or a fix run that was lost."""
        for s in self.sessions.values():
            ep = s.episode
            p = self.projects.get(s.st.project_id)
            if ep is None or p is None:
                continue
            m = self.moments.get(ep.get("moment") or "")
            try:
                if ep.get("red_status") == "control" and not ep.get("decided"):
                    ep["red_status"] = None
                    self._maybe_red_check(p, s, ep)
                elif (
                    m is not None
                    and m.state in ("held", "sealed")
                    and ep.get("green_tree")
                    and not self.keys.has(m.id)
                ):
                    self._fix_check(p, s, ep, m)
            except Exception:
                _LOGGER.exception("cannot resume episode %s", ep.get("id"))
