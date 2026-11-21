# MegaBit Trajectories — Data Card

Last updated: 2026-11-20
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
    reasoning. v1 disabled reasoning in all 132 provider configs. Fingerprints
    are preserved; the label is honest about what the record contains.
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

## Intended use

- Continued pretraining of coding agents and coding assistants.
- Failure and recovery research: malformed tool calls, rejected commands, retries.
- Agent harness evaluation and debugging.
- Research on process data, review loops, and test-driven iteration.

This is pretraining data: the record is the whole transcript, in order, with no
per-turn labels or preferences attached. It is not an instruction-tuning set.

Thinking was not captured at this version of datasets. You have to clean and reformat this data properly to finetune, THEN IT WILL BECOME A PROPER FINE TUNE DATASET. ELSE ITS FOR PRE TRAINING.

Not intended as: a leaderboard benchmark, a claim of state-of-the-art scale, or a
replacement for SWE-bench-style evaluation.

## Contact

Sumama Jameel — MegaBit
GitHub: https://github.com/Sumama-Jameel
Email: sumamajamil2005@gmail.com
