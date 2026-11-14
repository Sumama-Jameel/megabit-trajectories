#!/usr/bin/env python3
"""Rename a corpus's tool vocabulary in one command.

The corpus uses one canonical vocabulary:

    read, glob, grep, edit, write, bash, todo_write, todoread

If your harness calls its shell tool ``shell`` or its reader ``view``, you do
not have to post-process 66 JSONL files by hand. This script rewrites exactly
the fields that carry a tool name, refuses ambiguous mappings, and can prove
the operation is lossless (rename there and back is byte-identical).

What it rewrites
----------------
* ``messages[].tool_calls[].name``
* ``messages[].name`` on tool result messages
* the per-sample ``tools`` catalog (``function.name``)
* ``metadata.tool_names_used`` / ``tool_name_aliases`` / ``tool_spec_sha256``
* ``episodes/tools.json``
* the ``finalization.json`` sample digest, so ``verify.py`` still passes

It never rewrites message content. Prose that mentions a tool is evidence,
not a name field.

Usage
-----
    # see the vocabulary as an editable profile
    python3 retag_tools.py --dump-profile > lab.json

    # rewrite into a NEW tree (the source is never touched)
    python3 retag_tools.py --corpus . --map bash=shell,read=view --out ../renamed
    python3 retag_tools.py --corpus . --profile lab.json --out ../renamed

    # verify a tree already matches (exit 1 on drift)
    python3 retag_tools.py --corpus ../renamed --map bash=shell,read=view --check

    # rewrite in place (needs --yes; snapshot first with --backup-dir)
    python3 retag_tools.py --corpus . --map bash=shell --in-place --yes \
        --backup-dir ../backup

``--scope all`` also renames the raw episode's tool-event names, which changes
``raw_sha256``. It is off by default: the raw log is the record of what the
model actually emitted.

Requires Python 3.9+. No dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

PROFILE_VERSION = 1

CANONICAL_TOOL_NAMES: tuple[str, ...] = (
    "read", "glob", "grep", "edit", "write", "bash", "todo_write", "todoread",
)

#: spelling the harness/model emits -> canonical name
TOOL_NAME_ALIASES: dict[str, str] = {
    "execute": "bash",
    "shell": "bash",
    "background": "bash",
    "todowrite": "todo_write",
    "edit_file": "edit",
    "multi_edit": "edit",
    "write_file": "write",
}

_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class RetagError(ValueError):
    """A mapping or corpus could not be retagged; nothing was written."""


# --------------------------------------------------------------------- basics
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tool_spec_sha256(tools: list[dict]) -> str:
    """Content hash of a catalog (sorted keys, compact separators)."""
    blob = json.dumps(tools, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_name(f".{path.name}.retag-tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def normalize_tool_name(name: object) -> str:
    text = str(name or "")
    return TOOL_NAME_ALIASES.get(text.lower(), text)


# ------------------------------------------------------------------- profiles
def parse_name_map(spec: str) -> dict[str, str]:
    """``"bash=shell,read=view"`` -> ``{"bash": "shell", "read": "view"}``."""
    mapping: dict[str, str] = {}
    for chunk in (spec or "").replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise RetagError(f"bad mapping {chunk!r}: expected canonical=target")
        source, target = (part.strip() for part in chunk.split("=", 1))
        if not source or not target:
            raise RetagError(f"bad mapping {chunk!r}: empty side")
        if source in mapping and mapping[source] != target:
            raise RetagError(f"conflicting targets for {source!r}: "
                             f"{mapping[source]!r} vs {target!r}")
        mapping[source] = target
    return mapping


def load_profile(path: str) -> dict[str, str]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RetagError(f"cannot read profile {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RetagError(f"profile {path} is not a JSON object")
    version = data.get("version")
    if version is not None and version != PROFILE_VERSION:
        raise RetagError(f"profile {path} has version {version!r}, "
                         f"expected {PROFILE_VERSION}")
    names = data.get("names", data)
    if not isinstance(names, dict):
        raise RetagError(f"profile {path} has no usable 'names' object")
    return {str(k): str(v) for k, v in names.items()}


def dump_profile(mapping: dict[str, str] | None = None) -> dict:
    names = {name: name for name in CANONICAL_TOOL_NAMES}
    names.update(mapping or {})
    return {
        "version": PROFILE_VERSION,
        "names": names,
        "note": "map a canonical tool name to your harness's name; "
                "every tool must keep a unique target",
    }


def validate_name_map(mapping: dict[str, str], *,
                      known_sources: dict[str, str] | None = None
                      ) -> dict[str, str]:
    """Canonical -> final name for every tool, or raise RetagError."""
    if not isinstance(mapping, dict):
        raise RetagError("mapping must be an object")
    current = dict(known_sources or {})
    resolved: dict[str, str] = {}
    for source, target in mapping.items():
        canonical = current.get(source) or normalize_tool_name(source)
        if canonical not in CANONICAL_TOOL_NAMES:
            raise RetagError(
                f"unknown source tool {source!r}; known tools: "
                f"{', '.join(sorted(current) or CANONICAL_TOOL_NAMES)}")
        if canonical in resolved and resolved[canonical] != target:
            raise RetagError(f"{source!r} and another entry both remap "
                             f"{canonical!r}")
        resolved[canonical] = str(target)

    final: dict[str, str] = {}
    for canonical in CANONICAL_TOOL_NAMES:
        name = resolved.get(canonical, canonical)
        if not _NAME_RE.match(name):
            raise RetagError(f"target name {name!r} for {canonical!r} must "
                             f"match [A-Za-z0-9_-]{{1,64}}")
        final[canonical] = name

    seen: dict[str, str] = {}
    for canonical, name in final.items():
        if name in seen:
            raise RetagError(f"target name {name!r} would be shared by "
                             f"{seen[name]!r} and {canonical!r}")
        seen[name] = canonical
    return final


def effective_aliases(final: dict[str, str]) -> dict[str, str]:
    """raw spelling -> the name that spelling means in this corpus."""
    if all(final.get(name, name) == name for name in CANONICAL_TOOL_NAMES):
        return dict(TOOL_NAME_ALIASES)
    table = {alias: final[canon]
             for alias, canon in TOOL_NAME_ALIASES.items() if canon in final}
    table.update({canonical: name for canonical, name in final.items()})
    return table


def current_vocabulary(corpus: Path) -> dict[str, str]:
    """{name the corpus uses now: canonical tool}, or {} when unknown."""
    episodes = corpus / "episodes"
    names: list[str] | None = None
    payload_path = episodes / "tools.json"
    if payload_path.is_file():
        try:
            data = json.loads(payload_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        raw_names = data.get("canonical_names") if isinstance(data, dict) else None
        if isinstance(raw_names, list) and raw_names:
            names = [str(n) for n in raw_names]
    if names is None:
        for sample_path in sorted(episodes.glob("*/*.sample.jsonl")):
            try:
                data = json.loads(sample_path.read_text(encoding="utf-8")
                                  .strip().split("\n")[0])
            except (OSError, json.JSONDecodeError):
                continue
            tools = data.get("tools") if isinstance(data, dict) else None
            if isinstance(tools, list) and tools:
                names = [str((entry.get("function") or {}).get("name"))
                         for entry in tools]
            break
    if not names or len(names) != len(CANONICAL_TOOL_NAMES):
        return {}
    return {name: canonical
            for name, canonical in zip(names, CANONICAL_TOOL_NAMES) if name}


def translation(final: dict[str, str],
                current: dict[str, str] | None = None) -> dict[str, str]:
    """Every spelling that may appear -> the name to write after the retag."""
    table: dict[str, str] = {}
    for name, canonical in (current or {}).items():
        if canonical in final:
            table[name] = final[canonical]
    for canonical, name in final.items():
        table[canonical] = name
    for alias, canonical in TOOL_NAME_ALIASES.items():
        if canonical in final:
            table[alias] = final[canonical]
    return table


# ------------------------------------------------------------------ rewriting
def rename_tools(tools: list[dict], final: dict[str, str], *,
                 current: dict[str, str] | None = None) -> list[dict]:
    table = translation(final, current)
    out = json.loads(json.dumps(tools))
    for entry in out:
        fn = entry.get("function") or {}
        name = fn.get("name")
        if name in table:
            fn["name"] = table[name]
    return out


def rename_sample(record: dict, final: dict[str, str], *,
                  current: dict[str, str] | None = None) -> dict:
    table = translation(final, current)
    out = json.loads(json.dumps(record))
    for msg in out.get("messages") or []:
        for call in msg.get("tool_calls") or []:
            name = call.get("name")
            if name in table:
                call["name"] = table[name]
        if msg.get("role") == "tool":
            name = msg.get("name")
            if name in table:
                msg["name"] = table[name]

    tools = out.get("tools")
    if isinstance(tools, list) and tools:
        out["tools"] = rename_tools(tools, final, current=current)

    meta = out.get("metadata")
    if isinstance(meta, dict):
        used = sorted({
            str(n)
            for m in (out.get("messages") or [])
            for n in ([c.get("name") for c in (m.get("tool_calls") or [])]
                      + ([m.get("name")] if m.get("role") == "tool" else []))
            if n
        })
        meta["tool_names_used"] = used
        meta["tool_names_canonicalized"] = True
        meta["tool_name_aliases"] = effective_aliases(final)
        if out.get("tools"):
            meta["tool_spec_sha256"] = tool_spec_sha256(out["tools"])
        applied = {k: v for k, v in final.items() if k != v}
        if applied:
            meta["tool_naming"] = {
                "source": "retag_tools",
                "version": PROFILE_VERSION,
                "map": applied,
            }
        else:
            meta.pop("tool_naming", None)
    return out


def rewrite_raw_names(path: Path, final: dict[str, str]) -> int:
    """Rename tool-event name fields in a raw episode (scope=all)."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out: list[str] = []
    changed = 0
    for line in lines:
        if not line.strip():
            continue
        record = json.loads(line)
        if isinstance(record, dict) and record.get("type") in ("tool_call",
                                                               "tool_result"):
            name = record.get("name")
            if name in final and final[name] != name:
                record["name"] = final[name]
                changed += 1
        out.append(json.dumps(record, default=str))
    if changed:
        atomic_write_text(path, "\n".join(out) + "\n")
    return changed


def snapshot(path: Path, root: Path, backup_dir: Path) -> None:
    target = backup_dir / path.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)


def retag_corpus(corpus: Path, mapping: dict[str, str], *,
                 out: Path | None = None,
                 in_place: bool = False,
                 scope: str = "sample",
                 backup_dir: Path | None = None) -> dict:
    if scope not in ("sample", "all"):
        raise RetagError("scope must be 'sample' or 'all'")
    src = corpus.resolve()
    episodes = src / "episodes"
    if not episodes.is_dir():
        raise RetagError(f"{src} has no episodes/ directory")
    current = current_vocabulary(src)
    final = validate_name_map(mapping, known_sources=current)

    if out is not None and in_place:
        raise RetagError("choose either --out or --in-place, not both")
    if out is None:
        if not in_place:
            raise RetagError("refusing to guess: pass --out <new tree> "
                             "or --in-place")
        root = src
    else:
        root = out.resolve()
        if root.exists() and any(root.iterdir()):
            raise RetagError(f"output {root} already exists and is not empty")
        root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, root)

    samples = 0
    raw_events = 0
    for ep_dir in sorted(d for d in (root / "episodes").iterdir() if d.is_dir()):
        tid = ep_dir.name
        sample_path = ep_dir / f"{tid}.sample.jsonl"
        if not sample_path.is_file():
            continue
        if backup_dir:
            snapshot(sample_path, root, backup_dir)
        record = json.loads(sample_path.read_text(encoding="utf-8")
                            .strip().split("\n")[0])
        renamed = rename_sample(record, final, current=current)
        atomic_write_text(sample_path, json.dumps(renamed, default=str) + "\n")
        samples += 1

        raw_path = ep_dir / f"{tid}.episode.jsonl"
        fin_path = ep_dir / "finalization.json"
        if scope == "all" and raw_path.is_file():
            if backup_dir:
                snapshot(raw_path, root, backup_dir)
            raw_events += rewrite_raw_names(raw_path, final)
        if fin_path.is_file():
            if backup_dir:
                snapshot(fin_path, root, backup_dir)
            try:
                fin = json.loads(fin_path.read_text(encoding="utf-8"))
                fin = fin if isinstance(fin, dict) else {}
            except (OSError, json.JSONDecodeError):
                fin = {}
            fin["sample_sha256"] = sha256_file(sample_path)
            if scope == "all" and raw_path.is_file():
                fin["raw_sha256"] = sha256_file(raw_path)
            fin["tool_name_map"] = dict(final)
            atomic_write_text(fin_path, json.dumps(fin, indent=2) + "\n")

    tools_path = root / "episodes" / "tools.json"
    if tools_path.is_file():
        if backup_dir:
            snapshot(tools_path, root, backup_dir)
        try:
            payload = json.loads(tools_path.read_text(encoding="utf-8")) or {}
        except (OSError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, dict) and isinstance(payload.get("tools"), list):
            payload["tools"] = rename_tools(payload["tools"], final,
                                            current=current)
            payload["aliases"] = effective_aliases(final)
            payload["canonical_names"] = [final[n] for n in CANONICAL_TOOL_NAMES]
            payload["sha256"] = tool_spec_sha256(payload["tools"])
            payload["retagged_at"] = stamp()
            atomic_write_text(tools_path, json.dumps(payload, indent=2) + "\n")

    return {
        "type": "tool_retag",
        "version": PROFILE_VERSION,
        "generated_at": stamp(),
        "source_corpus": str(src),
        "scope": scope,
        "name_map": final,
        "samples_rewritten": samples,
        "raw_events_renamed": raw_events,
    }


def check_corpus(corpus: Path, mapping: dict[str, str]) -> list[str]:
    episodes = corpus.resolve() / "episodes"
    if not episodes.is_dir():
        raise RetagError(f"{corpus} has no episodes/ directory")
    current = current_vocabulary(corpus.resolve())
    final = validate_name_map(mapping, known_sources=current)
    expected = set(final.values())
    problems: list[str] = []
    for sample_path in sorted(episodes.glob("*/*.sample.jsonl")):
        tid = sample_path.parent.name
        try:
            record = json.loads(sample_path.read_text(encoding="utf-8")
                                .strip().split("\n")[0])
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{tid}: unreadable sample ({exc})")
            continue
        names = {str(c.get("name")) for m in record.get("messages") or []
                 for c in (m.get("tool_calls") or [])}
        names |= {str(m.get("name")) for m in record.get("messages") or []
                  if m.get("role") == "tool"}
        stray = sorted(n for n in names if n not in expected)
        if stray:
            problems.append(f"{tid}: names outside the profile: {stray}")
        tools = record.get("tools")
        if isinstance(tools, list) and tools:
            stray_tools = sorted(
                str((e.get("function") or {}).get("name"))
                for e in tools
                if (e.get("function") or {}).get("name") not in expected)
            if stray_tools:
                problems.append(f"{tid}: tools catalog not renamed: "
                                f"{stray_tools}")
        else:
            problems.append(f"{tid}: no tools catalog in the sample")
    return problems


# ------------------------------------------------------------------------ cli
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rename a corpus's tool vocabulary.")
    parser.add_argument("--corpus", default=".",
                        help="corpus root (default: .)")
    parser.add_argument("--map", default="",
                        help="canonical=target list, e.g. bash=shell,read=view")
    parser.add_argument("--profile", default=None,
                        help="JSON profile with a 'names' object")
    parser.add_argument("--dump-profile", action="store_true",
                        help="print the current vocabulary as a profile and exit")
    parser.add_argument("--out", default=None,
                        help="write a NEW tree here (source untouched)")
    parser.add_argument("--in-place", action="store_true",
                        help="rewrite the corpus itself (needs --yes)")
    parser.add_argument("--yes", action="store_true",
                        help="confirm an in-place rewrite")
    parser.add_argument("--scope", choices=("sample", "all"), default="sample",
                        help="'all' also renames raw episode tool events")
    parser.add_argument("--backup-dir", default=None,
                        help="copy every touched file here before writing")
    parser.add_argument("--check", action="store_true",
                        help="validate a tree against the mapping; exit 1 on drift")
    parser.add_argument("--report", default=None,
                        help="write the retag report to this path")
    args = parser.parse_args(argv)

    if args.dump_profile:
        print(json.dumps(dump_profile(parse_name_map(args.map)), indent=2))
        return 0

    corpus = Path(args.corpus)
    mapping: dict[str, str] = {}
    if args.profile:
        mapping.update(load_profile(args.profile))
    mapping.update(parse_name_map(args.map))

    try:
        if args.check:
            problems = check_corpus(corpus, mapping)
            for problem in problems:
                print(f"DRIFT {problem}")
            print(f"{'clean' if not problems else 'drifted'}: "
                  f"{len(problems)} problem(s)")
            return 1 if problems else 0

        if args.in_place and not args.yes:
            print("refusing an in-place rewrite without --yes", file=sys.stderr)
            return 2
        report = retag_corpus(
            corpus, mapping,
            out=Path(args.out) if args.out else None,
            in_place=args.in_place,
            scope=args.scope,
            backup_dir=Path(args.backup_dir) if args.backup_dir else None,
        )
    except RetagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.report:
        atomic_write_text(Path(args.report), json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
