# Feedback report

## Tests

The harness ran the Diff2 suite three times with `python -m pytest`. All three runs
had `exit_code=0` and were classified `substantive`.

Run 1 (0.80s), run 2 (1.15s), run 3 (1.31s) each reported:

```
tests/test_compat.py ................................................... [ 16%]
........................................................................ [ 38%]
....................................................                     [ 55%]
tests/test_formatting.py .....................................           [ 66%]
tests/test_utils/test_style.py ......................................... [ 79%]
................................................................         [100%]

============================= 317 passed in 0.80s ==============================
```

Totals across all three runs: 317 tests collected, 317 passed, 0 failed. The runs were
identical, so the result is stable and not flaky. The three files the ticket points at
(`tests/test_compat.py`, `tests/test_formatting.py`, `tests/test_utils/test_style.py`)
all pass.

## What is missing

Nothing that the ticket asked for is missing, based on the code I read:

- `src/click/_compat.py:23` now defines the control-mark pattern using the ECMA-48 CSI
  grammar, `re.compile(r"\033\[[\x30-\x3f]*[\x20-\x2f]*[\x40-\x7e]")`, in place of the
  older narrower pattern. `strip_ansi` (around `src/click/_compat.py:495`) and
  `term_len` (around `src/click/_compat.py:540`) both already use this pattern, so both
  the "remove the marks" path and the "measure visible width" path share the same
  definition.
- `src/click/_textwrap.py` measures and wraps using `term_len` (via its visible-width
  helper and `TextWrapper._wrap_chunks`), so wrapping and truncation also ignore these
  marks. This file is unchanged from the initial commit and already measured by visible
  width.
- `src/click/termui.py` `style()` and `unstyle()` are consistent: `unstyle()` delegates
  to `strip_ansi`, so removing style also removes the newly covered marks.

The changed surface is small: `git diff HEAD --stat` shows only `CHANGES.md` (+5) and
`src/click/_compat.py` (+10/-1).

One non-blocking note: the new pattern covers CSI sequences only. OSC sequences
(`ESC ] ... BEL`/`ST`) are not matched. The ticket's wording and its examples are about
terminal control marks of the CSI family (colon SGR, private modes, intermediate bytes,
non-letter final bytes), and the present tests all pass, so I do not treat this as a
defect. I mention it only as a boundary of what is covered.

## Why it fails

No test failed. All 317 tests passed in each of the three harness runs.

## Verdict

VERDICT: approve

## Experience difference

The product the ticket describes is one where Click treats the full family of terminal
control marks as invisible: they do not leak into `unstyle()` output, they do not count
toward visible length in `term_len`, and they do not break wrapping or truncation. The
product that exists now matches this in the paths I read.

Concretely, before the change the pattern was `\033\[[;?0-9]*[a-zA-Z]`
(`src/click/_compat.py`, initial commit). It only matched a CSI sequence built from
digits, `;` and `?` and ended by a letter. It missed, for example:

- colon-separated SGR like `ESC[38:2:255:0:0m` and `ESC[38;5:200m`, because `:` is not in
  the old class.
- private/parameter-byte sequences like `ESC[?1049h` and `ESC[?25l` (the `?` is allowed
  but the form still must end in a letter, and combos such as `ESC[<0;30;40M` with `<`
  are not).
- intermediate-byte sequences such as `ESC[0 q` (cursor shape), which end in a space plus
  a letter, and do not fit the old digit/`;`/`?` class.
- sequences whose final byte is not a letter, such as `ESC[3~`.

With the old pattern, such marks would have been treated as visible text: they would
survive `strip_ansi`/`unstyle` and would be counted by `term_len`, so padded/aligned
output and wrapped help or error text could be miscounted by the number of characters in
the mark. The current pattern `\033\[[\x30-\x3f]*[\x20-\x2f]*[\x40-\x7e]` accepts the
general ECMA-48 CSI shape: optional parameter bytes in the `\x30-\x3f` range (which
includes `:`, `<`, `?`, `;`, digits), optional intermediate bytes in `\x20-\x2f` (which
includes the space), and a final byte in `\x40-\x7e`. That is a superset of the old
pattern, so no sequence that was removed before stops being removed, and the newly
covered classes are now removed and ignored for width too.

End-user experience: `unstyle()` and `strip_ansi` now return plain text with these marks
gone, so styled output shown on a terminal without colour or captured to a file no longer
contains stray escape text. Alignment and wrapping that rely on `term_len` now line up for
output that uses colon-form colours or cursor/terminal marks, instead of being shifted by
the invisible characters. The behaviour with plain text and with the previously covered
basic sequences is unchanged, which the passing `tests/test_compat.py`,
`tests/test_formatting.py` and `tests/test_utils/test_style.py` confirm.