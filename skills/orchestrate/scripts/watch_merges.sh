#!/usr/bin/env bash
# Wait until any of the given pull requests merges into the main branch, then print which and exit.
#
# Meant to run under a background monitor (Claude Code's Monitor tool), so an orchestrator spends no
# model tokens while it waits and wakes as soon as the human merges. It reads merges from git: a PR
# counts as merged when a commit subject on origin/<main> ends with "(#N)", which is what a squash
# merge writes. One small fetch per interval. On timeout it exits 0 too, listing what still waits, so
# the session wakes and can say so instead of waiting forever.
#
# Usage: watch_merges.sh --repo <checkout> [--main main] [--interval 300] [--timeout 86400] PR [PR...]
set -euo pipefail

repo=. main=main interval=300 timeout=86400 prs=()
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) repo="$2"; shift 2 ;;
    --main) main="$2"; shift 2 ;;
    --interval) interval="$2"; shift 2 ;;
    --timeout) timeout="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) prs+=("${1#\#}"); shift ;;
  esac
done
if [ "${#prs[@]}" -eq 0 ]; then
  echo "watch_merges: name at least one pull request number" >&2
  exit 2
fi

deadline=$(( $(date +%s) + timeout ))
while :; do
  git -C "$repo" fetch -q origin "$main" || echo "watch_merges: fetch failed, retrying next interval" >&2
  subjects="$(git -C "$repo" log -1000 --format=%s "origin/$main" 2>/dev/null || true)"
  merged=() waiting=()
  for pr in "${prs[@]}"; do
    if grep -qE "\(#${pr}\)\$" <<<"$subjects"; then merged+=("#$pr"); else waiting+=("#$pr"); fi
  done
  if [ "${#merged[@]}" -gt 0 ]; then
    echo "merged: ${merged[*]}"
    [ "${#waiting[@]}" -gt 0 ] && echo "still waiting: ${waiting[*]}"
    exit 0
  fi
  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "still waiting: ${waiting[*]} (timed out after ${timeout}s)"
    exit 0
  fi
  sleep "$interval"
done
