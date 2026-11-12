"""Sweep every active run's state.md and check its claims against git.

Prints, for the human:
- units whose status starts with "ready", meaning ready to send for approval (PR, sha, run), and every "**Needs you:**" line;
- stale rows: a unit not marked merged/done/dropped whose PR is already on the main branch;
- recheck rows: a ready unit whose branch tip moved past the sha in its ready line, or whose
  changed files were also changed on main after its gate sha;
- PRs still to check for CI (this script never calls GitHub).

Usage: python3 -I sweep.py --repo <checkout> [--days 3] [--run NAME ...] [--no-fetch]
State root: ORCHESTRATE_HOME, else ~/.config/agent-orchestrate.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys
import time
from dataclasses import dataclass

FINISHED = ("merged", "done", "dropped")
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")
PR = re.compile(r"#(\d{3,})")


@dataclass
class Unit:
    run: str
    name: str
    status: str
    pr: str | None
    branch: str | None

    @property
    def state(self) -> str:
        word = re.match(r"[a-z-]+", self.status.strip().lower())
        return word.group(0) if word else ""

    @property
    def ready_sha(self) -> str | None:
        found = SHA.search(self.status) if self.state == "ready" else None
        return found.group(0) if found else None


def cells(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def align(header: list[str], row: list[str]) -> dict[str, str]:
    """Map a row to its header. A row with a missing or extra cell keeps its left half aligned
    from the left and its right half (status, PR, last checked) aligned from the right."""
    if len(row) == len(header):
        return dict(zip(header, row))
    half = len(header) // 2
    got = dict(zip(header[:half], row[:half]))
    for i, name in enumerate(header[half:], start=half):
        j = i - len(header) + len(row)
        if half <= j < len(row):
            got[name] = row[j]
    return got


def parse_state(run: str, text: str) -> tuple[bool, list[str], list[Unit]]:
    """Whether the run is closed, its Needs-you lines, and the rows of its units table."""
    lines = text.splitlines()
    closed = any(line.startswith("**Closed:**") for line in lines)
    needs = [line.split(":**", 1)[1].strip() for line in lines if line.startswith("**Needs you:**")]
    units: list[Unit] = []
    header: list[str] | None = None
    for line in lines:
        if not line.startswith("|"):
            header = None
            continue
        row = cells(line)
        if header is None:
            lowered = [c.lower() for c in row]
            header = lowered if "unit" in lowered and "status" in lowered else None
            continue
        if set("".join(row)) <= set("-: "):
            continue
        get = align(header, row)
        pr = PR.search(get.get("pr", ""))
        branch = get.get("branch", "").strip("` ")
        units.append(
            Unit(
                run=run,
                name=get["unit"],
                status=get["status"],
                pr=pr.group(1) if pr else None,
                branch=branch if branch and branch not in ("-", "none") and " " not in branch else None,
            )
        )
    return closed, needs, units


SESSION = re.compile(r"^(?P<name>[\w.-]+)\s*(?P<ref>\[[0-9a-f]{4,}\])?")


def _unit_key(name: str) -> str:
    return name.split()[0] if name.split() else name


DATED_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def closeable_sessions(run: str, text: str, units: list[Unit], closed: bool) -> list[str]:
    """Worker sessions with nothing left to do, as `name [ref]`.

    A run with a Workers table (worker, session, units, status) is trusted only by each row's own
    status: done, dropped or "can be closed". Rows go stale when a worker is reused, so its units
    are not used to guess. A run without one is read from the units table's implementer and
    verifier columns: a session is free when every unit it appears on is merged, done or dropped.
    In a closed run every named worker is free. Names with no session ref and no dated run prefix
    are skipped as notes, not sessions, and so are a mini run's subagents (session `subagent`),
    which end with the run instead of being closed by the human."""
    finished = {_unit_key(u.name): u.state in FINISHED for u in units}
    refs: dict[str, str] = {}
    free: set[str] = set()
    holds: dict[str, list[bool]] = {}
    has_workers = any(
        line.startswith("|") and {"worker", "status"} <= {c.lower() for c in cells(line)}
        for line in text.splitlines()
    )

    def note(name: str, ref: str) -> str | None:
        ref = ref.strip().strip("[]")
        if re.fullmatch(r"[0-9a-f]{4,}", ref or ""):
            refs[name] = ref
        elif not DATED_NAME.match(name):
            return None
        return name

    header: list[str] | None = None
    for line in text.splitlines():
        if not line.startswith("|"):
            header = None
            continue
        row = cells(line)
        if header is None:
            header = [c.lower() for c in row]
            continue
        if set("".join(row)) <= set("-: "):
            continue
        get = align(header, row)
        if "worker" in header and "status" in header:
            name = note(get.get("worker", "").split()[0] if get.get("worker") else "", get.get("session", ""))
            if not name or "stray" in get.get("worker", "") or get.get("session", "").startswith("subagent"):
                continue
            status = get.get("status", "").lower()
            word = re.match(r"[a-z-]+", status.strip())
            if closed or (word and word.group(0) in FINISHED) or "can be closed" in status:
                free.add(name)
        elif "unit" in header and not has_workers:
            key = _unit_key(get.get("unit", ""))
            for column in ("implementer", "verifier"):
                found = SESSION.match(get.get(column, "").strip())
                if not found:
                    continue
                name = note(found.group("name"), found.group("ref") or "")
                if name:
                    holds.setdefault(name, []).append(finished.get(key, False))
    for name, held in holds.items():
        if closed or (held and all(held)):
            free.add(name)
    return sorted(f"{n} [{refs[n]}]" if n in refs else n for n in free)


class Git:
    def __init__(self, repo: pathlib.Path, main: str) -> None:
        self.repo, self.main = repo, main

    def __call__(self, *args: str, check: bool = True) -> str:
        done = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True)
        if check and done.returncode:
            raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
        return done.stdout if done.returncode == 0 else ""

    def merged_prs(self, depth: int = 3000) -> set[str]:
        subjects = self("log", f"-{depth}", "--format=%s", f"origin/{self.main}")
        return {m.group(1) for s in subjects.splitlines() for m in [re.search(r"\(#(\d+)\)$", s)] if m}

    def tips(self, branches: list[str]) -> dict[str, str]:
        if not branches:
            return {}
        out = self("ls-remote", "origin", *[f"refs/heads/{b}" for b in branches], check=False)
        return {ref.removeprefix("refs/heads/"): sha for sha, ref in (l.split("\t") for l in out.splitlines())}

    def touched_since_gate(self, gate: str) -> list[str]:
        """Files the branch changed that main also changed after the branch's base, as of the gate."""
        base = self("merge-base", f"origin/{self.main}", gate, check=False).strip()
        if not base:
            return []
        mine = set(self("diff", "--name-only", base, gate).split())
        theirs = set(self("diff", "--name-only", base, f"origin/{self.main}").split())
        return sorted(mine & theirs)


def active_runs(root: pathlib.Path, days: float, names: list[str]) -> list[pathlib.Path]:
    runs = sorted(p for p in (root / "runs").iterdir() if (p / "state.md").is_file())
    if names:
        return [p for p in runs if p.name in names]
    cutoff = time.time() - days * 86400
    return [p for p in runs if (p / "state.md").stat().st_mtime >= cutoff]


def sweep(git: Git, runs: list[pathlib.Path], fetch: bool) -> list[str]:
    parsed = []
    free: list[str] = []
    for run in runs:
        text = (run / "state.md").read_text()
        closed, needs, units = parse_state(run.name, text)
        free += [f"{run.name}: {who}" for who in closeable_sessions(run.name, text, units, closed)]
        if not closed:
            parsed.append((run.name, needs, units))
    units = [u for _, _, us in parsed for u in us]
    ready = [u for u in units if u.state == "ready"]
    if fetch:
        refspecs = [f"refs/heads/{u.branch}" for u in ready if u.branch]
        git("fetch", "-q", "origin", git.main, check=True)
        if refspecs:
            git("fetch", "-q", "origin", *refspecs, check=False)
    merged = git.merged_prs()
    tips = git.tips(sorted({u.branch for u in ready if u.branch}))

    out: list[str] = []
    head = git("rev-parse", "--short=11", f"origin/{git.main}").strip()
    out.append(f"origin/{git.main} at {head}; runs: {', '.join(n for n, _, _ in parsed) or 'none'}")

    out.append("\nReady to send for approval")
    recheck: list[str] = []
    for u in ready:
        if u.pr in merged:
            continue
        out.append(f"- {u.run} | {u.name} | #{u.pr or '?'} | {u.status}")
        tip = tips.get(u.branch or "")
        if u.ready_sha and tip and not tip.startswith(u.ready_sha):
            recheck.append(f"- {u.name} #{u.pr}: branch tip {tip[:11]} moved past the ready sha {u.ready_sha}")
        elif u.branch and not tip:
            recheck.append(f"- {u.name} #{u.pr}: branch {u.branch} not found on origin")
        if u.ready_sha and git("cat-file", "-t", u.ready_sha, check=False).strip() == "commit":
            both = git.touched_since_gate(u.ready_sha)
            if both:
                shown = ", ".join(both[:5]) + (f" (+{len(both) - 5} more)" if len(both) > 5 else "")
                recheck.append(f"- {u.name} #{u.pr}: main changed files this PR changes since its gate: {shown}")

    out.append("\nNeeds you")
    out += [f"- {name}: {line}" for name, needs, _ in parsed for line in needs] or ["- none"]

    stale = [u for u in units if u.pr in merged and u.state not in FINISHED]
    out.append("\nStale (PR on main, state not updated)")
    out += [f"- {u.run} | {u.name} | #{u.pr} | {u.status[:80]}" for u in stale] or ["- none"]

    out.append("\nRecheck before merge")
    out += recheck or ["- none"]

    waiting = [u for u in units if u.pr and u.pr not in merged and u.state not in FINISHED]
    out.append("\nOpen PRs to check for CI (not checked here)")
    out.append("- " + (" ".join(sorted({f"#{u.pr}" for u in waiting})) or "none"))

    out.append("\nSessions you can close (their units are finished)")
    out += [f"- {line}" for line in free] or ["- none"]

    counts: dict[str, dict[str, int]] = {}
    for u in units:
        if u.state not in FINISHED and u not in stale:
            counts.setdefault(u.run, {}).setdefault(u.state, 0)
            counts[u.run][u.state] += 1
    out.append("\nIn progress")
    for name, by_state in counts.items():
        out.append(f"- {name}: " + ", ".join(f"{k} {v}" for k, v in sorted(by_state.items())))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", default=".", help="git checkout whose origin holds the PRs")
    ap.add_argument("--main", default="main")
    ap.add_argument("--days", type=float, default=3, help="runs whose state.md changed in this many days")
    ap.add_argument("--run", action="append", default=[], help="sweep only these runs")
    ap.add_argument("--no-fetch", action="store_true")
    args = ap.parse_args()
    root = pathlib.Path(os.environ.get("ORCHESTRATE_HOME", "~/.config/agent-orchestrate")).expanduser()
    git = Git(pathlib.Path(args.repo).expanduser(), args.main)
    print("\n".join(sweep(git, active_runs(root, args.days, args.run), fetch=not args.no_fetch)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
