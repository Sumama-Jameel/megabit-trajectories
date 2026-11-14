# The three repair tools

This page covers three scripts in this repository and nothing else. They all
work on the published corpus, they need no dependencies, and they never touch
the raw `.episode.jsonl` log unless you explicitly ask for it.

| Tool | File | What it is for |
|---|---|---|
| Merge parallel calls | `merge_parallel_calls.py` | Puts tool calls that were issued together back into one assistant turn |
| Check message shape | `check_shape.py` | Reports whether any sample still carries split turns |
| Rename tools | `retag_tools.py` | Rewrites the tool names into your harness vocabulary |

All three are plain Python 3.9 and up. Run them from the repository root.

---

## 1. `merge_parallel_calls.py` (the exporter rule)

A model can ask for two or three tools at the same moment. In the raw event
log each request is its own `tool_call` event, back to back, with no result in
between. If an exporter writes one assistant message per request, the sample
says the agent made the calls one after another, which is not what happened.

This script applies the rule the engine uses in
`megabit/export.py::_build_messages`: a new assistant turn is opened only when
the previous message is not already an assistant turn holding open tool calls
with no text of its own. Calls that were issued together end up in one turn.

```
before                            after
assistant {tool_calls: [read]}    assistant {tool_calls: [read, read, grep]}
assistant {tool_calls: [read]}    tool      {read result}
assistant {tool_calls: [grep]}    tool      {read result}
tool      {read result}           tool      {grep result}
...
```

What it rewrites:

- `messages[]` on each sample: the split turns become one turn.
- `metadata.messages_normalization.merged_parallel_tool_calls`: the running
  count of calls folded into a compound turn.
- the `sample_sha256` in `finalization.json`, so `verify.py` still passes.

What it never changes: call ids, call order, call names, argument objects, tool
result content, and the raw `*.episode.jsonl` file. Every call that goes in
comes out.

Check first, then choose where the output lands:

```bash
python3 merge_parallel_calls.py --corpus . --check          # read only, exit 1 if split turns remain
python3 merge_parallel_calls.py --corpus . --out ../merged  # writes a new tree, source untouched
python3 merge_parallel_calls.py --corpus . --in-place --yes --backup-dir ../backup
```

`--backup-dir` copies every file before it is written. An in place run refuses
to start without `--yes`. `--report out.json` saves the counts.

The published samples already hold the merged shape, so on this corpus the
command reports `episodes_changed: 0`. It is here for corpora built by an
older exporter. Run over the pre-rebuild samples, it folds 553 calls into
compound turns across 65 of the 66 episodes, and every call id comes through
in the same order.

---

## 2. `check_shape.py` (the verify guards)

This script carries the three guard functions from the engine's
`megabit/verify.py`:

- `sample_merge_invariant(messages)`: True when no assistant turn with a
  single call and no text is followed by another assistant turn that opens
  calls.
- `sample_has_no_split_tool_blocks(messages)`: the same rule, named for the
  message stream.
- `check_sample_message_shape(path)`: loads one sample and returns `ok`,
  `tool_call_blocks`, `compound_blocks` and `violations`.

It reads the sample the way a consumer would, so it is an independent check
of the exporter, not a replay of the raw events.

```bash
python3 check_shape.py                                  # whole corpus, one line per episode
python3 check_shape.py --quiet                          # summary only
python3 check_shape.py --episode 012ad533e237baaf       # one episode
python3 check_shape.py --json                           # machine readable
```

Exit code 0 means every sample holds the merged shape, 1 means at least one
does not, 2 means the corpus could not be read.

`blocks` counts assistant turns that declare tool calls. `compound` counts
how many of those hold more than one call. A sample with zero compound turns
and zero violations is simply a session where the model never asked for two
tools at once. A sample with split turns shows up as `violations=1`.

---

## 3. `retag_tools.py` (the vocabulary rename)

The corpus uses one canonical vocabulary: `read`, `glob`, `grep`, `edit`,
`write`, `bash`, `todo_write`, `todoread`. If your harness calls the shell
something else, this script rewrites the names instead of you editing 66 JSONL
files by hand.

It rewrites `messages[].tool_calls[].name`, `messages[].name` on tool
results, the per sample `tools` catalog, `metadata.tool_names_used`,
`metadata.tool_name_aliases`, `metadata.tool_spec_sha256`,
`episodes/tools.json`, and the sample digest in `finalization.json`. It never
rewrites message content, because prose that mentions a tool is evidence, not
a name field.

```bash
python3 retag_tools.py --dump-profile > lab.json
python3 retag_tools.py --corpus . --map bash=shell,read=view --out ../renamed
python3 retag_tools.py --corpus . --profile lab.json --out ../renamed
python3 retag_tools.py --corpus ../renamed --map bash=shell,read=view --check
python3 retag_tools.py --corpus . --map bash=shell --in-place --yes --backup-dir ../backup
```

`--check` exits 1 on drift. Renaming there and back is byte identical, so the
operation is lossless. `--scope all` also renames the raw episode's tool
events, which changes `raw_sha256`; it is off by default because the raw log
is the record of what the model emitted.

---

## Order to run them in

On a corpus built by an older exporter:

```bash
python3 merge_parallel_calls.py --corpus . --check      # 1. are there split turns?
python3 merge_parallel_calls.py --corpus . --out ../fixed
python3 check_shape.py --corpus ../fixed                # expect 0 violations
python3 verify.py                                       # expect 66/66
```

Then, if your harness needs different tool names, run `retag_tools.py` on the
tree you just checked, and `check_shape.py` again after the rename. A rename
does not change the message shape, so it should not change the shape report.

## What none of these tools do

They do not re-run anything in a sandbox. They do not add, remove or rewrite
tool results, ticket text, diffs or test output. They do not regenerate the
`episodes/index.json` table, so after a merge or a rename that changes counts,
treat that table as older than the samples.
