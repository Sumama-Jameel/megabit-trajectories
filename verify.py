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


def find_episodes(root: Path) -> list:  # returns episode dirs
    episodes = root / "episodes"
    if episodes.is_dir():
        dirs = sorted(
            d for d in episodes.iterdir()
            if d.is_dir() and (d / f"{d.name}.episode.jsonl").exists()
        )
        if dirs:
            return dirs, "episodes/"
    # Kaggle auto-extracted layout: ./<task_id>/episodes/<task_id>/...
    # where the extraction root doubles as the dataset repo root
    eps = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        inner = d / "episodes" / d.name
        if (inner / f"{d.name}.episode.jsonl").exists():
            eps.append(inner)
    return eps, "kaggle<task_id>/episodes/<task_id>/"


def _check_v2_sample(ep: Path, problems: list) -> None:
    """Validate a kept-rejection v2 sample when one ships beside v1.

    v1 bytes are never touched. A v2 file uses the same one-line JSONL shape,
    with bad model-made calls in the labeled ``parse_status: error`` wrapper
    and a paired tool turn carrying the rejection. Strict readers can branch
    on ``parse_status`` before parsing arguments.
    """
    v2 = ep / f"{ep.name}.sample_v2.jsonl"
    if not v2.exists():
        return
    rows = read_jsonl(v2)
    if len(rows) != 1:
        problems.append("sample_v2 must contain exactly one JSON line")
        return
    messages = rows[0].get("messages") or []
    kept: dict[str, dict] = {}
    for m in messages:
        for call in (m.get("tool_calls") or []):
            if (call.get("parse_status") == "error"
                    and isinstance(call.get("arguments_raw"), str)
                    and call.get("arguments_raw")):
                kept[str(call.get("id"))] = call
    tool_by_id = {str(m.get("tool_call_id")): m for m in messages
                  if m.get("role") == "tool"}
    for cid, call in kept.items():
        tool = tool_by_id.get(cid)
        if tool is None:
            problems.append(f"kept rejection has no tool result: {cid}")
            continue
        if tool.get("error") != "rejected":
            problems.append(f"kept rejection lacks rejection marker: {cid}")
        if not str(tool.get("content") or "").strip():
            problems.append(f"kept rejection has no error text: {cid}")


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

    _check_v2_sample(ep, problems)
    return problems


def main() -> int:
    quiet = "--quiet" in sys.argv
    dirs, layout = find_episodes(ROOT)
    if not dirs:
        print(f"episodes not found under {ROOT}/episodes or ./<task_id>/episodes/<task_id>/")
        return 1
    if not quiet:
        print(f"layout: {layout} ({len(dirs)} episode dirs)")
    failures = 0

    manifest_path = ROOT / "training_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            rows = manifest.get("episodes") or []
            if len(rows) != len(dirs):
                print("FAIL training_manifest episode count mismatch")
                failures += 1
            for row in rows:
                rel, digest = row.get("path"), row.get("sha256")
                target = ROOT / str(rel)
                if not target.is_file() or sha256(target) != digest:
                    print(f"FAIL training_manifest checksum: {row.get('episode')}")
                    failures += 1
        except Exception as exc:
            print(f"FAIL training_manifest unreadable: {exc}")
            failures += 1
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
