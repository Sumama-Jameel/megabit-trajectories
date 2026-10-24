# MegaBit Trajectories — Data Card

Last updated: 2026-10-24
Corpus: 59 episodes (v1)
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
| Episodes | 59 |
| Repositories | packaging (21), click (20), attrs (17), cli (1) |
| Languages | Python |
| Tool calls (all attempts) | 2,342 |
| Tool calls (shipped segments) | 2,113 |
| Median tool calls per episode | 30 (range 11–100) |
| Tests passing at end | 59 / 59 |
| Review rounds | 1 round: 57 episodes; 3 rounds: 2 episodes |
| Attempts | 1: 54 episodes; 2: 3; 3: 2 |
| Terminal state | final_answer: 57; iteration_cap: 2 (flagged) |
| Composite similarity | 39 episodes recorded, range 0.4815–1.000, median 0.6602 |
| Line similarity | 59 episodes, range 0.3107–1.000, median 0.5732 |
| Total size | ~57 MB |
| Models used | stealth/space-bunny-alpha (33), deepseek-v4.1-flash:free (26) |

### Similarity, stated precisely

The pass gate is **composite similarity ≥ 0.45**, not line similarity. Composite
similarity is a weighted score over file overlap, line similarity, token similarity,
and hunk containment. Line similarity is a stricter sub-score and can fall below
0.45 even when the composite passes. 20 older episodes predate the composite field
and carry line similarity only. Do not read the corpus as "every line matches the
human patch."

### Licenses of upstream repositories

| License | Episodes |
|---|---|
| Apache-2.0 | 21 |
| MIT | 17 |
| BSD-3-Clause | 16 |
| BSD-2-Clause | 5 |

Each episode's `provenance.license_spdx` records the license detected at the base
commit. Upstream repositories retain their original licenses and copyright. If you
redistribute derived data, keep the upstream notices.

## Files

```
episodes/<task_id>/
  <task_id>.episode.jsonl    raw log: header, every event, footer
  <task_id>.sample.jsonl     training format: messages[] + provenance + verification
  ticket.md                  the ticket the agent received
  briefing.md                the briefing the agent received
  hints.md                   file-path hints only
  feedback/round_N.md        reviewer reports
  logs/                      coder, reviewer, ticket agent, retry journal
  config.snapshot.json       run config, secrets redacted
  setup_state.json           setup-step record
  finalization.json          export verdict + sha256 of both JSONL files
```

`sample.jsonl` carries `provenance` (repo, commits, license, model, session,
task fingerprint, HMAC validity, source verification) and `metadata` (tool calls,
attempts, tests, similarity breakdown, terminal state).

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

## Intended use

- Supervised fine-tuning of coding agents and coding assistants.
- Failure and recovery research: malformed tool calls, rejected commands, retries.
- Agent harness evaluation and debugging.
- Research on process data, review loops, and test-driven iteration.

Not intended as: a leaderboard benchmark, a claim of state-of-the-art scale, or a
replacement for SWE-bench-style evaluation.

## Known limits

- Python only in v1. No Rust, Go, C/C++, or kernel-scale data yet.
- Four repositories. Narrow domain coverage.
- Two episodes ended at the iteration cap; they are flagged in metadata even though
  the test suite passed.
- 20 episodes lack composite similarity; line similarity is reported instead.
- Model quality varies. The corpus records what happened, including weak attempts.
- The sandbox is a real container, but it is not a security boundary for untrusted
  code.

## Contact

Sumama Jameel — MegaBit
GitHub: https://github.com/Sumama-Jameel
Email: sumamajamil2005@gmail.com
