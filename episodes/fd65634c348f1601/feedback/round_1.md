# Feedback report

## Tests

I did not run any tests myself. The pipeline ran the Diff2 suite for this workspace three times. All three runs were identical and all passed.

Command: `python -m pytest`

Totals from the harness output (run 1 of 3, exit_code=0):

- collected 33095 items / 31000 deselected / 2095 selected
- final line: `======== 2070 passed, 24 skipped, 31000 deselected, 1 xfailed in 12.32s ========`

Run 2 of 3 (exit_code=0): `======== 2070 passed, 24 skipped, 31000 deselected, 1 xfailed in 12.92s ========`

Run 3 of 3 (exit_code=0): `======== 2070 passed, 24 skipped, 31000 deselected, 1 xfailed in 11.36s ========`

So: 2095 selected, 2070 passed, 24 skipped, 1 xfailed, 0 failed, 0 errors, in all three runs.

## What is missing

Nothing that the ticket asked for is missing from the product side. One coverage note, not a defect:

The ticket's headline case is a *custom* parameter type getting `help`. `tests/test_info_dict.py:279-283` only parametrizes over the two shipped kinds:

```python
PARAM_KINDS = [
    pytest.param(lambda **kwargs: click.Option(["--name"], **kwargs), id="option"),
    pytest.param(lambda **kwargs: click.Argument(["name"], **kwargs), id="argument"),
]
```

A grep for custom subclasses in `tests/` (`class \w+\((click\.)?Parameter\)`) found none, so no test builds a third-party `Parameter` and passes `help=` to it. The new tests at `tests/test_info_dict.py:300` and `:321` cover `Option` and `Argument` only. The code path is the same one, so this is a coverage observation, not a missing feature.

## Why it fails

No test fails. There is nothing to explain here. The three harness runs are green with 0 failures.

## Verdict

VERDICT: approve

## Experience difference

The product the ticket describes and the product that now exists match. Walking through the user experience:

- **Help on any parameter kind.** `help` is now a declared argument of `Parameter` (`src/click/core.py`, `help: str | None = None` in `Parameter.__init__`, and the class-level annotation `help: str | None`). A custom `Parameter` subclass that forwards `**kwargs` to `super().__init__` can now take `help` without the constructor raising `TypeError`. Before this change, only `Option` and `Argument` had it.

- **Options unchanged for users.** `help` was removed from the `Option.__init__` signature and now travels through `**attrs` into `Parameter`. Existing code that writes `click.option("--x", help="...")` or `@click.option(..., help="...")` behaves exactly as before. The docstring at the `Option` `:param attrs:` entry now points readers at `Parameter` for `help`.

- **Arguments unchanged for users.** `Argument` likewise routes `help` through `**attrs`, so `@click.argument("dst", help="destination path")` keeps working. `tests/test_info_dict.py:334-345` builds a command with two helped arguments and checks both names and both help strings in the info dict.

- **Dedenting and the deprecation label are unchanged in behaviour, just moved.** The `inspect.cleandoc` call and the `f"{help} {label}" if help else label` label append now live once in `Parameter.__init__` instead of being duplicated in `Option` and `Argument`. The label text still comes from the shared `_format_deprecated_label` helper. `tests/test_info_dict.py:300-302` covers `None`, `""`, single-line, and a multi-line string that is dedented to `first line\nsecond line`; `tests/test_info_dict.py:321-324` covers `(DEPRECATED)`, `(DEPRECATED: USE THE CRATE)`, and the label-only case where no help text was given. Every case passes.

- **Info dict.** `Parameter.to_info_dict` now emits `"help": self.help` (`core.py`, added line in the returned dict), so the settings dict reports help for every parameter kind, not only options and arguments.

- **Docs and changelog.** The `Parameter` docstring gained a `:param help:` block and a `.. versionchanged:: 8.5.1` note; `Option` gained a matching note explaining that `help` moved to `Parameter`; `Parameter.to_info_dict` gained a note that `help` is now reported for every kind. `CHANGES.md` has an 8-line Unreleased entry describing the same change. `git diff --cached --stat` shows exactly two files changed: `CHANGES.md` (+8) and `src/click/core.py` (+36/−31 net across 67 changed lines).
