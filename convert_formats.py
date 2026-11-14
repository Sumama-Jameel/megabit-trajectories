#!/usr/bin/env python3
"""Convert a corpus into common training formats, losslessly, in one command.

The samples are already OpenAI-ish JSONL, but every stack wants a different
shape: some want native ``tool_calls`` with ``type: "function"``, some want
ShareGPT ``from``/``value``, some want Hermes ``<tool_call>`` blocks, some want
one rendered ``text`` per episode. Hand-writing that conversion for 66 files is
where people quietly lose messages, drop tool ids, or rewrite content.

This script converts into a NEW directory and then proves the conversion:

* every message, tool call and tool result survives, and the checker says so;
* the source tree is never opened for writing, and its sha256 values are
  recorded before and after;
* parallel calls that the exporter split across several assistant turns are
  merged into one turn (``--no-merge-parallel`` keeps the split), because the
  split form is not valid chat structure;
* a ``MANIFEST.json`` records source digest, output digest and a logical digest
  per episode, so ``--check`` can re-verify a tree later, byte for byte.

Formats
-------
``openai``     ``messages[]`` with native ``tool_calls`` and a ``tools`` catalog
``sharegpt``   ``conversations[]`` with ``from``/``value`` entries
``hermes``     assistant content carries ``<tool_call>{...}</tool_call>`` blocks
``text``       one rendered string per episode with explicit role markers

Usage
-----
    python3 convert_formats.py --list

    python3 convert_formats.py --corpus . --format openai   --out ../ft/openai
    python3 convert_formats.py --corpus . --format sharegpt --out ../ft/sharegpt
    python3 convert_formats.py --corpus . --format hermes  --out ../ft/hermes
    python3 convert_formats.py --corpus . --format text    --out ../ft/text

    # prove a tree is a lossless conversion of the corpus (exit 1 on drift)
    python3 convert_formats.py --corpus . --format sharegpt --out ../ft/sharegpt --check

    # a JSON report of sizes and preservation counts
    python3 convert_formats.py --corpus . --format text --out ../ft/text \
        --report ../ft/text-report.json

Nothing is written back into the corpus. The raw episode logs are never read.

Requires Python 3.9+. No dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

MANIFEST_VERSION = 1
TOOL_BLOCK = re.compile(r"\n?<tool_call>(\{.*?\})</tool_call>", re.S)
ROLE_MARKERS = ("system", "user", "assistant", "tool")
END_MARKER = "<|end|>\n"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def digest(obj) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def canonical(messages: list[dict]) -> list[dict]:
    """The logical record, independent of any serialized shape."""
    out = []
    for m in messages:
        role = m.get("role")
        item = {"role": role, "content": m.get("content") or ""}
        if role == "assistant":
            calls = m.get("tool_calls") or []
            if calls:
                item["tool_calls"] = [
                    {"id": c.get("id"), "name": c.get("name"),
                     "arguments": c.get("arguments") or {}} for c in calls]
        if role == "tool":
            item["tool_call_id"] = m.get("tool_call_id")
            item["name"] = m.get("name")
        out.append(item)
    return out


def canonical_for(fmt: str, messages: list[dict]) -> list[dict]:
    """Canonical form, reduced to what the format actually carries.

    The ``text`` format renders tool results as plain role blocks, so a result's
    ``tool_call_id`` and ``name`` are not represented. Results still follow
    their call in order, which is how the format links them. Every other
    format carries the ids, so nothing is reduced there.
    """
    out = canonical(messages)
    if fmt == "text":
        for item in out:
            if item["role"] == "tool":
                item.pop("tool_call_id", None)
                item.pop("name", None)
    return out


def merge_parallel(messages: list[dict]) -> tuple[list[dict], int, int]:
    """Collapse call-only assistant turns into one turn with several calls.

    The exporter can emit ``assistant(call A)``, ``assistant(call B)``,
    ``tool(A)``, ``tool(B)`` for one parallel turn, which is not valid chat
    structure. Merging is purely structural: every call keeps its id, name and
    arguments, and every result keeps its id. Nothing is reordered or dropped.
    """
    out, merged, skipped = [], 0, 0
    i = 0
    while i < len(messages):
        m = messages[i]
        if m.get("role") == "assistant" and m.get("tool_calls"):
            if (m.get("content") or "").strip():
                skipped += 1
                out.append(m)
                i += 1
                continue
            calls = list(m["tool_calls"])
            j = i + 1
            while (j < len(messages)
                   and messages[j].get("role") == "assistant"
                   and messages[j].get("tool_calls")
                   and not (messages[j].get("content") or "").strip()):
                calls += list(messages[j]["tool_calls"])
                merged += 1
                j += 1
            merged_turn = dict(m)
            merged_turn["tool_calls"] = calls
            out.append(merged_turn)
            i = j
        else:
            out.append(m)
            i += 1
    return out, merged, skipped


class Unsupported(Exception):
    """This episode cannot be represented in the requested format."""


def guard_markers(text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker in text:
            raise Unsupported(f"content contains the format marker {marker!r}")


# --------------------------------------------------------------------------- #
# formats
# --------------------------------------------------------------------------- #

def emit_openai(record: dict, messages: list[dict]) -> dict:
    out = []
    for m in messages:
        role = m.get("role")
        if role == "assistant":
            item = {"role": "assistant", "content": m.get("content") or ""}
            calls = m.get("tool_calls") or []
            if calls:
                item["tool_calls"] = [{
                    "id": c.get("id"),
                    "type": "function",
                    "function": {
                        "name": c.get("name"),
                        "arguments": json.dumps(c.get("arguments") or {},
                                                ensure_ascii=False,
                                                sort_keys=True),
                    },
                } for c in calls]
            out.append(item)
        elif role == "tool":
            out.append({"role": "tool",
                        "tool_call_id": m.get("tool_call_id"),
                        "name": m.get("name"),
                        "content": m.get("content") or ""})
        else:
            out.append({"role": role, "content": m.get("content") or ""})
    return {"messages": out, "tools": record.get("tools"),
            "metadata": record.get("metadata") or {}}


def parse_openai(item: dict) -> list[dict]:
    out = []
    for m in item.get("messages") or []:
        role = m.get("role")
        if role == "assistant":
            entry = {"role": "assistant", "content": m.get("content") or ""}
            calls = m.get("tool_calls") or []
            if calls:
                entry["tool_calls"] = [{
                    "id": c.get("id"),
                    "name": (c.get("function") or {}).get("name"),
                    "arguments": json.loads(
                        (c.get("function") or {}).get("arguments") or "{}"),
                } for c in calls]
            out.append(entry)
        elif role == "tool":
            out.append({"role": "tool", "content": m.get("content") or "",
                        "tool_call_id": m.get("tool_call_id"),
                        "name": m.get("name")})
        else:
            out.append({"role": role, "content": m.get("content") or ""})
    return out


def emit_sharegpt(record: dict, messages: list[dict]) -> dict:
    names = {"system": "system", "user": "human", "assistant": "gpt",
             "tool": "observation"}
    out = []
    for m in messages:
        role = m.get("role")
        entry = {"from": names.get(role, role),
                 "value": m.get("content") or ""}
        if role == "assistant":
            calls = m.get("tool_calls") or []
            if calls:
                entry["tool_calls"] = [
                    {"id": c.get("id"), "name": c.get("name"),
                     "arguments": c.get("arguments") or {}} for c in calls]
        if role == "tool":
            entry["tool_call_id"] = m.get("tool_call_id")
            entry["name"] = m.get("name")
        out.append(entry)
    return {"conversations": out, "tools": record.get("tools"),
            "metadata": record.get("metadata") or {}}


def parse_sharegpt(item: dict) -> list[dict]:
    names = {"system": "system", "human": "user", "gpt": "assistant",
             "observation": "tool"}
    out = []
    for m in item.get("conversations") or []:
        role = names.get(m.get("from"), m.get("from"))
        entry = {"role": role, "content": m.get("value") or ""}
        if role == "assistant":
            calls = m.get("tool_calls") or []
            if calls:
                entry["tool_calls"] = [
                    {"id": c.get("id"), "name": c.get("name"),
                     "arguments": c.get("arguments") or {}} for c in calls]
        if role == "tool":
            entry["tool_call_id"] = m.get("tool_call_id")
            entry["name"] = m.get("name")
        out.append(entry)
    return out


def emit_hermes(record: dict, messages: list[dict]) -> dict:
    out = []
    for m in messages:
        role = m.get("role")
        content = m.get("content") or ""
        if role == "assistant":
            if m.get("tool_calls"):
                guard_markers(content, ("<tool_call>", "</tool_call>"))
            for call in m.get("tool_calls") or []:
                block = json.dumps({"id": call.get("id"),
                                    "name": call.get("name"),
                                    "arguments": call.get("arguments") or {}},
                                   ensure_ascii=False)
                guard_markers(block, ("<tool_call>", "</tool_call>"))
                content += f"\n<tool_call>{block}</tool_call>"
        out.append({"role": role, "content": content})
        if role == "tool":
            out[-1]["tool_call_id"] = m.get("tool_call_id")
            out[-1]["name"] = m.get("name")
    return {"messages": out, "tools": record.get("tools"),
            "metadata": record.get("metadata") or {}}


def parse_hermes(item: dict) -> list[dict]:
    out = []
    for m in item.get("messages") or []:
        role = m.get("role")
        content = m.get("content") or ""
        if role == "assistant" and "<tool_call>" in content:
            calls = []
            for raw in TOOL_BLOCK.findall(content):
                call = json.loads(raw)
                calls.append({"id": call.get("id"), "name": call.get("name"),
                              "arguments": call.get("arguments") or {}})
            content = TOOL_BLOCK.sub("", content)
            out.append({"role": "assistant", "content": content,
                        "tool_calls": calls})
        else:
            entry = {"role": role, "content": content}
            if role == "tool":
                entry["tool_call_id"] = m.get("tool_call_id")
                entry["name"] = m.get("name")
            out.append(entry)
    return out


def emit_text(record: dict, messages: list[dict]) -> dict:
    parts = []
    for m in messages:
        role = m.get("role")
        content = m.get("content") or ""
        if role == "assistant":
            for call in m.get("tool_calls") or []:
                block = json.dumps({"id": call.get("id"),
                                    "name": call.get("name"),
                                    "arguments": call.get("arguments") or {}},
                                   ensure_ascii=False)
                content += f"\n<tool_call>{block}</tool_call>"
        guard_markers(content, ("<|end|>",)
                      + tuple(f"<|{r}|>" for r in ROLE_MARKERS))
        parts.append(f"<|{role}|>\n{content}{END_MARKER}")
    return {"text": "".join(parts), "metadata": record.get("metadata") or {}}


def parse_text(item: dict) -> list[dict]:
    text = item.get("text") or ""
    if not text.endswith(END_MARKER):
        raise ValueError("rendered text does not end with the role marker")
    segments = text[: -len(END_MARKER)].split(END_MARKER)
    out = []
    for segment in segments:
        header, _, body = segment.partition("\n")
        role = header.strip("<|>")
        if role not in ROLE_MARKERS:
            raise ValueError(f"unknown role marker {header!r}")
        if role == "assistant" and "<tool_call>" in body:
            calls = []
            for raw in TOOL_BLOCK.findall(body):
                call = json.loads(raw)
                calls.append({"id": call.get("id"), "name": call.get("name"),
                              "arguments": call.get("arguments") or {}})
            body = TOOL_BLOCK.sub("", body)
            out.append({"role": "assistant", "content": body,
                        "tool_calls": calls})
        else:
            out.append({"role": role, "content": body})
    return out


FORMATS = {
    "openai": {"emit": emit_openai, "parse": parse_openai,
               "note": "messages[] with native tool_calls (type: function)"},
    "sharegpt": {"emit": emit_sharegpt, "parse": parse_sharegpt,
                 "note": "conversations[] with from/value"},
    "hermes": {"emit": emit_hermes, "parse": parse_hermes,
               "note": "assistant content carries <tool_call> blocks"},
    "text": {"emit": emit_text, "parse": parse_text,
             "note": "one rendered text per episode"},
}


# --------------------------------------------------------------------------- #
# corpus io
# --------------------------------------------------------------------------- #

def episode_paths(corpus: Path) -> list[Path]:
    return sorted((corpus / "episodes").glob("*/*.sample.jsonl"))


def load_episode(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                return json.loads(line)
    raise ValueError(f"{path} is empty")


def build(record: dict, fmt: str, merge: bool) -> tuple[dict, dict]:
    messages = record.get("messages") or []
    before = len(messages)
    merged = skipped = 0
    if merge:
        messages, merged, skipped = merge_parallel(messages)
    item = FORMATS[fmt]["emit"](record, messages)
    stats = {"messages_in": before, "messages_out": len(messages),
             "merged_turns": merged, "merge_skipped": skipped,
             "calls": sum(len(m.get("tool_calls") or []) for m in messages),
             "results": sum(1 for m in messages if m.get("role") == "tool")}
    return item, stats


def write_readme(out: Path, fmt: str, corpus: Path, merge: bool) -> None:
    lines = [
        f"MegaBit Trajectories, converted to the {fmt} format.",
        "",
        f"Source: {corpus}",
        f"Format: {fmt} - {FORMATS[fmt]['note']}",
        f"Parallel calls merged into single assistant turns: {'yes' if merge else 'no'}",
        "",
        "One JSON object per episode, one episode per line, in this directory.",
        "MANIFEST.json records the source sha256, the output sha256 and the",
        "logical digest of every episode.",
        "",
        "Verify this tree against the corpus:",
        f"  python3 convert_formats.py --corpus {corpus} --format {fmt} --out . --check",
        "",
        "The raw episode logs were not read and nothing was written back to the",
        "corpus.",
        "",
    ]
    (out / "README.txt").write_text("\n".join(lines), encoding="utf-8")


def convert(corpus: Path, out: Path, fmt: str, merge: bool, limit: int | None,
            tools: dict | None) -> dict:
    paths = episode_paths(corpus)
    if limit:
        paths = paths[:limit]
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    totals = {"episodes": 0, "messages": 0, "calls": 0, "results": 0,
              "merged_turns": 0, "chars": 0, "unsupported": 0}
    started = time.time()
    for path in paths:
        tid = path.parent.name
        record = load_episode(path)
        try:
            item, stats = build(record, fmt, merge)
        except (Unsupported, ValueError) as exc:
            rows.append({"task_id": tid, "skipped": str(exc)})
            totals["unsupported"] += 1
            continue
        payload = json.dumps(item, ensure_ascii=False) + "\n"
        target = out / f"{tid}.jsonl"
        target.write_text(payload, encoding="utf-8")
        rebuilt = FORMATS[fmt]["parse"](json.loads(payload))
        logical = digest(canonical_for(fmt, rebuilt))
        rows.append({
            "task_id": tid,
            "source_sha256": sha256_file(path),
            "output_sha256": sha256_bytes(payload.encode("utf-8")),
            "logical_sha256": logical,
            "chars": len(payload),
            **stats,
        })
        totals["episodes"] += 1
        totals["messages"] += stats["messages_out"]
        totals["calls"] += stats["calls"]
        totals["results"] += stats["results"]
        totals["merged_turns"] += stats["merged_turns"]
        totals["chars"] += len(payload)
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "format": fmt,
        "merge_parallel": merge,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generator": "convert_formats.py",
        "source": {"corpus": str(corpus.resolve()),
                   "samples": len(paths),
                   "tools_sha256": sha256_file(corpus / "episodes" / "tools.json")
                   if (corpus / "episodes" / "tools.json").exists() else None},
        "totals": {**totals, "estimated_tokens": totals["chars"] // 4},
        "seconds": round(time.time() - started, 2),
        "episodes": rows,
    }
    (out / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if tools:
        (out / "tools.json").write_text(
            json.dumps(tools, indent=2) + "\n", encoding="utf-8")
    write_readme(out, fmt, corpus.resolve(), merge)
    return manifest


# --------------------------------------------------------------------------- #
# verification
# --------------------------------------------------------------------------- #

def check(corpus: Path, out: Path, fmt: str, merge: bool | None) -> int:
    manifest_path = out / "MANIFEST.json"
    if not manifest_path.exists():
        print(f"no MANIFEST.json in {out}")
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format") != fmt:
        print(f"this tree was written as {manifest.get('format')}, "
              f"not {fmt}")
        return 2
    if merge is None:
        merge = bool(manifest.get("merge_parallel"))
    recorded = {r["task_id"]: r for r in manifest.get("episodes") or []}
    problems = []
    checked = skipped = 0
    for path in episode_paths(corpus):
        tid = path.parent.name
        row = recorded.get(tid)
        target = out / f"{tid}.jsonl"
        if row is None:
            problems.append(f"{tid}: not in the manifest")
            continue
        if "skipped" in row:
            skipped += 1
            continue
        if not target.exists():
            problems.append(f"{tid}: output file missing")
            continue
        raw = target.read_bytes()
        if sha256_bytes(raw) != row["output_sha256"]:
            problems.append(f"{tid}: output changed since conversion")
            continue
        record = load_episode(path)
        merged_messages, merged_count, _ = merge_parallel(
            record.get("messages") or [])
        merged = merged_count if merge else 0
        expected = merged_messages if merge else record.get("messages") or []
        got = FORMATS[fmt]["parse"](json.loads(raw))
        if digest(canonical_for(fmt, got)) != digest(canonical_for(fmt, expected)):
            problems.append(f"{tid}: message content differs from the source")
            continue
        if sha256_file(path) != row["source_sha256"]:
            problems.append(f"{tid}: source sample changed since conversion")
            continue
        if row["merged_turns"] != merged:
            problems.append(f"{tid}: merge count differs")
            continue
        checked += 1
    missing = set(recorded) - {p.parent.name for p in episode_paths(corpus)}
    for tid in sorted(missing):
        problems.append(f"{tid}: in the manifest but not in the corpus")
    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for line in problems[:20]:
            print("  " + line)
        return 1
    note = f", {skipped} skipped by the converter" if skipped else ""
    print(f"OK: {checked}/{checked} episodes are lossless in the {fmt} format{note}")
    return 0


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert the corpus into training formats without losing "
                    "data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Formats:\n" + "\n".join(
            f"  {name:<9} {spec['note']}" for name, spec in FORMATS.items()))
    parser.add_argument("--corpus", default=".",
                        help="corpus root (default: current directory)")
    parser.add_argument("--format", choices=tuple(FORMATS),
                        help="target format")
    parser.add_argument("--out", default=None,
                        help="new, empty directory to write into")
    parser.add_argument("--check", action="store_true",
                        help="verify an existing output tree against the corpus")
    parser.add_argument("--no-merge-parallel", dest="merge", action="store_false",
                        help="keep split parallel calls as separate turns")
    parser.add_argument("--limit", type=int, default=None,
                        help="only convert the first N episodes")
    parser.add_argument("--report", default=None,
                        help="write the manifest to this JSON path as well")
    parser.add_argument("--list", action="store_true",
                        help="print the formats and exit")
    args = parser.parse_args(argv)

    if args.list:
        for name, spec in FORMATS.items():
            print(f"{name:<9} {spec['note']}")
        return 0
    if not args.format:
        parser.error("--format is required")
    corpus = Path(args.corpus).resolve()
    if not (corpus / "episodes").is_dir():
        print(f"not a corpus: {corpus} has no episodes/ directory")
        return 2

    if args.check:
        if not args.out:
            parser.error("--check needs --out")
        merge = None if args.merge else False
        return check(corpus, Path(args.out).resolve(), args.format, merge)

    if not args.out:
        parser.error("--out is required (conversion never writes into the corpus)")
    out = Path(args.out).resolve()
    if out == corpus or corpus in out.parents:
        print("refusing to write inside the corpus; choose a directory outside it")
        return 2
    if out.exists():
        print(f"refusing to write into {out}: it already exists")
        return 2
    tools = None
    tools_path = corpus / "episodes" / "tools.json"
    if tools_path.exists():
        tools = json.loads(tools_path.read_text(encoding="utf-8"))

    manifest = convert(corpus, out, args.format, args.merge, args.limit, tools)
    totals = manifest["totals"]
    print(f"{args.format}: {totals['episodes']} episodes, "
          f"{totals['messages']} messages, {totals['calls']} tool calls, "
          f"{totals['merged_turns']} split calls merged")
    print(f"wrote {out}")
    if totals["unsupported"]:
        print(f"skipped {totals['unsupported']} episode(s) this format cannot "
              f"represent; see MANIFEST.json")
    if args.report:
        Path(args.report).write_text(json.dumps(manifest, indent=2) + "\n",
                                     encoding="utf-8")
        print(f"report: {args.report}")
    print(f"verify with: python3 convert_formats.py --corpus {corpus} "
          f"--format {args.format} --out {out} --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
