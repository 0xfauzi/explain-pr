"""The engine's actions and read models: what the Room and the CLI call.

A mixin for `engine.Engine`, split out to keep each file under the size limit.
Every method takes the engine's lock. Lines for a text channel come from
`keys.agent_output`, through the engine's helpers.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Literal

from firsthand import ask, events, gitwatch, paths, views
from firsthand.keys import agent_output
from firsthand.model import EngineError, FirsthandError, Moment, Reply
from firsthand.record import new_ulid

if TYPE_CHECKING:
    from firsthand.engine import Check, Engine, Project, Session

GLOBAL_KEYS = (
    "dial",
    "daily_limit",
    "findings_to_agent",
    "quiet_today",
    "work_computer",
    "check_time_limit_s",
)
PROJECT_KEYS = (
    "test_command",
    "quiet",
    "high_stakes_add",
    "high_stakes_remove",
    "name",
)
DIAL_ORDER = ("off", "notes", "standard", "deep")
QUIET_ACKS = {
    "quiet": "quiet",
    "quiet today": "quiet-today",
    "quiet here": "quiet-here",
}
QUIET_SCOPES = {"quiet": "session", "quiet today": "today", "quiet here": "here"}


class Actions:
    """Mixed into Engine. `self` is always an Engine."""

    # ------------------------------------------------------------ lookups

    def find(self: Engine, ref: str) -> Moment:
        ref = (ref or "").strip()
        m = self.moments.get(ref)
        if m is None:
            short = ref.lower()
            m = next(
                (x for x in self.moments.values() if views.short_ref(x.id) == short),
                None,
            )
        if m is None:
            raise EngineError(f"No question has the reference {ref!r}.", "not_found")
        return m

    def project_at(self: Engine, cwd: str | None) -> str | None:
        if cwd is None:
            return self.last_project
        root = gitwatch.project_root(cwd)
        return gitwatch.project_id(root) if root is not None else None

    def moment_at(self: Engine, cwd: str | None) -> Moment:
        pid = self.project_at(cwd)
        candidates = (
            [self.projects[pid]]
            if pid in self.projects
            else []
            if cwd is not None
            else list(self.projects.values())
        )
        live = [m for p in candidates if (m := self.live(p)) is not None]
        if not live:
            raise EngineError("No question is open. Nothing to answer.", "no_question")
        return max(live, key=lambda m: m.id)

    def _target(
        self: Engine, ref: str | None, cwd: str | None
    ) -> tuple[Project, Moment]:
        m = self.find(ref) if ref else self.moment_at(cwd)
        return self.projects[m.project_id], m

    # -------------------------------------------------------------- views

    def view_input(self: Engine) -> views.ViewInput:
        known = set(self.projects)
        known |= {
            e["project"]
            for e in self.record.events(types=("task.started",))
            if e.get("project")
        }
        projects = {pid: p for pid in sorted(known) if (p := self.config.project(pid))}
        settings = self.config.load()
        today = self.day(self.now())
        quiet_all = {
            pid: self._quiet_scopes(pid, settings, today.isoformat())
            for pid in projects
        }
        quiet = {
            pid: (scopes[0] if scopes else None) for pid, scopes in quiet_all.items()
        }
        lines = {
            m.id: self.open_line(m)
            for m in self.moments.values()
            if m.state == "open" or self.brief_confirming(m)
        }
        return views.ViewInput(
            events=self.record.events(),
            moments=self.moments,
            settings=settings,
            projects=projects,
            tz=self.tz,
            today=today,
            room_url=self.room_url,
            read_source=self._read_source,
            record_path=views.record_label(self.record.root, paths.user_home()),
            quiet=quiet,
            quiet_all=quiet_all,
            lines=lines,
        )

    def _read_source(self: Engine, project_id: str, tree: str, path: str) -> str | None:
        try:
            if project_id not in self.projects:
                return None
            return self.store(project_id).read_file(tree, path)
        except (FirsthandError, OSError):
            return None

    def _quiet_scopes(self: Engine, pid: str, settings, today: str) -> tuple[str, ...]:
        """Every quiet scope in force for the project, narrowest first."""
        scopes = []
        if any(s.st.quiet for s in self.sessions.values() if s.st.project_id == pid):
            scopes.append("session")
        if settings.quiet_today == today:
            scopes.append("today")
        proj = self.config.project(pid)
        if proj is not None and proj.quiet:
            scopes.append("here")
        return tuple(scopes)

    def _pick_project(self: Engine, project: str | None) -> str | None:
        return project or self.last_project

    def inbox(self: Engine, project: str | None = None) -> dict:
        with self._mutex:
            return views.inbox_view(self.view_input(), self._pick_project(project))

    def question(
        self: Engine,
        ref: str | None = None,
        *,
        cwd: str | None = None,
        seen: bool = True,
    ) -> dict:
        with self._mutex:
            _, m = self._target(ref, cwd)
            if seen and m.state == "open" and not m.seen:
                m.seen = True
                self.checkpoint()
            elif (
                seen
                and self.brief_confirming(m)
                and not (m.extra or {}).get("confirm_seen")
            ):
                m.extra = {**(m.extra or {}), "confirm_seen": True}
                self.checkpoint()
            view = views.question_view(self.view_input(), m)
            if seen and view["result"] is not None and not m.opened:
                m.opened = True
                self.checkpoint()
                self.notify("inbox")
            return view

    def journal(self: Engine, project: str | None = None, limit: int = 200) -> dict:
        with self._mutex:
            return views.journal_view(
                self.view_input(), self._pick_project(project), limit
            )

    def skills(self: Engine, project: str | None = None) -> dict:
        with self._mutex:
            return views.skills_view(self.view_input(), self._pick_project(project))

    def settings(self: Engine, project: str | None = None) -> dict:
        with self._mutex:
            return views.settings_view(self.view_input(), self._pick_project(project))

    def status(self: Engine, cwd: str | None = None) -> dict:
        with self._mutex:
            project = self._status_project(cwd)
            question = None
            pid = project.get("id") if project else None
            p = self.projects.get(pid or "")
            m = self.live(p) if p is not None else None
            if m is not None and (m.state == "open" or self.brief_confirming(m)):
                question = {"ref": views.short_ref(m.id), "line": self.open_line(m)}
            return views.status_view(self.view_input(), project, question)

    def _status_project(self: Engine, cwd: str | None) -> dict | None:
        root = gitwatch.project_root(cwd) if cwd else None
        if root is None:
            return None
        pid = gitwatch.project_id(root)
        if pid is None:
            return {
                "id": None,
                "name": root.name,
                "test_command": None,
                "watched": False,
                "why_not": "no commit yet",
            }
        proj = self.config.ensure_project(pid, str(root))
        return {
            "id": pid,
            "name": proj.name,
            "test_command": proj.test_command,
            "watched": bool(proj.test_command),
            "why_not": None if proj.test_command else "no test command",
        }

    def open_line(self: Engine, m: Moment) -> str | None:
        """The one-line form of what the moment asks now: its question, or the confirm."""
        if self.brief_confirming(m):
            return agent_output(
                "confirm", moment=m, store=self.keys, ctx=self.ctx(m.task_name)
            )
        return self.question_line(m)

    def _view(self: Engine, m: Moment, said: str | None = None) -> dict:
        say = said.split("\n") if said else None
        return views.question_view(self.view_input(), m, say)

    # ------------------------------------------------------------ actions

    def _parse(self: Engine, m: Moment, answer: str) -> Reply:
        text = (answer or "").strip()
        module, n = self.mod(m), self.reply_n(m)
        canonical = {w for w in module.reply_words(n) if w != "don't know"}
        if text in canonical | {"dont_know"}:
            return Reply(text, None)  # type: ignore[arg-type]
        reply = module.parse_reply(text, n)
        if reply is None:
            hint = getattr(module, "reply_hint", None)  # the Revert test's set form
            listed = ", ".join(module.reply_words(n))
            message = hint(n) if hint else f"Reply with one of: {listed}. Or skip."
            raise EngineError(message, "invalid")
        return reply

    def lock(
        self: Engine,
        ref: str | None,
        answer: str,
        *,
        channel,
        final: bool,
        cwd: str | None = None,
    ) -> dict:
        with self._mutex:
            p, m = self._target(ref, cwd)
            if m.kind == "brief":
                said = self._brief_lock(p, m, answer, channel)
                self.checkpoint()
                return self._view(m, said)
            if m.state != "open":
                ask.step(m.state, "seal")
            reply = self._parse(m, answer)
            said = None
            if final or reply.answer == "dont_know":
                said, _ = self.seal_call(
                    p, m, reply.answer, reply.confidence, channel, self.now()
                )
            else:
                m.state = ask.step(m.state, "pick")
                m.pending = {
                    "kind": "pick",
                    "answer": reply.answer,
                    "confidence": reply.confidence,
                    "at": self.now(),
                }
                self.notify("question", m.id)
            self.checkpoint()
            return self._view(m, said)

    def _brief_lock(
        self: Engine, p: Project, m: Moment, answer: str, channel
    ) -> str | None:
        """The Brief from the Room or the CLI: the line, then yes or no. Both final."""
        if m.state == "open":
            return self.brief_seal_line(p, m, answer, str(channel), self.now())
        reply = self.mod(m).parse_reply(answer or "")
        if not self.brief_confirming(m):
            ask.step(m.state, "seal")  # the state error for this moment
        if reply is None:
            raise EngineError("Reply with one of: yes, no. Or skip.", "invalid")
        return self.brief_confirm(p, m, reply.answer, str(channel), self.now())

    def undo(self: Engine, ref: str) -> dict:
        with self._mutex:
            _, m = self._target(ref, None)
            m.state = ask.step(m.state, "undo")
            m.pending = None
            self.checkpoint()
            self.notify("question", m.id)
            return self._view(m)

    def show(self: Engine, ref: str) -> dict:
        with self._mutex:
            p, m = self._target(ref, None)
            if m.state == "open" or (
                m.state == "held" and (m.pending or {}).get("kind") != "pick"
            ):
                raise EngineError("Pick an answer first.", "state")
            if m.state == "held":
                self.settle_held(p, m)
            view = self._view(m)
            if view["result"] is not None:
                m.opened = True
            self.checkpoint()
            return view

    def confidence(self: Engine, ref: str, value: str | None) -> dict:
        with self._mutex:
            _, m = self._target(ref, None)
            if m.state != "held" or (m.pending or {}).get("kind") != "pick":
                raise EngineError(
                    "Set How sure after you answer and before the result.", "state"
                )
            if value not in ("high", "low", None):
                raise EngineError("value must be high, low or null.", "invalid")
            m.pending = {**(m.pending or {}), "confidence": value}
            self.checkpoint()
            return self._view(m)

    def skip(
        self: Engine, ref: str | None, *, channel, final: bool, cwd: str | None = None
    ) -> dict:
        with self._mutex:
            p, m = self._target(ref, cwd)
            if self.brief_confirming(m):
                self.release_brief(p, m, reason="skipped")
                self.checkpoint()
                ack = "skip" if final else None
                said = agent_output(
                    "ack", moment=m, store=self.keys, ctx=self.ctx(m.task_name, ack=ack)
                )
                return self._view(m, said if final else None)
            if m.state != "open":
                ask.step(m.state, "skip_final")
            if final:
                how = "cli" if channel == "chat" else "room"
                said = self.skip_final(p, m, how, self.now())
                self.checkpoint()
                return self._view(m, said)
            m.state = ask.step(m.state, "skip_room")
            m.pending = {"kind": "skip", "at": self.now()}
            self.checkpoint()
            self.notify("inbox")
            return self._view(m)

    def wrong_start(self: Engine, ref: str) -> dict:
        with self._mutex:
            p, m = self._target(ref, None)
            if m.state != "open":
                raise EngineError("Use Wrong start before you answer.", "state")
            if m.kind in ("call_it", "brief"):
                raise EngineError(
                    "Wrong start is not offered on this question.", "state"
                )
            s = self.session_of(m)
            task = s.st.task if s is not None else None
            new_base = (
                (s.st.previous_base or self.store(p.id).head_tree() or task.base_tree)
                if s is not None and task is not None and s.done_tree
                else None
            )
            if s is None or task is None or new_base in (None, task.base_tree):
                raise EngineError(
                    "There is no earlier start for this task: it already starts at "
                    "the last commit.",
                    "state",
                )
            # The check ran from the wrong base: its result is dropped, never shown.
            c = self.check_of(m.id)
            if c is not None:
                self.cancel(c)
            self.close_moment(p, m, "wrong-start", self.now())
            self._move_base(p, s, m, new_base)
            self.checkpoint()
            new = self.live(p)
            return self._view(new if new is not None and new.id != m.id else m)

    def _move_base(
        self: Engine, p: Project, s: Session, m: Moment, new_base: str
    ) -> None:
        task = s.st.task
        assert task is not None
        body = {
            "task": task.id,
            "kind": "base_moved",
            "spool_id": None,
            "from": task.base_tree,
            "to": new_base,
            "why": "wrong-start",
        }
        self.append("task.event", body, project=p.id, change=s.st.change_id)
        task.base_tree = new_base
        s.st.change_asked = False
        p.live, p.replaces = None, m.id
        c = self.check_of(p.check or "")
        if c is not None and c.status in ("control", "undoing"):
            self.cancel(c)
        p.check = None
        assert s.done_tree is not None
        self.start_check(p, s, s.done_tree)
        self.try_offer(p, s, None)

    def dispute(self: Engine, ref: str, reason: str) -> dict:
        with self._mutex:
            p, m = self._target(ref, None)
            if m.kind == "call_it":
                raise EngineError("A Call it result cannot be rechecked yet.", "state")
            if m.kind == "brief":
                raise EngineError("A Brief result cannot be rechecked yet.", "state")
            text, _ = events.scan_secrets((reason or "").strip())
            if not text:
                raise EngineError("Say in a few words what looks wrong.", "invalid")
            ran = self.record.events(types=("check.ran",), moment=m.id)
            scored = self.record.events(types=("call.scored",), moment=m.id)
            if (
                m.state != "settled"
                or not ran
                or not scored
                or any(e["body"].get("rerun_of") for e in ran)
            ):
                raise EngineError(
                    "This result can be rechecked once, after it is scored.", "state"
                )
            s = self.session_of(m)
            cand = self.candidate_for(p, m, new_ulid())
            c = self._dispute_check(cand, s, ran[-1]["id"], text, m)
            self.launch(p, c)
            self.checkpoint()
            return self._view(m)

    def _dispute_check(
        self: Engine, cand, s, ran_id: str, text: str, m: Moment
    ) -> Check:
        from firsthand.engine import Check

        c = Check(
            cand,
            s.key if s is not None else "",
            decided=True,
            rerun_of=ran_id,
            reason=text,
        )
        c.status = "undoing"
        self.dispute_of[c.id] = m.id
        return c

    def dispute_finished(self: Engine, p: Project, c: Check, outcome) -> None:
        mid = self.dispute_of.pop(c.id, None)
        self.checks.pop(c.id, None)
        m = self.moments.get(mid or "")
        if m is None:
            return
        if outcome.key is None:
            body = {
                "check_kind": c.cand.kind,
                "check": c.id,
                "reason": outcome.unavailable,
                "step": outcome.step or "setup",
                "base_tree": c.cand.base_tree,
                "head_tree": c.cand.head_tree,
                "command": None,
                "exit": None,
            }
            self.append(
                "check.unavailable", body, project=p.id, change=m.change_id, moment=m.id
            )
            return
        self.keys.put(outcome.key)
        k = self.keys.reveal(c.id, m)
        first = self.record.get(c.rerun_of or "")
        self.append(
            "check.ran",
            self._ran_body(c, k),
            project=p.id,
            change=m.change_id,
            moment=m.id,
        )
        self.keys.discard(c.id)
        old = {
            r["id"]: r["result"]
            for r in (first or {}).get("body", {}).get("results", ())
        }
        new = {t.id: t.result for t in k.tests}
        if old != new:
            last = self.record.events(types=("call.scored",), moment=m.id)[-1]
            body = {
                "result": "unscored",
                "checked_by": "runner",
                "check": None,
                "outcome_kind": last["body"]["outcome_kind"],
                "catch": False,
                "unscored_reason": "check-unavailable",
                "supersedes": last["id"],
            }
            self.append(
                "call.scored", body, project=p.id, change=m.change_id, moment=m.id
            )
        self.record.commit("events")
        self.notify("question", m.id)

    # -------------------------------------------------------------- quiet

    def set_quiet_word(
        self: Engine, p: Project, s: Session, m: Moment, word: str, at: str
    ) -> str:
        """A chat word "quiet", "quiet today" or "quiet here" while a question is open."""
        self._apply_quiet(p, s, QUIET_SCOPES[word], True, at)
        return (
            agent_output(
                "ack",
                moment=m,
                store=self.keys,
                ctx=self.ctx(m.task_name, ack=QUIET_ACKS[word]),
            )
            or ""
        )

    def _apply_quiet(
        self: Engine,
        p: Project | None,
        s: Session | None,
        scope: str,
        on: bool,
        at: str,
    ) -> None:
        if scope == "session" and s is not None:
            s.st.quiet = on
        elif scope == "today":
            self.config.set("quiet_today", self.day(at).isoformat() if on else None)
        elif scope == "here" and p is not None:
            self.config.set_project(p.id, "quiet", on)
        if on:
            for proj, m in self._quiet_targets(p, s, scope):
                self.close_moment(proj, m, "quiet", at)

    def _quiet_targets(
        self: Engine, p: Project | None, s: Session | None, scope: str
    ) -> list[tuple[Project, Moment]]:
        """The open questions a quiet of this scope closes."""
        projects = (
            list(self.projects.values()) if scope == "today" else [p] if p else []
        )
        found = []
        for proj in projects:
            m = self.live(proj)
            if m is None or m.state != "open":
                continue
            other_session = s is None or m.session != s.st.session
            if scope == "session" and other_session:
                continue
            found.append((proj, m))
        return found

    def quiet(
        self: Engine,
        scope: Literal["session", "today", "here"],
        on: bool = True,
        *,
        cwd: str | None = None,
        session: str | None = None,
    ) -> dict:
        if scope not in ("session", "today", "here"):
            raise EngineError("scope must be session, today or here.", "invalid")
        with self._mutex:
            pid = self.project_at(cwd)
            p = self.projects.get(pid or "")
            if scope == "here" and pid is not None and p is None:
                p = self._project_from_cwd(cwd)
            s = self._quiet_session(pid, session)
            if scope in ("session", "here") and (p is None and s is None):
                raise EngineError(
                    "This folder is not a project Firsthand has seen.", "invalid"
                )
            self._apply_quiet(p, s, scope, on, self.now())
            self.checkpoint()
            self.notify("inbox")
            self.notify("settings")
            if not on:
                from firsthand import words  # a fixed line that carries no result

                return {"lines": [words.QUIET_OFF]}
            ack = {"session": "quiet", "today": "quiet-today", "here": "quiet-here"}[
                scope
            ]
            line = agent_output(
                "ack", moment=None, store=self.keys, ctx=self.ctx(ack=ack)
            )
            return {"lines": [line] if line else []}

    def _project_from_cwd(self: Engine, cwd: str | None) -> Project | None:
        root = gitwatch.project_root(cwd) if cwd else None
        pid = gitwatch.project_id(root) if root is not None else None
        if root is None or pid is None:
            return None
        self.config.ensure_project(pid, str(root))
        return self._project(pid, str(root))

    def _quiet_session(
        self: Engine, pid: str | None, session: str | None
    ) -> Session | None:
        found = [
            s
            for s in self.sessions.values()
            if (pid is None or s.st.project_id == pid)
            and (session is None or s.st.session == session)
        ]
        return max(found, key=lambda s: s.last_at) if found else None

    # ----------------------------------------------------------- settings

    def set_settings(
        self: Engine,
        changes: Mapping[str, object],
        *,
        project: str | None = None,
        source: Literal["room", "cli", "agent"],
        confirm: bool = False,
    ) -> dict:
        with self._mutex:
            self._check_keys(changes, project)
            current = self.config.load()
            proj = self.config.project(project) if project else None
            if project and proj is None:
                raise EngineError(f"No settings for project {project}.", "not_found")
            if self._widens(changes, current, proj):
                if source == "agent":
                    raise EngineError(
                        "This change asks or sends more, so it is not taken from inside an "
                        "agent. Run it in a terminal you opened.",
                        "refused",
                    )
                if source == "room" and not confirm:
                    raise EngineError(
                        "This change asks or sends more. Confirm it.", "confirm"
                    )
            for key, value in changes.items():
                self._apply_setting(key, value, project, current.dial)
            self.checkpoint()
            self.notify("settings")
            self.notify("inbox")
            return views.settings_view(self.view_input(), project or self.last_project)

    @staticmethod
    def _check_keys(changes: Mapping[str, object], project: str | None) -> None:
        if not changes:
            raise EngineError("Name at least one setting to change.", "invalid")
        unknown = [k for k in changes if k not in GLOBAL_KEYS + PROJECT_KEYS]
        if unknown:
            allowed = ", ".join(GLOBAL_KEYS + PROJECT_KEYS)
            raise EngineError(
                f"Not a setting: {', '.join(unknown)}. Use: {allowed}.", "invalid"
            )
        if project is None and any(k in PROJECT_KEYS for k in changes):
            raise EngineError("A project setting needs the project.", "invalid")

    @staticmethod
    def _widens(changes: Mapping[str, object], current, proj) -> bool:
        dial = changes.get("dial")
        if dial in DIAL_ORDER and DIAL_ORDER.index(dial) > DIAL_ORDER.index(
            current.dial
        ):
            return True
        limit = changes.get("daily_limit")
        if (
            isinstance(limit, int)
            and not isinstance(limit, bool)
            and limit > current.daily_limit
        ):
            return True
        if changes.get("findings_to_agent") is True and not current.findings_to_agent:
            return True
        return "test_command" in changes and (
            proj is None or changes["test_command"] != proj.test_command
        )

    def _apply_setting(
        self: Engine, key: str, value: object, project: str | None, dial_before: str
    ) -> None:
        if key in PROJECT_KEYS:
            assert project is not None
            self.config.set_project(project, key, value)
            return
        if key == "quiet_today":
            if not isinstance(value, bool):
                raise EngineError("quiet_today must be true or false.", "invalid")
            p = self.projects.get(project or self.last_project or "")
            self._apply_quiet(p, None, "today", value, self.now())
            return
        if key == "dial" and value == "off" and dial_before != "off":
            self.config.set("dial_before_off", dial_before)
            self.config.set("dial", "off")
            self._close_all("off")
            return
        self.config.set(key, value)

    def _close_all(self: Engine, how: str) -> None:
        for p in self.projects.values():
            m = self.live(p)
            if m is not None and m.state == "held":
                self.settle_held(p, m)
                continue
            if m is not None and m.state == "open":
                self.close_moment(p, m, how, self.now())
