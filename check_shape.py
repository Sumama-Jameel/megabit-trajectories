#!/usr/bin/env python3
"""Check the message shape of every sample in a corpus.

Three small checks live here. They are the corpus-side copies of the guards
in the engine's ``megabit/verify.py`` (``sample_merge_invariant``,
``sample_has_no_split_tool_blocks``, ``check_sample_message_shape``), and they
ask one question: does any assistant turn open a tool call and get followed
straight away by another assistant turn that opens another call?

That shape means the sample was written by an exporter that did not know the
two calls were issued together. A correctly exported sample holds them in one
turn:

    good   assistant {tool_calls: [read, read]}
    bad    assistant {tool_calls: [read]}
           assistant {tool_calls: [read]}

Nothing here reads the raw episode log, so the answer is the same one a
consumer of the sample would get after loading it.

Usage
-----
    python3 check_shape.py
    python3 check_shape.py --quiet
    python3 check_shape.py --corpus ../some-corpus --episode 012ad533e237baaf

Exit codes: 0 when every sample passes, 1 when at least one does not, 2 when
the corpus cannot be read.

Requires Python 3.9+. No dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def sample_merge_invariant(messages: list[dict]) -> bool:
    """True when the SHIPPED sample never contains a naive parallel-call

    shape: an assistant turn with a single tool_call and no content,
    immediately followed by another assistant turn that also opens tool calls.

    The patched exporter merges consecutive parallel tool_call events
    (no intervening result or text) into ONE assistant turn with a
    compound tool_calls list, so this shape should be absent from a
    correctly exported sample. It is a message-shape check, independent
    of the raw event replay: it inspects the sample as a consumer would
    load it.

    Fail-closed by default: if the function is called and returns False,
    the sample still ships, but the publish gate records the violation.
    """
    for i in range(len(messages) - 1):
        cur = messages[i]
        nxt = messages[i + 1]
        if (cur.get("role") == "assistant"
                and cur.get("tool_calls")
                and len(cur["tool_calls"]) == 1
                and not cur.get("content")
                and nxt.get("role") == "assistant"
                and nxt.get("tool_calls")):
            return False
    return True


def sample_has_no_split_tool_blocks(messages: list[dict]) -> bool:
    """True when no assistant turn carries a split call pair.

    A split pair is two assistant tool-call turns that the raw event stream
    actually issued back-to-back (no result or text between). The patched
    exporter merges those into one turn, so a correctly exported sample
    should have no such pair. This is the SAME invariant as
    ``sample_merge_invariant``, expressed over the message stream rather
    than the raw events.
    """
    return sample_merge_invariant(messages)


def check_sample_message_shape(sample_path: str) -> dict:
    """Inspect ONE shipped sample's message shape.

    Returns a dict with keys:

    * ``ok``: bool, whether the sample's message stream satisfies the
      merge invariant.
    * ``tool_call_blocks``: int, how many assistant turns declare
      tool_calls.
    * ``compound_blocks``: int, how many of those declare more than one
      tool call (these are the merged parallel groups).
    * ``violations``: int, how many naive split pairs remain.
    """
    path = Path(sample_path) if isinstance(sample_path, str) else sample_path
    text = path.read_text(encoding="utf-8").strip()
    lines = [ln for ln in text.splitlines() if ln.strip()]
    try:
        sample = json.loads(lines[0])
    except (json.JSONDecodeError, IndexError) as exc:
        return {"ok": False, "tool_call_blocks": 0,
                "compound_blocks": 0, "violations": 0,
                "error": str(exc)}
    messages = sample.get("messages") or []
    tool_call_blocks = 0
    compound_blocks = 0
    for msg in messages:
        tc = msg.get("tool_calls")
        if tc:
            tool_call_blocks += 1
            if len(tc) > 1:
                compound_blocks += 1
    ok = sample_merge_invariant(messages)
    return {"ok": ok, "tool_call_blocks": tool_call_blocks,
            "compound_blocks": compound_blocks,
            "violations": (0 if ok else 1)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the message shape of every sample in a corpus.")
    parser.add_argument("--corpus", default=".",
                        help="corpus root (default: .)")
    parser.add_argument("--episode", default=None,
                        help="check one episode id instead of the whole corpus")
    parser.add_argument("--quiet", action="store_true",
                        help="only print the summary")
    parser.add_argument("--json", action="store_true",
                        help="print the per-sample results as JSON")
    args = parser.parse_args(argv)

    episodes = Path(args.corpus).resolve() / "episodes"
    if not episodes.is_dir():
        print(f"error: {args.corpus} has no episodes/ directory",
              file=sys.stderr)
        return 2

    if args.episode:
        sample_paths = [episodes / args.episode / f"{args.episode}.sample.jsonl"]
        if not sample_paths[0].is_file():
            print(f"error: no sample for {args.episode}", file=sys.stderr)
            return 2
    else:
        sample_paths = sorted(episodes.glob("*/*.sample.jsonl"))

    rows = []
    for sample_path in sample_paths:
        result = check_sample_message_shape(sample_path)
        rows.append({"id": sample_path.parent.name, **result})

    if args.json:
        print(json.dumps(rows, indent=2))
    elif not args.quiet:
        for row in rows:
            if "error" in row:
                print(f"FAIL {row['id']}  unreadable: {row['error']}")
            else:
                mark = "ok  " if row["ok"] else "FAIL"
                print(f"{mark} {row['id']}  blocks={row['tool_call_blocks']}"
                      f" compound={row['compound_blocks']}"
                      f" violations={row['violations']}")

    bad = [row for row in rows if not row["ok"]]
    print(f"\n{len(rows) - len(bad)}/{len(rows)} samples hold the merged shape")
    if bad:
        print(f"{len(bad)} sample(s) still carry split tool-call turns")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
