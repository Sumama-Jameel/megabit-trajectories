# MegaBit Trajectories

[![Episodes](https://img.shields.io/badge/Episodes-66-blue)](#composition)
[![Verified](https://img.shields.io/badge/Verified-66%2F66-success)](verify.py)
[![Tool calls](https://img.shields.io/badge/Tool%20calls-2,541-informational)](#composition)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)](#read-this-before-you-pretrain)

**Real coding-agent trajectories, recorded in a real sandbox. 66 sessions where an agent reads a repository, calls tools, runs the tests, hits real errors, and recovers. Every episode is verified, every tool output is genuine, and the whole thing is MIT licensed.**

---

## What This Solves

A coding agent does not fail because it cannot write a function. It fails because it calls a tool with the wrong schema, edits the wrong file, misreads a traceback, and then repeats the same mistake. Static code teaches none of that. Synthetic trajectories teach a version of it that never happened.

It is pretraining data for four capabilities:

- **Coding.** Real commits from real open source repositories: packaging, click, attrs, tenacity, cli.
- **Planning.** A ticket is read, the repository is explored, the next step is chosen, edits happen in a sensible order, and the session ends when the work verifies. The planning is visible in the todo lists, the greps before the edits, and the tests before the final answer.
- **Tool calls.** Every call carries its full JSON schema, its arguments, and the exact output the tool returned. Malformed calls stay in the raw logs (the sample layer excludes the one unparseable call, see below).
- **Recovery from failures.** Failed commands, rejected calls, broken tests and the steps that fixed them are kept in order, not filtered out.

The claim is not that a model becomes better at everything. It is narrower and measurable: this is pretraining data for the loop of act, observe, fail, repair.

Research on process data points the same way. Understanding by Reconstruction showed gains on coding and agentic benchmarks after continuing pretraining on reconstructed trajectories. daVinci-Agency got +47% relative on Toolathlon from 239 long-horizon trajectories. Toucan's 1.5M real tool-calling trajectories produced models that beat GPT-4.5-Preview on BFCL V3. Megabit's contribution is simpler: it ships the trajectories with real execution and an audit, instead of a pipeline and a promise.

---

## Try It In 60 Seconds

No install, no API key, no service:

```bash
git clone https://github.com/Sumama-Jameel/megabit-trajectories.git
cd megabit-trajectories

# Check every sha256 and verdict (66/66 should pass)
python3 verify.py

# Look at one episode
head -c 1200 episodes/012ad533e237baaf/012ad533e237baaf.sample.jsonl
```

Load it into a training or inspection loop:

```python
import json, glob

records = [json.load(open(p)) for p in
           sorted(glob.glob("episodes/*/*.sample.jsonl"))]

sft = [r for r in records if r["metadata"]["split"] == "sft"]
ep = sft[0]
print(ep["provenance"]["repo_name"], ep["provenance"]["license_spdx"])
print(len(ep["messages"]), "messages,", len(ep["tools"]), "tools")
print(ep["messages"][0]["content"][:400])       # the system prompt
```

Each file is a single JSON object. `messages` is OpenAI chat format, `tools` is OpenAI function-calling format, so it drops into most SFT stacks without a converter.

---

## Composition

| Item | Value |
|---|---|
| Episodes | 66 |
| Verified at export | 66 / 66 |
| Raw tool_call events | 2,541 |
| Tool calls in published samples | 2,311 |
| Split parallel blocks repaired in samples | 553 |
| Parallel-call batches in samples | 455 |
| Tool executions that failed in samples | 60 |
| Raw tool_call events missing tool_call_id | 0 |
| Repositories | attrs, cli, click, packaging, tenacity |
| Median tool calls per episode | 29 (shipped segments) |
| Tool outputs capped in samples | 138 |
| Split | sft: 64, research_only: 2 |
| Line similarity median | 0.5723 |
| Composite similarity median | 0.6593 |
| License | MIT (data packaging); upstream code keeps its own license |

The raw log carries 2,541 `tool_call` events, and every one of them carries a non-empty `tool_call_id`. 605 of those events sit directly after another call with no text or result between them; the samples ship them merged into one assistant turn per batch (455 batches). The merge preserves id order and all call content, so it is a grouping change, not a content change. The merged shape is the default sample shape: a strict chat-format loader can read every message as shipped.

One call in the corpus carries stream-truncated arguments that no parser can read. The sample layer excludes that call and its tool result — an unpaired result is not valid chat structure — and the raw log keeps both verbatim, marked `args_corrupt: true`. `episodes/failures.jsonl` indexes the call with the same-tool calls that follow it, so the recovery arc stays in the corpus in its original bytes.

"60 tool executions that failed" counts tool messages that record an error (`error` set, or output beginning "Tool execution failed"). The successful retries that follow keep every failure visible in order; nothing is filtered out.

### Message shape

```
system    role prompt: what tools exist, what the workspace is, what is hidden
user      the ticket: what to change and how it will be judged
assistant tool_calls[]  read, grep, edit, bash, todo_write ...
tool      the exact output of that call, capped with a marker if huge
assistant ...
tool      a failing test run
assistant the fix, the retry, the passing run
```

Every assistant step and every tool result is in order. Nothing is summarized and nothing is invented.

### Files per episode

```
episodes/<task_id>/
  <task_id>.episode.jsonl    raw event log: header, every event, footer
  <task_id>.sample.jsonl     training record: messages[] + tools + provenance
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

---

## Why It Is Usable

- **Real execution only.** Every tool call ran in a Docker sandbox. Outputs are stored as the tool produced them, including the failures.
- **The answer was not in the room.** The workspace is rebased onto a fresh root commit, so `git log`, `git diff` and the reflog cannot reveal the human fix.
- **Verified, not asserted.** An episode ships only if the project's tests pass and the agent's diff clears a composite similarity gate against the human patch. `verify.py` re-checks all 66 files offline.
- **Self-describing records.** Each sample carries its tool catalog, the alias table, the tool-output policy, the message-normalization record, `split`, `ends_with_final_answer`, and `terminal_state`. A consumer can filter without opening the raw log.
- **Provenance per episode.** Repository, base and target commit, SPDX license, model, session, task HMAC and the verification report travel with the data.
- **Failure is data.** Malformed commands, rejected calls, broken installs and the recovery after them are kept. Two episodes ended at the iteration cap and are labelled `research_only` instead of deleted.
- **Rename it to your vocabulary.** `retag_tools.py` rewrites the shell tool to `SHELL` or `execute`, the reader to `view`, in one command, with a `--check` mode. Renaming there and back is byte-identical.

---

## Pretrain On It

This is continued-pretraining data, not an instruction-tuning set. There is no per-step label or preference to optimize against; the supervision is the whole transcript, in order. The corpus is deliberately boring to load and hard to fake.

1. **Use every episode.** All 66 are sessions, not answers. The 2 `research_only` ones show what a session looks like when it runs out of budget, which is useful context for a model that has to decide when to stop.
2. **Pack whole sessions.** The median sample is about 62k characters, roughly 15k tokens; the largest is about 230k characters. Pack at your context length and keep the order. Do not shuffle messages inside an episode.
3. **Keep tool results verbatim.** Cap markers are part of the record. Do not re-summarize them, or you throw away the failure signal.
4. **Measure the loop, not a vibe.** Tool-call schema validity, tool-call parse rate, tests passed at the end of a session, and recovery rate (does the session fix its own failed call) are the scores this data is built to move. A held-out protocol test is the right instrument, not a general coding leaderboard.

Our first attempt used a fine-tune, which is the wrong tool for transcript data. It raised tool-call schema validity on our held-out protocol test from 43% to 80%, but the full battery showed regressions in other instruments, so we rebuilt the corpus and are retraining. No clean win yet, and no claim of one.

If you pretrain on it, tell us the numbers, including the bad ones. That is how this gets useful.

---

## How It Compares

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

---

## The Episodes

| Episode | Repository | Sim | Tool calls | Review rounds | Tests pass | Time |
|---|---|---|---|---|---|---|
| [`3fc1a5fb92713be9`](episodes/3fc1a5fb92713be9/) | packaging (Apache-2.0) | 1.000 | 26 | 1 | yes | 40 min |
| [`611e35323caaf082`](episodes/611e35323caaf082/) | attrs (MIT) | 1.000 | 61 | 3 | yes | 12 min |
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
| [`490a433138e1fe8e`](episodes/490a433138e1fe8e/) | cli (BSD-3-Clause) | 0.552 | 56 | 1 | yes | 12 min |
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
| [`966101f98864fafa`](episodes/966101f98864fafa/) | click (BSD-2-Clause) | 0.452 | 51 | 1 | yes | 20 min |

`Sim` is composite similarity against the human patch (1.000 = identical). The pass
gate is composite >= 0.45, not line similarity; line similarity is a stricter sub-score
and can fall below 0.45 while the composite passes. Older episodes without a recorded
composite show line similarity instead.

## Read This Before You Pretrain

- **66 sessions, about 1.5M tokens.** Nearly every token is a real action or a real observation, so the density is high: 2,311 tool calls, 455 parallel-call batches and 60 tool executions that failed. That makes it a strong component in a pretraining mixture. It is not a corpus to pretrain on alone, and a gain here is a protocol-instrument result, not a general capability claim.
- **Python only.** Five mainstream libraries. No systems code, no frontend, no infrastructure.
- **The tickets are near-spec.** Every ticket names the files to look at and every episode ships a hints file with paths; the QA tests are seeded from the human patch. The median recorded change is 22 added and 5 removed lines over 2 files.
- **Not contamination-free.** The target commit is public, so the fix is derivable from upstream. Use it for training and research, not as a clean leaderboard.
- **Two episodes are labelled `research_only`** because they ended at the iteration cap, and both record an agent-written test log inside their final diff. They are kept and flagged, not hidden.

---

## Verify

```bash
python3 verify.py            # 66/66, exit 0
python3 verify.py --quiet
```

It re-computes both sha256 values per episode, checks header and footer presence, tool-call counts, the export verdict, provenance fields, and the recorded `task_mac_valid` verdict (it does not re-derive the HMAC). It does not re-run the sandbox; it checks that the record you downloaded is the record that was published.

Operational records (setup state, setup logs, retry journals, feedback reports, finalization, config snapshots) carry placeholders instead of the build machine's paths: `<MEGABIT_DATA>`, `<MEGABIT_REPO>`, `<HOME>`, `<SANDBOX_HOME>`. Raw logs and samples are untouched, so every sha256 above still covers the published bytes.

---

## Rename The Tools

```bash
python3 retag_tools.py --dump-profile > lab.json
python3 retag_tools.py --corpus . --profile lab.json --out ../renamed
python3 retag_tools.py --corpus ../renamed --profile lab.json --check
```

It rewrites tool call names, tool result names, each sample's catalog, `episodes/tools.json` and the `finalization.json` digest. Message content is never touched. No dependencies.

---

## Change The Format

The samples ship as JSONL with `messages[]`, a `tools` catalog and flat call records (`id`, `name`, `arguments`). If your stack wants native `tool_calls`, ShareGPT, Hermes or one rendered text per episode, convert instead of hand-editing 66 files:

```bash
python3 convert_formats.py --list
python3 convert_formats.py --corpus . --format openai   --out ../ft/openai
python3 convert_formats.py --corpus . --format sharegpt --out ../ft/sharegpt
python3 convert_formats.py --corpus . --format hermes   --out ../ft/hermes
python3 convert_formats.py --corpus . --format text     --out ../ft/text
python3 convert_formats.py --corpus . --format sharegpt --out ../ft/sharegpt --check
```

It writes a new tree and never the corpus. `MANIFEST.json` records the source sha256, the output sha256 and a logical digest per episode; `--check` re-derives every episode from the corpus and exits non-zero if one message, call id or result moved. The rendered `text` format cannot carry a tool result's id, and the manifest states that instead of pretending otherwise.

The samples already ship parallel calls as one assistant turn with several calls, so `convert_formats.py`'s own merge pass is a no-op on them; it exists for a corpus produced by an older exporter, and `--no-merge-parallel` turns it off. Nothing is dropped either way: every call keeps its id, name and arguments.

---

## Repo Layout

```
retag_tools.py                 rename the tool vocabulary (no deps)
convert_formats.py             export to openai / sharegpt / hermes / text
merge_parallel_calls.py        merge split parallel calls (no deps)
check_shape.py                 check the merged tool-call shape (no deps)
verify.py                      offline integrity check
TOOLS.md                       guide to the three repair tools
episodes/
  tools.json                   the tool contract for the whole corpus
  index.json                   one row per episode
  failures.jsonl               malformed calls excluded from samples, with pointers
  <task_id>/                   one episode
DATA_CARD.md                   composition, limits, changelog
LICENSE                        MIT
```

### Upstream repositories

- [attrs](https://github.com/python-attrs/attrs) - under MIT
- [cli](https://github.com/httpie/cli) - under BSD-3-Clause
- [click](https://github.com/pallets/click) - under BSD-2-Clause / BSD-3-Clause
- [packaging](https://github.com/pypa/packaging) - under Apache-2.0
- [tenacity](https://github.com/jd/tenacity) - under Apache-2.0

---

## What We Need

- **Pretrain on it and report the number.** Even one instrument, even if it got worse.
- **Point the engine at another language.** Python is what is published; the engine handles JS, TS, Go and Rust.
- **Break it.** Open an issue with the episode id. The defects consumers reported in November 2026 are fixed and listed in the changelog; there are more.

---

## License

MIT. See [LICENSE](LICENSE).

Upstream source code in the corpus keeps its original license: Apache-2.0, MIT, BSD-3-Clause and BSD-2-Clause. Upstream notices travel with the data.

Built by Sumama Jameel. Contact: sumamajamil2005@gmail.com
