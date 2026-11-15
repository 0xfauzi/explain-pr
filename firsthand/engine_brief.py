"""Brief in the engine: the trigger, the line, the done check and the release.

A mixin for `engine.Engine`. One Brief moment walks through four phases, kept in
`Moment.extra["phase"]`:

- `line`: open. The question asks for one line. A chat reply, a Room answer or
  `firsthand answer` seals it, and the line goes to the agent as work product.
- `building`: sealed. The agent works. Nothing is shown until the next done signal.
- `checking`, then `confirm`: at that done signal the first test added in the task
  is found and the Revert test's check runs on it alone. Once its control run
  passes, "Is this your check?" is asked. The key stays locked until yes or no.
- `done`: settled.

Being asked never depends on what a run found: the gates decide at the first edits,
the line is sealed before any test exists, and the confirm is asked as soon as the
control run passes, whatever the undone run then finds. `release_brief` is the only
place a Brief result leaves the key store.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from firsthand import ask, gitwatch
from firsthand.keys import agent_output
from firsthand.model import Candidate, CheckOutcome, EngineError, Moment, SpoolEvent
from firsthand.moments import brief, revert_test
from firsthand.moments.revert_test import RunContext
from firsthand.record import new_ulid
from firsthand.state import Project, Session

if TYPE_CHECKING:
    from firsthand.engine import Engine

_LOGGER = logging.getLogger("firsthand.engine")
BRIEF_KIND = brief.KIND


@dataclass(eq=False)
class BriefCheck:
    cand: Candidate
    skey: str
    status: str = "control"  # control, undoing, finished, cancelled
    cancel: threading.Event = field(default_factory=threading.Event)

    @property
    def id(self) -> str:
        return self.cand.check_id


def _phase(m: Moment) -> str:
    return str((m.extra or {}).get("phase") or "line")


def _set(m: Moment, **values: object) -> None:
    m.extra = {**(m.extra or {}), **values}


class Brief:
    """Mixed into Engine. `self` is always an Engine."""

    # ------------------------------------------------------------- lookups

    def brief_live(self: Engine, p: Project, s: Session) -> Moment | None:
        """The live Brief of this session's change, if any."""
        m = self.live(p)
        if (
            m is None
            or m.kind != BRIEF_KIND
            or m.session != s.st.session
            or m.change_id != s.st.change_id
        ):
            return None
        return m

    def brief_holds(self: Engine, p: Project, s: Session) -> bool:
        """A live Brief owns this change's done check: the Revert test stays out."""
        return "brief" in self.modules and self.brief_live(p, s) is not None

    def brief_confirming(self: Engine, m: Moment) -> bool:
        extra = m.extra or {}
        return (
            m.kind == BRIEF_KIND
            and m.state == "sealed"
            and _phase(m) == "confirm"
            and not extra.get("confirm")
        )

    # ------------------------------------------------------------- trigger

    def brief_event(self: Engine, p: Project, s: Session, ev: SpoolEvent) -> None:
        """The trigger (a task start, then its first edits or a plan) and the red ids."""
        if BRIEF_KIND not in self.modules:
            return
        task = s.st.task
        if ev.event == "prompt_submit":
            if task is not None and task.first_prompt_id == ev.id:
                self._brief_watch(p, s, ev)
        elif ev.event == "turn_end":
            if s.brief is not None:
                s.brief["open"] = False  # only the first response of a task counts
        elif ev.event == "tool_failed":
            self._brief_red(p, s, ev)
        else:
            self._brief_first_edits(p, s, ev)

    def _brief_red(self: Engine, p: Project, s: Session, ev: SpoolEvent) -> None:
        """The first failing test run after the line: the test written first is the check."""
        m = self.brief_live(p, s)
        proj = self.config.project(p.id)
        if m is None or not ev.failing or _phase(m) != "building":
            return
        if proj is None or not gitwatch.is_test_run(
            ev.command or "", proj.test_command
        ):
            return
        if not (m.extra or {}).get("red_ids"):
            _set(m, red_ids=list(ev.failing))

    def _brief_first_edits(
        self: Engine, p: Project, s: Session, ev: SpoolEvent
    ) -> None:
        w, task = s.brief, s.st.task
        if w is None or task is None or w.get("task") != task.id or not w.get("open"):
            return
        if ev.event == "after_tool" and ev.tool == "edit":
            root = p.root.rstrip("/") + "/"
            w["paths"] = list(w.get("paths", ())) + [
                x.removeprefix(root) for x in ev.paths
            ]
        elif ev.event == "before_tool" and ev.tool == "plan":
            w["plan"] = True
        else:
            return
        cats = brief.categories(w.get("paths", ()))
        if brief.qualifies(cats, bool(w.get("plan"))):
            w["open"] = False
            self._brief_try_offer(p, s, ev, cats)

    def _brief_watch(self: Engine, p: Project, s: Session, ev: SpoolEvent) -> None:
        proj = self.config.project(p.id)
        task = s.st.task
        assert task is not None
        named = brief.names_check(ev.prompt, proj.test_command if proj else None)
        s.brief = {
            "task": task.id,
            "open": not named and not brief.is_question(ev.prompt),
            "paths": [],
            "plan": False,
        }

    def _brief_try_offer(
        self: Engine, p: Project, s: Session, ev: SpoolEvent, cats: list[str]
    ) -> None:
        if self._pytest_project(p) is None:
            self.log("brief not asked: not a pytest project")
            return
        reason = (
            ask.gates(self.gate_input(p, s, ev.at))
            if self.live(p) is None
            else "change"
        )
        if reason is not None:
            self.log(f"brief not asked: {reason}")
            return
        self._brief_offer(p, s, ev, cats)

    def _brief_offer(
        self: Engine, p: Project, s: Session, ev: SpoolEvent, cats: list[str]
    ) -> None:
        task = s.st.task
        assert task is not None
        m = Moment(
            id=new_ulid(),
            kind=BRIEF_KIND,
            state="open",
            project_id=p.id,
            change_id=s.st.change_id or task.change_id,
            task_id=task.id,
            session=s.st.session,
            task_name=task.name,
            base_at=task.base_at,
            base_tree=task.base_tree,
            head_tree=task.base_tree,
            tests=(),
            how="pytest",
            high_stakes=None,
            offered_at=ev.at,
            extra={"phase": "line", "line": None, "categories": cats, "red_ids": []},
        )
        self.moments[m.id] = m
        p.live = m.id
        s.st.change_asked = True
        body = {
            "moment_kind": BRIEF_KIND,
            "form": "line",
            "skill": brief.SKILL,
            "break": "task_start",
            "fading": "full",
            "task": task.id,
            "base_tree": task.base_tree,
            "head_tree": task.base_tree,
            "how": "pytest",
            "tests": [],
            "high_stakes": None,
            "replaces": None,
            "categories": cats,
            "plan": bool((s.brief or {}).get("plan")),
        }
        self.append(
            "moment.offered",
            body,
            project=p.id,
            change=m.change_id,
            moment=m.id,
            at=ev.at,
        )
        self.prune_moments()
        self.notify("inbox")

    # -------------------------------------------------------------- the line

    def brief_prompt(
        self: Engine,
        p: Project,
        s: Session,
        m: Moment,
        ev: SpoolEvent,
        printable: list[str],
        carried: list,
    ) -> bool:
        """A prompt while a Brief is live. Returns True when the prompt was consumed.

        The line itself is not consumed: it is also the person's message to the
        agent, and it may start the next task of the change.
        """
        text = ev.prompt or ""
        if m.state == "open":
            return self._brief_line_prompt(p, s, m, ev, printable, carried)
        if not self.brief_confirming(m) or not (m.extra or {}).get("confirm_seen"):
            return False
        reply = brief.parse_reply(text)
        if reply is not None:
            said = self.brief_confirm(p, m, reply.answer, "chat", ev.at)
            if said:
                printable.append(said)
                carried.append(("result", m.id))
            return True
        if ask.control_word(text) == "skip":
            self.release_brief(p, m, reason="skipped")
            printable.append(
                agent_output(
                    "ack",
                    moment=m,
                    store=self.keys,
                    ctx=self.ctx(m.task_name, ack="skip"),
                )
                or ""
            )
            return True
        self.release_brief(p, m, reason="moved-on")
        return False

    def _brief_line_prompt(
        self: Engine,
        p: Project,
        s: Session,
        m: Moment,
        ev: SpoolEvent,
        printable: list[str],
        carried: list,
    ) -> bool:
        text = ev.prompt or ""
        if not m.seen:
            task = s.st.task
            if task is not None and task.done:  # this prompt starts another task
                self.close_moment(p, m, "unseen", ev.at)
            return False
        word = ask.control_word(text)
        if word == "skip":
            printable.append(self.skip_final(p, m, "chat", ev.at))
            return True
        if word is not None:
            printable.append(self.set_quiet_word(p, s, m, word, ev.at))
            return True
        line = brief.line_of_reply(text)
        if line is None:
            # Not "check: ...": the person is talking to the agent and moved on.
            self.close_moment(p, m, "moved-on", ev.at)
            return False
        said = self.brief_seal_line(p, m, line, "chat", ev.at)
        if said:
            printable.append(said)
            carried.append(("sent", m.id))
        return m.answer == "dont_know"

    def brief_seal_line(
        self: Engine, p: Project, m: Moment, text: str, channel: str, at: str
    ) -> str | None:
        """Seal the person's line and queue it for the agent. Returns the line to print."""
        line = brief.clean_line(text)
        if not line:
            raise EngineError("Write your check in one line.", "invalid")
        dont_know = brief.is_dont_know(line)
        m.state = ask.step(m.state, "seal")
        m.answer = "dont_know" if dont_know else "line"  # type: ignore[assignment]
        m.channel, m.pending = channel, None  # type: ignore[assignment]
        _set(
            m,
            phase="done" if dont_know else "building",
            line=None if dont_know else line,
            line_at=at,
        )
        body = {
            "moment_kind": BRIEF_KIND,
            "form": "line",
            "answer": m.answer,
            "line": None if dont_know else line,
            "channel": channel,
            "case_chosen_by": "engine",
            "picked_at": at,
        }
        self.append(
            "call.sealed", body, project=p.id, change=m.change_id, moment=m.id, at=at
        )
        if dont_know:
            m.state = ask.step(m.state, "settle")
            self.commit_question(m, "dont-know")
            self.notify("inbox")
            self.notify("question", m.id)
            return None
        s = self.session_of(m)
        work = agent_output("work", moment=m, store=self.keys, ctx=self.ctx())
        if s is not None and work:
            s.queue.append({"text": work, "check": m.id, "kind": "work"})
        self.notify("inbox")
        self.notify("question", m.id)
        return agent_output(
            "pending", moment=m, store=self.keys, ctx=self.ctx(m.task_name)
        )

    # ---------------------------------------------------------- done check

    def _brief_case(
        self: Engine, p: Project, m: Moment, tree: str
    ) -> tuple[Candidate | None, str | None]:
        """The check for this tree: the first test added since the base, kept, with the
        non-test changes undone. Or the reason there is none."""
        store = self.store(p.id)
        changes = store.diff(m.base_tree, tree)
        source, _ = gitwatch.split_changes(changes)
        found = brief.new_tests(store, m.base_tree, tree, changes)
        item = brief.first_test(found, (m.extra or {}).get("red_ids") or ())
        if item is None:
            return None, "no-test"
        if not source:
            return None, "no-change"
        cand = Candidate(
            kind=BRIEF_KIND,
            check_id=m.id,
            project_id=p.id,
            project_root=p.root,
            task_id=m.task_id,
            change_id=m.change_id,
            base_tree=m.base_tree,
            head_tree=tree,
            source_changes=source,
            tests=(item,),
            how="pytest",
            high_stakes=None,
        )
        return cand, None

    def brief_early(self: Engine, p: Project, s: Session, tree: str) -> None:
        """The agent's own test run passed: start the check now, so the confirm is often
        ready at the done signal (as the Revert test does, learning.md section 4.1)."""
        m = self.brief_live(p, s)
        if m is None or m.state != "sealed" or _phase(m) != "building":
            return
        old = self.brief_checks.get(m.id)
        if old is not None and old.cand.head_tree == tree:
            return
        cand, _ = self._brief_case(p, m, tree)
        if cand is None:
            return
        self._brief_drop(m.id)
        _set(m, early_tree=tree)
        self._brief_launch(p, BriefCheck(cand, s.key))

    def _brief_drop(self: Engine, check_id: str) -> None:
        c = self.brief_checks.pop(check_id, None)
        if c is not None:
            c.status = "cancelled"
            c.cancel.set()
        self.keys.discard(check_id)

    def brief_done(
        self: Engine, p: Project, s: Session, ev: SpoolEvent, tree: str
    ) -> bool:
        """The done signal. True when a live Brief owns it (the Revert test stays out)."""
        m = self.brief_live(p, s) if BRIEF_KIND in self.modules else None
        if m is None:
            return False
        if m.state != "sealed" or _phase(m) != "building":
            return True
        _set(m, done_at=ev.at, done_event=ev.id, done_tree=tree)
        early = self.brief_checks.get(m.id)
        reuse = self._brief_reuse(m, tree)
        if not reuse:
            self._brief_drop(m.id)
        cand, reason = self._brief_case(p, m, tree)
        if cand is None:
            self._brief_none(p, s, m, reason or "no-test")
            return True
        item = cand.tests[0]
        m.tests, m.head_tree = (item,), tree
        ready = reuse and (
            self.keys.has(m.id) or (early is not None and early.status != "control")
        )
        _set(
            m,
            phase="confirm" if ready else "checking",
            test=item.id,
            confirm=None,
            confirm_seen=False,
        )
        if not reuse:
            self._brief_launch(p, BriefCheck(cand, s.key))
        return True

    def _brief_reuse(self: Engine, m: Moment, tree: str) -> bool:
        """The early check ran on this same tree and is still running or has its key."""
        same = (m.extra or {}).get("early_tree") == tree
        return same and (m.id in self.brief_checks or self.keys.has(m.id))

    def _brief_none(
        self: Engine, p: Project, s: Session, m: Moment, reason: str
    ) -> None:
        """No test to check, or no change to undo: not scored, said at this stop."""
        self._brief_drop(m.id)
        self._brief_unscored(p, m, reason)
        if s.brief is None:
            s.brief = {"task": None, "open": False}
        s.brief["due"] = [reason, m.id]

    def _brief_launch(self: Engine, p: Project, c: BriefCheck) -> None:
        self.brief_checks[c.id] = c
        self._executor(lambda: self._brief_worker(p, c))

    def _brief_worker(self: Engine, p: Project, c: BriefCheck) -> None:
        s = self.sessions.get(c.skey)
        settings = self.config.load()
        ctx = RunContext(
            store=self.store(p.id),
            project=self.config.project(p.id),
            venv_hint=s.st.venv if s else None,
            time_limit_s=float(settings.check_time_limit_s),
            on_control=lambda ok: self._brief_control(p, c, ok),
            cancel=c.cancel,
        )
        try:
            out = revert_test.run(c.cand, ctx)
        except Exception:
            _LOGGER.exception("brief check %s failed", c.id)
            out = CheckOutcome(None, "snapshot failed", "setup")
        with self._mutex:
            try:
                self._brief_finished(p, c, out)
            finally:
                if s is not None:
                    self.answer_deferred(p, s)
                self.checkpoint()

    def _brief_control(self: Engine, p: Project, c: BriefCheck, ok: bool) -> None:
        with self._mutex:
            m = self.moments.get(c.id)
            if c.status == "cancelled" or not ok or m is None:
                return
            c.status = "undoing"
            if m.state == "sealed" and _phase(m) == "checking":
                _set(m, phase="confirm")
                self.notify("inbox")
                self.notify("question", m.id)
            s = self.sessions.get(c.skey)
            if s is not None:
                self.answer_deferred(p, s)
            self.checkpoint()

    def _brief_finished(self: Engine, p: Project, c: BriefCheck, out) -> None:
        if self.brief_checks.get(c.id) is c:  # a newer check may have the same id
            self.brief_checks.pop(c.id)
        m = self.moments.get(c.id)
        if c.status == "cancelled" or m is None:
            return
        if out.unavailable:
            self._brief_unavailable(p, c, m, out)
        elif out.key is not None:
            self.keys.put(out.key)
            c.status = "finished"
            if m.state == "sealed" and (m.extra or {}).get("confirm"):
                self.release_brief(p, m)

    def _brief_unavailable(
        self: Engine, p: Project, c: BriefCheck, m: Moment, out
    ) -> None:
        if _phase(m) == "building":
            _set(m, early_tree=None)  # an early check: the done signal runs it again
            return
        steps = out.steps[-1:] if out.steps else ()
        body = {
            "check_kind": BRIEF_KIND,
            "check": c.id,
            "reason": out.unavailable,
            "step": out.step or "setup",
            "base_tree": c.cand.base_tree,
            "head_tree": c.cand.head_tree,
            "command": steps[0].command if steps else None,
            "exit": steps[0].exit if steps else None,
        }
        self.append(
            "check.unavailable", body, project=p.id, change=m.change_id, moment=m.id
        )
        if m.state == "sealed":
            self._brief_unscored(p, m, "check-unavailable")

    def brief_waiting(self: Engine, s: Session) -> bool:
        """The stop should wait briefly: the control run of this session's check is going."""
        return any(
            c.skey == s.key and c.status == "control"
            for c in self.brief_checks.values()
        )

    def brief_may_speak(self: Engine, p: Project, s: Session) -> bool:
        if (s.brief or {}).get("due"):
            return True
        m = self.brief_live(p, s) if BRIEF_KIND in self.modules else None
        return (
            m is not None
            and m.state == "sealed"
            and _phase(m) in ("checking", "confirm")
        )

    # ------------------------------------------------------------- the stop

    def brief_stop(
        self: Engine, p: Project, s: Session, ev: SpoolEvent
    ) -> tuple[str | None, list] | None:
        """A Brief line for this stop: the done-check note, or "Is this your check?"."""
        from firsthand import words_brief

        due = (s.brief or {}).pop("due", None) if s.brief else None
        if due:
            return words_brief.stop_line(due[0]), [("brief_note", due[1])]
        m = self.brief_live(p, s) if BRIEF_KIND in self.modules else None
        if (
            m is None
            or not self.brief_confirming(m)
            or (m.extra or {}).get("confirm_seen")
        ):
            return None
        if not ask.fact_allowed(self.gate_input(p, s, ev.at)):
            return None
        line = agent_output(
            "confirm", moment=m, store=self.keys, ctx=self.ctx(m.task_name)
        )
        return (line, [("confirm", m.id)]) if line else None

    def brief_delivered(self: Engine, event_id: str, kind: str, ref: str) -> None:
        m = self.moments.get(ref)
        if m is None:
            return
        if kind == "confirm":
            _set(m, confirm_seen=True)
            if self.config.load().work_computer:
                self.work_notice_done = True
        line = {"confirm": "question", "brief_note": "result"}.get(kind, kind)
        self._line_delivered(m.project_id, m.task_id, m.change_id, event_id, line, m.id)

    # ----------------------------------------------------- confirm, release

    def brief_confirm(
        self: Engine, p: Project, m: Moment, value: str, channel: str, at: str
    ) -> str | None:
        """Yes or no to "Is this your check?". Returns the chat lines, if any."""
        if not self.brief_confirming(m):
            raise EngineError("This question is already answered.", "state")
        if value not in ("yes", "no"):
            raise EngineError("Reply with one of: yes, no. Or skip.", "invalid")
        _set(m, confirm=value, confirm_channel=channel, confirm_seen=True)
        body = {
            "moment_kind": BRIEF_KIND,
            "value": value,
            "channel": channel,
            "test": (m.extra or {}).get("test"),
        }
        self.append(
            "call.confirmed", body, project=p.id, change=m.change_id, moment=m.id, at=at
        )
        if self.keys.has(m.id):
            return self.release_brief(p, m)
        if m.id not in self.brief_checks:
            self._brief_unscored(p, m, "check-unavailable")
            return None
        self.notify("question", m.id)
        return agent_output(
            "pending", moment=m, store=self.keys, ctx=self.ctx(m.task_name)
        )

    def release_brief(
        self: Engine, p: Project, m: Moment, *, reason: str | None = None
    ) -> str | None:
        """The only place a Brief result leaves the key store."""
        if not self.keys.has(m.id):
            c = self.brief_checks.pop(m.id, None)
            if c is not None:
                c.status = "cancelled"
                c.cancel.set()
            self._brief_unscored(p, m, reason or "check-unavailable")
            return None
        k = self.keys.reveal(m.id, m)
        ran = self.append(
            "check.ran",
            self._brief_ran_body(m, k),
            project=p.id,
            change=m.change_id,
            moment=m.id,
        )
        confirm = (m.extra or {}).get("confirm")
        sc = brief.score(confirm, k) if reason is None else None
        if reason is None and confirm == "no":
            reason = "not-your-check"
        body = {
            "result": sc.result if sc else "unscored",
            "checked_by": "runner",
            "check": ran["id"],
            "outcome_kind": sc.outcome_kind if sc else "common",
            "catch": sc.catch if sc else False,
            "unscored_reason": None if sc else reason or "check-unavailable",
            "supersedes": None,
        }
        self.append("call.scored", body, project=p.id, change=m.change_id, moment=m.id)
        m.state = ask.step(m.state, "settle")
        _set(m, phase="done")
        chat = (m.extra or {}).get("confirm_channel") == "chat"
        said = (
            agent_output("result", moment=m, store=self.keys, ctx=self.ctx(m.task_name))
            if chat and confirm
            else None
        )
        self._brief_finding(m, k, chat)
        self.keys.discard(m.id)
        self.commit_question(m, self.outcome_word(m))
        self.notify("inbox")
        self.notify("question", m.id)
        return said

    def _brief_finding(self: Engine, m: Moment, k, chat: bool) -> None:
        """A check that cannot tell done from not done is a fact about the agent's work."""
        s = self.session_of(m)
        if s is None or chat or not brief.finding(k):
            return
        if not self.config.load().findings_to_agent:
            return
        text = agent_output(
            "finding", moment=m, store=self.keys, check_id=m.id, ctx=self.ctx()
        )
        if text:
            s.queue.append({"text": text, "check": m.id})

    @staticmethod
    def _brief_ran_body(m: Moment, k) -> dict:
        return {
            "check_kind": BRIEF_KIND,
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
                    "assert_line": t.assert_line,
                    "fail_line": t.fail_line,
                }
                for t in k.tests
            ],
            "undone_paths": list(k.undone_paths),
            "duration_s": k.duration_s,
            "rerun_of": None,
            "reason": None,
        }

    def _brief_unscored(self: Engine, p: Project, m: Moment, reason: str) -> None:
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
        _set(m, phase="done")
        self.keys.discard(m.id)
        self.commit_question(m, "unscored")
        self.notify("inbox")
        self.notify("question", m.id)

    # ------------------------------------------------------- other endings

    def brief_revealed(self: Engine, p: Project, m: Moment) -> None:
        """A Brief skipped or closed in its line phase is committed at once."""
        del p
        if m.state in ("skipped", "closed"):
            self.commit_question(m, self.outcome_word(m))

    def brief_end_change(self: Engine, p: Project, s: Session) -> None:
        """A commit or a branch switch: a Brief still waiting is not scored.

        The timeline has already cleared the session's change id, so the live
        moment is matched by session only.
        """
        m = self.live(p)
        if (
            m is None
            or m.kind != BRIEF_KIND
            or m.session != s.st.session
            or m.state != "sealed"
        ):
            return
        if _phase(m) == "building":
            self._brief_unscored(p, m, "never-done")
        else:
            self.release_brief(p, m, reason="no-confirm")

    def brief_running(self: Engine) -> bool:
        return bool(self.brief_checks)

    def resume_briefs(self: Engine) -> None:
        """After a restart: run a lost done check again from the stored trees."""
        for p in self.projects.values():
            m = self.live(p)
            if m is None or m.kind != BRIEF_KIND or m.state != "sealed":
                continue
            s = self.session_of(m)
            if s is None or _phase(m) not in ("checking", "confirm"):
                continue
            if self.keys.has(m.id) or m.id in self.brief_checks:
                continue
            try:
                cand = self.candidate_for(p, m, m.id)
            except Exception:
                _LOGGER.exception("cannot resume brief %s", m.id)
                continue
            self._brief_launch(p, BriefCheck(cand, s.key, status="undoing"))
