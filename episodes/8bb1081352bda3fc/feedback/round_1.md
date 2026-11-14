# Feedback report

## Tests

The pipeline ran the suite 3 times. Every run used the command `python -m pytest` and every run was green.

- Total tests: 8
- Passed: 8
- Failed: 0
- Errors: 0

Run 1 of 3, exit_code=0:

```
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspace
collected 8 items

tests/test_basic.py ........                                             [100%]

============================== 8 passed in 0.02s ===============================
```

Run 2 of 3, exit_code=0: same 8 collected, same 8 dots, `8 passed in 0.03s`.
Run 3 of 3, exit_code=0: same 8 collected, same 8 dots, `8 passed in 0.03s`.

The UUID coverage named in the ticket, `test_uuid_option` at `tests/test_basic.py:97-116`, is inside the 8 dots and passed. I did not run any test myself; the numbers above are quoted from the harness runs.

## What is missing

Only one ticket item is not actually delivered, and it is a user-facing one.

1. **The help text does not show `uuid`.** The ticket says the help text "names the value `uuid`". The change sets `name = 'uuid'` on the new type (`click/types.py:154`), which is the right attribute to set. But in this version of the code nothing reads it. `make_metavar` in `click/core.py` builds the placeholder from the parameter name uppercased, not from the type's `name`. So `@click.option('--u', type=click.UUID)` renders as `--u U` under `--help`. The user gets no hint about the expected value shape. Note this is not a UUID-specific regression: `integer`, `floating point`, and `boolean` are in the same boat here, so the type is consistent with its neighbours, just not with the ticket's promise.

2. **`docs/parameters.rst:54` uses the wrong role.** The new line is `- :class:`click.UUID`` while every other built-in type in the same list uses `:data:` (`:data:`click.INT``, `:data:`click.FLOAT``, `:data:`click.BOOL``, `:data:`click.UUID`` at the neighbouring lines), and `UUID` is declared with `.. autodata::` in `docs/api.rst:87`. `:class:` points at a class, not at data. Cosmetic, but it will not link to the autodata target and can trip a nitpicky docs build.

Two things that are **not** missing, checked because they looked like gaps:

- No new test was added by this diff, and that is fine. `tests/test_basic.py` is not in the diff at all; `test_uuid_option` already exists in HEAD. The ticket's "the test file now checks ..." describes the state after the change, not a test this change had to add.
- Nothing was removed or altered. The diff touches only `click/types.py` (adds `UUIDParameterType` and the `UUID` singleton, `click/types.py:152-166` and `click/types.py:261-262`), `click/__init__.py:27` and `click/__init__.py:50` (import plus `__all__` entry), and the two doc pages. The other built-in types are untouched.

## Why it fails

No test fails. All 8 pass in all 3 runs, so this section is empty of failures.

The three assertions in `test_uuid_option` each have a matching code path:

- Default value: `convert` does `if value is not None: return uuid.UUID(value)` before any parse, so the default `ba122011-…` string reaches the command already as a `uuid.UUID`.
- Command-line value: the same branch parses `--u 12345678-…`.
- Bad value: `bar` fails the `uuid.UUID(value, version=4)` parse and hits `self.fail('... is not a valid UUID value')` at `click/types.py:163`. The `Invalid value for "--u": ` prefix is added by `ParamType.fail` in `click/types.py:44`, so the full message is the exact string the ticket asks for.

The two findings above are outside what the tests assert, which is why the suite is green while they are still real: the metavar path is not exercised by `test_uuid_option`, and the sphinx role in `docs/parameters.rst` is not checked by pytest at all.

## Verdict

VERDICT: approve

## Experience difference

What the ticket describes versus what exists now.

**Working as promised.** A command author writes `@click.option('--u', type=click.UUID)` and gets a real `uuid.UUID` object in the callback, both from the default and from a command-line value. `click.UUID` is importable from the top-level `click` package and appears in `__all__`, so it reads the same as `click.INT` and `click.BOOL`. A bad value is stopped before the command body runs, with the message `Invalid value for "--u": bar is not a valid UUID value`, which names the offending option, echoes the bad text, and says what went wrong. That is the main pain point from the ticket, and it is closed.

**Help output is the gap.** The ticket frames the new type as useful in the same way as `integer` and `floating point`, whose value names show up in help. Here they do not, and `uuid` does not either. A user who runs `--help` sees `--u U`. Nothing in the help output tells them the value must be a UUID, or shows `ba122011-…` as an example. For a brand-new type this matters more than for the existing ones: a user has no prior knowledge that this option takes a UUID, and this is exactly the discovery problem the ticket opened with. The type's `name` attribute is correct and would be the right thing for help to use; the help path just does not consult it in this codebase.

**Docs.** Both pages were updated, so the type is listed in `docs/api.rst` alongside the other built-ins and in the type table in `docs/parameters.rst`. The one blemish is the role on `docs/parameters.rst:54` (`:class:` where the file uses `:data:`), which breaks the link to the `.. autodata::` target rather than creating a new problem.

**Behaviour beyond the ticket.** `convert` strips a leading `urn:` before parsing, so `urn:uuid:…` input is accepted. The ticket did not ask for this. It is harmless, but note the error message echoes the *stripped* text, not the raw input, so a user who typed `urn:bar` would be told about `bar` rather than what they actually entered.

**Not verifiable here.** The `--help` rendering claim and the sphinx build were checked by reading `click/core.py` and `docs/parameters.rst`; I did not run a docs build or a help-printing command, and the pytest suite does not cover either. Those two points should be confirmed by hand if they matter to you.
