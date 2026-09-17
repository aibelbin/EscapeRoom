import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from leaderboard import LeaderboardError, add_finish, load, ranked


class LeaderboardTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.path = Path(self._tmp.name) / "leaderboard.json"

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_missing_file_is_empty(self):
        self.assertEqual(load(self.path), {"entries": []})

    def test_add_finish_appends_and_ranks(self):
        add_finish(self.path, name="Jonah Reed", time_ms=541000, finished_at="2026-09-17T19:40:00")
        result = add_finish(
            self.path, name="Ada Lovelace", time_ms=492340, finished_at="2026-09-17T19:42:03"
        )
        names = [row["name"] for row in result["entries"]]
        self.assertEqual(names, ["Ada Lovelace", "Jonah Reed"])
        saved = json.loads(self.path.read_text())
        self.assertEqual(saved["entries"][0]["name"], "Jonah Reed")
        self.assertEqual(ranked(saved["entries"])[0]["name"], "Ada Lovelace")

    def test_rank_ties_use_finished_at(self):
        add_finish(self.path, name="Later", time_ms=1000, finished_at="2026-09-17T20:00:00")
        add_finish(self.path, name="Earlier", time_ms=1000, finished_at="2026-09-17T19:00:00")
        names = [row["name"] for row in load(self.path)["entries"]]
        ranked_names = [row["name"] for row in ranked(load(self.path)["entries"])]
        self.assertEqual(names, ["Later", "Earlier"])
        self.assertEqual(ranked_names, ["Earlier", "Later"])

    def test_reject_empty_name(self):
        with self.assertRaisesRegex(LeaderboardError, "Need a name"):
            add_finish(self.path, name="   ", time_ms=1000, finished_at="2026-09-17T19:00:00")

    def test_reject_zero_time(self):
        with self.assertRaisesRegex(LeaderboardError, "Start the clock first"):
            add_finish(self.path, name="Ada", time_ms=0, finished_at="2026-09-17T19:00:00")


if __name__ == "__main__":
    unittest.main()
