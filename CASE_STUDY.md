# Proof of work: same corpus, two recipes, opposite behavior

This is the evidence file for one narrow claim: **MegaBit Trajectories carries proof of work for what the dataset says it teaches.** It is not a model launch and it does not claim general model improvement.

The claim the dataset makes is that its transcripts teach the agent loop: act, observe, fail, repair. That claim is testable. It was tested twice, on the same rows, with two recipes. One recipe learned the behavior from zero. The other did not learn it at all.

Both arms are recorded here with weights hashes, recipes, and the instruments that produced each number. Numbers are instrument-specific. Nothing in this file says a model "got better" in general, because one of the two runs got worse in general.

## Setup

Base model: Qwen3-0.6B-Base, continued pretraining (CPT) on the full transcript, in order.

Corpus: the public `megabit-trajectories` release at remediation commit `70e02ab`, 66 sessions, 2,312 tool calls in the training rows, 1,556,286 o200k tokens, 1,909 packed training rows in the recipe dataset.

Both arms trained on that same packed corpus. Only the recipe differs.

| | v6 | v7 (candidate A) |
|---|---|---|
| epochs | 3 | 1 |
| learning rate | 4e-5 | 2e-5 |
| steps completed | 717 / 717 | completed, banked |
| precision | fp32 master + fp16 AMP | adamw_torch, MAX_LEN 6144 |
| seed | 42 | pre-registered rule sha `b55df0df...5989` |
| weights sha256 | `1997b0fa264b3b21457e9236cd238c3639948e3bd9bd05bdb473854ed0bf0759` | `6e42ee04dd233790a39f8cef9a445645c7e53fba90cc86f09ef2aff13d4e7e6b` |

## Results

Both arms scored by the same offline evaluator, on the same instruments, against the same base checkpoint.

| instrument | base | v6 | v7 |
|---|---|---|---|
| recovery /99 | 0 | **87** (emitted 95) | 0 |
| tool call /8 | 0 | **2** | 0 |
| nll_tool | 1.7955 | **0.3611** | 0.3936 |
| nll_notool | 1.5960 | 1.1672 | **0.9159** |
| refusal pooled /36 | 34 | 31 | 31 |
| gsm8k pooled /40 | 21 | 10 | 16 |

Read the top row. Base recovers nothing. v6 recovers 87 of 99. Same rows, same checksums, same evaluator.

Then read the same row for v7. Zero. Not a degraded score, not a crash: zero emitted recovery calls, and zero tool-call markup in the raw output. That was audited as a real model result, not a pipeline bug. The v7 resume had no fatal error, no OOM, no CUDA fault, no tokenizer fault and no parse error, and v6 raw output through the unchanged parser still scored 87/99.

So the corpus can move a 0.6B base model from 0 to 87 on the supervised behavior, and a different recipe on the identical corpus can leave it at 0. That is the finding. The corpus is doing work. The recipe decides whether the work survives into the checkpoint.

## What this proves

- The recovery signal is real and it is learnable from these rows. Base 0 to 87/99 is not a rounding effect.
- The token-level effect is large and matches the behavior: tool-call NLL 1.7955 to 0.3611, a 79.9 percent cut.
- The behavior is recipe-sensitive, and the sensitivity is not subtle. One epoch at half the learning rate produced no tool-call markup at all. A recipe that under-trains the format channel yields a checkpoint that has read the corpus and does not use it.

## What this does not prove

- **Not general improvement.** GSM8K pooled fell 21/40 to 10/40 and refusal pooled fell 34/36 to 31/36. v6 learned recovery and forgot general behavior. v7 kept more general behavior (GSM8K 16/40) and lost the recovery behavior. Neither arm dominates the base model.
- **Not a shippable checkpoint.** The pre-registered shipping floor for tool calls is 4/8. v6 reached 2/8. The floor is a ship gate, not a test of whether the data works. It was not met, so v6 is a NO_SHIP checkpoint.
- **Not a precise rate on tool calls.** The instrument is 8 items. 0 to 2 is a direction. It is not an estimate with meaningful error bars.
- **Not a served-model claim.** Banked recovery 87/99 and served recovery 0/10 on the same v6 weights is a protocol mismatch, documented in `PROJECT_STATE.md`. Both numbers are real; they measure different protocols and must never be quoted together as a range.
- **Not a scale claim.** 66 sessions on one 0.6B base model, 5 repositories, Python only. One base model, two recipes. That is a natural experiment, not a scaling study.

## What it means for the corpus

The dataset's claim is that its transcripts teach act, observe, fail, repair. Twice now, the measurement went the way the claim predicts: the behavior appears when the recipe supervises the format and disappears when it does not. The failure was an engineering outcome in the recipe, and it is written up here as one.

Training is paused. GPU quota after the v7 run was 3.18 hours, and a resume needs a 6 hour window that the free tier does not currently give. The record is complete and banked, so it does not need to be re-run to be read.

## Reproduce

- Corpus integrity: `python3 verify.py` in this repo, 66 of 66. `release_manifest.json` covers 2,351 files and is HMAC signed; it was regenerated in the same commit that added this file, so this file is inside the signature rather than beside it.
- Corpus measurements and version pins: the audit bundle, `COMPARISON.md` and `VERSIONS.md`, published with this case study.
- Training records, recipes, kernels, banks, weights hashes and the v7 postmortem: `SCORECARD_v6.md`, `scorecard_v6.json` and section 18 of `PROJECT_STATE.md` in the MegaBit training repository, available on request.
