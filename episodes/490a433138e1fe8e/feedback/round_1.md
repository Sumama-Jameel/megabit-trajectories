# Feedback report

Ticket: `/megabit/ticket.md` — replace the `--digest` / `-d` boolean flag with a `--auth-type` option that takes `basic` or `digest`, default `basic`, and error out when `--auth-type` is used without `--auth`.

## Tests

The pipeline ran the suite three times. I did not run tests myself; these are the harness results.

Command: `python -m pytest` (rootdir `/workspace`, `configfile: pytest.ini`).

- Run 1: `exit_code=0`, `collected 15 items`, `tests/tests.py ............... [100%]`, `15 passed in 14.34s`
- Run 2: `exit_code=0`, `collected 15 items`, `tests/tests.py ............... [100%]`, `15 passed in 16.34s`
- Run 3: `exit_code=0`, `collected 15 items`, `tests/tests.py ............... [100%]`, `15 passed in 17.41s`

Totals: 15 tests, 15 passed, 0 failed, 0 errors, across 3 runs. All runs stable, no flakiness.

The two auth tests that matter here both pass:
- `tests/tests.py:144` `test_basic_auth` — `http('--auth', 'user:password', 'GET', 'httpbin.org/basic-auth/user/password')`
- `tests/tests.py:150` `test_digest_auth` — `http('--auth-type=digest', '--auth', 'user:password', 'GET', 'httpbin.org/digest-auth/auth/user/password')`

The test file itself was not changed by this work (`git show HEAD:tests/tests.py` already contains `--auth-type=digest` at line 151).

## What is missing

The ticket's own requirements are all present in the code:

- `httpie/cli.py:27-29` defines `AUTH_BASIC = 'basic'`, `AUTH_DIGEST = 'digest'`, `AUTH_TYPES = [AUTH_BASIC, AUTH_DIGEST]`.
- `httpie/cli.py:229-231` replaces `'--digest', '-d', action='store_true'` with `'--auth-type', default=None, choices=AUTH_TYPES`. The old flag and its short form are gone.
- `httpie/cli.py:110-112` adds `_validate_auth`, wired into `parse_args` at `cli.py:107`, which calls `self.error('--auth-type only works with --auth.')` when `args.auth_type` is set and `args.auth` is not.
- `httpie/__main__.py:137-142` selects the requests auth class from a dict keyed on `args.auth_type or cli.AUTH_BASIC`, so the default is basic.
- `-d` was not silently reused: the short options present in `cli.py` are `-j -f -u -p -v -t -b -s -a` only.
- `README.rst` usage block and option list were updated to `--auth-type {basic,digest}`.

What is genuinely not covered, and I want to be clear these are gaps rather than failures:

- No test for the error path. `grep -n auth tests/tests.py` returns only lines 144-147 and 150-153. Nothing asserts that `--auth-type digest` without `--auth` exits non-zero with the message. The behavior exists at `cli.py:110-112` but is unproven by the suite.
- No test that `--auth-type bogus` is rejected by `choices`. Also unproven.
- The suite says nothing about `--help` output. The README claims the new usage line; no test compares them.

Two changes ride along that the ticket does not ask for:

- `httpie/__main__.py:66` changed `body=request._enc_data` to `body=getattr(request, '_enc_data', None) or request.body`. This is a real behavior change to the request body path, unrelated to auth. The `or` means a legitimately empty `_enc_data` falls through to `request.body`. Grep shows `_enc_data` now has exactly one reference in the package — this line — so the fallback is the only reason it still compiles.
- New untracked `conftest.py` monkeypatches `requests.compat.is_py26` and `requests.compat.str` back into existence, because the locked `tests/tests.py:5` imports those names and requests 2.34.2 no longer has them. The file's own docstring says so. New `pytest.ini` with `python_files = tests.py` came with it.

## Why it fails

Nothing fails. 15 of 15 tests pass in all three runs, `exit_code=0` each time. There is no failing test to explain.

The one thing I could not verify from the harness output is whether the suite would pass without the new `conftest.py`. The tests import `requests.compat.is_py26` at module import time; if that name is missing, collection fails before any test runs. The harness shows `collected 15 items`, so collection succeeded, which means the shim is doing its job under the current environment. I am reporting what the run shows and not claiming more.

## Verdict

VERDICT: approve

## Experience difference

What a user gets now, against what the ticket describes.

Authentication flags. Before, digest was opt-in through a boolean switch: `http -d --auth user:password ...`. The short form `-d` is removed entirely — a user who had it in muscle memory or in a shell alias now gets an argparse "unrecognized arguments" failure. Nothing in the change keeps `-d` as a working alias, and the ticket does not ask for one, so this is a clean break rather than a bug. The replacement is `http --auth-type=digest --auth user:password ...`, and the space-separated form `--auth-type digest` works equally well because argparse takes both.

Choosing the mechanism. `--auth-type` accepts exactly `basic` and `digest` and nothing else, enforced by `choices` at `cli.py:229-230`. A typo like `--auth-type=Basic` or `--auth-type=token` is rejected at parse time with argparse's own "invalid choice" message, which names the valid options. The old boolean had no such state to get wrong.

The default. Plain `http --auth user:password ...` still means basic, confirmed by `tests.py:144-147` passing. The ticket asked for a default of `basic` and that is what happens. One implementation detail worth naming: the argparse default is `None`, not `'basic'`, and the fallback is applied at the point of use in `__main__.py:141` via `args.auth_type or cli.AUTH_BASIC`. Behavior is right. The help text at `cli.py:230-231` says `Defaults to "basic"`, which is true from the user's side even though the parsed namespace holds `None`. Nobody outside `__main__.py` reads `auth_type`, so this does not leak.

Using the type without credentials. `http --auth-type digest httpbin.org/...` with no `--auth` fails fast at parse time. `cli.py:110-112` raises through `self.error`, which argparse turns into a usage message plus `SystemExit(2)`. The request is never built and no network call is made. The text is `--auth-type only works with --auth.` — short and it names both flags involved. I confirmed the code path exists; I want to be straight that no test exercises it, so it is correct by reading, not by running.

Documentation. `README.rst` was updated in both places that matter: the usage synopsis gained `[--auth-type {basic,digest}]` and the options list gained the entry with its default note. The old `--digest` line is gone from the help block. The two stay in sync as far as I can tell by reading both, though no test enforces that.

Scope. Two things a reviewer of the product itself will notice. First, `__main__.py:66` is unrelated to auth — it makes body construction fall back from `_enc_data` to `request.body` when the former is missing or falsy. It is small and the suite is green, but it changes what gets sent in a case the old code would have raised on, and it is not mentioned in the ticket. Second, the new `conftest.py` exists to keep a locked test module importable under a modern requests by reintroducing two removed names, `is_py26` and `str`, at collection time. It works, and it is honest about why it is there, but it is test-harness scaffolding committed alongside a product change. Neither blocks the ticket, and both should be visible to whoever reviews this next.

Test coverage shape. Fifteen tests, all passing, three consecutive clean runs. The happy paths for both auth types are covered. The error paths — auth type without credentials, invalid auth type value — are implemented and read correctly but are not covered by any test, so a later change could break them without the suite noticing.
