"""The engine's checks, the release of results and the moment changes.

A mixin for `engine.Engine`, split out to keep each file under the size limit.
`release` is the only place a result leaves the key store.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

from firsthand import ask
from firsthand.keys import agent_output
from firsthand.model import REVEALED, Candidate, CheckOutcome, Moment, SpoolEvent
from firsthand.moments.revert_test import MatchInput, RunContext
from firsthand.record import new_ulid
from firsthand.state import Check, Project, Session

if TYPE_CHECKING:
    from firsthand.engine import Engine

_LOGGER = logging.getLogger("firsthand.engine")
RUNNING = ("control", "undoing")


class Checks:
    """Mixed into Engine. `self` is always an Engine."""

    # ------------------------------------------------------------- checks

    def start_check(self: Engine, p: Project, s: Session, tree: str) -> None:
        proj = self.config.project(p.id)
        task = s.st.task
        if proj is None or not proj.test_command or task is None:
            return
        if self.brief_holds(p, s):
            self.brief_early(p, s, tree)  # the Brief's own check, on its one test
            return
        cand = self._match(p, s, tree, proj)
        if cand is None:
            return
        c = self.check_of(p.check or "")
        if c is not None and c.cand.head_tree == tree and c.cand.task_id == task.id:
            return
        if c is not None and c.cand.task_id == task.id and not c.decided:
            self.cancel(c)
        elif c is not None and c.status in RUNNING:
            p.queued = (s.key, cand)
            return
        self.launch(p, Check(cand, s.key))

    def _match(
        self: Engine, p: Project, s: Session, tree: str, proj, base: str | None = None
    ) -> Candidate | None:
        task = s.st.task
        assert task is not None
        base = base or task.base_tree
        store = self.store(p.id)
        changes = store.diff(base, tree)
        mi = MatchInput(
            project_id=p.id,
            project_root=p.root,
            task_id=task.id,
            change_id=s.st.change_id or task.change_id,
            base_tree=base,
            head_tree=tree,
            changes=changes,
            test_command=proj.test_command,
            high_stakes=proj.high_stakes,
        )
        return self.module.match(mi, store, new_ulid)

    def cancel(self: Engine, c: Check) -> None:
        c.status = "cancelled"
        c.cancel.set()
        self.keys.discard(c.id)

    def launch(self: Engine, p: Project, c: Check) -> None:
        self.checks[c.id] = c
        if c.rerun_of is None:
            p.check = c.id
        self._executor(lambda: self._worker(p, c))

    def _worker(self: Engine, p: Project, c: Check) -> None:
        s = self.sessions.get(c.skey)
        settings = self.config.load()
        proj = self.config.project(p.id)
        ctx = RunContext(
            store=self.store(p.id),
            project=proj,
            venv_hint=s.st.venv if s else None,
            time_limit_s=float(settings.check_time_limit_s),
            on_control=lambda ok: self.on_control(p, c, ok),
            cancel=c.cancel,
        )
        try:
            outcome = self.module.run(c.cand, ctx)
        except Exception:
            _LOGGER.exception("check %s failed", c.id)
            outcome = CheckOutcome(None, "snapshot failed", "setup")
        self.on_finished(p, c, outcome)

    def on_control(self: Engine, p: Project, c: Check, ok: bool) -> None:
        with self._mutex:
            if c.status == "cancelled" or c.rerun_of is not None:
                return
            c.status = "undoing" if ok else "failed"
            s = self.sessions.get(c.skey)
            if ok and s is not None:
                self.try_offer(p, s, None)
            elif s is not None:
                self.answer_deferred(p, s)
            self.checkpoint()

    def try_offer(self: Engine, p: Project, s: Session, ev: SpoolEvent | None) -> None:
        """Ask, or decide not to. It never looks at a result."""
        c = self.check_of(p.check or "")
        if (
            c is None
            or c.decided
            or c.status not in ("undoing", "finished")
            or c.cand.head_tree != s.done_tree
            or c.skey != s.key
        ):
            return
        c.decided = True
        at = ev.at if ev is not None else self.now()
        reason = (
            ask.gates(self.gate_input(p, s, at)) if self.live(p) is None else "change"
        )
        if reason is None:
            self.offer(p, s, c, at)
            self.answer_deferred(p, s)
            return
        c.silent = True
        self.log(f"check {c.id} not asked: {reason}")
        if self.keys.has(c.id):
            self.release(p, c)
            self.answer_deferred(p, s)

    def gate_input(self: Engine, p: Project, s: Session, at: str) -> ask.GateInput:
        settings = self.config.load()
        proj = self.config.project(p.id)
        task = s.st.task
        today = self.day(at)
        quiet = (
            s.st.quiet
            or settings.quiet_today == today.isoformat()
            or bool(proj and proj.quiet)
        )
        branch = s.st.head.branch if s.st.head else None
        return ask.GateInput(
            dial=settings.dial,
            quiet=quiet,
            pressure=ask.is_pressure(branch, task.prompts if task else ()),
            asked_today=self.asked_today(today),
            daily_limit=settings.daily_limit,
            change_asked=s.st.change_asked,
            first_prompt_turn=s.st.turn_first_of_day,
            session_stopped=s.st.skips >= 2,
        )

    def asked_today(self: Engine, today: date) -> int:
        not_counted = {
            e["moment"]
            for e in self.record.events(types=("moment.closed",))
            if e["body"].get("how") in ("unseen", "wrong-start")
            or (
                e["body"].get("how") == "fix-started" and e["body"].get("seen") is False
            )
        }
        return sum(
            1
            for e in self.record.events(types=("moment.offered",))
            if self.day(e["at"]) == today and e["moment"] not in not_counted
        )

    def offer(self: Engine, p: Project, s: Session, c: Check, at: str) -> None:
        task = s.st.task
        assert task is not None
        cand = c.cand
        m = Moment(
            id=c.id,
            kind=cand.kind,
            state="open",
            project_id=p.id,
            change_id=cand.change_id,
            task_id=task.id,
            session=s.st.session,
            task_name=task.name,
            base_at=task.base_at,
            base_tree=cand.base_tree,
            head_tree=cand.head_tree,
            tests=cand.tests,
            how=cand.how,
            high_stakes=cand.high_stakes,
            offered_at=at,
        )
        self.moments[m.id] = m
        p.live = m.id
        s.st.change_asked = True
        if self.current_event:
            self.offered_in[m.id] = self.current_event
        body = {
            "moment_kind": cand.kind,
            "form": "single" if len(cand.tests) == 1 else "pick",
            "skill": self.module.SKILL,
            "break": "done",
            "fading": "full",
            "task": task.id,
            "base_tree": cand.base_tree,
            "head_tree": cand.head_tree,
            "how": cand.how,
            "tests": [
                {
                    "n": t.n,
                    "id": t.id,
                    "path": t.path,
                    "line": t.line,
                    "status": t.status,
                    "assert_lines": list(t.assert_lines),
                }
                for t in cand.tests
            ],
            "high_stakes": cand.high_stakes,
            "replaces": p.replaces,
        }
        p.replaces = None
        self.append(
            "moment.offered",
            body,
            project=p.id,
            change=cand.change_id,
            moment=m.id,
            at=at,
        )
        self.prune_moments()
        self.notify("inbox")

    def on_finished(self: Engine, p: Project, c: Check, outcome: CheckOutcome) -> None:
        with self._mutex:
            try:
                self._finished(p, c, outcome)
            finally:
                self._next_queued(p)
                s = self.sessions.get(c.skey)
                if s is not None:
                    self.answer_deferred(p, s)
                self.checkpoint()

    def _finished(self: Engine, p: Project, c: Check, outcome: CheckOutcome) -> None:
        if c.status == "cancelled" or (
            outcome.key is None and outcome.unavailable is None
        ):
            c.status = "cancelled"
            self.checks.pop(c.id, None)
            return
        if c.rerun_of is not None:
            self.dispute_finished(p, c, outcome)
            return
        m = self.moments.get(c.id)
        if outcome.unavailable:
            self._unavailable(p, c, m, outcome)
            return
        assert outcome.key is not None
        self.keys.put(outcome.key)
        c.status = "finished"
        if (m is not None and m.state in REVEALED) or (m is None and c.silent):
            self.release(p, c)

    def _unavailable(
        self: Engine, p: Project, c: Check, m: Moment | None, o: CheckOutcome
    ) -> None:
        c.status = "unavailable"
        steps = o.steps[-1:] if o.steps else ()
        body = {
            "check_kind": c.cand.kind,
            "check": c.id,
            "reason": o.unavailable,
            "step": o.step or "setup",
            "base_tree": c.cand.base_tree,
            "head_tree": c.cand.head_tree,
            "command": steps[0].command if steps else None,
            "exit": steps[0].exit if steps else None,
        }
        self.append(
            "check.unavailable",
            body,
            project=p.id,
            change=c.cand.change_id,
            moment=m.id if m else None,
        )
        self.checks.pop(c.id, None)
        if m is not None and m.state == "held":
            m.state, m.pending = "open", None
        if m is not None and m.state == "open":
            self.close_moment(p, m, "check-dropped", self.now())
        elif m is not None and m.state == "sealed":
            body = {
                "result": "unscored",
                "checked_by": "runner",
                "check": None,
                "outcome_kind": "common",
                "catch": False,
                "unscored_reason": "check-unavailable",
                "supersedes": None,
            }
            self.append(
                "call.scored", body, project=p.id, change=m.change_id, moment=m.id
            )
            m.state = ask.step(m.state, "settle")
            self.commit_question(m, "unscored")
        self.notify("inbox")
        if m is not None:
            self.notify("question", m.id)

    def _next_queued(self: Engine, p: Project) -> None:
        c = self.check_of(p.check or "")
        if p.queued is None or (c is not None and c.status in RUNNING):
            return
        key, cand = p.queued
        p.queued = None
        self.launch(p, Check(cand, key))

    # ------------------------------------------------------------- release

    def release(
        self: Engine, p: Project, c: Check, *, commit: bool = True
    ) -> str | None:
        """The only place a result leaves the key store."""
        m = self.moments.get(c.id)
        s = self.sessions.get(c.skey)
        k = self.keys.reveal(c.id, m, silent=c.silent)
        ran = self.append(
            "check.ran",
            self._ran_body(c, k),
            project=p.id,
            change=c.cand.change_id,
            moment=m.id if m else None,
        )
        said = (
            self._score(p, m, k, ran) if m is not None and m.state == "sealed" else None
        )
        self._findings(p, c, s, m, k, ran)
        self.keys.discard(c.id)
        self.checks.pop(c.id, None)
        if m is not None and commit:
            self.commit_question(m, self.outcome_word(m))
        self.notify("inbox")
        self.notify("question", m.id if m else None)
        return said

    def _ran_body(self: Engine, c: Check, k) -> dict:
        return {
            "check_kind": c.cand.kind,
            "check": c.id,
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
            "rerun_of": c.rerun_of,
            "reason": c.reason,
        }

    def _score(self: Engine, p: Project, m: Moment, k, ran: dict) -> str | None:
        sc = self.mod(m).score(m.answer, k)
        if sc is not None:
            body = {
                "result": sc.result,
                "checked_by": "runner",
                "check": ran["id"],
                "outcome_kind": sc.outcome_kind,
                "catch": sc.catch,
                "unscored_reason": sc.unscored_reason,
                "supersedes": None,
            }
            self.append(
                "call.scored", body, project=p.id, change=m.change_id, moment=m.id
            )
        m.state = ask.step(m.state, "settle")
        if m.channel != "chat":
            return None
        return agent_output(
            "result", moment=m, store=self.keys, ctx=self.ctx(m.task_name)
        )

    def _findings(
        self: Engine,
        p: Project,
        c: Check,
        s: Session | None,
        m: Moment | None,
        k,
        ran: dict,
    ) -> None:
        found = self.module.finding(k)
        if not found:
            return
        fact = self._fact_due(c, s, m, k)
        if m is None or fact:
            self._post_note(p, c, k, found, ran, fact)
        if s is None:
            return
        to_agent = self.config.load().findings_to_agent
        if to_agent and not (m is not None and m.channel == "chat"):
            text = agent_output(
                "finding",
                moment=m,
                store=self.keys,
                check_id=c.id,
                silent=c.silent,
                ctx=self.ctx(),
            )
            if text:
                s.queue.append({"text": text, "check": c.id})
        if fact:
            s.fact_due = agent_output(
                "fact",
                moment=m,
                store=self.keys,
                check_id=c.id,
                silent=c.silent,
                ctx=self.ctx(high_stakes=c.cand.high_stakes),
            )
            s.fact_check = c.id

    @staticmethod
    def _fact_due(c: Check, s: Session | None, m: Moment | None, k) -> bool:
        """A test still passes on a high-stakes change, not yet printed, nobody answered."""
        passes = any(t.result == "still_passes" for t in k.tests)
        nobody = m is None or m.state in ("skipped", "closed")
        printed = s is None or s.st.fact_printed
        return bool(passes and c.cand.high_stakes and nobody and not printed)

    def _post_note(
        self: Engine, p: Project, c: Check, k, found, ran: dict, fact: bool
    ) -> None:
        from firsthand import words  # note_fact is record text, not an agent line

        body = {
            "note_kind": c.cand.kind,
            "check": ran["id"],
            "fact": words.note_fact(k),
            "evidence": [
                {
                    "test": t.id,
                    "path": t.id.split("::", 1)[0],
                    "line": t.assert_line or t.fail_line,
                }
                for t in found
            ],
            "printed": "fact" if fact else None,
            "high_stakes": c.cand.high_stakes,
        }
        self.append("note.posted", body, project=p.id, change=c.cand.change_id)

    def outcome_word(self: Engine, m: Moment) -> str:
        if m.state == "skipped":
            return "skipped"
        if m.state == "closed":
            return "closed"
        if m.answer == "dont_know":
            return "dont-know"
        scored = self.record.events(types=("call.scored",), moment=m.id)
        return scored[-1]["body"]["result"] if scored else "unscored"

    def commit_question(self: Engine, m: Moment, outcome: str) -> None:
        try:
            self.record.commit(f"question {m.id} {outcome}")
        except Exception:
            _LOGGER.exception("commit for %s failed", m.id)

    # ------------------------------------------------------- moment changes

    def seal_call(
        self: Engine,
        p: Project,
        m: Moment,
        answer: str,
        confidence: str | None,
        channel: str,
        at: str,
        picked_at: str | None = None,
    ) -> tuple[str | None, str]:
        m.state = ask.step(m.state, "seal")
        m.answer, m.confidence, m.channel, m.pending = answer, confidence, channel, None
        body = {
            "moment_kind": m.kind,
            "form": "single" if len(m.tests) == 1 else "pick",
            "answer": answer,
            "channel": channel,
            "case_chosen_by": "engine",
            "picked_at": picked_at or at,
        }
        self.append(
            "call.sealed", body, project=p.id, change=m.change_id, moment=m.id, at=at
        )
        if confidence:
            self.append(
                "call.confidence",
                {"value": confidence},
                project=p.id,
                change=m.change_id,
                moment=m.id,
                at=at,
            )
        said = self.revealed(p, m)
        if said:
            return said, "result"
        pending = agent_output(
            "pending", moment=m, store=self.keys, ctx=self.ctx(m.task_name)
        )
        self.notify("question", m.id)
        return pending, "pending"

    def skip_final(self: Engine, p: Project, m: Moment, how: str, at: str) -> str:
        m.state = ask.step(m.state, "skip_final")
        m.pending = None
        s = self.session_of(m)
        skips = 0
        if s is not None:
            s.st.skips += 1
            skips = s.st.skips
        self.append(
            "moment.skipped",
            {"moment_kind": m.kind, "how": how, "session_skips": skips},
            project=p.id,
            change=m.change_id,
            moment=m.id,
            at=at,
        )
        self.revealed(p, m)
        self.notify("inbox")
        ack = "skip2" if skips >= 2 else "skip"
        return (
            agent_output(
                "ack", moment=m, store=self.keys, ctx=self.ctx(m.task_name, ack=ack)
            )
            or ""
        )

    def close_moment(self: Engine, p: Project, m: Moment, how: str, at: str) -> None:
        if m.state == "held":
            m.state, m.pending = "open", None
        m.state = ask.step(m.state, "close")
        m.close_how = how  # type: ignore[assignment]
        body: dict[str, object] = {"moment_kind": m.kind, "how": how}
        if how == "fix-started":
            body["seen"] = bool(m.seen or m.opened)
            if not body["seen"]:
                # Closed before anyone saw it: it used neither the day's question
                # nor the change's (decision 11), so a later moment may still ask.
                s = self.session_of(m)
                if s is not None and s.st.change_id == m.change_id:
                    s.st.change_asked = False
        self.append(
            "moment.closed",
            body,
            project=p.id,
            change=m.change_id,
            moment=m.id,
            at=at,
        )
        self.revealed(p, m)
        self.notify("inbox")
        self.notify("question", m.id)

    def settle_held(self: Engine, p: Project, m: Moment) -> None:
        pending = m.pending or {}
        if pending.get("kind") == "skip":
            self.skip_final(p, m, "room", self.now())
            return
        self.seal_call(
            p,
            m,
            pending.get("answer", "dont_know"),
            pending.get("confidence"),
            "room",
            self.now(),
            picked_at=pending.get("at"),
        )

    def revealed(self: Engine, p: Project, m: Moment) -> str | None:
        """Called whenever a moment enters sealed, skipped or closed."""
        if m.kind == "call_it":
            self.callit_revealed(p, m)
            return None
        if m.kind == "brief":
            self.brief_revealed(p, m)
            return None
        c = self.check_of(m.id)
        if self.keys.has(m.id) and c is not None:
            return self.release(p, c)
        over = c is None or c.status not in (*RUNNING, "finished")
        if over and m.state != "sealed":
            self.commit_question(m, self.outcome_word(m))
        return None

    def end_change(self: Engine, p: Project, s: Session, at: str) -> None:
        """A commit or a branch switch."""
        m = self.live(p)
        if m is not None and m.state == "open" and not m.seen:
            self.close_moment(p, m, "unseen", at)
        if "call_it" in self.modules:
            self.callit_end_change(p, s)
        if "brief" in self.modules:
            self.brief_end_change(p, s)
        c = self.check_of(p.check or "")
        if c is None or c.skey != s.key or c.decided:
            return
        if c.status in RUNNING:
            self.cancel(c)
        elif c.status == "finished":
            c.decided, c.silent = True, True
            self.release(p, c)

    # ---------------------------------------------------------- delivery

    def delivered(self: Engine, event_id: str, ok: bool) -> None:
        with self._mutex:
            items = self.carried.pop(event_id, [])
            if not ok:
                for s in self.sessions.values():
                    for q in s.queue:
                        if q.get("sent") == event_id:
                            q.pop("sent")
                return
            for kind, ref in items:
                try:
                    self._delivered_item(event_id, kind, ref)
                except Exception:
                    _LOGGER.exception("delivery of %s failed", event_id)
            self.checkpoint()

    def _delivered_item(self: Engine, event_id: str, kind: str, ref: str) -> None:
        handler = {
            "question": self._delivered_question,
            "fact": self._delivered_fact,
            "finding": self._delivered_finding,
            "result": self._delivered_result,
            "work": self._delivered_work,
        }.get(kind)
        if handler is not None:
            handler(event_id, ref)
        elif kind in ("sent", "confirm", "brief_note"):
            self.brief_delivered(event_id, kind, ref)

    def _delivered_question(self: Engine, event_id: str, ref: str) -> None:
        m = self.moments.get(ref)
        if m is None:
            return
        m.seen = True
        if self.config.load().work_computer:
            self.work_notice_done = True  # the line carried the one-time sentence
        self._line_delivered(
            m.project_id, m.task_id, m.change_id, event_id, "question", m.id
        )

    def _delivered_fact(self: Engine, event_id: str, ref: str) -> None:
        s = self.sessions.get(ref)
        if s is None:
            return
        check = s.fact_check
        s.st.fact_printed, s.fact_due, s.fact_check = True, None, None
        self._session_delivered(s, event_id, "fact", check)

    def _delivered_finding(self: Engine, event_id: str, ref: str) -> None:
        self._delivered_queued(event_id, ref, "finding")

    def _delivered_work(self: Engine, event_id: str, ref: str) -> None:
        self._delivered_queued(event_id, ref, "work")

    def _delivered_queued(self: Engine, event_id: str, ref: str, kind: str) -> None:
        """Queued agent-only lines of this kind and check were delivered."""
        for s in self.sessions.values():
            before = len(s.queue)
            s.queue = [
                q
                for q in s.queue
                if q["check"] != ref or q.get("kind", "finding") != kind
            ]
            if len(s.queue) != before:
                self._session_delivered(s, event_id, kind, ref)

    def _delivered_result(self: Engine, event_id: str, ref: str) -> None:
        m = self.moments.get(ref)
        if m is not None:
            m.opened = True
            self._line_delivered(
                m.project_id, m.task_id, m.change_id, event_id, "result", m.id
            )

    def _session_delivered(
        self: Engine, s: Session, event_id: str, line: str, check: str | None
    ) -> None:
        task = s.st.task.id if s.st.task else None
        self._line_delivered(
            s.st.project_id, task, s.st.change_id, event_id, line, check
        )

    def _line_delivered(
        self: Engine,
        pid: str,
        task: str | None,
        change: str | None,
        event_id: str,
        line: str,
        check: str | None,
    ) -> None:
        body = {
            "task": task,
            "kind": "line_delivered",
            "spool_id": event_id,
            "line": line,
            "check": check,
        }
        self.append("task.event", body, project=pid, change=change)
