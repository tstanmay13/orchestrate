"""Run: python3 -I -m unittest discover -s skills/orchestrate/scripts"""

import pathlib
import subprocess
import tempfile
import threading
import time
import unittest

SCRIPT = pathlib.Path(__file__).parent / "watch_merges.sh"


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class WatchMerges(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self.tmp.name)
        self.origin, self.work = tmp / "origin.git", tmp / "work"
        sh(tmp, "git", "init", "-q", "--bare", "-b", "main", str(self.origin))
        sh(tmp, "git", "clone", "-q", str(self.origin), str(self.work))
        self.commit("start")

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, msg):
        g = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        (self.work / "f.txt").write_text(msg)
        sh(self.work, *g, "add", "f.txt")
        sh(self.work, *g, "commit", "-q", "-m", msg)
        sh(self.work, "git", "push", "-q", "origin", "main")

    def run_watch(self, *args, timeout=30):
        return subprocess.run(
            ["bash", str(SCRIPT), "--repo", str(self.work), "--interval", "1", *args],
            capture_output=True, text=True, timeout=timeout,
        )

    def test_already_merged_exits_at_once(self):
        self.commit("A change (#17001)")
        done = self.run_watch("17001", "17002")
        self.assertEqual(done.returncode, 0)
        lines = done.stdout.splitlines()
        self.assertEqual(lines, ["merged: #17001", "still waiting: #17002"])

    def test_wakes_when_a_pr_merges_later(self):
        threading.Timer(2, self.commit, args=("Later (#17003)",)).start()
        started = time.time()
        done = self.run_watch("17003")
        self.assertEqual(done.returncode, 0)
        self.assertIn("merged: #17003", done.stdout)
        self.assertGreater(time.time() - started, 1)

    def test_times_out_saying_what_is_still_waiting(self):
        done = self.run_watch("17004", "--timeout", "2")
        self.assertEqual(done.returncode, 0)
        self.assertIn("still waiting: #17004", done.stdout)

    def test_a_number_inside_another_does_not_match(self):
        self.commit("Other (#170050)")
        done = self.run_watch("17005", "--timeout", "2")
        self.assertIn("still waiting: #17005", done.stdout)

    def test_needs_at_least_one_pr(self):
        done = self.run_watch()
        self.assertNotEqual(done.returncode, 0)


if __name__ == "__main__":
    unittest.main()
