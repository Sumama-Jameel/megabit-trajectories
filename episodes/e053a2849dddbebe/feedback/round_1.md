# Feedback report

## Tests

The harness ran the project suite three times, all with the same command and the
same result.

Command: `python -m pytest` (rootdir `/workspace`, `configfile: pyproject.toml`,
`testpaths: tests`).

Run 1: `exit_code=0`, `collected 96 items`,
`============================== 96 passed in 0.23s ==============================`
Run 2: `exit_code=0`, `collected 96 items`,
`============================== 96 passed in 0.27s ==============================`
Run 3: `exit_code=0`, `collected 96 items`,
`============================== 96 passed in 0.25s ==============================`

Totals: 96 tests, 96 passed, 0 failed. The suite covers
`tests/test_basic.py`, which contains the two tests that exercise this feature:
`test_custom_version_option` (parametrized over `--version` and `-V`, expecting
`"custom 9.9.9\n"` and exit code 0) and `test_custom_version_option_receives_context`
(expecting `"mytool 1.0\n"`). Both are inside the 96 that passed. No test skipped,
no error, and the run is stable across all three attempts.

## What is missing

I found nothing the ticket asked for that is absent.

The ticket asks for a new ready-made option (a sibling of the existing
`version_option`) that takes a callback, passes the current run `Context` to it,
prints the text the callback returns, and exits; with the existing
`version_option` unchanged and its placeholder set fixed. In the code I read:

- `src/click/decorators.py` defines `custom_version_option`, with `--version`
  as the default param decl, `is_flag`/`expose_value=False`/`is_eager=True` and a
  `help` default set, an inner callback that returns early under
  `resilient_parsing`, echoes `callback(ctx)` with `ctx.color`, and calls
  `ctx.exit()`.
- `src/click/decorators.py` still contains the original `version_option` next to
  it, so the old behavior is kept.
- `src/click/__init__.py` exports `custom_version_option`.
- `docs/api.md` documents it with an `autofunction` entry.
- `CHANGES.md` describes it.

The callback signature receives the context, which is what the ticket asks for.
The "-V" short-flag case is handled: the test passes `-V` explicitly to the
decorator, and that test passed, so the short flag is reachable when declared.
I did not read any line that contradicts the ticket.

## Why it fails

Nothing fails. All 96 tests passed in all three harness runs, and I found no test
failure output to explain. The two feature tests named above are among the
passing 96.

## Verdict

VERDICT: approve

## Experience difference

The ticket describes a Click user who wants a version-style flag driven by their
own callback instead of Click's built-in version string assembly: they write a
function that takes the current `Context` and returns the exact text, attach it
with one decorator line, and get that text printed followed by a clean exit when
`--version` (or a short flag they also declare) is used. The product that exists
now matches that description. A user can import `click.custom_version_option`,
give it a callback that uses the passed context (for example the program name via
`ctx.info_name`), and the output is exactly the callback's returned text plus a
newline, with exit code 0. Declaring an extra short alias is possible by passing
additional param decls, and the passing parametrized test confirms `-V` works
when declared. The eager/flag nature means the version text prints before other
processing and does not interfere with `--help` or normal parsing, and the
`resilient_parsing` guard means shell completions are not disturbed by it. The
pre-existing `version_option` is still there and still behaves as before, so
users of the old API see no change; its `%(prog)s`/`%(package)s`/`%(version)s`
placeholders remain the fixed set, as the ticket states. The feature is visible
to users in the public `click` namespace, in the API docs page, and in the
changelog, so it is discoverable rather than private. The only gaps relative to
the ticket are ones the ticket itself does not require, so they do not change the
user experience described: nothing is missing from what a user asked for.
