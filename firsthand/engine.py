"""The engine: applies spool events, runs checks, asks, scores and records.

`Engine` implements `model.EngineAPI`. The loop follows build-2a-contract.md
section 8.2. Every string for an agent channel comes from `keys.agent_output`.
The Room and CLI actions and the read models live in `engine_actions.py`.
"""

from __future__ import annotations

import logging
import queue
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import UTC, date, datetime, tzinfo
from pathlib import Path
from types import ModuleType

from firsthand import ask, events, gitwatch, state, timeline
from firsthand import moments as moment_registry
from firsthand.engine_actions import Actions
from firsthand.engine_brief import Brief
from firsthand.engine_callit import CallIt
from firsthand.engine_checks import RUNNING, Checks
from firsthand.keys import KeyStore, OutputContext, agent_output
from firsthand.model import (
    Candidate,
    HookReply,
    Moment,
    SettingsStore,
    SpoolEvent,
)
from firsthand.record import Record, new_ulid
from firsthand.runner.snapshot import SnapshotStore
from firsthand.state import Check, PendingReply, Project, Session, skey
from firsthand.timeline import Observed, SessionState

_LOGGER = logging.getLogger("firsthand.engine")
DEFER_S = 0.25
SPEAKS = ("prompt_submit", "turn_end")


class Engine(Checks, Actions, CallIt, Brief):
    def __init__(
        self,
        *,
        record: Record,
        settings: SettingsStore,
        room_url: str | None,
        clock: Callable[[], datetime] | None = None,
        tz: tzinfo | None = None,
        executor: Callable[[Callable[[], None]], None] | None = None,
        moments: Sequence[ModuleType] | None = None,
        log: Callable[[str], None] | None = None,
    ) -> None:
        self.record = record
        self.config = settings
        self.room_url = room_url
        self._clock = clock or (lambda: datetime.now(UTC))
        self.tz = tz or datetime.now().astimezone().tzinfo or UTC
        self._executor = executor or self._thread_executor
        mods = tuple(moments or _registry())
        self.module = mods[0]  # the Revert test, or a test's fake
        self.modules = {m.KIND: m for m in mods}
        self._log_fn = log
        self._mutex = threading.RLock()
        self.keys = KeyStore()
        self.projects: dict[str, Project] = {}
        self.sessions: dict[str, Session] = {}
        self.moments: dict[str, Moment] = {}
        self.checks: dict[str, Check] = {}
        self.call_checks: dict = {}  # Call it runs, engine_callit.py
        self.brief_checks: dict = {}  # Brief done checks, engine_brief.py
        self.stores: dict[str, SnapshotStore] = {}
        self.offered_in: dict[str, str] = {}
        self.dispute_of: dict[str, str] = {}
        self.carried: dict[str, list[tuple[str, str]]] = {}
        self.deferred: dict[str, PendingReply] = {}
        self.seen_ids: list[str] = []
        self.first_day: str | None = None
        self.work_notice_done = False
        self.last_project: str | None = None
        self.current_event: str | None = None
        self._listeners: list[Callable[[dict], None]] = []
        self._seq = 0
        self._queue: queue.Queue | None = None
        self._closed = False
        self._load()

    # --------------------------------------------------------------- basics

    def log(self, message: str) -> None:
        if self._log_fn is not None:
            self._log_fn(message)
        else:
            _LOGGER.info(message)

    def now(self) -> str:
        return events.now_stamp(self._clock())

    def day(self, at: str) -> date:
        when = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        return when.astimezone(self.tz).date()

    def _thread_executor(self, fn: Callable[[], None]) -> None:
        if self._queue is None:
            self._queue = queue.Queue()
            threading.Thread(
                target=self._drain, name="firsthand-check", daemon=True
            ).start()
        self._queue.put(fn)

    def _drain(self) -> None:
        assert self._queue is not None
        while True:
            fn = self._queue.get()
            if fn is None:
                return
            try:
                fn()
            except Exception:
                _LOGGER.exception("check worker failed")

    def store(self, project_id: str) -> SnapshotStore:
        if project_id not in self.stores:
            root = Path(self.projects[project_id].root)
            self.stores[project_id] = SnapshotStore(root, project_id)
        return self.stores[project_id]

    def subscribe(self, fn: Callable[[dict], None]) -> Callable[[], None]:
        with self._mutex:
            self._listeners.append(fn)

        def remove() -> None:
            with self._mutex:
                if fn in self._listeners:
                    self._listeners.remove(fn)

        return remove

    def notify(self, topic: str, moment_id: str | None = None) -> None:
        self._seq += 1
        notice = {"seq": self._seq, "topic": topic, "id": moment_id}
        for fn in list(self._listeners):
            try:
                fn(notice)
            except Exception:
                _LOGGER.exception("a listener failed")

    def append(
        self,
        type_: str,
        body: dict,
        *,
        project: str,
        change: str | None,
        moment: str | None = None,
        at: str | None = None,
    ) -> dict:
        return self.record.append(
            type_,
            body,
            project=project,
            change=change,
            moment=moment,
            surface="claude-code",
            at=at or self.now(),
        )

    def ctx(
        self, task: str = "", *, ack: str | None = None, high_stakes: str | None = None
    ) -> OutputContext:
        s = self.config.load()
        return OutputContext(
            room_url=self.room_url,
            work_computer=s.work_computer,
            work_notice=s.work_computer and not self.work_notice_done,
            task_name=task,
            high_stakes=high_stakes,
            ack=ack,
        )

    # ----------------------------------------------------------- lookups

    def live(self, p: Project) -> Moment | None:
        m = self.moments.get(p.live or "")
        if m is None or m.state not in ("open", "held", "sealed"):
            p.live = None
            return None
        return m

    def session_of(self, m: Moment) -> Session | None:
        for s in self.sessions.values():
            if s.st.session == m.session and s.st.project_id == m.project_id:
                return s
        return None

    def check_of(self, check_id: str) -> Check | None:
        return self.checks.get(check_id)

    def mod(self, m: Moment) -> ModuleType:
        """The moment module that owns `m`."""
        return self.modules.get(m.kind, self.module)

    def reply_n(self, m: Moment) -> int:
        """What a moment's reply words count: its tests, or Call it's picks."""
        if m.extra and "picks" in m.extra:
            return len(m.extra["picks"])
        return len(m.tests)

    def _project(self, pid: str, root: str) -> Project:
        p = self.projects.get(pid)
        if p is None:
            p = self.projects[pid] = Project(pid, root)
        return p

    def _session(self, ev: SpoolEvent, pid: str, root: str) -> Session:
        key = skey(ev.agent, ev.session, pid)
        s = self.sessions.get(key)
        if s is None:
            st = SessionState(
                agent=ev.agent, session=ev.session, project_id=pid, project_root=root
            )
            s = self.sessions[key] = Session(key, st)
        s.last_at = ev.at
        return s

    # ------------------------------------------------------------- events

    def handle(self, ev: SpoolEvent, reply: Callable[[HookReply], None]) -> None:
        r = PendingReply(ev, reply)
        with self._mutex:
            if ev.id in self.seen_ids:
                return
            self.seen_ids = (self.seen_ids + [ev.id])[-state.MAX_SEEN :]
            self.current_event = ev.id
            try:
                self._handle(ev, r)
            except Exception:
                _LOGGER.exception("event %s failed", ev.id)
                self.log(f"event {ev.id} failed")
            finally:
                self.current_event = None
                if ev.event in SPEAKS and not r.done and r.deadline == 0.0:
                    self.answer(r, None)
                self.checkpoint()

    def answer(
        self, r: PendingReply, text: str | None, carried: list | None = None
    ) -> None:
        """Send the one reply of a prompt or a stop."""
        if r.done:
            return
        r.done = True
        if r.ev.event == "prompt_submit":
            out = HookReply(r.ev.id, r.ev.session, "prompt_submit", context=text)
        else:
            out = HookReply(r.ev.id, r.ev.session, "turn_end", visible=text)
        if text and carried:
            self.carried[r.ev.id] = carried
        try:
            r.fn(out)
        except Exception:
            _LOGGER.exception("reply for %s failed", r.ev.id)

    def _handle(self, ev: SpoolEvent, r: PendingReply) -> None:
        root = gitwatch.project_root(ev.cwd)
        pid = gitwatch.project_id(root) if root is not None else None
        settings = self.config.load()
        if pid is None or root is None or settings.dial == "off":
            return
        proj = self.config.ensure_project(pid, str(root))
        p = self._project(pid, str(root))
        s = self._session(ev, pid, str(root))
        self.last_project = pid
        first = False
        if ev.event == "prompt_submit":
            consumed, first = self._prompt_fast(p, s, ev, r)
            if consumed:
                return
        elif ev.event == "turn_end" and not self.may_speak(p, s):
            self.answer(r, None)
        tree = None
        if timeline.needs_snapshot(s.st, ev, proj.test_command):
            tree = self.store(pid).take()
        obs = Observed(tree=tree, head=gitwatch.head(root))
        effects = timeline.step(
            s.st,
            ev,
            obs,
            test_command=proj.test_command,
            first_of_day=first,
            new_id=new_ulid,
        )
        for fx in effects:
            self._effect(p, s, ev, fx)
        self._call_event(p, s, ev, tree)
        self.brief_event(p, s, ev)
        if ev.event == "turn_end" and not r.done:
            self._stop_reply(p, s, r)

    def _call_event(
        self, p: Project, s: Session, ev: SpoolEvent, tree: str | None
    ) -> None:
        """Call it's triggers that are not timeline effects."""
        if "call_it" not in self.modules:
            return
        if ev.event == "prompt_submit":
            self.callit_prompt(p, s, ev, tree)
        elif ev.event == "after_tool" and ev.tool == "edit":
            self.callit_edit(p, s, ev)
        elif ev.event == "turn_end":
            self.callit_turn_end(p, s, ev)

    def _stop_reply(self, p: Project, s: Session, r: PendingReply) -> None:
        c = self.check_of(p.check or "")
        waiting = (
            (
                c is not None
                and c.status == "control"
                and not c.decided
                and c.cand.head_tree == s.done_tree
                and c.skey == s.key
            )
            or self.call_waiting(s)
            or self.brief_waiting(s)
        )
        if waiting:
            old = self.deferred.pop(s.key, None)
            if old is not None:
                self.answer(old, None)
            r.deadline = time.monotonic() + DEFER_S
            self.deferred[s.key] = r
            return
        text, carried = self.stop_line(p, s, r.ev)
        self.answer(r, text, carried)

    def _first_prompt(self, ev: SpoolEvent) -> bool:
        today = self.day(ev.at).isoformat()
        first = self.first_day != today
        self.first_day = today
        return first

    def _prompt_fast(
        self, p: Project, s: Session, ev: SpoolEvent, r: PendingReply
    ) -> tuple[bool, bool]:
        printable: list[str] = []
        carried: list[tuple[str, str]] = []
        consumed = False
        m = self.live(p)
        if m is not None and m.state == "held":
            self.settle_held(p, m)
            m = self.live(p)
        if m is not None and m.kind == "brief":
            consumed = self.brief_prompt(p, s, m, ev, printable, carried)
        elif m is not None and m.state == "open":
            consumed = self._prompt_word(p, s, m, ev, printable, carried)
        first = False if consumed else self._first_prompt(ev)
        # A finding goes out once; it is sent again only if delivery failed. The first
        # prompt of the day holds findings back, but not the work line: it answers
        # what the person has just typed (a Brief line sealed by this prompt).
        sending = [
            q
            for q in s.queue
            if not q.get("sent") and (not first or q.get("kind") == "work")
        ]
        for q in sending:
            q["sent"] = ev.id
        agent_only = [q["text"] for q in sending]
        carried += [(q.get("kind", "finding"), q["check"]) for q in sending]
        text = self._context(printable, agent_only)
        self.answer(r, text, carried)
        return consumed, first

    def _context(self, printable: list[str], agent_only: list[str]) -> str | None:
        from firsthand import words  # context_text only joins agent_output values

        return words.context_text(printable, agent_only)

    def _prompt_word(
        self,
        p: Project,
        s: Session,
        m: Moment,
        ev: SpoolEvent,
        printable: list[str],
        carried: list,
    ) -> bool:
        reply = self.mod(m).parse_reply(ev.prompt or "", self.reply_n(m))
        word = ask.control_word(ev.prompt or "")
        if reply is not None:
            said, kind = self.seal_call(
                p, m, reply.answer, reply.confidence, "chat", ev.at
            )
            if said:
                printable.append(said)
                carried.append((kind, m.id))
            return True
        if word == "skip":
            printable.append(self.skip_final(p, m, "chat", ev.at))
            return True
        if word is not None:
            printable.append(self.set_quiet_word(p, s, m, word, ev.at))
            return True
        if m.seen:
            self.close_moment(p, m, "moved-on", ev.at)
        return False

    def _effect(
        self, p: Project, s: Session, ev: SpoolEvent, fx: timeline.Effect
    ) -> None:
        body = dict(fx.body)
        change = s.st.change_id
        if fx.kind == "change_ended":
            self.end_change(p, s, ev.at)
        elif fx.kind == "task_started":
            self.append("task.started", body, project=p.id, change=change, at=ev.at)
        elif fx.kind == "task_event":
            self.append("task.event", body, project=p.id, change=change, at=ev.at)
        elif fx.kind == "test_passed":
            if "call_it" in self.modules:
                self.callit_green(p, s, ev, body.get("tree"))  # type: ignore[arg-type]
            self.start_check(p, s, str(body["tree"]))
        elif fx.kind == "test_failed" and "call_it" in self.modules:
            self.callit_failed(p, s, ev, body)
        elif fx.kind == "done":
            self._done(p, s, ev, str(body["tree"]))

    def _done(self, p: Project, s: Session, ev: SpoolEvent, tree: str) -> None:
        task = s.st.task
        assert task is not None
        changes = self.store(p.id).diff(task.base_tree, tree)
        tests = [c for c in changes if gitwatch.is_test_path(c.path)]
        body = {
            "task": task.id,
            "kind": "done",
            "spool_id": ev.id,
            "tree": tree,
            "paths": [c.path for c in changes][:200],
            "files": len(changes),
            "tests_changed": len(tests),
        }
        self.append("task.event", body, project=p.id, change=s.st.change_id, at=ev.at)
        s.done_tree = tree
        if self.brief_done(p, s, ev, tree):
            self._silent_revert(p, s, tree)
            return
        self.start_check(p, s, tree)
        self.try_offer(p, s, ev)

    def _silent_revert(self, p: Project, s: Session, tree: str) -> None:
        """A Brief owns this done signal, so the Revert test asks nothing. Its check
        still runs on the other new or edited tests, never offered, so its note, the
        finding and a high-stakes fact line still come (learning.md 6.4 and 6.5)."""
        proj = self.config.project(p.id)
        if proj is None or not proj.test_command or s.st.task is None:
            return
        m = self.brief_live(p, s)
        # The Brief's base: its task may have ended at the first edits, and the tests
        # come in a later task of the same change.
        cand = self._match(p, s, tree, proj, m.base_tree if m is not None else None)
        if cand is None:
            return
        mine = {t.id for t in (m.tests if m is not None else ())}
        tests = [t for t in cand.tests if t.id not in mine]
        if not tests:
            return
        cand = replace(
            cand, tests=tuple(replace(t, n=i + 1) for i, t in enumerate(tests))
        )
        if self._silent_blocked(p, cand, tree):
            return
        self.launch(p, Check(cand, s.key, decided=True, silent=True))

    def _silent_blocked(self, p: Project, cand, tree: str) -> bool:
        """True when a check for this tree exists or another one must keep running.
        A stale undecided check of the same task is cancelled to make room."""
        c = self.check_of(p.check or "")
        if c is None:
            return False
        same_task = c.cand.task_id == cand.task_id
        if c.cand.head_tree == tree and same_task:
            return True
        if c.status not in RUNNING:
            return False
        if not same_task or c.decided:
            return True  # another check is running; this done signal stays quiet
        self.cancel(c)
        return False

    def may_speak(self, p: Project, s: Session) -> bool:
        """Cheap, no git: can this stop carry a line at all?"""
        if s.fact_due or self.call_may_speak(s) or self.brief_may_speak(p, s):
            return True
        m = self.live(p)
        if (
            m is not None
            and m.state == "open"
            and not m.seen
            and m.session == s.st.session
        ):
            return True
        c = self.check_of(p.check or "")
        if (
            c is not None
            and c.skey == s.key
            and not c.decided
            and c.status in (*RUNNING, "finished")
        ):
            return True
        task = s.st.task
        # This stop may be the done signal: the snapshot decides.
        return (
            task is not None
            and not task.done
            and not task.pending_ask
            and task.last_test_exit in (None, 0)
        )

    # ---------------------------------------------------------- stop lines

    def stop_line(
        self, p: Project, s: Session, ev: SpoolEvent
    ) -> tuple[str | None, list]:
        """One stop carries at most one line."""
        said = self.brief_stop(p, s, ev)
        if said is not None:
            return said
        m = self.live(p)
        if m is None or m.state != "open" or m.seen or m.session != s.st.session:
            m = None
        if m is not None and self.offered_in.get(m.id) == ev.id:
            return self.question_line(m), [("question", m.id)]
        c = self.check_of(m.id) if m is not None else None
        if m is not None and m.high_stakes and c is not None and c.status == "finished":
            self._close_high_stakes(p, s, m, c, ev.at)
            m = None
        g = self.gate_input(p, s, ev.at)
        if s.fact_due and ask.fact_allowed(g):
            return s.fact_due, [("fact", s.key)]
        if m is None or m.change_id != s.st.change_id:
            return None, []
        if self.day(m.offered_at) != self.day(ev.at) or not ask.fact_allowed(g):
            return None, []
        if g.dial in ("standard", "deep"):
            return self.question_line(m), [("question", m.id)]
        return None, []

    def _close_high_stakes(
        self, p: Project, s: Session, m: Moment, c: Check, at: str
    ) -> None:
        """Decision 12: close without looking, then record why from what follows."""
        m.state = ask.step(m.state, "close")
        self.release(p, c, commit=False)  # one commit, after moment.closed
        how = "shown-first" if s.fact_due else "unseen"
        m.close_how = how  # type: ignore[assignment]
        self.append(
            "moment.closed",
            {"moment_kind": m.kind, "how": how},
            project=p.id,
            change=m.change_id,
            moment=m.id,
            at=at,
        )
        self.commit_question(m, "closed")
        self.notify("inbox")

    def question_line(self, m: Moment) -> str | None:
        return agent_output(
            "question", moment=m, store=self.keys, ctx=self.ctx(m.task_name)
        )

    def answer_deferred(self, p: Project, s: Session) -> None:
        r = self.deferred.pop(s.key, None)
        if r is None:
            return
        text, carried = self.stop_line(p, s, r.ev)
        self.answer(r, text, carried)

    # -------------------------------------------------------- tick, idle

    def tick(self) -> None:
        with self._mutex:
            try:
                self._tick()
            except Exception:
                _LOGGER.exception("tick failed")

    def _tick(self) -> None:
        now = time.monotonic()
        for key, r in list(self.deferred.items()):
            if r.deadline <= now:
                s = self.sessions.get(key)
                p = self.projects.get(s.st.project_id) if s else None
                if s is None or p is None:
                    self.deferred.pop(key, None)
                    self.answer(r, None)
                else:
                    self.answer_deferred(p, s)
        today = self.day(self.now())
        for p in self.projects.values():
            m = self.live(p)
            if (
                m is not None
                and m.state == "open"
                and not m.seen
                and self.day(m.offered_at) < today
            ):
                self.close_moment(p, m, "unseen", self.now())
                self.checkpoint()

    def idle(self) -> bool:
        with self._mutex:
            if self.deferred or any(p.queued for p in self.projects.values()):
                return False
            if any(c.status in RUNNING for c in self.checks.values()):
                return False
            if self.call_running() or self.brief_running():
                return False
            return all(self.live(p) is None for p in self.projects.values())

    def close(self) -> None:
        with self._mutex:
            if self._closed:
                return
            self._closed = True
            for p in self.projects.values():
                m = self.live(p)
                if m is not None and m.state == "held":
                    self.settle_held(p, m)
            for r in list(self.deferred.values()):
                self.answer(r, None)
            self.deferred.clear()
            self.checkpoint()
            try:
                if self.record.dirty():
                    self.record.commit("events")
            except Exception:
                _LOGGER.exception("final commit failed")
            if self._queue is not None:
                self._queue.put(None)

    # -------------------------------------------------------- checkpoint

    def prune_moments(self) -> None:
        if len(self.moments) <= state.MAX_MOMENTS:
            return
        live = {p.live for p in self.projects.values()}
        for mid in sorted(self.moments)[: len(self.moments) - state.MAX_MOMENTS]:
            if mid not in live:
                self.moments.pop(mid, None)

    def checkpoint(self) -> None:
        try:
            state.save(
                {
                    "seen": self.seen_ids,
                    "first_day": self.first_day,
                    "work_notice_done": self.work_notice_done,
                    "last_project": self.last_project,
                    "projects": {
                        pid: {"root": p.root, "live": p.live, "replaces": p.replaces}
                        for pid, p in self.projects.items()
                    },
                    "sessions": [
                        {
                            "key": s.key,
                            "st": state.session_to(s.st),
                            "done_tree": s.done_tree,
                            "queue": s.queue,
                            "fact_due": s.fact_due,
                            "fact_check": s.fact_check,
                            "last_at": s.last_at,
                            "episode": s.episode,
                            "brief": s.brief,
                        }
                        for s in self.sessions.values()
                    ],
                    "moments": [state.moment_to(m) for m in self.moments.values()],
                }
            )
        except Exception:
            _LOGGER.exception("checkpoint failed")

    def _load(self) -> None:
        data = state.load()
        self.seen_ids = list(data.get("seen", ()))
        self.first_day = data.get("first_day")
        self.work_notice_done = bool(data.get("work_notice_done"))
        self.last_project = data.get("last_project")
        for pid, p in (data.get("projects") or {}).items():
            self.projects[pid] = Project(
                pid, p["root"], live=p.get("live"), replaces=p.get("replaces")
            )
        for row in data.get("sessions", ()):
            self.sessions[row["key"]] = Session(
                row["key"],
                state.session_from(row["st"]),
                done_tree=row.get("done_tree"),
                queue=list(row.get("queue", ())),
                fact_due=row.get("fact_due"),
                fact_check=row.get("fact_check"),
                last_at=row.get("last_at", ""),
                episode=row.get("episode"),
                brief=row.get("brief"),
            )
        for row in data.get("moments", ()):
            m = state.moment_from(row)
            self.moments[m.id] = m
        self._resume_checks()

    def _resume_checks(self) -> None:
        """A live moment gets its check back: from its key file, or by running it again."""
        live = set()
        for p in self.projects.values():
            m = self.live(p)
            s = self.session_of(m) if m is not None else None
            if m is None or s is None:
                continue
            live.add(m.id)
            if m.kind not in ("call_it", "brief"):  # each resumes its own below
                self._resume_one(p, s, m)
        for check_id in self.keys.pending():
            if check_id not in live:
                self.keys.discard(check_id)
        if "call_it" in self.modules:
            self.resume_calls()
        if "brief" in self.modules:
            self.resume_briefs()

    def _resume_one(self, p: Project, s: Session, m: Moment) -> None:
        try:
            cand = self.candidate_for(p, m, m.id)
        except Exception:
            _LOGGER.exception("cannot resume %s", m.id)
            return
        c = Check(cand, s.key, decided=True)
        if self.keys.has(m.id):
            c.status = "finished"
            self.checks[c.id] = c
            p.check = c.id
        else:
            self.launch(p, c)

    def candidate_for(self, p: Project, m: Moment, check_id: str) -> Candidate:
        changes = self.store(p.id).diff(m.base_tree, m.head_tree)
        source, _ = gitwatch.split_changes(changes)
        return Candidate(
            kind=m.kind,
            check_id=check_id,
            project_id=p.id,
            project_root=p.root,
            task_id=m.task_id,
            change_id=m.change_id,
            base_tree=m.base_tree,
            head_tree=m.head_tree,
            source_changes=source,
            tests=m.tests,
            how=m.how,
            high_stakes=m.high_stakes,
        )


def _registry() -> Sequence[ModuleType]:
    return moment_registry.REGISTRY
