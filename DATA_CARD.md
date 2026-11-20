# MegaBit Trajectories — Data Card

Last updated: 2026-11-19
Corpus: 66 episodes (samples rebuilt 2026-11-12; remediated in place 2026-11-17; raw episode files unchanged)
Generator: MegaBit (private factory)
License of this packaging: MIT. Upstream source code remains under its original license.

## What this is

Real coding sessions recorded step by step. An AI agent gets a ticket, explores a
real repository, edits files, runs commands, reads the errors, retries, and ships a
patch. Every tool call executes in a real sandbox. Nothing is simulated.

Each episode preserves the failure path, not only the final answer: malformed
commands, failed tests, rejected tool calls, retries, and the recovery that follows.
That is the part most public trajectory corpora drop.

## Composition

| Item | Value |
|---|---|
| Episodes | 66 |
| Repositories | packaging (21), click (20), attrs (18), tenacity (6), cli (1) |
| Languages | Python |
| Tool calls (raw log events) | 2,541 |
| Tool-call attempts at export | 2,312 |
| Rejected at export (preserved) | 1 |
| Tool-call records in published samples | 2,311 |
| Authentic calls restored from failed attempts | 221 (`failure_recovery`) |
| Median tool calls per episode | 29 (range 11–100) |
| Tests passing at end | 66 / 66 |
| Review rounds | 1 round: 64 episodes; 3 rounds: 2 |
| Attempts | 1: 61; 2: 3; 3: 2 |
| Terminal state | final_answer: 64; iteration_cap: 2 |
| Plan detected before first edit | 60 of 66 (plan_detector_v1); 6 `legacy_unplanned` |
| Composite similarity | present on 66; median 0.6593, range 0.4517–1.0000 (see the note below) |
| Line similarity | 66 episodes, range 0.3107–1.0000, median 0.5723 |
| Splits | action_only: 56, legacy_unplanned: 6, network_dependent: 1, quarantine_test_only: 1, research_only: 2 |
| Trainable SFT episodes | 0 (see “Splits and transcript flags”) |
| /tmp write denials (raw / sample) | 39 events in 36 episodes / 35 events in 35 episodes |
| v2 diff score | not recomputable: target diffs are not published; every manifest records `v1_not_recomputed` |
| Transcripts ending on an answer | 64 (`ends_with_final_answer`); 2 end on a tool result |
| Tool output truncated in samples | 138 messages, cap 8,000 chars (see policy below) |
| Total size | ~63 MB |
| Models used | stealth/space-bunny-alpha (33), deepseek-v4.1-flash:free (32), codestral-latest (1) |

### Similarity, stated precisely

The pass gate is **composite similarity ≥ 0.45**, not line similarity. Composite
similarity is a weighted score over file overlap, line similarity, token similarity,
and hunk containment. Line similarity is a stricter sub-score and can fall below
0.45 even when the composite passes. Do not read the corpus as "every line matches
the human patch."

### v2 source-aware score

The 2026-11-19 engine adds `diff_score_v2`: source-file overlap plus the four
existing components, with hard rejection of targets that change only tests,
docs or a license. The published v1 corpus cannot carry that score because it
publishes target diff hashes and file lists, not target diff text. Every
manifest therefore says `version: v1_not_recomputed` and states the reason.
This is a missing input, not a passing score. New episodes record v2.

### Briefing defect in 20 v1 prompts

20 of 66 episodes were run with a prompt that called `git status`, `git diff`
and `git log` useless. The statement was wrong for inspecting the agent's own
work. The archived prompt bytes are unchanged, because they are the record of
what the agent actually saw. Each episode carries
`evidence/briefing_policy.json`; the 20 affected episodes are marked
`false_git_useless`, `sft_eligible: false`, and are excluded from every
trainable list. The current engine template allows `git status` and `git diff`
and a unit test forbids the old sentence from returning.

All 66 episodes carry `composite_similarity` today: in the `verification` block of
each raw footer and in `metadata` of each sample. The median is 0.6593, and every
sample also carries a full `similarity_breakdown`. The 2026-11-12 sample rebuild
filled `metadata.composite_similarity` for episodes whose export predates the field
by copying the gate value already in `metadata.similarity` under its current name.
Nothing about the human fix or the agent's work changed: no verification number was
recomputed.

### Licenses of upstream repositories

| License | Episodes |
|---|---|
| Apache-2.0 | 27 |
| MIT | 18 |
| BSD-3-Clause | 16 |
| BSD-2-Clause | 5 |

Each episode's `provenance.license_spdx` records the license detected at the base
commit. Upstream repositories retain their original licenses and copyright. If you
redistribute derived data, keep the upstream notices.

## Files

Remediation (2026-11-17) added machine-readable evidence per episode under
episodes/<task_id>/evidence/: manifest.json (v2 manifest with hashes, split,
plan, reasoning, harness round, provenance), calls.json (per-call dispositions),
plan.json, reasoning.json, harness.json, review.json, ticket_path_audit.json
(66/66 pass), restore_*.jsonl, file_match_report.json, upstream.json, and any
applicable markers (harness_friction.jsonl, network_attempt_failed.json,
model_uncertainty.json, segments.jsonl for a066c3d9cbcb7e18). a066c3d9cbcb7e18
additionally ships episode.clean.jsonl, a derived view excluding the degenerate
first attempt; raw episode.jsonl is untouched.

```
retag_tools.py               rename the tool vocabulary (no deps)
merge_parallel_calls.py      merge split parallel calls (no deps)
check_shape.py               check the merged tool-call shape (no deps)
TOOLS.md                     guide to the three repair tools
episodes/
  tools.json                 the tool contract for the whole corpus
  index.json                 one row per episode (sim, tool calls, split, ...)
episodes/<task_id>/
  <task_id>.episode.jsonl    raw log: header, every event, footer
  <task_id>.sample.jsonl     training format: messages[] + provenance + verification + tools
  ticket.md                  the ticket the agent received
  briefing.md                the briefing the agent received
  hints.md                   file-path hints only
  .coder.appendix.md         coder role prompt (tools, rules)
  .coder.config.json         coder role config
  .ticket_gen.appendix.md    ticket-agent role prompt
  .ticket_gen.config.json    ticket-agent role config
  feedback/round_N.md        reviewer reports (+ round_N.json raw report)
  logs/                      coder, reviewer, ticket agent, retry journal,
                             setup log and setup steps
  logs/test_seed.patch       the QA tests seeded into the workspace
  config.snapshot.json       run config, secrets redacted
  setup_state.json           setup-step record
  finalization.json          export verdict + sha256 of both JSONL files
```

`sample.jsonl` carries `provenance` (repo, commits, license, model, session,
task fingerprint, HMAC validity, source verification) and `metadata` (tool calls,
attempts, tests, similarity breakdown, terminal state).

## Tool contract

Every sample is self-describing. It carries a `tools` array in OpenAI
function-calling shape (name, description, JSON-Schema parameters), and the whole
corpus ships one copy at `episodes/tools.json`.

Canonical names: `read`, `glob`, `grep`, `edit`, `write`, `bash`, `todo_write`,
`todoread`. The harness registers some tools twice, so the samples are
canonicalized and the alternate spellings are listed in
`metadata.tool_name_aliases`:

| Raw spelling | Canonical |
|---|---|
| `execute`, `shell`, `background` | `bash` |
| `todowrite` | `todo_write` |
| `edit_file`, `multi_edit` | `edit` |
| `write_file` | `write` |

The raw `episode.jsonl` keeps exactly what the model emitted.

If your harness uses different names, you do not need to post-process the files by
hand. This repository ships `retag_tools.py`, a no-dependency script that rewrites
every name field, the tool catalog and the digests in one command, and refuses
ambiguous mappings:

```bash
python3 retag_tools.py --corpus . --map bash=shell,read=view --out ../corpus-shell
python3 retag_tools.py --corpus ../corpus-shell --check --map bash=shell,read=view
```

Map it there and back and the samples are byte-identical. `--scope all` also renames
the raw episode's tool-event names (this changes `raw_sha256`); it is off by default
because the raw log is the record of what the model actually emitted.

### Tool output policy

Sample-side tool results keep at most **8,000 characters** (head 6,000 / tail
2,000) on line boundaries, plus one marker line, so the largest truncated message
is 8,124 characters. A cut message carries `truncated: true`, `original_chars`
and `dropped_chars`, and `metadata.tool_output_policy` records the rule. 138
messages are capped in this corpus. The raw `episode.jsonl` keeps every character
the tool actually emitted, so the full output is never lost.

### Splits and transcript flags

- `metadata.split` is one of:
  - `action_only` (56) — real action/observation data with no captured
    reasoning. v1 disabled reasoning in all 132 provider configs, so nothing
    v1 ships as reasoning-bearing SFT data. Fingerprints are preserved; the
    label is honest about what the record contains.
  - `research_only` (2) — the iteration-cap episodes, kept for failure research.
  - `legacy_unplanned` (6) — no plan detected before the first edit by
    `plan_detector_v1` (`7bd0a927168a14f3`, `a0b5794e7403ed3d`,
    `b8d783f57b4b84eb`, `b9e9143d07b01282`, `d6f9cc39994bea23`,
    `ebaa0de9c4092fd4`). Kept as negative examples; not plan-compliant SFT data.
  - `network_dependent` (1) — `490a433138e1fe8e` (live httpbin.org in coder and
    seeded tests; no egress-relaxation record; includes root-level coder
    `conftest.py`/`pytest.ini`). Not offline-reproducible research data.
  - `quarantine_test_only` (1) — `966101f98864fafa` (human fix is test-only;
    seeded tests were locked; produced diff touches LICENSE only; the old
    composite gate passed on the LICENSE hunk). Kept as evidence; excluded from
    every training-ready list.
- No split is presented as reasoning-bearing SFT. An SFT split requires episodes
  recorded with reasoning enabled, a plan before the first edit, and a canonical
  harness round of three sequential green runs.
- `metadata.ends_with_final_answer` says whether the transcript closes on an
  assistant answer. 64 do; the 2 iteration-cap episodes end on a tool result.
- `metadata.terminal_state` records how the session ended.
- `metadata.messages_normalization` records whether a duplicated terminal
  narration turn was dropped while building the sample.

## Provenance and integrity

- Every mined task is stamped with an HMAC. `provenance.task_mac_valid` records it.
- `provenance.source_verified` re-checks commits and license when the repo cache is
  present.
- `finalization.json` records sha256 for the episode and sample files.
- `verify.py` in this repository re-checks the sha256 values, header/footer presence,
  tool-call counts, and the export verdict. It does not re-run the sandbox.

```bash
python3 verify.py
```

## What is withheld

The gold patch is not shipped as a file. However, `provenance.target_commit` is a
public upstream commit, so the human fix is derivable from the public repository.
Treat this corpus as **training and research data, not as a contamination-free
benchmark**. For contamination-free evaluation, generate on private or post-cutoff
repositories.

The agent's own work is not withheld: `produced_diff` is in the episode footer and
the final patch is in the sample messages.

The seeded QA tests are shipped as `logs/test_seed.patch`. It touches test files only
(40 distinct test targets, no source files), so it states the expected behaviour
without giving away the implementation. That is deliberate: the tests are what the
agent had to satisfy.

## How guided these tasks are

Read this before quoting a pass rate. The tickets are close to a specification,
not a bug report from a stranger:

- every ticket (66/66) names at least one `.py` file to look at;
- every episode ships a `hints.md` whose lines are file paths into the repository;
- the ticket prose states the required behaviour precisely (for example "show a
  question mark where the seconds normally go"), not a vague symptom;
- the QA tests are seeded from the gold patch in all 66 episodes, so the agent is
  told what "done" looks like.

The median recorded change is 22 added / 5 removed lines over 2 files. These are
small, well-scoped edits with the target files handed over.

That makes the corpus strong **format, planning and recovery** data: it shows a real agent
reading a repo, calling tools, running tests, hitting errors and correcting them.
It is weak **debugging-under-uncertainty** data: it does not measure how an agent
finds a bug from a vague report with no file names, and a 66/66 pass rate here is
not open-ended agent performance. Use it for the process it records, not as a
benchmark of autonomous debugging.

## Intended use

- Continued pretraining of coding agents and coding assistants.
- Failure and recovery research: malformed tool calls, rejected commands, retries.
- Agent harness evaluation and debugging.
- Research on process data, review loops, and test-driven iteration.

This is pretraining data: the record is the whole transcript, in order, with no
per-turn labels or preferences attached. It is not an instruction-tuning set.

Not intended as: a leaderboard benchmark, a claim of state-of-the-art scale, or a
replacement for SWE-bench-style evaluation.

## Known limits

- v1 captured no reasoning. All 132 coder and ticket configs have `"reasoning": false`.
- One episode (`490a433138e1fe8e`) depends on a live external host; one (`966101f98864fafa`)
  has a test-only human target; six have no detected plan before the first edit. All eight
  are labelled or quarantined rather than hidden.
- 966 is kept as useful failure-mode data: 51 real tool calls, a real recovery arc and a
  correct refusal. Its target had no source change, so it is not a coding lesson and stays
  out of every training-ready list (1 of 66).
- 490's two auth tests were re-run in a reconstructed environment with network access on,
  using the recorded requests 2.34.2, the coder's `conftest.py` and `pytest.ini`, and three
  sequential passes. No original image digest was recorded, so the result is labeled
  reconstructed, not canonical (`evidence/network_replay.json`).
- `611e35323caaf082` recorded no three-run harness round in its export journal (the reviewer
  executed the suite). An offline replay of its final diff passes 3/3 against the locked
  seeded tests (evidence/harness_replay.json). All 66 episodes now carry
  `evidence/harness_v2.json` with complete per-run fields from a reconstructed host replay.
  Docker was unavailable, so every one is labeled `environment_match: reconstructed` and
  `canonical: false`; 31 replays are green and 35 are not green in this environment.
- The 68 `/tmp`-denial rejections previously reported were re-measured with one matcher:
  39 raw denial events across 36 episodes and 35 in samples across 35 episodes. `counts.json`
  is the single source of truth; the old 41/38 figure came from a broader source and does not
  reproduce from this corpus's bytes. Annotated as harness friction, not model error.
- Python only in v1. No Rust, Go, C/C++, or kernel-scale data yet.
- Five repositories. Narrow domain coverage.
- Two episodes ended at the iteration cap; they are flagged in metadata even though
  the test suite passed.
- 20 episodes predate the composite field; their `composite_similarity` was
  filled from `similarity` during the 2026-11-12 sample rebuild (same metric,
  current name). No verification number was recomputed.
- The tickets are near-spec rather than bug-report-shaped (see "How guided these
  tasks are"). Do not read the pass rate as open-ended debugging performance.
- Model quality varies. The corpus records what happened, including weak attempts.
- The sandbox is a real container, but it is not a security boundary for untrusted
  code.

## Changes

### 2026-11-13 — similarity paragraph corrected

The old paragraph quoted 20 episodes predating the field, 46 recorded at export and
a 0.6552 median. None of those is reproducible from the shipped records: all 66 raw
footers and all 66 samples carry `composite_similarity`, median 0.6593, and every
sample also carries `similarity_breakdown`. The paragraph now states the measured
facts. No data file changed.

### 2026-11-13 — host paths in operational records

Operational records used to carry the absolute path of the machine that built
the corpus: `setup_state.json`, `logs/setup.log`, `logs/setup_steps.ndjson`,
`logs/retry_journal.jsonl`, `finalization.json`, `feedback/round_N.json`,
`config.snapshot.json` and a few `logs/*.json`. Those strings are now
placeholders: `<MEGABIT_DATA>` for the data root, `<MEGABIT_REPO>` for the
engine checkout, `<HOME>` for the build user's home and `<SANDBOX_HOME>` for
the sandbox account's home. 477 files changed, 936 occurrences. No field was
added or removed, and no verdict, count or similarity value changed.

The raw `*.episode.jsonl` and `*.sample.jsonl` files were not touched: their
bytes and their sha256 values are identical to 2026-11-12, and `verify.py`still reports 66/66. Six of those files (three episodes' raw log and sample)
still contain the sandbox account's home path inside recorded tool output.
That is the evidence of what the sandbox printed and it is digest-bound, so
it stays verbatim rather than being rewritten.

### 2026-11-12 — positioning and docs

The corpus is documented as continued-pretraining data, not a fine-tuning set, and
the four capability claims are coding, planning, tool calls and recovery from
failures. No data changed in this edit; the raw logs and samples keep their
sha256 values.

### 2026-11-12 — sample rebuild (raw episodes untouched)

A consumer reported five defects in the exported samples. All five are fixed in
the exporter and repaired in the corpus. The raw `*.episode.jsonl` files are
byte-identical before and after; only `*.sample.jsonl` and the digests in
`finalization.json` changed, so **every sample sha256 is new**.

1. **Duplicated final turn (55 of 66).** The harness emits its accumulated
   narration buffer as the `done` payload, and the exporter appended it as an
   extra assistant message after the real answer. Removed. `metadata.
   messages_normalization.flattened_done_dropped` records it per episode.
2. **No tool definitions.** Every sample now carries a `tools` array, and the
   corpus ships `episodes/tools.json`. Parameter shapes are guarded against the
   harness by a test that parses its Go source.
3. **Un-normalized tool names.** `execute` (52 calls) and `todowrite` (10 calls)
   are now `bash` and `todo_write`. The alias table is in
   `metadata.tool_name_aliases`.
4. **Unbounded tool output.** Tool results are capped at 8,000 chars with
   head+tail retention, a marker, and `truncated` / `original_chars` /
   `dropped_chars` on the message.
5. **Junk files in `produced_diff`.** Two episodes recorded an agent-written test
   log as part of the change (`pytest_full.log`, `.pytest_stress.log`). Their
   diffs and verdicts are left exactly as published; both are labelled
   `metadata.split = "research_only"` with `split_reason`. The capture path now
   drops run artifacts before a diff is stored, so this cannot recur, and a
   gold-touched file is never dropped.

The corpus's own `verify.py` reports 66/66 after the rebuild. Tool-call totals
are unchanged: 2,541 raw, 2,312 attempts at export, 2,311 records in published samples.

### 2026-11-14 — counts corrected

README said 553 split parallel calls repaired in samples; the published
samples carry 552. README claimed a median sample of about 72k characters and
about 17k tokens; measured on len() of message content it is about 62k
(~15.5k tokens, 4 chars/token), and the largest is about 230k. DATA_CARD said
2,312 export attempts; the published v1 samples carry 2,311
tool-call records (attempts at export here total 2,312; the corrupt call of
b37ef87e467d64e6 is excluded from the sample layer and kept verbatim in
the raw log). The logs/ description promised a provider alerts file; no
episode ships one. episodes/index.json now mirrors the sample metadata
for the attempts value of a066c3d9cbcb7e18 (from 1 to 2; the sample
metadata and its attempt_segments both say 2). No episode.jsonl or
sample.jsonl changed; verify.py reports 66/66.

### 2026-11-16 — counts unified, byte claims corrected

The export/attempts accounting is now stated the same way everywhere: 2,541 raw
tool_call events; 2,312 tool-call attempts at export (includes the corrupt
attempt, kept verbatim in the raw logs and indexed by failures.jsonl);
2,311 tool-call records in the published samples. The GitHub badge now reads
2,312 so the headline matches the export summary everywhere. No episode file
changed; `episodes/index.json`'s `tool_calls_shipped` already sums to 2,312 and
is now consistently described as attempts at export, not records-in-samples.

Measured on `len()` of message content: median sample 62,067 characters
(~15.5k tokens at 4 chars/token), largest 230,301, total corpus content about
4.7M characters (~1.17M tokens). Earlier draft claims of "~72k / ~260k /
~1.5M tokens" were not reproducible from the shipped files and have been
corrected in README and the Kaggle description. No verification number, count,
split or license changed; `verify.py` reports 66/66.

### 2026-11-17 — remediation (audit fixes applied in place)

A read-only audit (`TRAJECTORY_VERIFICATION_2026-11-17`) found file integrity
clean (66/66 digests, zero secret matches in 2,738 byte-scanned files) and the
training story weaker than advertised. Everything was fixed in place with the
raw `*.episode.jsonl` files untouched (SHA-256 verified against the
pre-mutation manifest); every change is listed with before/after hashes in
`remediation_manifest.json`. Headline changes: one quarantine (`quarantine_test_only`),
one `network_dependent`, six `legacy_unplanned`, reasoning marked unrecoverable
(`action_only` instead of `sft`), 221 authentic failed-attempt calls restored as
`failure_recovery`, one corrupt call preserved with its rejection, a degenerate
segment fenced off into a clean view, Diff1-only ticket/hint path firewall
(66/66 pass), full provenance booleans with evidence, and a generated
`counts.json` as the single source of truth. Details: `REMEDIATION_REPORT_2026-11-17.md`.

## Contact

Sumama Jameel — MegaBit
GitHub: https://github.com/Sumama-Jameel
Email: sumamajamil2005@gmail.com
