# Megabit Trajectories

Real coding sessions recorded step by step. An AI agent explores a codebase,
gets a ticket, fixes the bug, runs tests, gets reviewed — and we capture
every single move.

## What's here

39 episodes: 39 verified passes (tests green and the
agent's diff independently scored against the upstream fix, similarity
≥ 0.45). 1718 tool
calls total. Repositories: attrs, cli, click, packaging.

## How We Made It

1. Cloned each repo at the commit before the fix
2. Gave the agent a ticket describing the bug
3. The agent explored the code, found the problem, wrote a fix
4. A reviewer agent checked the work and asked for changes
5. Agent iterated until all tests passed
6. Every step was recorded — and the run only counts if an independent
   audit re-verifies the episode

## The Hard Part

We used free APIs because we're broke. Free APIs are slow, rate limited,
and sometimes just fail. We built a fallback chain that tries multiple
providers one after another. It took a lot of debugging.

## Episodes

| Episode | Repository | Sim | Tool calls | Review rounds | Tests pass | Time |
|---|---|---|---|---|---|---|
| [`611e35323caaf082`](episodes/611e35323caaf082/) | attrs (MIT) | 1.000 | 61 | 3 | yes | 12 min |
| [`8a4bf108bb03b794`](episodes/8a4bf108bb03b794/) | packaging () | 1.000 | 28 | 1 | yes | 18 min |
| [`b37ef87e467d64e6`](episodes/b37ef87e467d64e6/) | attrs (MIT) | 1.000 | 45 | 1 | yes | 6 min |
| [`d6f9cc39994bea23`](episodes/d6f9cc39994bea23/) | packaging (Apache-2.0) | 1.000 | 35 | 1 | yes | 9 min |
| [`8bb1081352bda3fc`](episodes/8bb1081352bda3fc/) | click (BSD-2-Clause) | 0.938 | 30 | 1 | yes | 5 min |
| [`3a35d6717919075a`](episodes/3a35d6717919075a/) | attrs (MIT) | 0.850 | 33 | 1 | yes | 6 min |
| [`73246683fe7ee6c6`](episodes/73246683fe7ee6c6/) | attrs (MIT) | 0.835 | 24 | 1 | yes | 5 min |
| [`a066c3d9cbcb7e18`](episodes/a066c3d9cbcb7e18/) | attrs (MIT) | 0.780 | 20 | 1 | yes | 8 min |
| [`864a19a5d07ecac7`](episodes/864a19a5d07ecac7/) | click (BSD-3-Clause) | 0.765 | 31 | 1 | yes | 10 min |
| [`afd00fe36c2ad88c`](episodes/afd00fe36c2ad88c/) | click (BSD-2-Clause) | 0.765 | 26 | 1 | yes | 6 min |
| [`979988594a97aafb`](episodes/979988594a97aafb/) | click (BSD-3-Clause) | 0.741 | 27 | 1 | yes | 12 min |
| [`31fc77740af45bd4`](episodes/31fc77740af45bd4/) | attrs (MIT) | 0.735 | 39 | 1 | yes | 23 min |
| [`fe34f71ffe61ad61`](episodes/fe34f71ffe61ad61/) | click (BSD-3-Clause) | 0.731 | 26 | 1 | yes | 8 min |
| [`2f219d6f06d064cc`](episodes/2f219d6f06d064cc/) | attrs (MIT) | 0.726 | 37 | 1 | yes | 18 min |
| [`57b500b3a9ee36b6`](episodes/57b500b3a9ee36b6/) | click (BSD-2-Clause) | 0.725 | 25 | 1 | yes | 8 min |
| [`b9e9143d07b01282`](episodes/b9e9143d07b01282/) | packaging (Apache-2.0) | 0.709 | 17 | 1 | yes | 11 min |
| [`efd63c576c434d63`](episodes/efd63c576c434d63/) | packaging (Apache-2.0) | 0.678 | 57 | 1 | yes | 15 min |
| [`4f8401a368bba994`](episodes/4f8401a368bba994/) | click (BSD-3-Clause) | 0.672 | 123 | 1 | yes | 41 min |
| [`8b48d640ad1f1576`](episodes/8b48d640ad1f1576/) | attrs (MIT) | 0.665 | 46 | 1 | yes | 10 min |
| [`33da938be0a526fb`](episodes/33da938be0a526fb/) | attrs (MIT) | 0.658 | 27 | 1 | yes | 10 min |
| [`fd65634c348f1601`](episodes/fd65634c348f1601/) | click (BSD-3-Clause) | 0.650 | 56 | 1 | yes | 21 min |
| [`012ad533e237baaf`](episodes/012ad533e237baaf/) | packaging () | 0.649 | 26 | 1 | yes | 14 min |
| [`5760e3b4271e5d3e`](episodes/5760e3b4271e5d3e/) | click (BSD-3-Clause) | 0.641 | 50 | 1 | yes | 11 min |
| [`349db9dae0e05b9e`](episodes/349db9dae0e05b9e/) | click (BSD-3-Clause) | 0.637 | 69 | 1 | yes | 22 min |
| [`2b67051b08a2794f`](episodes/2b67051b08a2794f/) | attrs (MIT) | 0.619 | 51 | 1 | yes | 14 min |
| [`2288ac90554bcfa6`](episodes/2288ac90554bcfa6/) | packaging () | 0.615 | 40 | 1 | yes | 25 min |
| [`ebaa0de9c4092fd4`](episodes/ebaa0de9c4092fd4/) | packaging (Apache-2.0) | 0.598 | 12 | 1 | yes | 11 min |
| [`7bd0a927168a14f3`](episodes/7bd0a927168a14f3/) | attrs (MIT) | 0.583 | 16 | 1 | yes | 3 min |
| [`b8d783f57b4b84eb`](episodes/b8d783f57b4b84eb/) | packaging (Apache-2.0) | 0.582 | 27 | 1 | yes | 47 min |
| [`7d2d3557467897b4`](episodes/7d2d3557467897b4/) | click (BSD-3-Clause) | 0.576 | 33 | 1 | yes | 8 min |
| [`81a8b6b065bafe21`](episodes/81a8b6b065bafe21/) | attrs (MIT) | 0.562 | 95 | 1 | yes | 36 min |
| [`490a433138e1fe8e`](episodes/490a433138e1fe8e/) | cli (BSD-3-Clause) | 0.552 | 56 | 1 | yes | 12 min |
| [`f20d68038c27594c`](episodes/f20d68038c27594c/) | click (BSD-3-Clause) | 0.541 | 70 | 1 | yes | 18 min |
| [`4c434330ee44b096`](episodes/4c434330ee44b096/) | attrs (MIT) | 0.539 | 27 | 1 | yes | 5 min |
| [`0571b7eb5d6b7555`](episodes/0571b7eb5d6b7555/) | attrs (MIT) | 0.538 | 134 | 3 | yes | 34 min |
| [`94dab878e2c9a0ec`](episodes/94dab878e2c9a0ec/) | packaging (Apache-2.0) | 0.534 | 39 | 1 | yes | 13 min |
| [`25e452d88c01814e`](episodes/25e452d88c01814e/) | packaging () | 0.491 | 35 | 1 | yes | 20 min |
| [`c929463c84ceb538`](episodes/c929463c84ceb538/) | click (BSD-2-Clause) | 0.481 | 74 | 1 | yes | 11 min |
| [`966101f98864fafa`](episodes/966101f98864fafa/) | click (BSD-2-Clause) | 0.452 | 51 | 1 | yes | 20 min |

`Sim` is the line similarity between the agent's diff and the upstream
fix (1.000 = identical).

## What You Get

### `<task>.episode.jsonl` (raw log)

Every single event, one per line: header, tool calls, tool results,
assistant text, footer with the verification verdict.

### `<task>.sample.jsonl` (training format)

Clean conversation format in a `messages` array — ready for SFT. The
header carries provenance (repo, commits, license, model) and the
verification block.

### `ticket.md` / `briefing.md` / `hints.md`

What the agent was actually given.

### `feedback/` (reviewer reports)

Markdown reports from each review round. What the reviewer found and
what needed fixing.

### `logs/` (full agent logs)

Raw logs from the coder and reviewer agents, the ticket generator,
setup steps, the seeded-test patch, and a retry journal for debugging.

### `config.snapshot.json` / `setup_state.json` / `finalization.json`

Run configuration (secrets stored only as `(set)`/`(unset)`), setup-step
record, and the export verdict with sha256 of the episode and sample.

## Not published, on purpose

The ground-truth fix patches (`diff2.patch`, diff summaries) are held
back: publishing the answer would make these tasks useless as
benchmarks. The agent's own work lives in the trajectory — that's the
point.

## File Structure

```
episodes/<task_id>/
├── <task_id>.episode.jsonl
├── <task_id>.sample.jsonl
├── ticket.md / briefing.md / hints.md
├── config.snapshot.json
├── setup_state.json
├── finalization.json
├── feedback/
│   └── round_N.md
└── logs/
    ├── coder.ndjson
    ├── reviewer.ndjson
    ├── ticket_agent.ndjson
    └── retry_journal.jsonl
```

## Upstream repositories

- [attrs](https://github.com/python-attrs/attrs) — under MIT
- [cli](https://github.com/httpie/cli) — under BSD-3-Clause
- [click](https://github.com/pallets/click) — under BSD-2-Clause / BSD-3-Clause
- [packaging](https://github.com/pypa/packaging) — under Apache-2.0

## License

MIT. See [LICENSE](LICENSE).

The trajectory data was generated by Megabit. Source repositories retain
their original licenses.
