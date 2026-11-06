"""Behaviour tests for the learning record scripts.

Each test runs the real command-line scripts against a fresh temporary record,
the same way the skill runs them. Nothing is mocked: the scripts read and
write real files, and the server test talks to a real server over HTTP.

Run with:  python3 -m unittest discover -s tests
"""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "learning-while-building"
LEARNING = SKILL / "scripts" / "learning.py"
CHECK_EXPLAINER = SKILL / "scripts" / "check_explainer.py"


class Record:
    """A throwaway record directory driven through the CLI."""

    def __init__(self, work: Path) -> None:
        self.work = work
        self.dir = work / ".learning"

    def run(
        self, *args: str, today: str | None = None, ok: bool = True, stdin: str = ""
    ) -> str:
        cmd = [sys.executable, str(LEARNING), "--dir", str(self.dir)]
        if today:
            cmd += ["--today", today]
        done = subprocess.run(
            cmd + list(args),
            cwd=self.work,
            capture_output=True,
            text=True,
            input=stdin,
            check=False,
        )
        if ok and done.returncode != 0:
            raise AssertionError(
                f"{args} failed ({done.returncode}): {done.stderr}{done.stdout}"
            )
        if not ok and done.returncode == 0:
            raise AssertionError(f"{args} should have failed: {done.stdout}")
        return done.stdout + done.stderr

    def attempt(self, attempt_id: str) -> dict:
        return json.loads((self.dir / "attempts" / f"{attempt_id}.json").read_text())

    def ask(self, topic: str, kind: str, today: str | None = None, *extra: str) -> str:
        out = self.run(
            "ask",
            "--topic",
            topic,
            "--kind",
            kind,
            "--question",
            "q",
            "--rubric",
            "r",
            *extra,
            today=today,
        )
        return out.split()[1]

    def post(self, topic: str, question: str = "q") -> str:
        out = self.run(
            "post",
            "--topic",
            topic,
            "--kind",
            "retrieval",
            "--question",
            question,
            "--rubric",
            "r",
        )
        return out.split()[1].rstrip(".")

    def grade(
        self,
        attempt_id: str,
        outcome: str,
        hint: int = 0,
        today: str | None = None,
        *extra: str,
    ) -> str:
        return self.run(
            "grade",
            "--attempt",
            attempt_id,
            "--outcome",
            outcome,
            "--hint",
            str(hint),
            *extra,
            today=today,
        )


class RecordTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.rec = Record(self.tmp)
        self.rec.run("init")
        self.rec.run(
            "topic",
            "add",
            "--id",
            "t",
            "--dimension",
            "concurrency",
            "--concept",
            "c",
            today="2026-01-01",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def answer_chat(
        self,
        today: str,
        kind: str,
        outcome: str,
        hint: int = 0,
        confidence: str = "medium",
    ) -> str:
        attempt_id = self.rec.ask("t", kind, today)
        return self.rec.grade(
            attempt_id,
            outcome,
            hint,
            today,
            "--confidence",
            confidence,
            "--answer",
            "a",
        )


class ScheduleTest(RecordTest):
    def test_intervals_grow_with_unaided_correct_answers(self) -> None:
        days = ["2026-01-02", "2026-01-05", "2026-01-12", "2026-02-02", "2026-04-03"]
        expected = [
            "2026-01-05",
            "2026-01-12",
            "2026-02-02",
            "2026-04-03",
            "2026-09-30",
        ]
        for day, due in zip(days, expected):
            out = self.answer_chat(day, "retrieval", "correct")
            self.assertIn(f"Next review of t: {due}", out)

    def test_hinted_answer_resets_the_streak(self) -> None:
        for day in ["2026-01-02", "2026-01-05", "2026-01-12"]:
            self.answer_chat(day, "retrieval", "correct")
        self.assertIn(
            "2026-02-03", self.answer_chat("2026-02-02", "retrieval", "correct", hint=2)
        )
        self.assertIn(
            "2026-02-06", self.answer_chat("2026-02-03", "retrieval", "correct")
        )

    def test_correct_at_h3_is_refused(self) -> None:
        attempt_id = self.rec.ask("t", "retrieval")
        out = self.rec.run(
            "grade",
            "--attempt",
            attempt_id,
            "--outcome",
            "correct",
            "--hint",
            "3",
            "--confidence",
            "low",
            "--answer",
            "a",
            ok=False,
        )
        self.assertIn("Hint level 3", out)


class EvidenceTest(RecordTest):
    def test_later_miss_shows_in_current_evidence_not_highest(self) -> None:
        self.answer_chat("2026-01-02", "explain-back", "correct")
        self.answer_chat("2026-01-05", "transfer", "correct")
        self.answer_chat("2026-01-12", "retrieval", "wrong", confidence="high")
        out = self.rec.run("map", "--topic", "t", today="2026-01-12")
        self.assertIn("highest demonstrated: transfers (2026-01-05)", out)
        self.assertIn(
            "current evidence: uncertain: latest review was wrong, unaided", out
        )
        self.assertIn("confident-and-wrong answers: 1", out)

    def test_field_report_without_evidence_does_not_raise_level(self) -> None:
        out = self.answer_chat("2026-01-02", "field", "correct")
        self.assertIn("Self-report recorded", out)
        self.assertIn(
            "highest demonstrated: not yet", self.rec.run("map", "--topic", "t")
        )

    def test_field_report_with_evidence_counts(self) -> None:
        attempt_id = self.rec.ask("t", "field", "2026-01-02")
        self.rec.grade(
            attempt_id,
            "correct",
            0,
            "2026-01-02",
            "--confidence",
            "high",
            "--answer",
            "fixed it",
            "--evidence",
            "commit abc123",
        )
        self.assertIn(
            "highest demonstrated: transfers", self.rec.run("map", "--topic", "t")
        )

    def test_default_map_lists_only_topics_not_holding(self) -> None:
        self.rec.run(
            "topic",
            "add",
            "--id",
            "u",
            "--dimension",
            "concurrency",
            "--concept",
            "c2",
            today="2026-01-01",
        )
        self.answer_chat("2026-01-02", "retrieval", "correct")
        out = self.rec.run("map", today="2026-01-03")
        self.assertIn("  u: highest not yet", out)
        self.assertNotIn("  t: highest", out)


class AskingTest(RecordTest):
    def test_open_chat_question_blocks_the_next_one(self) -> None:
        self.rec.ask("t", "retrieval")
        out = self.rec.run(
            "ask",
            "--topic",
            "t",
            "--kind",
            "retrieval",
            "--question",
            "q",
            "--rubric",
            "r",
            ok=False,
        )
        self.assertIn("Still ungraded", out)

    def test_batch_allows_three_open_questions(self) -> None:
        for _ in range(3):
            self.rec.ask("t", "retrieval", None, "--batch")
        out = self.rec.run(
            "ask",
            "--batch",
            "--topic",
            "t",
            "--kind",
            "retrieval",
            "--question",
            "q",
            "--rubric",
            "r",
            ok=False,
        )
        self.assertIn("at most 3", out)

    def test_posted_questions_never_block_chat(self) -> None:
        self.rec.post("t")
        self.rec.ask("t", "retrieval")


class RoomTest(RecordTest):
    def test_post_answer_inbox_grade_feedback(self) -> None:
        attempt_id = self.rec.post("t", "Why a key?")
        self.assertIn("1 question(s) waiting", self.rec.run("questions"))
        self.rec.run(
            "answer",
            "--text",
            "Because a timeout is not a failure.",
            "--confidence",
            "high",
        )
        self.assertIn("Because a timeout", self.rec.run("inbox"))
        self.rec.grade(attempt_id, "correct", 0, None, "--feedback", "Correct.")
        out = self.rec.run("questions")
        self.assertIn("CORRECT  Why a key?", out)
        self.assertIn("Correct.", out)
        self.assertEqual(self.rec.attempt(attempt_id)["graded"]["confidence"], "high")

    def test_answer_locks(self) -> None:
        attempt_id = self.rec.post("t")
        self.rec.run("answer", "--dont-know")
        out = self.rec.run(
            "answer",
            "--attempt",
            attempt_id,
            "--text",
            "again",
            "--confidence",
            "high",
            ok=False,
        )
        self.assertIn("locked", out)
        self.assertEqual(
            self.rec.attempt(attempt_id)["response"]["answer"], "I don't know."
        )

    def test_terminal_prompt_reads_answer_and_confidence(self) -> None:
        attempt_id = self.rec.post("t")
        self.rec.run("answer", stdin="line one\nline two\n\nh\n")
        response = self.rec.attempt(attempt_id)["response"]
        self.assertEqual(
            (response["answer"], response["confidence"]), ("line one\nline two", "high")
        )

    def test_push_and_pull_round_trip(self) -> None:
        attempt_id = self.rec.post("t", "Why a key?")
        push = self.tmp / "push"
        self.rec.run("room-push", "--out", str(push))
        doc = json.loads((push / f"{attempt_id}.json").read_text())
        self.assertEqual((doc["status"], doc["rubric"]), ("open", "r"))
        doc.update(
            status="graded",
            answer="a",
            confidence="low",
            outcome="partial",
            feedback="Not quite.",
            gap="g",
            restatement="r1",
        )
        pulled = self.tmp / "pulled"
        pulled.mkdir()
        (pulled / f"{attempt_id}.json").write_text(json.dumps(doc))
        self.assertIn(
            "1 new answer(s), 1 graded there",
            self.rec.run("room-pull", "--from", str(pulled)),
        )
        self.assertIn(
            "0 new answer(s), 0 graded there",
            self.rec.run("room-pull", "--from", str(pulled)),
        )
        graded = self.rec.attempt(attempt_id)["graded"]
        self.assertEqual(
            (graded["grader"], graded["via"], graded["outcome"]),
            ("claude", "page", "partial"),
        )


class ServerTest(RecordTest):
    def setUp(self) -> None:
        super().setUp()
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            self.port = s.getsockname()[1]
        cmd = [
            sys.executable,
            str(LEARNING),
            "--dir",
            str(self.rec.dir),
            "serve",
            "--port",
            str(self.port),
        ]
        self.server = subprocess.Popen(
            cmd, cwd=self.tmp, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        self.server.stdout.readline()  # the "Learning room at ..." line means it is listening

    def tearDown(self) -> None:
        self.server.terminate()
        self.server.wait(timeout=10)
        self.server.stdout.close()
        super().tearDown()

    def post_json(self, path: str, body: dict) -> int:
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code

    def test_page_and_api_hide_the_rubric(self) -> None:
        self.rec.post("t")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as r:
            self.assertIn(b"Learning Room", r.read())
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/questions") as r:
            rows = json.load(r)
        self.assertEqual(len(rows), 1)
        self.assertNotIn("rubric", rows[0])

    def test_concurrent_answers_are_accepted_once(self) -> None:
        attempt_id = self.rec.post("t")
        codes = []
        threads = [
            threading.Thread(
                target=lambda i=i: codes.append(
                    self.post_json(
                        "/api/answer",
                        {"id": attempt_id, "answer": f"a{i}", "confidence": "low"},
                    )
                )
            )
            for i in range(20)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(codes.count(200), 1)
        self.assertEqual(codes.count(400), 19)

    def test_bad_requests_are_refused(self) -> None:
        self.assertEqual(
            self.post_json(
                "/api/answer", {"id": "nope", "answer": "a", "confidence": "low"}
            ),
            400,
        )
        self.assertEqual(self.post_json("/api/elsewhere", {}), 404)


class MergeTest(unittest.TestCase):
    """Two sessions on two branches each record an attempt; git must merge them."""

    def test_branches_merge_without_conflict(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not installed")
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        git = lambda *a: subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", *a],
            cwd=tmp,
            check=True,
            capture_output=True,
        )
        git("init", "-q", "-b", "main")
        rec = Record(tmp)
        rec.run("init")
        rec.run(
            "topic", "add", "--id", "t", "--dimension", "concurrency", "--concept", "c"
        )
        git("add", "-A")
        git("commit", "-qm", "base")
        for branch in ("a", "b"):
            git("checkout", "-q", "-b", branch, "main")
            rec.grade(
                rec.ask("t", "retrieval"),
                "correct",
                0,
                None,
                "--confidence",
                "low",
                "--answer",
                "x",
            )
            git("add", "-A")
            git("commit", "-qm", branch)
        git("checkout", "-q", "a")
        git("merge", "-q", "b", "-m", "merge")
        self.assertIn("2 attempt(s)", rec.run("check"))


class MigrateTest(unittest.TestCase):
    def test_old_field_reports_become_self_reports(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        old = tmp / ".learning"
        old.mkdir()
        topics = {
            "schema_version": 1,
            "dimensions": ["security"],
            "topics": {
                "s": {
                    "dimension": "security",
                    "concept": "c",
                    "anchors": [],
                    "created": "2026-01-01",
                    "status": "active",
                }
            },
        }
        (old / "topics.json").write_text(json.dumps(topics))
        events = [
            {
                "event": "ask",
                "attempt": 1,
                "topic": "s",
                "kind": "field",
                "question": "q",
                "rubric": "r",
                "at": "2026-01-02T12:00:00",
            },
            {
                "event": "grade",
                "attempt": 1,
                "outcome": "correct",
                "hint": 0,
                "confidence": "high",
                "answer": "a",
                "gap": "",
                "at": "2026-01-02T12:00:01",
            },
        ]
        (old / "attempts.jsonl").write_text(
            "\n".join(json.dumps(e) for e in events) + "\n"
        )
        rec = Record(tmp)
        self.assertIn("old single-file format", rec.run("map", ok=False))
        rec.run("migrate")
        self.assertEqual(rec.attempt("v1-0001")["graded"]["grader"], "self")
        self.assertIn("highest demonstrated: not yet", rec.run("map", "--topic", "s"))


class ExplainerCheckTest(unittest.TestCase):
    def run_check(self, page: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CHECK_EXPLAINER), str(page), "--no-browser"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_template_needs_its_example_markers_replaced(self) -> None:
        done = self.run_check(SKILL / "assets" / "explainer-template.html")
        self.assertEqual(done.returncode, 1)
        self.assertIn("template marker", done.stdout)

    def test_filled_template_passes_static_checks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        page = tmp / "page.html"
        page.write_text(
            (SKILL / "assets" / "explainer-template.html")
            .read_text()
            .replace("EXAMPLE", "")
        )
        done = self.run_check(page)
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_answer_shown_on_load_is_caught(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        page = tmp / "page.html"
        html = (
            (SKILL / "assets" / "explainer-template.html")
            .read_text()
            .replace("EXAMPLE", "")
        )
        page.write_text(
            html.replace('<div class="ex-reveal" hidden>', '<div class="ex-reveal">', 1)
        )
        self.assertIn("lacks the hidden attribute", self.run_check(page).stdout)


if __name__ == "__main__":
    unittest.main()
