#!/usr/bin/env python3
"""Merge split parallel tool-call turns into one assistant turn.

A model can ask for several tools at the same moment. In the raw event log
each request is its own ``tool_call`` event, back to back, with no result
between them. An exporter that does not know about that writes one assistant
message per request:

    assistant {tool_calls: [read]}
    assistant {tool_calls: [read]}
    assistant {tool_calls: [grep]}
    tool      {read result}
    tool      {read result}
    tool      {grep result}

A consumer that formats chat data expects the calls that were issued
together to sit in ONE assistant turn:

    assistant {tool_calls: [read, read, grep]}
    tool      {read result}
    tool      {read result}
    tool      {grep result}

This script applies that merge to samples produced by an older exporter. It
is the corpus-side copy of the rule the engine uses in
``megabit/export.py::_build_messages``: a new turn is opened only when the
previous message is not already an assistant turn holding open tool calls
with no text of its own.

What it rewrites
----------------
* ``messages[]``: consecutive open-call assistant turns become one turn with
  several calls. Call order is preserved, and so are every call id, name and
  argument object. No message is dropped.
* ``metadata.messages_normalization.merged_parallel_tool_calls``: the running
  count of calls folded into a compound turn.
* the ``finalization.json`` sample digest, so ``verify.py`` still passes.

It never rewrites ``*.episode.jsonl``. The raw log is the record of what the
model actually emitted, and it keeps every event verbatim.

Usage
-----
    # report only, exit 1 when split turns are still present
    python3 merge_parallel_calls.py --corpus . --check

    # merge into a NEW tree (the source is never touched)
    python3 merge_parallel_calls.py --corpus . --out ../merged

    # merge in place (needs --yes; snapshot first with --backup-dir)
    python3 merge_parallel_calls.py --corpus . --in-place --yes \
        --backup-dir ../backup

Requires Python 3.9+. No dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPORT_VERSION = 1


class MergeError(ValueError):
    """The corpus could not be merged; nothing was written."""


# --------------------------------------------------------------------- basics
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    """Write a file in one step so a crash cannot leave half a sample."""
    handle_fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        try:
            os.chmod(tmp, path.stat().st_mode & 0o7777)
        except OSError:
            pass
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def snapshot(path: Path, root: Path, backup_dir: Path) -> None:
    target = backup_dir / path.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)


def load_sample(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        raise MergeError(f"{path} is empty")
    try:
        record = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise MergeError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(record, dict):
        raise MergeError(f"{path} does not hold a JSON object")
    return record


# ------------------------------------------------------------------ the merge
def is_open_call_turn(message) -> bool:
    """True for an assistant turn that only opens tool calls.

    This is the engine's test: an assistant message that carries a non-empty
    ``tool_calls`` list and no text of its own is still "open", so the next
    call issued before any result belongs in the same turn.
    """
    return (isinstance(message, dict)
            and message.get("role") == "assistant"
            and isinstance(message.get("tool_calls"), list)
            and bool(message["tool_calls"])
            and not message.get("content"))


def count_split_pairs(messages: list) -> int:
    """How many adjacent open-call turns a merge would combine."""
    return sum(1 for index in range(len(messages) - 1)
               if is_open_call_turn(messages[index])
               and is_open_call_turn(messages[index + 1]))


def merge_messages(messages: list) -> int:
    """Fold adjacent open-call turns together in place.

    Returns the number of calls that moved into an earlier turn, which is the
    number this operation reports as merged.
    """
    merged = 0
    out: list = []
    for message in messages:
        if out and is_open_call_turn(out[-1]) and is_open_call_turn(message):
            out[-1]["tool_calls"].extend(message["tool_calls"])
            merged += len(message["tool_calls"])
            continue
        out.append(message)
    messages[:] = out
    return merged


# ------------------------------------------------------------------- the tree
def check_corpus(corpus: Path) -> list[dict]:
    """Look for split turns without writing anything."""
    episodes = corpus.resolve() / "episodes"
    if not episodes.is_dir():
        raise MergeError(f"{corpus} has no episodes/ directory")
    found: list[dict] = []
    for sample_path in sorted(episodes.glob("*/*.sample.jsonl")):
        record = load_sample(sample_path)
        messages = record.get("messages") or []
        split_pairs = count_split_pairs(messages)
        blocks = [m for m in messages if m.get("tool_calls")]
        found.append({
            "id": sample_path.parent.name,
            "tool_call_blocks": len(blocks),
            "compound_blocks": sum(1 for m in blocks if len(m["tool_calls"]) > 1),
            "split_pairs": split_pairs,
        })
    return found


def merge_corpus(corpus: Path, *, out: Path | None = None,
                 in_place: bool = False,
                 backup_dir: Path | None = None) -> dict:
    src = corpus.resolve()
    episodes = src / "episodes"
    if not episodes.is_dir():
        raise MergeError(f"{src} has no episodes/ directory")
    if out is not None and in_place:
        raise MergeError("choose either --out or --in-place, not both")
    if out is None and not in_place:
        raise MergeError("refusing to guess: pass --out <new tree> "
                         "or --in-place")

    if out is None:
        root = src
    else:
        root = out.resolve()
        if root.exists() and any(root.iterdir()):
            raise MergeError(f"output {root} already exists and is not empty")
        root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, root)

    scanned = 0
    changed = 0
    merged_total = 0
    for ep_dir in sorted(d for d in (root / "episodes").iterdir() if d.is_dir()):
        tid = ep_dir.name
        sample_path = ep_dir / f"{tid}.sample.jsonl"
        if not sample_path.is_file():
            continue
        scanned += 1
        record = load_sample(sample_path)
        messages = record.get("messages") or []
        if not count_split_pairs(messages):
            continue

        if backup_dir:
            snapshot(sample_path, root, backup_dir)
        merged = merge_messages(messages)
        record["messages"] = messages
        meta = record.get("metadata")
        if isinstance(meta, dict):
            norm = meta.get("messages_normalization")
            if not isinstance(norm, dict):
                norm = {}
            norm["merged_parallel_tool_calls"] = (
                int(norm.get("merged_parallel_tool_calls") or 0) + merged)
            meta["messages_normalization"] = norm
        atomic_write_text(sample_path, json.dumps(record, default=str) + "\n")

        fin_path = ep_dir / "finalization.json"
        if fin_path.is_file():
            if backup_dir:
                snapshot(fin_path, root, backup_dir)
            try:
                fin = json.loads(fin_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise MergeError(f"{fin_path} is unreadable: {exc}") from exc
            if not isinstance(fin, dict):
                raise MergeError(f"{fin_path} does not hold a JSON object")
            fin["sample_sha256"] = sha256_file(sample_path)
            atomic_write_text(fin_path, json.dumps(fin, indent=2) + "\n")

        changed += 1
        merged_total += merged

    return {
        "type": "parallel_call_merge",
        "version": REPORT_VERSION,
        "source_corpus": str(src),
        "episodes_scanned": scanned,
        "episodes_changed": changed,
        "calls_merged": merged_total,
    }


# ------------------------------------------------------------------------ cli
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Merge split parallel tool-call turns in a corpus.")
    parser.add_argument("--corpus", default=".",
                        help="corpus root (default: .)")
    parser.add_argument("--out", default=None,
                        help="write a NEW tree here (source untouched)")
    parser.add_argument("--in-place", action="store_true",
                        help="rewrite the corpus itself (needs --yes)")
    parser.add_argument("--yes", action="store_true",
                        help="confirm an in-place rewrite")
    parser.add_argument("--backup-dir", default=None,
                        help="copy every touched file here before writing")
    parser.add_argument("--check", action="store_true",
                        help="report split turns only; exit 1 if any remain")
    parser.add_argument("--quiet", action="store_true",
                        help="only print the summary")
    parser.add_argument("--report", default=None,
                        help="write the merge report to this path")
    args = parser.parse_args(argv)

    corpus = Path(args.corpus)
    try:
        if args.check:
            rows = check_corpus(corpus)
            dirty = [r for r in rows if r["split_pairs"]]
            if not args.quiet:
                for row in rows:
                    mark = "split" if row["split_pairs"] else "ok   "
                    print(f"{mark} {row['id']}  blocks={row['tool_call_blocks']}"
                          f" compound={row['compound_blocks']}"
                          f" split_pairs={row['split_pairs']}")
            print(f"\n{len(rows) - len(dirty)}/{len(rows)} samples already "
                  f"merged")
            if dirty:
                print(f"{len(dirty)} sample(s) still carry split turns")
                return 1
            return 0

        if args.in_place and not args.yes:
            print("refusing an in-place rewrite without --yes",
                  file=sys.stderr)
            return 2
        report = merge_corpus(
            corpus,
            out=Path(args.out) if args.out else None,
            in_place=args.in_place,
            backup_dir=Path(args.backup_dir) if args.backup_dir else None,
        )
    except MergeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.report:
        atomic_write_text(Path(args.report), json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
