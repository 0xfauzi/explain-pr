"""firsthand.record: layout, ULIDs, the event envelope, filters and commits."""

from __future__ import annotations

import json
import stat
from datetime import UTC, datetime, timedelta

import support

from firsthand import ENGINE, paths, record


class RecordTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.root = record.ensure_record()

    def log(self) -> list[str]:
        return support.git(self.root, "log", "--format=%s|%an|%ae").splitlines()

    def test_layout_modes_and_first_commit(self) -> None:
        self.assertEqual(self.root, paths.record_dir())
        self.assertEqual(stat.S_IMODE(self.root.stat().st_mode), 0o700)
        self.assertEqual((self.root / "FORMAT").read_text(), "firsthand-record 1\n")
        self.assertTrue((self.root / ".git").is_dir())
        self.assertEqual(self.log(), ["init|firsthand|firsthand@localhost"])
        record.ensure_record()  # idempotent
        self.assertEqual(len(self.log()), 1)

    def test_ulids_sort_by_time(self) -> None:
        t0 = datetime(2026, 11, 14, 9, 0, tzinfo=UTC)
        ids = [record.new_ulid(t0 + timedelta(milliseconds=i * 7)) for i in range(20)]
        self.assertEqual(ids, sorted(ids))
        self.assertTrue(all(len(i) == 26 for i in ids))
        self.assertTrue(
            all(set(i) <= set("0123456789ABCDEFGHJKMNPQRSTVWXYZ") for i in ids)
        )
        burst = [record.new_ulid() for _ in range(200)]
        self.assertEqual(burst, sorted(burst))
        self.assertEqual(len(set(burst)), 200)

    def test_append_writes_envelope_and_path(self) -> None:
        r = record.Record()
        ev = r.append(
            "call.sealed",
            {"answer": "2"},
            project="prj_1",
            moment="M1",
            surface="claude-code",
            at="2026-11-14T09:41:11Z",
        )
        path = self.root / "events" / "2026" / "11" / f"{ev['id']}.json"
        self.assertTrue(path.is_file())
        text = path.read_text()
        self.assertTrue(text.endswith("}\n"))
        data = json.loads(text)
        self.assertEqual(text, json.dumps(data, indent=2, sort_keys=True) + "\n")
        self.assertEqual(
            set(data),
            {
                "format",
                "id",
                "type",
                "project",
                "change",
                "moment",
                "surface",
                "engine",
                "at",
                "body",
                "x",
            },
        )
        self.assertEqual(data["format"], 1)
        self.assertEqual(data["engine"], ENGINE)
        self.assertIsNone(data["change"])
        self.assertEqual(data["body"], {"answer": "2"})
        self.assertEqual(r.get(ev["id"]), ev)
        self.assertIsNone(r.get("nope"))

    def test_unknown_type_refused(self) -> None:
        r = record.Record()
        with self.assertRaises(record.RecordError):
            r.append("episode.blue", {})

    def test_events_filters_and_reload(self) -> None:
        r = record.Record()
        a = r.append("task.started", {}, project="p1", at="2026-11-14T09:00:00Z")
        b = r.append(
            "moment.offered", {}, project="p1", moment="m1", at="2026-11-14T10:00:00Z"
        )
        c = r.append("note.posted", {}, project="p2", at="2026-11-15T10:00:00Z")
        self.assertEqual([e["id"] for e in r.events()], [a["id"], b["id"], c["id"]])
        self.assertEqual(r.events(types={"note.posted"}), [c])
        self.assertEqual(r.events(project="p1"), [a, b])
        self.assertEqual(r.events(moment="m1"), [b])
        self.assertEqual(r.events(since="2026-11-14T09:30:00Z"), [b, c])
        again = record.Record()
        self.assertEqual(again.events(), r.events())

    def test_commit(self) -> None:
        r = record.Record()
        self.assertFalse(r.commit("events"))
        self.assertFalse(r.dirty())
        r.append("task.started", {})
        self.assertTrue(r.dirty())
        self.assertTrue(r.commit("question 01ABC match"))
        self.assertFalse(r.dirty())
        self.assertEqual(
            self.log()[0], "question 01ABC match|firsthand|firsthand@localhost"
        )

    def test_missing_or_wrong_format(self) -> None:
        with self.assertRaises(record.RecordError):
            record.Record(self.tmp / "nowhere")
        (self.root / "FORMAT").write_text("something else\n")
        with self.assertRaises(record.RecordError):
            record.Record()

    def test_read_json_errors(self) -> None:
        bad = self.tmp / "bad.json"
        bad.write_text("<<<<<<< HEAD\n{}\n")
        with self.assertRaises(record.RecordError):
            record.read_json(bad)
        bad.write_text("{nope")
        with self.assertRaises(record.RecordError):
            record.read_json(bad)
        good = self.tmp / "sub" / "good.json"
        record.write_json(good, {"b": 1, "a": 2})
        self.assertEqual(good.read_text(), '{\n  "a": 2,\n  "b": 1\n}\n')
        self.assertEqual(record.read_json(good), {"a": 2, "b": 1})
