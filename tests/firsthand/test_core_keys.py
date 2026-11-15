"""firsthand.keys: the key store, the reveal gate and the one output rule."""

from __future__ import annotations

import importlib
import json
import stat
import sys
import types

import support

from firsthand import keys, paths
from firsthand.model import REVEALED, Key, KeyItem, KeyLocked, Moment, StepRun


def _key(moment: str = "01MOMENT") -> Key:
    return Key(
        moment=moment,
        kind="revert_test",
        how="pytest",
        base_tree="9d1c",
        head_tree="fbc5",
        made_at="2026-11-14T09:40:02Z",
        tests=(
            KeyItem(
                "tests/test_refunds.py::test_same_key_refunds_once",
                "fails_on_assertion",
                23,
                "assert len(ledger.refunds(charge)) == 1",
                23,
            ),
            KeyItem(
                "tests/test_refunds.py::test_refund_response_is_stable",
                "still_passes",
                41,
                "assert resp.status_code == 200",
                None,
            ),
        ),
        steps=(
            StepRun("control", "python -m pytest ...", 0, (), "a" * 64),
            StepRun(
                "undone",
                "python -m pytest ...",
                1,
                ("tests/test_refunds.py::test_same_key_refunds_once",),
                "b" * 64,
            ),
        ),
        undone_paths=("refunds/service.py",),
        duration_s=3.2,
    )


def _moment(state: str, moment_id: str = "01MOMENT") -> Moment:
    return Moment(
        id=moment_id,
        kind="revert_test",
        state=state,
        project_id="prj",
        change_id="C",
        task_id="T",
        session="s",
        task_name="idempotent refunds",
        base_at="2026-11-14T09:12:03Z",
        base_tree="9d1c",
        head_tree="fbc5",
        tests=(),
        how="pytest",
        high_stakes=None,
        offered_at="2026-11-14T09:40:00Z",
    )


CTX = keys.OutputContext(
    room_url="http://127.0.0.1:4127",
    work_computer=False,
    work_notice=False,
    task_name="idempotent refunds",
    high_stakes="refunds/**",
    ack="skip",
)


def _words_module() -> types.ModuleType:
    """The real firsthand.words when it exists, else a stand-in that tags each call."""
    try:
        return importlib.import_module("firsthand.words")
    except ImportError:
        pass
    fake = types.ModuleType("firsthand.words")
    fake.question_line = lambda m, ctx: f"question:{m.id}"
    fake.ack_line = lambda ack, task: f"ack:{ack}:{task}"
    fake.pending_line = lambda m, ctx: f"pending:{m.id}"
    fake.result_lines = lambda m, k, ctx: ["result", m.id]
    fake.finding_line = lambda k: f"finding:{k.moment}"
    fake.fact_line = lambda k, pattern: f"fact:{k.moment}:{pattern}"
    return fake


class KeyStoreTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        paths.ensure_private_dirs()

    def test_put_writes_private_file_and_reloads(self) -> None:
        store = keys.KeyStore()
        store.put(_key())
        f = paths.key_file("01MOMENT")
        self.assertEqual(stat.S_IMODE(f.stat().st_mode), 0o600)
        data = json.loads(f.read_text())
        self.assertEqual(data["v"], 1)
        self.assertEqual(data["moment"], "01MOMENT")
        self.assertEqual(data["tests"][1]["result"], "still_passes")
        self.assertEqual(
            set(data["tests"][0]),
            {"id", "result", "assert_line", "assert_text", "fail_line"},
        )
        self.assertEqual(
            data["steps"][1]["failing"],
            ["tests/test_refunds.py::test_same_key_refunds_once"],
        )
        again = keys.KeyStore()
        self.assertTrue(again.has("01MOMENT"))
        self.assertEqual(again.reveal("01MOMENT", _moment("settled")), _key())
        self.assertEqual(again.pending(), ("01MOMENT",))

    def test_put_replaces_and_discard(self) -> None:
        store = keys.KeyStore()
        store.put(_key())
        newer = Key(**{**_key().__dict__, "duration_s": 9.0})
        store.put(newer)
        self.assertEqual(store.reveal("01MOMENT", None, silent=True).duration_s, 9.0)
        store.discard("01MOMENT")
        store.discard("01MOMENT")
        self.assertFalse(store.has("01MOMENT"))
        self.assertFalse(paths.key_file("01MOMENT").exists())
        self.assertEqual(keys.KeyStore().pending(), ())

    def test_custom_directory_and_broken_file(self) -> None:
        where = self.tmp / "k"
        store = keys.KeyStore(where)
        store.put(_key("01X"))
        (where / "broken.json").write_text("{nope")
        self.assertEqual(keys.KeyStore(where).pending(), ("01X",))

    def test_reveal_gate(self) -> None:
        store = keys.KeyStore()
        store.put(_key())
        for state in ("open", "held"):
            with self.assertRaises(KeyLocked):
                store.reveal("01MOMENT", _moment(state))
            with self.assertRaises(KeyLocked):
                store.reveal("01MOMENT", _moment(state), silent=True)
        with self.assertRaises(KeyLocked):
            store.reveal("01MOMENT", None)
        for state in sorted(REVEALED):
            self.assertEqual(store.reveal("01MOMENT", _moment(state)), _key())
        self.assertEqual(store.reveal("01MOMENT", None, silent=True), _key())
        with self.assertRaises(KeyError):
            store.reveal("01OTHER", _moment("settled"))
        self.assertEqual(KeyLocked("x").code, "locked")


class AgentOutputTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        paths.ensure_private_dirs()
        self.words = _words_module()
        if "firsthand.words" not in sys.modules:
            sys.modules["firsthand.words"] = self.words
            self.addCleanup(sys.modules.pop, "firsthand.words", None)
        self.store = keys.KeyStore()
        self.store.put(_key())

    def out(self, want: str, moment: Moment | None, **kw) -> str | None:
        return keys.agent_output(want, moment=moment, store=self.store, ctx=CTX, **kw)

    def test_results_never_leave_before_reveal(self) -> None:
        for state in ("open", "held"):
            m = _moment(state)
            for want in ("result", "finding", "fact"):
                self.assertIsNone(self.out(want, m), (want, state))
                self.assertIsNone(self.out(want, m, check_id="01MOMENT"), (want, state))
                self.assertIsNone(self.out(want, m, silent=True), (want, state))
        for want in ("finding", "fact"):
            self.assertIsNone(self.out(want, None, check_id="01MOMENT"))

    def test_question_is_only_the_question_line(self) -> None:
        m = _moment("open")
        self.assertEqual(self.out("question", m), self.words.question_line(m, CTX))
        for state in ("held", "sealed", "settled", "skipped", "closed"):
            self.assertIsNone(self.out("question", _moment(state)))
        self.assertIsNone(self.out("question", None))

    def test_pending_ack_and_revealed_lines(self) -> None:
        sealed = _moment("sealed")
        self.assertEqual(
            self.out("pending", sealed), self.words.pending_line(sealed, CTX)
        )
        self.assertIsNone(self.out("pending", _moment("open")))
        self.assertEqual(
            self.out("ack", None), self.words.ack_line("skip", "idempotent refunds")
        )
        settled = _moment("settled")
        self.assertEqual(
            self.out("result", settled),
            "\n".join(self.words.result_lines(settled, _key(), CTX)),
        )
        self.assertEqual(self.out("finding", settled), self.words.finding_line(_key()))
        self.assertEqual(
            self.out("fact", None, check_id="01MOMENT", silent=True),
            self.words.fact_line(_key(), "refunds/**"),
        )
        self.assertIsNone(self.out("result", None, check_id="01MOMENT", silent=True))
        self.assertIsNone(self.out("finding", _moment("settled", "01NOKEY")))
