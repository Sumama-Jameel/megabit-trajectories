#!/usr/bin/env python3
"""Verify the exported MegaBit trajectory artifacts.

Checks sha256 values recorded in finalization.json, header/footer presence,
tool-call counts, and the export verdict. Does not re-run the sandbox.

Usage:
    python3 verify.py
    python3 verify.py --quiet
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EPISODES = ROOT / "episodes"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def check_episode(ep: Path) -> list:
    problems = []
    fin_path = ep / "finalization.json"
    if not fin_path.exists():
        return ["missing finalization.json"]
    try:
        fin = json.loads(fin_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"unreadable finalization.json: {exc}"]

    episode_path = ep / f"{ep.name}.episode.jsonl"
    sample_path = ep / f"{ep.name}.sample.jsonl"
    if not episode_path.exists():
        problems.append("missing episode.jsonl")
    if not sample_path.exists():
        problems.append("missing sample.jsonl")
    if problems:
        return problems

    if sha256(episode_path) != fin.get("raw_sha256"):
        problems.append("episode sha256 mismatch")
    if sha256(sample_path) != fin.get("sample_sha256"):
        problems.append("sample sha256 mismatch")
    if fin.get("export_committed") is not True:
        problems.append("export_committed is not true")

    events = read_jsonl(episode_path)
    if not events:
        problems.append("empty episode.jsonl")
    else:
        if events[0].get("type") != "episode_header":
            problems.append("missing episode_header")
        if events[-1].get("type") != "episode_footer":
            problems.append("missing episode_footer")
        tool_calls = sum(1 for e in events if e.get("type") == "tool_call")
        seg = events[-1].get("segmentation", {}) or {}
        seg_counts = seg.get("tool_calls")
        if isinstance(seg_counts, list):
            seg_total = sum(seg_counts)
            if seg_total != tool_calls:
                problems.append(f"tool calls {tool_calls} != footer {seg_total}")

    sample = read_jsonl(sample_path)
    if not sample:
        problems.append("empty sample.jsonl")
    else:
        row = sample[0]
        if not row.get("messages"):
            problems.append("sample messages empty")
        prov = row.get("provenance", {}) or {}
        for key in ("repo_name", "base_commit", "target_commit", "license_spdx", "task_fingerprint"):
            if not prov.get(key):
                problems.append(f"provenance missing {key}")
        if prov.get("task_mac_valid") is False:
            problems.append("task MAC invalid")
        verification = row.get("verification", {}) or {}
        if verification.get("passed") is False:
            problems.append("verification.passed is false")

    return problems


def main() -> int:
    quiet = "--quiet" in sys.argv
    if not EPISODES.is_dir():
        print(f"episodes directory not found: {EPISODES}")
        return 1

    dirs = sorted(d for d in EPISODES.iterdir() if d.is_dir())
    failures = 0
    for ep in dirs:
        problems = check_episode(ep)
        if problems:
            failures += 1
            print(f"FAIL {ep.name}")
            for p in problems:
                print(f"     - {p}")
        elif not quiet:
            print(f"ok   {ep.name}")

    total = len(dirs)
    print(f"\n{total - failures}/{total} episodes verified")
    if failures:
        print(f"{failures} failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
