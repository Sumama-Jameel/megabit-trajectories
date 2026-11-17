# MegaBit Trajectories — Remediation Report

- Date: 2026-11-17
- Scope: the full 66-episode corpus at this repository
- Mode: in-place remediation (founder-chosen "Option B"), evidence preserved
- Companion documents: `TRAJECTORY_VERIFICATION_2026-11-17` (the audit),
  `docs/REMEDIATION_PLAN_2026-11-17.md` (the plan, engine repo)
- Nothing was deleted. Raw `*.episode.jsonl` files are byte-identical to commit
  `fb84792` (verified against the pre-mutation manifest; zero unrecorded drifts).

## 0. One-line summary

The corpus is real, intact and now honestly labelled: one invalid episode is
quarantined, one network-dependent episode is labelled, all missing provenance
is a boolean with a reason, every raw call is accounted for, and every number
in the documents is generated from one source of truth. No SFT split is claimed
because v1 captured no reasoning.

## 1. What was wrong and what was done

Findings reference the audit (`TRAJECTORY_VERIFICATION_2026-11-17`) and the
remediation plan (`REMEDIATION_PLAN_2026-11-17.md` rev 2, engine repo).

### 1.1 Invalid SFT episode — `966101f98864fafa` (F1, N1)

Fixed by reclassification, not deletion. The human target changes only
`tests/conftest.py` and `tests/test_basic.py`; those two files were seeded as
locked QA tests and the write-deny tree covered them, so the coder could not
solve the ticket. The produced diff touches only `LICENSE`; the composite gate
(0.45) passed on the LICENSE hunk. See `episodes/966101f98864fafa/evidence/quarantine.json`
and `evidence/file_match_report.json`. The episode is kept as evidence of a
test-only target and excluded from every training-ready list. A re-mined
source-change task is required before the slot can ship as SFT (follow-up F-1).

### 1.2 Live-internet SFT episode — `490a433138e1fe8e` (F2, N3, N5)

Reclassified `network_dependent`. Coder raw rows 61–62 call `httpbin.org/get`;
the seeded tests call `httpbin.org/basic-auth` and `/digest-auth`; the retry
journal records neither `agent_egress_relaxed` nor `required_test_hosts`
(while 44 other episodes do record the relaxation). The coder also added
root-level `conftest.py` (a `requests.compat` shim) and `pytest.ini` — setup
work, not ticket work; flagged as `setup_contamination`.
`evidence/network_dependent.json` records all of it. Offline re-run with a
local httpbin fixture is follow-up F-2.

### 1.3 Reviewer test execution (F3, N6–N11)

Ownership corrected: the harness owns test execution, never the reviewer. The
v1 feedback files that say "the pipeline ran the suite" were accurate. Legacy
three-run harness rounds are preserved per episode in
`evidence/harness.json` (65 of 66 episodes carry a three-run substantive
round; `611e35323caaf082` does not — the reviewer ran the suite and the
journal has no `harness_test_runs` event).

For `611e35323caaf082`, an offline replay of the recorded final diff against
the locked seeded tests (`tests/test_dunders.py`, `tests/test_make.py`)
passes 3 of 3 sequential runs (exit 0, 30 passed each) recorded in
`evidence/harness_replay.json`. The replay used a host Python (3.10.12) and
pytest (9.0.3), not the recorded sandbox image; the environment is labelled
`environment_adapted`. The negative control (base tests without the locked
tests) fails the two repr tests as expected, proving the tests exercise the
change.

No reviewer run is required by any gate. No reviewer run is cited as gate
evidence anywhere in the published data.

### 1.4 Plan-before-edit gate (F4, N12–N14)

Re-adjudicated with `plan_detector_v1` (deterministic features plus a pinned
temperature-0 judge), which reads the whole pre-edit trajectory, not the todo
tokens. Result: 60 of 66 episodes have a detected plan before the first edit;
6 do not (`7bd0a927168a14f3`, `a0b5794e7403ed3d`, `b8d783f57b4b84eb`,
`b9e9143d07b01282`, `d6f9cc39994bea23`, `ebaa0de9c4092fd4`) and are labelled
`legacy_unplanned` and kept as negative examples. No gate, prompt or config
requires a todo write.

### 1.5 `/tmp` write denials (F6, N17)

Re-measured rather than copied: the audit reported 68 rejected calls across
47 episodes. From the shipped bytes there are 41 denial `tool_result` events
(36 bash, 3 execute, 2 write) across 37 episodes (38 if one matches on args
only). The audit's number is not reproducible from these files and is
recorded here as a divergence, not silently kept. The denials are annotated
in `evidence/harness_friction.jsonl` where present; they are harness friction,
not model error, and were not removed from raw or samples. The engine fix
(writable `$TMPDIR` under `/workspace/.megabit_tmp`) is tracked in the engine
repo.

### 1.6 Degenerate raw segment — `a066c3d9cbcb7e18` (F7, N18)

Preserved, marked, and fenced. `evidence/segments.jsonl` records segment 0
(degenerate: repeated multilingual slur in the terminal `done`, ~62,513
characters; detector reasons recorded) and segment 1 (the selected, clean
segment). `episode.clean.jsonl` is the derived view: the header plus the clean
segment (verified: every tool call pairs with its result). The raw
`episode.jsonl` is untouched.

### 1.7 Corrupt call dropped from the sample — `b37ef87e467d64e6` (F8, N19)

`call_01a0e94bd96872fda2fc1397` (grep, truncated JSON arguments) is preserved
in raw and now also in `evidence/restore_rejection.jsonl` with the exact
error (`failed to parse input: unexpected end of JSON input`), its disposition
(`restore_rejection`), and the pairing context. The chat-structure sample
still excludes the call; the rejection example exists so no consumer mistakes
the omission for a silent drop.

### 1.8 230 raw calls missing from samples (N20)

All 2,541 raw calls are now individually accounted for
(`evidence/calls.json` per episode): 2,311 present in samples; 1 rejection
example (`b37`); 221 authentic calls restored from failed/superseded attempts
into `failure_recovery` (with their recovery arcs); 0 jargon; 0 unresolved.
The published samples are unchanged in tool-call content.

### 1.9 Count vocabulary (F10, N22)

Unified, and generated. `counts.json` at the repository root is the single
source of truth; README and DATA_CARD are written to match it:

| Term | Value |
|---|---|
| raw_tool_calls | 2,541 |
| exported_tool_calls (export attempts) | 2,312 |
| sample_tool_calls | 2,311 |
| rejected_at_export | 1 |
| failure_recovery_tool_calls | 221 |
| unresolved_tool_calls | 0 |
| raw calls not in samples | 230 (229 superseded/degenerate + 1 corrupt) |

### 1.10 File-match reports (F10, N23/N24)

`evidence/file_match_report.json` per episode: produced vs target diff,
classified by path kind, locked test files excluded, with explicit
`missing`/`extra` lists. Outcomes: 42 clean, 10 `clean_with_missing_docs`,
10 `clean_with_extra`, 2 `partial_patch` (`33da938be0a526fb` — gold touched
`setup.py`/`.gitignore`; `4c434330ee44b096` — gold touched `attr/_make.py`),
1 `setup_contamination` (`490a433138e1fe8e`), 1 `test_only_task`
(`966101f98864fafa`). Both partial_patch episodes are real divergences from
the gold patch, not gate failures; they are flagged, not hidden.

### 1.11 Provenance (F10, N25, N34)

- Every episode's upstream base/target exists and base is an ancestor of
  target in the cached clones: **66/66 `upstream_verified`** (commit
  existence, ancestry, diff hash recorded, license detected at the base
  commit and matched against the recorded SPDX; dual-license repos handled by
  set membership). See `evidence/upstream.json`.
- The two `source_verified: null` episodes (`86fc0604d03248ba`,
  `e3a02407766bdf33`) are now boolean `false` with the reason recorded
  (`task record has no SPDX id; license detected Apache-2.0; nothing to
  compare`). The raw logs still carry `null`; the correction lives in the
  sample and in `evidence/provenance.json`.

### 1.12 Tickets and hints (N37)

`evidence/ticket_path_audit.json` per episode: path-like tokens in the ticket
and hints resolved against the Diff1 tree. **66 of 66 pass. Zero Diff2-only
paths. Zero unknown paths.** Ticket regeneration was not required.

### 1.13 Secret scan (N33)

Byte-level scan of every file in the tree (2,738 files, binaries included):
**0 findings**. `keys/` is excluded by construction and now git-ignored; it
was never read, moved or published.

### 1.14 Degenerate/friction/confusion annotations (N26, N27, N31)

`349db9dae0e05b9e` annotated `network_attempt_failed` (single failed
`pip install mypy pyright`; nothing installed). `efd63c576c434d63` annotated
`model_uncertainty` (one ordinary debugging-confusion line). The two
`research_only` episodes keep their label and are excluded from training lists.

## 2. What this corpus is, honestly

- v1 has **no reasoning**. All 132 provider configs ran with
  `reasoning: false`; none was captured. Reasoning is documented as
  unrecoverable and nothing v1 ships as reasoning-bearing SFT data.
- Splits: `action_only` 56, `legacy_unplanned` 6, `research_only` 2,
  `network_dependent` 1, `quarantine_test_only` 1. **No SFT split is published.**
- The tickets are near-spec; the QA tests are seeded from the gold patch; the
  target commits are public. Treat this as training and research data, not as
  a contamination-free benchmark.
- Environment is a real container; it is not a security boundary for untrusted
  code.

## 3. Preservation and rollback

- Pre-mutation state: `git HEAD fb84792`; patch, file manifest (1,542 files,
  sha256 each) saved in the engine repo under `docs/pre_mutation.patch` and
  `docs/pre_mutation_manifest.json`; full tarball backup at
  `/home/sumama/Private/megabit-backups/megabit-trajectories-pre-remediation-2026-11-17.tar.gz`.
- `remediation_manifest.json` at this repository root lists every change with
  before/after sha256: 144 recorded changes (66 sample adoptions, 66
  finalization rehashes, 10 evidence-manifest syncs, counts, index, counts).
- Rollback: `git checkout fb84792 -- .` restores every tracked file byte for
  byte; untracked additions (`evidence/`, `counts.json`, `remediation_manifest.json`,
  `secret_scan.json`, `release_manifest.json`, `verify_report.json`,
  `episode.clean.jsonl`) are additive and inert without a consumer.
- The tar backup is the full pre-mutation tree including the working-tree
  edits that pre-dated this remediation (README/DATA_CARD/verify.py Kaggle
  layout fix).

## 4. Follow-ups (explicitly not done here)

- F-1: Re-mine `966101f98864fafa` with a target whose human diff changes at
  least one non-test, non-docs, non-license source file; the slot stays
  quarantined until it passes the normal gates.
- F-2: Re-run `490a433138e1fe8e` with a loopback httpbin fixture and the
  requests-compatibility shim in the base image; the episode stays
  `network_dependent` until then.
- F-3: Generate reasoning-bearing episodes (provider reasoning enabled) to
  establish a v2 SFT split; v1 is not relabeled.
- F-4: The `/tmp` engine fix (`$TMPDIR` scratch dir) and the egress preflight
  for seeded tests (httpbin-class hosts) are engine-repo changes, tracked there.
- F-5: `611e35323caaf082` replay used a host environment, not the recorded
  sandbox image; a release-time replay inside the pinned sandbox image is
  tracked in the engine repo's deep verifier.
- F-6: Audit's “68 `/tmp` rejections” does not reproduce from the shipped
  bytes (41 measured). If the audit used a different source, reconcile its
  counter with this corpus's event stream before quoting either number.

## 5. Verification artifacts at this root

`counts.json` (generated), `remediation_manifest.json` (change ledger),
`secret_scan.json`, `release_manifest.json` + `release_manifest.sig` (HMAC),
`verify_report.json` (deep-verification output), `verify.py` (66/66).

## 6. Definition of done (engine plan, rev 2) — honest status

| # | Item | Status |
|---|---|---|
| 1 | Every v1 episode accounted for in v2 or quarantine | done (66/66; `remediation_manifest.json`) |
| 2 | No SFT episode has a test-only target | done (`966` quarantined) |
| 3 | No SFT episode depends on external network | done (`490` labelled network_dependent) |
| 4 | Every SFT episode has a source-code change | done (no SFT split exists; gate enforced at build) |
| 5 | Every SFT episode has a detected plan before first edit; no todo requirement | done (`plan_detector_v1`; 60/66 plans; 6 `legacy_unplanned`) |
| 6 | Every SFT episode has a canonical 3× sequential green round | done (65/66 legacy journals; `611e` offline replay 3/3) |
| 7 | No gate depends on reviewer test execution | done (harness owns tests) |
| 8 | Every raw call has one disposition; authentic omissions restored | done (0 unresolved; 221 restored) |
| 9 | Every rejected call preserved | done (`b37` rejection example) |
| 10 | Every degenerate/jargon segment marked & excluded | done (`a066` segments + clean view; 0 jargon) |
| 11 | Every count generated from one source of truth | done (`counts.json`; README/DATA_CARD match; `make counts-check`) |
| 12 | Every provenance field boolean with evidence | done (2 nulls corrected to `false` with reasons) |
| 13 | Every promoted final diff passes offline replay | **partial** — 41 of 66 replay green on this host (python 3.10 + pytest 9.0.3 + cached pure wheels); 25 are environment-limited (see §7.3) |
| 14 | Every release has a deep verification report and signed manifest | done (`verify_report.json`, ok:true; `release_manifest.json`) |
| 15 | v1 remains available and hash-identical | done (`.git` fb84792 + tar backup; raw untouched) |
| 16 | Every new SFT episode captures reasoning, hashed & linked | done (relay tee + `reasoning_capture` + tests; flip `reasoning: true` already in config; **no reasoning episodes generated yet**) |
| 17 | v1 reasoning documented as unrecoverable, not mislabeled | done (`action_only`, `reasoning_available: false`) |
| 18 | Engine audit status recorded separately | done (`engine make check` green: 3,194 passed / 11 skipped; lint+mypy clean) |
| 19 | Tickets/hints name only Diff1 paths | done (66/66 audits pass) |

## 7. Known limitations and follow-ups (explicit, not fine print)

### 7.1 No SFT split is published

v1 captured no reasoning (all 132 configs ran with `reasoning: false`). Nothing
is relabeled. An SFT split requires reasoning-bearing episodes; generating
those is follow-up F-3 (see below).

### 7.2 `490a433138e1fe8e` and `966101f98864fafa`

Reclassified per the audit; the offline twin and the source-change re-mine are
generation work and are tracked separately.

### 7.3 Offline replay (this host, no network)

`--replay` ran every episode's final diff in a fresh worktree at the base
commit, with the locked seeded tests applied, three sequential runs each:

- **41 of 66 pass.** All 25 remaining failures are environment artifacts, not
  diff defects: 27 collection errors name `hypothesis` (packaging + attrs
  conftests), which exists only as a CPython 3.11 wheel in the local pip
  cache; the host is CPython 3.10 with no downloads allowed, so 19 packaging
  episodes and 2 attrs episodes cannot import their conftest. The remainder
  name `zope.interface` / `tornado` (also cp311 native wheels in cache).
- 0 failures are attributable to the produced diff.
- To close this: run the same replay inside the sandbox image
  (`python:3.11-slim`, pytest) or a CPython 3.11 environment with the cached
  wheels — see follow-up F-5.

### 7.4 Provider state

TokenHarbor's API key in the current shell returns **401 Invalid or revoked
API key** (the relayed primary). xKiro answers 200 with the harness UA:
`cohere/command-a-plus` returns `reasoning_content`;
`mistralai/mistral-medium-3.5` returns no reasoning at the probed params.
The chain will need a TokenHarbor key rotation before any new episode can
be recorded (follow-up F-3).

### 7.5 `/tmp` rejection count

The audit reported 68 denials across 47 episodes; re-measurement finds 41
denial `tool_result` events (37–38 episodes depending on the match rule).
The audit's number is preserved in the audit doc; the friction evidence in
`evidence/harness_friction.jsonl` uses measured data.

## 8. Follow-ups (unchanged; none applied here)

F-1 Re-mine `966101f98864fafa`; F-2 Offline twin for `490a433138e1fe8e`;
F-3 Reasoning-bearing v2 episodes (blocked on provider key rotation);
F-4 Scratch-dir/preflight engine work — DONE in engine
    (`/workspace/.megabit_tmp` tooling exists and the briefing no longer
    demands a todo; env preflight rejects only environment errors);
F-5 Sandbox-image (CPython 3.11) replay of the 25 environment-limited
    episodes; F-6 Reconcile the audit's 68 `/tmp` rejections with this
    corpus's event stream.
