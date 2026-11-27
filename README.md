# MegaBit Trajectories

[![Episodes](https://img.shields.io/badge/Episodes-66-blue)](#composition)
[![Verified](https://img.shields.io/badge/Verified-66%2F66-success)](verify.py)
[![Tool calls](https://img.shields.io/badge/Tool%20calls-2%2C312-informational)](#composition)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-ffcc4d)](https://huggingface.co/datasets/Sumama-Jameel/megabit-trajectories)
[![Explorer](https://img.shields.io/badge/Explorer-Live-7c5cff)](https://huggingface.co/spaces/Sumama-Jameel/trajectory-explorer)

Real coding agent sessions. A ticket comes in. The agent reads the repo, calls tools, edits files, runs the tests, hits real errors, and fixes them. Every tool call ran in a real sandbox. Every session is checked. The packaging is MIT licensed, with upstream licenses kept per row.

This is the free dataset. Use it to train and study the agent loop: act, observe, fail, repair.

- Dataset: https://huggingface.co/datasets/Sumama-Jameel/megabit-trajectories
- Explorer: https://huggingface.co/spaces/Sumama-Jameel/trajectory-explorer
- Verifier: `python3 verify.py` in this repo
- Proof of work: [CASE_STUDY.md](CASE_STUDY.md), two runs that tested this corpus's claim and what they did and did not show

## Load it in 3 lines

```python
from datasets import load_dataset

ds = load_dataset("Sumama-Jameel/megabit-trajectories", split="train")
print(ds[0]["repo"], len(ds[0]["messages"]), "messages")
```

EASY AF.

## Explore it in the browser

Step through any session: play the loop, jump to a failed tool call, read the recovery, and inspect the raw JSON.

[Trajectory Explorer](https://huggingface.co/spaces/Sumama-Jameel/trajectory-explorer)

## What one row is

One row is one full session, in order.

```
system    the tools, the workspace, the rules
user      the ticket: what to change and how it will be checked
assistant tool calls: read, grep, edit, write, bash, todo
tool      the exact output, including errors
assistant the next step
tool      a failing test run
assistant the fix, the retry, the passing run
```

Nothing is summarized. Nothing is made up. The final patch is in the transcript.

## What it trains

| Capability | What the model sees | How to measure it |
|---|---|---|
| Coding | Real edits in attrs, click, packaging, tenacity, and cli | Tests pass at the end of the session |
| Planning | Ticket, repo exploration, ordered edits, tests before the answer | Plan before the first edit, edit order, time to green |
| Tool calls | Full JSON schema, arguments, exact output, parallel calls | Schema validity, parse rate, correct argument use |
| Agentic execution | Long in-order sessions, median 29 tool calls, up to 134 | Steps to completion, tool calls per session |
| Recovery | Failed commands, rejected calls, broken tests, retries | Recovery rate: does the session fix its own failed call |

The data is built to improve these five behaviors. You do not have to take that on faith. The repo ships a verifier, a per-call ledger, and a per-session provenance record, so you can check the signal before you train on it.

Every row is dense. The model sees the tool schema before the call, the exact output after the call, and the next action. When a call fails, the next turns show the diagnosis and the fix. That is the signal that teaches recovery.

## Composition

| Item | Value |
|---|---|
| Sessions | 66 |
| Repositories | attrs, click, packaging, tenacity, cli |
| Language | Python |
| Tool calls recorded in the raw logs | 2,541 |
| Tool calls in the training rows | 2,312 (2,311 parsed plus 1 rejected) |
| Recovered calls | 221 authentic calls from failed attempts |
| Failed tool executions kept with the fix | 60 |
| Rejected malformed calls kept with the error | 1 |
| Parallel call batches | 456 |
| Sessions with tests passing at the end | 66 of 66 |
| Audited checks per session | 4 of 4 |
| Models | 3, recorded per row in `provenance.model` |
| License | MIT for the packaging, upstream licenses kept per row |
| Size | about 1.17M tokens of message content |

The four audited checks are ticket path, provenance, license, and tests.

One row carries the model's malformed `grep` call exactly as issued, with `parse_status: error`, its raw argument text, and the rejection it received. It is kept on purpose. Clean-call data teaches the happy path. This row teaches the rest.

The 60 failed executions are tool messages with an error set, or output beginning "Tool execution failed". The rejected malformed call is counted separately. The successful retries that follow keep every failure visible in order; nothing is filtered out.

### Splits

| Split | Sessions |
|---|---|
| `action_only` | 56 |
| `legacy_unplanned` | 6 |
| `network_dependent` | 1 |
| `quarantine_test_only` | 1 |
| `research_only` | 2 |

The two `research_only` sessions ended at the iteration cap and are kept and flagged, not hidden.

## Try it in 60 seconds

No install, no API key, no service:

```bash
git clone https://github.com/Sumama-Jameel/megabit-trajectories.git
cd megabit-trajectories

# Check every sha256 and verdict (66/66 should pass)
python3 verify.py

# Look at one episode
head -c 1200 episodes/012ad533e237baaf/012ad533e237baaf.sample.jsonl
```

Or use the Hugging Face copy, which also ships parquet, JSONL, and an index:

```python
from datasets import load_dataset

ds = load_dataset("Sumama-Jameel/megabit-trajectories", split="train")
print(ds)
```

## How to train on it

### Pretraining

This data was collected for continued pretraining. The supervision is the whole transcript, in order.

1. Use every session. All 66 are full sessions, not answers.
2. Pack whole sessions. Keep the order. Do not shuffle messages inside a session.
3. Keep tool results verbatim. Cap markers are part of the record.
4. Measure the loop. Tool call schema validity, parse rate, tests passed at the end, and recovery rate are the right scores.

### Fine-tuning

The same 66 sessions can be used for fine-tuning. The repo ships `convert_formats.py`, which converts the corpus into the shapes that LoRA and most fine-tuning stacks load: OpenAI messages, ShareGPT, Hermes, and rendered text. Reformat first, then train. Do not feed the raw sample tree to a trainer that expects a chat template.

```bash
python3 convert_formats.py --list

# Write a new tree. The corpus is never modified.
python3 convert_formats.py --corpus . --format sharegpt --out ../ft/sharegpt
python3 convert_formats.py --corpus . --format openai   --out ../ft/openai
python3 convert_formats.py --corpus . --format hermes   --out ../ft/hermes
python3 convert_formats.py --corpus . --format text     --out ../ft/text

# Re-derive every episode and fail if one message, call id, or result moved.
python3 convert_formats.py --corpus . --format sharegpt --out ../ft/sharegpt --check
```

What the formats are for:

- `openai`: native `messages[]` with `tool_calls`, for TRL, Axolotl, Unsloth, and most chat-template trainers.
- `sharegpt`: `conversations[]` with `from` and `value`, for LLaMA-Factory, Axolotl, and LoRA recipes that expect ShareGPT.
- `hermes`: the Hermes function-calling layout.
- `text`: one rendered transcript per episode, for plain next-token training.

Cleaning. This is a small corpus with labeled splits, so clean by filtering rather than by rewriting. `metadata.split` is on every sample. Keep `action_only` (56 sessions) for the cleanest training set. `legacy_unplanned` sessions are kept as negative examples for planning; `research_only` ended at the budget cap; `quarantine_test_only` and `network_dependent` are labeled and should stay out of training-ready mixtures. The converter preserves what it is given, so filter the source first if you need a lighter tree. Every run writes a `MANIFEST.json` with source and output hashes.

A fine-tune is not a free win. Our first fine-tune raised tool-call schema validity on a held-out protocol test from 43% to 80%, but the full battery showed regressions in other instruments, so no clean claim is made. Reformat, keep the failure turns, and evaluate on your own held-out protocol test before you trust it.

## Schema

In the Hugging Face parquet file, each row has these columns:

- `episode_id`: the stable session id.
- `id`: the record id.
- `repo`, `repo_url`, `license`: the upstream repository and its SPDX license.
- `model`: the model that produced the session.
- `messages`: the full ordered transcript. Each message has `role`, `content`, `name`, `tool_call_id`, `tool_calls`, `error`, `truncated`, `duration_ms`, `dropped_chars`, and `original_chars`.
- `tools`: the OpenAI function-calling catalog used in the session.
- `metadata`: tool count, attempts, review rounds, normalization detail, terminal state.
- `provenance`: repo, base commit, target commit, license, model, session id, task check.
- `verification`: the export verdict and checks.
- `produced_diff_sha256`: the sha256 of the agent diff.

Inside `tool_calls`, `arguments` is JSON text. Parse it with `json.loads(tc["arguments"])`. The one malformed call has `arguments: null`, `arguments_raw` set, and `parse_status: "error"`, so a strict loader can branch before parsing.

```python
import json
row = ds[0]
for msg in row["messages"]:
    for tc in msg["tool_calls"] or []:
        if tc["parse_status"] != "error":
            args = json.loads(tc["arguments"])
```

In this repository, each episode ships as a JSONL file with `messages[]`, `tools`, `metadata`, `provenance`, `verification`, and `failure_recovery` records. A chat-format loader can read every message as shipped.

## Files

This repository ships:

```
episodes/                 the full record: raw log, sample, ticket, evidence
verify.py                 offline integrity check
check_shape.py            message shape check
retag_tools.py            rename the tool vocabulary
convert_formats.py        export to OpenAI, ShareGPT, Hermes, or text; the shapes LoRA and most fine-tuning stacks load
merge_parallel_calls.py   merge split parallel calls
counts.json               the source of truth for every count
training_manifest.json    canonical sample path and sha256 per episode
DATA_CARD.md              the full data card
TOOLS.md                  the tooling guide
THIRD_PARTY_NOTICES.md    upstream license notices
```

The Hugging Face dataset adds a flat training copy:

```
data/train.parquet        the 66 training rows, viewer ready
data/train.jsonl          the same rows, one JSON object per line
data/index.parquet        one flat row per session, easy to filter
data/index.json           the same index as JSON
data/tools.json           the tool contract for the whole corpus
PILOT.md                  how to get a private corpus for your lab
```

Long tool outputs in the flat copy are capped with an explicit marker. The full text is in `episodes/<id>/<id>.episode.jsonl`.

## Verify it yourself

```bash
python3 verify.py            # 66/66, exit 0
python3 verify.py --quiet
```

It re-computes both sha256 values per episode, checks header and footer presence, tool-call counts, the export verdict, provenance fields, and the recorded `task_mac_valid` verdict (it does not re-derive the HMAC). It does not re-run the sandbox; it checks that the record you downloaded is the record that was published.

Deeper checks live with the engine (`megabit-remediation` tooling): a deep verifier re-derives counts from the artifacts, re-checks every raw call disposition, re-audits every ticket and hint path against the Diff1 tree, re-scans secrets including binaries, and verifies the signed `release_manifest.json` at the repository root. `counts.json` is the single generated source of truth for every number above; the release manifest covers every file except itself, the signature, the replay report, and the deep-verification report.

Operational records carry placeholders instead of the build machine's paths: `<MEGABIT_DATA>`, `<MEGABIT_REPO>`, `<HOME>`, `<SANDBOX_HOME>`. Raw logs and samples are untouched, so every sha256 above still covers the published bytes.

## Rename the tools

```bash
python3 retag_tools.py --dump-profile > lab.json
python3 retag_tools.py --corpus . --profile lab.json --out ../renamed
python3 retag_tools.py --corpus ../renamed --profile lab.json --check
```

It rewrites tool call names, tool result names, each sample's catalog, `episodes/tools.json` and the `finalization.json` digest. Message content is never touched. No dependencies.

## Why it is usable

- Real execution only. Every tool call ran in a Docker sandbox. Outputs are stored as the tool produced them, including the failures.
- The answer was not in the room. The workspace is rebased onto a fresh root commit, so `git log`, `git diff` and the reflog cannot reveal the human fix.
- Verified, not asserted. An episode ships only if the project's tests pass and the agent's diff clears a composite similarity gate against the human patch. `verify.py` re-checks all 66 files offline.
- Self-describing records. Each sample carries its tool catalog, the alias table, the tool-output policy, the message-normalization record, `split`, `ends_with_final_answer`, and `terminal_state`. A consumer can filter without opening the raw log.
- Provenance per episode. Repository, base and target commit, SPDX license, model, session, task HMAC and the verification report travel with the data.
- Failure is data. Malformed commands, rejected calls, broken installs and the recovery after them are kept.
- Rename it to your vocabulary. `retag_tools.py` rewrites the shell tool to `SHELL` or `execute`, the reader to `view`, in one command, with a `--check` mode. Renaming there and back is byte-identical.

## How it compares

| Project | Real execution | Human answer hidden | Ships data | Scale |
|---|---|---|---|---|
| **MegaBit Trajectories** | **Yes, Docker sandbox** | **Yes, fresh root commit** | **Yes, 66 verified episodes, MIT** | 66 episodes, 5 repos, Python |
| Rig (AgentGen) | Yes | Yes | No, internal to their model | 200k+ episodes, 52 languages |
| Understanding by Reconstruction | No, tool outputs are simulated | No, whole repo is ground truth | Paper corpus | Academic |
| daVinci-Agency | Partial | No | OSS dataset | 239 trajectories |
| SWE-smith / SWE-Gym / R2E-Gym | Yes | Issue-based | OSS datasets | Tens of thousands |
| Toucan (IBM) | Yes | No | OSS dataset | 1.5M trajectories |
| CodeDelta | Not applicable | Not applicable | Free export tool | Commit pairs, no agent process |

Most of these are bigger. Rig is two orders of magnitude bigger with a trained model on top. The difference is what is shipped: execution-grounded episodes with an audit trail, a verifier, and a license record per episode, rather than a pipeline or a paper.

## The episodes

<details>
<summary>All 66 sessions, with similarity, tool calls, review rounds, tests, and time</summary>

| Episode | Repository | Sim | Tool calls | Review rounds | Tests pass | Time |
|---|---|---|---|---|---|---|
| [`3fc1a5fb92713be9`](episodes/3fc1a5fb92713be9/) | packaging (Apache-2.0) | 1.000 | 26 | 1 | yes | 40 min |
| [`611e35323caaf082`](episodes/611e35323caaf082/) | attrs (MIT) | 1.000 | 61 | 3 | yes | 12 min § |
| [`86fc0604d03248ba`](episodes/86fc0604d03248ba/) | packaging (Apache-2.0) | 1.000 | 21 | 1 | yes | 37 min |
| [`8a4bf108bb03b794`](episodes/8a4bf108bb03b794/) | packaging (Apache-2.0) | 1.000 | 28 | 1 | yes | 18 min |
| [`99a4bccd5addbb0e`](episodes/99a4bccd5addbb0e/) | packaging (Apache-2.0) | 1.000 | 16 | 1 | yes | 20 min |
| [`b37ef87e467d64e6`](episodes/b37ef87e467d64e6/) | attrs (MIT) | 1.000 | 45 | 1 | yes | 6 min |
| [`d6f9cc39994bea23`](episodes/d6f9cc39994bea23/) | packaging (Apache-2.0) | 1.000 | 35 | 1 | yes | 9 min |
| [`8bb1081352bda3fc`](episodes/8bb1081352bda3fc/) | click (BSD-2-Clause) | 0.938 | 30 | 1 | yes | 5 min |
| [`a0b5794e7403ed3d`](episodes/a0b5794e7403ed3d/) | packaging (Apache-2.0) | 0.913 | 33 | 1 | yes | 26 min |
| [`12817d803e8f9f1c`](episodes/12817d803e8f9f1c/) | packaging (Apache-2.0) | 0.898 | 17 | 1 | yes | 26 min |
| [`23fcc876cc35b523`](episodes/23fcc876cc35b523/) | tenacity (Apache-2.0) | 0.877 | 18 | 1 | yes | 7 min |
| [`aeb75d2533b23d63`](episodes/aeb75d2533b23d63/) | packaging (Apache-2.0) | 0.875 | 18 | 1 | yes | 21 min |
| [`114f10e73ae47ce3`](episodes/114f10e73ae47ce3/) | tenacity (Apache-2.0) | 0.861 | 50 | 1 | yes | 14 min |
| [`3a35d6717919075a`](episodes/3a35d6717919075a/) | attrs (MIT) | 0.850 | 33 | 1 | yes | 6 min |
| [`73246683fe7ee6c6`](episodes/73246683fe7ee6c6/) | attrs (MIT) | 0.835 | 24 | 1 | yes | 5 min |
| [`400b4635d276b767`](episodes/400b4635d276b767/) | tenacity (Apache-2.0) | 0.809 | 12 | 1 | yes | 5 min |
| [`a066c3d9cbcb7e18`](episodes/a066c3d9cbcb7e18/) | attrs (MIT) | 0.780 | 20 | 1 | yes | 8 min |
| [`864a19a5d07ecac7`](episodes/864a19a5d07ecac7/) | click (BSD-3-Clause) | 0.765 | 31 | 1 | yes | 10 min |
| [`afd00fe36c2ad88c`](episodes/afd00fe36c2ad88c/) | click (BSD-2-Clause) | 0.765 | 26 | 1 | yes | 6 min |
| [`1b1f2e9f7ff0fd2a`](episodes/1b1f2e9f7ff0fd2a/) | packaging (Apache-2.0) | 0.743 | 29 | 1 | yes | 31 min |
| [`979988594a97aafb`](episodes/979988594a97aafb/) | click (BSD-3-Clause) | 0.741 | 27 | 1 | yes | 12 min |
| [`a535207a360b1f44`](episodes/a535207a360b1f44/) | click (BSD-3-Clause) | 0.741 | 42 | 1 | yes | 15 min |
| [`31fc77740af45bd4`](episodes/31fc77740af45bd4/) | attrs (MIT) | 0.735 | 39 | 1 | yes | 23 min |
| [`fe34f71ffe61ad61`](episodes/fe34f71ffe61ad61/) | click (BSD-3-Clause) | 0.731 | 26 | 1 | yes | 8 min |
| [`e053a2849dddbebe`](episodes/e053a2849dddbebe/) | click (BSD-3-Clause) | 0.728 | 20 | 1 | yes | 6 min |
| [`2f219d6f06d064cc`](episodes/2f219d6f06d064cc/) | attrs (MIT) | 0.726 | 37 | 1 | yes | 18 min |
| [`57b500b3a9ee36b6`](episodes/57b500b3a9ee36b6/) | click (BSD-2-Clause) | 0.725 | 25 | 1 | yes | 8 min |
| [`b9e9143d07b01282`](episodes/b9e9143d07b01282/) | packaging (Apache-2.0) | 0.709 | 17 | 1 | yes | 11 min |
| [`407fa06b826e1657`](episodes/407fa06b826e1657/) | packaging (Apache-2.0) | 0.691 | 29 | 1 | yes | 27 min |
| [`efd63c576c434d63`](episodes/efd63c576c434d63/) | packaging (Apache-2.0) | 0.678 | 57 | 1 | yes | 15 min |
| [`4f8401a368bba994`](episodes/4f8401a368bba994/) | click (BSD-3-Clause) | 0.672 | 123 | 1 | yes | 41 min |
| [`8b48d640ad1f1576`](episodes/8b48d640ad1f1576/) | attrs (MIT) | 0.665 | 46 | 1 | yes | 10 min |
| [`e0de8e048c30d0d6`](episodes/e0de8e048c30d0d6/) | click (BSD-3-Clause) | 0.660 | 29 | 1 | yes | 9 min |
| [`33da938be0a526fb`](episodes/33da938be0a526fb/) | attrs (MIT) | 0.658 | 27 | 1 | yes | 10 min |
| [`fd65634c348f1601`](episodes/fd65634c348f1601/) | click (BSD-3-Clause) | 0.650 | 56 | 1 | yes | 21 min |
| [`012ad533e237baaf`](episodes/012ad533e237baaf/) | packaging (Apache-2.0) | 0.649 | 26 | 1 | yes | 14 min |
| [`5760e3b4271e5d3e`](episodes/5760e3b4271e5d3e/) | click (BSD-3-Clause) | 0.641 | 50 | 1 | yes | 11 min |
| [`349db9dae0e05b9e`](episodes/349db9dae0e05b9e/) | click (BSD-3-Clause) | 0.637 | 69 | 1 | yes | 22 min |
| [`2b67051b08a2794f`](episodes/2b67051b08a2794f/) | attrs (MIT) | 0.619 | 51 | 1 | yes | 14 min |
| [`2288ac90554bcfa6`](episodes/2288ac90554bcfa6/) | packaging (Apache-2.0) | 0.615 | 40 | 1 | yes | 25 min |
| [`44a7dbbd48675f67`](episodes/44a7dbbd48675f67/) | click (BSD-3-Clause) | 0.611 | 23 | 1 | yes | 8 min |
| [`ebaa0de9c4092fd4`](episodes/ebaa0de9c4092fd4/) | packaging (Apache-2.0) | 0.598 | 12 | 1 | yes | 11 min |
| [`e3a02407766bdf33`](episodes/e3a02407766bdf33/) | packaging (Apache-2.0) | 0.587 | 30 | 1 | yes | 34 min |
| [`9abc66072ab1bc9b`](episodes/9abc66072ab1bc9b/) | click (BSD-3-Clause) | 0.584 | 19 | 1 | yes | 8 min |
| [`1f3dfd68ce2f10fd`](episodes/1f3dfd68ce2f10fd/) | tenacity (Apache-2.0) | 0.583 | 24 | 1 | yes | 21 min |
| [`7bd0a927168a14f3`](episodes/7bd0a927168a14f3/) | attrs (MIT) | 0.583 | 16 | 1 | yes | 3 min |
| [`b8d783f57b4b84eb`](episodes/b8d783f57b4b84eb/) | packaging (Apache-2.0) | 0.582 | 27 | 1 | yes | 47 min |
| [`7d2d3557467897b4`](episodes/7d2d3557467897b4/) | click (BSD-3-Clause) | 0.576 | 33 | 1 | yes | 8 min |
| [`1039a0159065c3b0`](episodes/1039a0159065c3b0/) | packaging (Apache-2.0) | 0.574 | 35 | 1 | yes | 24 min |
| [`2d6f3e5f14681273`](episodes/2d6f3e5f14681273/) | attrs (MIT) | 0.566 | 43 | 1 | yes | 12 min |
| [`81a8b6b065bafe21`](episodes/81a8b6b065bafe21/) | attrs (MIT) | 0.562 | 95 | 1 | yes | 36 min |
| [`032c699ac1c2d252`](episodes/032c699ac1c2d252/) | packaging (Apache-2.0) | 0.559 | 19 | 1 | yes | 28 min |
| [`490a433138e1fe8e`](episodes/490a433138e1fe8e/) | cli (BSD-3-Clause) | 0.552 | 56 | 1 | yes | 12 min ‡ |
| [`a5e823c9f6618766`](episodes/a5e823c9f6618766/) | attrs (MIT) | 0.548 | 44 | 1 | yes | 16 min |
| [`21721c8be6eec2d5`](episodes/21721c8be6eec2d5/) | attrs (MIT) | 0.547 | 100 | 1 | yes | 46 min |
| [`f20d68038c27594c`](episodes/f20d68038c27594c/) | click (BSD-3-Clause) | 0.541 | 70 | 1 | yes | 18 min |
| [`4c434330ee44b096`](episodes/4c434330ee44b096/) | attrs (MIT) | 0.539 | 27 | 1 | yes | 5 min |
| [`0571b7eb5d6b7555`](episodes/0571b7eb5d6b7555/) | attrs (MIT) | 0.538 | 134 | 3 | yes | 34 min |
| [`94dab878e2c9a0ec`](episodes/94dab878e2c9a0ec/) | packaging (Apache-2.0) | 0.534 | 39 | 1 | yes | 13 min |
| [`1bdf5e7c144469b8`](episodes/1bdf5e7c144469b8/) | tenacity (Apache-2.0) | 0.530 | 25 | 1 | yes | 9 min |
| [`1eb9f1613651e8fb`](episodes/1eb9f1613651e8fb/) | attrs (MIT) | 0.519 | 58 | 1 | yes | 23 min |
| [`467619066bf26662`](episodes/467619066bf26662/) | tenacity (Apache-2.0) | 0.514 | 12 | 1 | yes | 5 min |
| [`d6f539cc3e8728e8`](episodes/d6f539cc3e8728e8/) | click (BSD-3-Clause) | 0.498 | 31 | 1 | yes | 10 min |
| [`25e452d88c01814e`](episodes/25e452d88c01814e/) | packaging (Apache-2.0) | 0.491 | 35 | 1 | yes | 20 min |
| [`c929463c84ceb538`](episodes/c929463c84ceb538/) | click (BSD-2-Clause) | 0.481 | 74 | 1 | yes | 11 min |
| [`966101f98864fafa`](episodes/966101f98864fafa/) | click (BSD-2-Clause) | 0.452 | 51 | 1 | yes | 20 min † |

`Sim` is composite similarity against the human patch (1.000 = identical). The pass
gate is composite >= 0.45, not line similarity; line similarity is a stricter sub-score
and can fall below 0.45 while the composite passes. Older episodes without a recorded
composite show line similarity instead.

- † `966101f98864fafa` is quarantined (`quarantine_test_only`): the human fix is test-only, the seeded tests were locked before the coder started, the produced diff touches only LICENSE, and the gate passed on the LICENSE hunk. Kept as evidence; excluded from every training-ready list.
- ‡ `490a433138e1fe8e` is `network_dependent`: live httpbin.org calls in the coder session and in the seeded tests, with no egress-relaxation record on file. Kept as labeled research data; do not present as offline-reproducible.
- § `611e35323caaf082` recorded no three-run harness round in its retry journal (the reviewer ran the suite). An offline replay of the final diff against the locked seeded tests passes 3 of 3 sequential runs; see `episodes/611e35323caaf082/evidence/harness_replay.json`. The replay is environment-adapted (host Python 3.10.12), so it is labeled a replay, not a canonical harness round.

</details>

## Read this before you pretrain

- **66 sessions, about 1.17M tokens (about 4.7M characters of message content).** Nearly every token is a real action or a real observation, so the density is high: 2,541 raw tool-call events, 2,312 tool-call records in the training rows (2,311 parsed plus 1 rejected), 221 authentic calls restored from failed attempts, 456 parallel-call batches, and 60 failed tool executions. That makes it a strong component in a pretraining mixture. It is not a corpus to pretrain on alone, and a gain here is a protocol-instrument result, not a general capability claim.
- **Python only.** Five mainstream libraries. No systems code, no frontend, no infrastructure.
- **Two episodes are labelled `research_only`** because they ended at the iteration cap, and both record an agent-written test log inside their final diff. They are kept and flagged, not hidden.
- **20 v1 prompts contained a false statement about git.** They called `git status`, `git diff` and `git log` useless. The statement was wrong for inspecting the agent's own work. The archived prompt bytes are unchanged. Each episode records `evidence/briefing_policy.json`; the 20 affected episodes are `sft_eligible: false` and excluded from every trainable list.
- **The quarantine and network labels are real.** `966101f98864fafa` passed on a LICENSE-only diff and is excluded from training lists. `490a433138e1fe8e` used live httpbin.org calls and is labelled `network_dependent`, so do not present it as offline-reproducible.

## Repo layout

```
retag_tools.py                 rename the tool vocabulary (no deps)
convert_formats.py             export to openai / sharegpt / hermes / text
merge_parallel_calls.py        merge split parallel calls (no deps)
check_shape.py                 check the merged tool-call shape (no deps)
verify.py                      offline integrity check
TOOLS.md                       guide to the three repair tools
counts.json                    generated source of truth for every count
training_manifest.json         canonical sample path and sha256 per episode
remediation_manifest.json      file-level adoption ledger (before/after sha256)
secret_scan.json               full-tree byte scan (0 findings)
release_manifest.json          signed manifest of every published file
verify_report.json             deep-verification output
REMEDIATION_REPORT_2026-11-17.md  audit findings and their dispositions
episodes/
  tools.json                   the tool contract for the whole corpus
  index.json                   one row per episode (split, split_reason, ...)
  failures.jsonl               malformed calls excluded from samples, with pointers
  <task_id>/                   one episode
DATA_CARD.md                   composition, limits, changelog
LICENSE                        MIT
```

Each episode directory contains:

```
episodes/<task_id>/
  <task_id>.episode.jsonl    raw event log: header, every event, footer
  <task_id>.sample.jsonl     training record: messages[] + tools + provenance
  evidence/                  machine-readable audit artifacts
  ticket.md                  what the agent was asked to do
  briefing.md                workspace facts it was given
  hints.md                   file paths it was allowed to see
  feedback/round_N.md        reviewer reports for each review round
  logs/                      coder, reviewer, ticket agent, setup, retries
  config.snapshot.json       run config, secrets redacted
  setup_state.json           10-step setup record
  finalization.json          verdict + sha256 of both JSONL files
```

The ground-truth patch is not shipped. The agent's own work is: `produced_diff` in the episode footer and the final patch in the sample messages.

### Upstream repositories

- [attrs](https://github.com/python-attrs/attrs) - under MIT
- [cli](https://github.com/httpie/cli) - under BSD-3-Clause
- [click](https://github.com/pallets/click) - under BSD-2-Clause / BSD-3-Clause
- [packaging](https://github.com/pypa/packaging) - under Apache-2.0
- [tenacity](https://github.com/jd/tenacity) - under Apache-2.0

## What we need

- **Train on it and report the number.** Pretraining or fine-tuning, even one instrument, even if it got worse.
- **Point the engine at another language.** Python is what is published; the engine handles JS, TS, Go and Rust.
- **Break it.** Open an issue with the episode id. The defects consumers reported in November 2026 are fixed and listed in the changelog; there are more.

## Want this on your stack?

The free dataset is the public proof. The pilot is the private version:

- Your repositories.
- Your languages. The public release is Python. The pilot covers your stack.
- Reasoning traces, if your training recipe needs them.
- Your harness, your tools, your tests.
- Your eval, run before and after.
- A fixed scope, a fixed timeline, and a verifier you keep.

If you are at an AI lab and you want a private corpus, email sumamajamil2005@gmail.com with the subject "MegaBit pilot". Tell us the model, the repos, the capabilities, and the eval you care about. We will send a scope and a date.

## Community results

We will list public results here. Send yours to sumamajamil2005@gmail.com.

## Cite this dataset

```bibtex
@dataset{megabit_trajectories_2026,
  title = {MegaBit Trajectories},
  author = {Jameel, Sumama},
  year = {2026},
  publisher = {MegaBit},
  url = {https://huggingface.co/datasets/Sumama-Jameel/megabit-trajectories},
  license = {MIT}
}
```

## Changelog

- 2026-11-20: v1.0.0, first public release on Hugging Face.
- 2026-11-22: audit follow-up, upstream license notices, and the b37 rejection record.

## License

MIT. See [LICENSE](LICENSE).

Upstream source code in the corpus keeps its original license: Apache-2.0, MIT, BSD-3-Clause and BSD-2-Clause. Upstream notices travel with the data.

Built by MegaBit. Contact: sumamajamil2005@gmail.com
