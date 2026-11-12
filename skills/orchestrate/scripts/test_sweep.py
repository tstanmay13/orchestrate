"""Run: python3 -I -m unittest discover -s skills/orchestrate/scripts"""

import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import sweep  # noqa: E402

STATE = """# State
**Needs you:** pick a ticket

## Units
| unit | stage | status | PR | branch |
|---|---|---|---|---|
| 01 a | done | merged: abc1234 | [#101](x) | t/a |
| 02 b | verify | ready: 1111111 green | #102 | t/b |
| 03 c | build | working: started | - | - |
| 04 d | done | merged 2222222 | #104 | t/d |

## Workers
| worker | units | status |
|---|---|---|
| w1 | 01 | working |
"""


class ParseState(unittest.TestCase):
    def test_rows(self):
        closed, needs, units = sweep.parse_state("run", STATE)
        self.assertFalse(closed)
        self.assertEqual(needs, ["pick a ticket"])
        got = [(u.name, u.state, u.pr, u.branch, u.ready_sha) for u in units]
        self.assertEqual(
            got,
            [
                ("01 a", "merged", "101", "t/a", None),
                ("02 b", "ready", "102", "t/b", "1111111"),
                ("03 c", "working", None, None, None),
                ("04 d", "merged", "104", "t/d", None),
            ],
        )

    def test_closed_run(self):
        self.assertTrue(sweep.parse_state("run", "**Closed:** 2026-11-09\n")[0])

    def test_columns_found_by_name_and_extra_cell(self):
        cases = [
            ("| unit | PR | status |\n|---|---|---|\n| x | #17009 | ready: 3333333 |", ("ready", "17009")),
            ("| unit | a | b | PR | status | c |\n|-|-|-|-|-|-|\n| x | 1 | 2 | extra | #17009 | ready: 3333333 | d |",
             ("ready", "17009")),
        ]
        for table, want in cases:
            with self.subTest(table=table):
                (u,) = sweep.parse_state("run", table)[2]
                self.assertEqual((u.state, u.pr), want)


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class AgainstGit(unittest.TestCase):
    """A stale row, a ready branch that moved, and a ready branch whose file main also changed."""

    def test_sweep(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            origin, work = tmp / "origin.git", tmp / "work"
            sh(tmp, "git", "init", "-q", "--bare", "-b", "main", str(origin))
            sh(tmp, "git", "clone", "-q", str(origin), str(work))
            git = lambda *a: sh(work, "git", "-c", "user.name=t", "-c", "user.email=t@t", *a)  # noqa: E731

            def commit(path, text, msg):
                (work / path).write_text(text)
                git("add", path)
                git("commit", "-q", "-m", msg)
                return git("rev-parse", "HEAD")

            commit("a.txt", "1", "start")
            git("push", "-q", "origin", "main")
            git("checkout", "-q", "-b", "t/moved")
            gate_moved = commit("b.txt", "1", "moved gate")
            commit("b.txt", "2", "after gate")
            git("push", "-q", "origin", "t/moved")
            git("checkout", "-q", "main")
            git("checkout", "-q", "-b", "t/near")
            gate_near = commit("a.txt", "2", "near gate")
            git("push", "-q", "origin", "t/near")
            git("checkout", "-q", "main")
            commit("a.txt", "3", "main touches a.txt (#17007)")
            git("push", "-q", "origin", "main")

            run = tmp / "runs" / "r"
            run.mkdir(parents=True)
            (run / "state.md").write_text(
                "| unit | status | PR | branch |\n|---|---|---|---|\n"
                "| s | working: x | #17007 | - |\n"
                f"| m | ready: {gate_moved[:7]} green | #17008 | t/moved |\n"
                f"| n | ready: {gate_near[:7]} green | #17009 | t/near |\n"
            )
            text = "\n".join(sweep.sweep(sweep.Git(work, "main"), [run], fetch=True))
            stale = text.split("Stale")[1].split("Recheck")[0]
            recheck = text.split("Recheck before merge")[1].split("Open PRs")[0]
            self.assertIn("| s | #17007", stale)
            self.assertIn("m #17008: branch tip", recheck)
            self.assertIn("n #17009: main changed files this PR changes since its gate: a.txt", recheck)
            self.assertNotIn("m #17008: main changed", recheck)


if __name__ == "__main__":
    unittest.main()


WORKERS = """# State
## Units
| unit | stage | status | PR | branch |
|---|---|---|---|---|
| 01 a | done | merged: abc1234 | #17101 | t/a |
| 02 b | verify | ready: 1111111 green | #17102 | t/b |

## Workers
| worker | role | session | worktree | units | status |
|---|---|---|---|---|---|
| run-01 | implementer | [aaa111] | wt/a | 01 | working: idle |
| run-02 | implementer | [bbb222] | wt/b | 02 | working: fixing |
| run-00 | worker | [ccc333] | wt/c | 00 | dropped: done, session can be closed |
| run-v | verifier | [ddd444] | wt/v | 01 02 | working: queue |
"""

INLINE = """| unit | implementer | verifier | status | PR |
|---|---|---|---|---|
| 01 a | run-i1 [eee555] | run-v1 [fff666] | merged: x | #17201 |
| 02 b | run-i2 [abc777] | run-v1 [fff666] | working: y | #17202 |
"""


class Closeable(unittest.TestCase):
    def test_workers_table(self):
        _, _, units = sweep.parse_state("r", WORKERS)
        got = sweep.closeable_sessions("r", WORKERS, units, closed=False)
        self.assertEqual(got, ["run-00 [ccc333]"])  # a Workers row is trusted only by its own status

    def test_inline_implementer_and_verifier_columns(self):
        _, _, units = sweep.parse_state("r", INLINE)
        got = sweep.closeable_sessions("r", INLINE, units, closed=False)
        self.assertEqual(got, ["run-i1 [eee555]"])

    def test_closed_run_frees_everyone(self):
        _, _, units = sweep.parse_state("r", INLINE)
        got = sweep.closeable_sessions("r", INLINE, units, closed=True)
        self.assertEqual(got, ["run-i1 [eee555]", "run-i2 [abc777]", "run-v1 [fff666]"])


    def test_subagent_workers_are_not_sessions_to_close(self):
        text = WORKERS + "| 2026-11-12-q-03 | implementer | subagent | wt/d | 03 | dropped: done |\n"
        _, _, units = sweep.parse_state("r", text)
        got = sweep.closeable_sessions("r", text, units, closed=True)
        self.assertNotIn("2026-11-12-q-03", " ".join(got))  # a mini run's subagents end with the run, not by the human

    def test_no_duplicates_or_junk_names(self):
        text = WORKERS.replace("| run-01 | implementer | [aaa111] | wt/a | 01 | working: idle |",
                               "| run-01 | implementer | [aaa111] | wt/a | 01 | done: finished |\n| orch | x | - | - | 01 | done |")
        text += "\n| unit | implementer | status | PR |\n|---|---|---|---|\n| 01 a | run-01 | merged: x | #17101 |\n"
        _, _, units = sweep.parse_state("r", text)
        got = sweep.closeable_sessions("r", text, units, closed=False)
        self.assertEqual(got, ["run-00 [ccc333]", "run-01 [aaa111]"])
