# Feedback report

Scope reviewed: uncommitted changes vs `HEAD` — `rich/markdown.py` (+24/−4), new
`tests/test_markdown_inline_code_table.py` (+92), `docs/source/markdown.rst` (+25),
`CHANGELOG.md` (+1). Ticket: `/megabit/ticket.md` — colored inline code must keep its
colors inside markdown table cells (heading row and body rows); nothing else in tables
may change.

## Tests

Main run — `python -m pytest tests -q` (in `/workspace`):

```
961 passed, 24 skipped, 1 warning in 5.48s
```

Zero failures. The single warning is pre-existing and unrelated
(`PytestRemovedIn10Warning` for `test_panel.py::test_render_panel`, argvalues type `zip`).

Focused run — `python -m pytest tests/test_markdown_inline_code_table.py tests/test_markdown.py -v`:

```
tests/test_markdown_inline_code_table.py::test_inline_code_in_table_body_cell PASSED
tests/test_markdown_inline_code_table.py::test_inline_code_in_table_heading_row PASSED
tests/test_markdown_inline_code_table.py::test_inline_code_in_table_matches_paragraph PASSED
tests/test_markdown_inline_code_table.py::test_inline_code_in_table_without_lexer_is_unchanged PASSED
tests/test_markdown_inline_code_table.py::test_plain_word_table_not_affected_by_lexer PASSED
tests/test_markdown.py::test_markdown_render PASSED
tests/test_markdown.py::test_inline_code PASSED
tests/test_markdown.py::test_markdown_table PASSED
tests/test_markdown.py::test_inline_styles_in_table PASSED
tests/test_markdown.py::test_inline_styles_with_justification PASSED
tests/test_markdown.py::test_partial_table PASSED
tests/test_markdown.py::test_table_with_empty_cells PASSED
============================== 12 passed in 0.16s ==============================
```

Size of the addition — `python -m pytest tests -q --ignore=tests/test_markdown_inline_code_table.py`:

```
956 passed, 24 skipped, 1 warning in 6.01s
```

961 − 956 = exactly 5 new tests, and the old 956 still pass.

Do the new tests actually catch the bug? I copied `rich/` at `HEAD`
(`git show HEAD:rich/markdown.py`) plus the new test file into `/tmp/origrepo` and ran it
there:

```
FAILED test_markdown_inline_code_table.py::test_inline_code_in_table_body_cell
FAILED test_markdown_inline_code_table.py::test_inline_code_in_table_heading_row
FAILED test_markdown_inline_code_table.py::test_inline_code_in_table_matches_paragraph
3 failed, 2 passed in 0.22s
```

Failure text, e.g. `test_inline_code_in_table_matches_paragraph`:

```
>       assert highlighted_runs(body_cell) == runs
E       AssertionError: assert [] == [('38;2;248;248;242;48;2;39;40;34', 'print'), ...]
```

So three of the five are real regression tests; the other two (`..._without_lexer_is_unchanged`,
`test_plain_word_table_not_affected_by_lexer`) already passed before the fix, which is correct —
they lock in "nothing else changes".

End-to-end through the command, same document
(`| Function | Example |` / `| print | \`print("hi", 1)\` |`), `python -m rich.markdown /tmp/t.md -i python -c`:

```
OLD: ^[[36m ^[[0mprint    ^[[36m ^[[0m^[[1;36;40mprint^[[0m^[[1;36;40m(^[[0m^[[1;36;40m"^[[0m^[[1;36;40mhi^[[0m...
NEW: ^[[36m ^[[0mprint    ^[[36m ^[[0m^[[97;40mprint^[[0m^[[97;40m(^[[0m^[[93;40m"^[[0m^[[93;40mhi^[[0m...
```

Command-line surface is unchanged: `python -m rich.markdown -h` output compared between
`HEAD` and the working tree — `diff` printed nothing (`HELP: IDENTICAL`), same flags
`-c -t -i -y -w -j -p`.

Not verified: type checks and formatting. `python -m mypy --version` → `No module named mypy`;
`python -m black --version` → `No module named black`. The project declares
`strict = true` for `files = ["rich"]` (`pyproject.toml:52-55`), so the typing state of the new
`Span` import and the `code_spans` list is unknown here, not confirmed clean.

## What is missing

Everything the ticket asks the product to do is implemented and verified. What is missing is
test and polish depth:

1. **No committed test for the offset maths.** All five tests put one snippet alone in a cell.
   The interesting code is `offset = len(self.content)` and
   `Span(offset + start, offset + end, style)` (`rich/markdown.py:344-352`), which only matters
   when the code is not at position 0. I probed by hand: header cell `` | Name `print("a")` x | ``
   and body cell with two snippets `` | `1+1` and `beta()` tail | `` both produce exactly the same
   code runs as the same text in a paragraph. So this is a coverage gap, not a product gap.
2. **No test for a wrapped code cell, or for theme/justify combinations.** Hand-checked: with
   `inline_code_theme` of `monokai`, `native`, `solarized-light`, `fruity`, the cell's code runs
   equal the paragraph's code runs; a snippet in a 20-column cell keeps per-token color across the
   wrap (`def` cyan, `very_long_functio…` green, `=` pink); a `|---:|` right-aligned cell is colored
   too. None of this is pinned by a test.
3. **The new test file re-declares `render()`** (`tests/test_markdown_inline_code_table.py:21-26`)
   instead of importing `tests/render.py`, so it skips `replace_link_ids`
   (`tests/render.py:10-15`, used by the existing markdown tests). Harmless today — no links in
   these five tests — but any future link case in this file would fail on random link ids.
4. **File placement differs from the hint** (`tests/test_markdown.py`). Cosmetic.
5. **Docs section nesting.** `docs/source/markdown.rst` has only two headings (`Markdown` at line 2,
   the new `Inline code` at lines 23-24). The pre-existing command-line paragraph at line 48
   ("You can also use the Markdown class from the command line…") now sits inside the new
   "Inline code" section with no heading of its own, so it reads as inline-code advice.
6. **Docs example shows a no-op option.** Line 45 passes `inline_code_theme="monokai"`, which is
   already the default (`code_theme: str = "monokai"`, `rich/markdown.py:567`, and
   `inline_code_theme or code_theme` at line 582), and there is no CLI flag for it (`-h` lists only
   `-t/--code-theme`).
7. **No guard for a stated assumption.** The comment at `rich/markdown.py:343` says "Only syntax
   highlighted inline code arrives as a Text object". That is true right now — the only place a
   `Text` reaches `on_text` is `rich/markdown.py:506-511` (`node_type in {"fence", "code_inline"}`
   with a syntax) — but nothing in the tests would notice if another `Text` producer appeared, and
   such a case would silently lose its styling in cells.

## Why it fails

No test fails. The full suite is `961 passed, 24 skipped` with 0 failures, and the 12-test focused
run is `12 passed`. The only failures I produced were the three listed above inside the isolated
pre-fix copy at `/tmp/origrepo`, which demonstrate the old bug rather than a current defect. The
one open item is not a test failure but an unverified check: mypy and black are not installed in
this environment, so strict typing and formatting of the diff are unknown.

## Verdict

VERDICT: approve

## Experience difference

- **Code in a body cell, with a lexer.** Before: the whole snippet was painted with one flat style
  (`markdown.code` = bold cyan on black, `rich/default_styles.py:147`; seen as `1;36;40` on every
  token, and zero code-theme runs in the render — `highlighted_runs(body_cell) == []`). After: each
  token gets its pygments foreground on the theme background
  (`38;2;248;248;242;48;2;39;40;34` for `print`, `230;219;116` for `"hi"`, `174;129;255` for `1`),
  byte-for-byte the same runs the same snippet produces inside a sentence
  (`test_inline_code_in_table_matches_paragraph`).
- **Code in the heading row, with a lexer.** Same change. Before, `markdown.table.header` covered
  the whole cell and flattened the snippet. Now the code spans are re-applied after the header style
  (`rich/markdown.py:262-266`), so the snippet is colored while the surrounding plain header words
  still come out `36` cyan and the padding runs are untouched.
- **Mixed cells.** `` Name `print("a")` x `` in a header cell: plain words cyan, snippet token-colored,
  in the right places. Before, all of it was one flat block.
- **Several snippets, hard breaks, alignment, unicode, narrow widths.** `` `one()`<br>`two()` ``,
  right-aligned columns, `` `héllo()` — ok `` and a 20-column wrap all keep per-token colors.
- **Visible text and layout are the same.** For every document I compared, the text with escapes
  stripped is identical (`visible text identical: True` for all 8 synthetic cases), including
  spacing and cell widths. The old bold `1;` never appears where the paragraph does not add it, and
  never disappears where it should stay.
- **Without a lexer, nothing moves.** `` | `print("hi", 1)` | `` is still `1;36;40` in body rows and
  `36;40` in the heading row (`test_inline_code_in_table_without_lexer_is_unchanged`, which passed
  both before and after the fix).
- **Wide regression sweep.** 46 repository `.md` files × 2 widths × {no lexer, python lexer} = 184
  renders, old code vs new, after normalizing random hyperlink ids: **0 differences**. Honest limit:
  `grep -lE '^\|.*`'` over those files returns 0 hits, so no repo document has inline code in a
  table — this sweep proves "no collateral change", not "the fix fires in real docs".
- **Synthetic sweep.** 8 documents × 2 widths × {no lexer, python} × {default theme, native} = 64
  renders, old vs new: 28 differ, and every differing one is a document with back-ticked code in a
  table cell **and** a lexer; the 32 no-lexer renders are all identical.
- **Settings and API surface unchanged.** No option added, none removed; `Markdown(markup,
  code_theme, justify, style, hyperlinks, inline_code_lexer, inline_code_theme)` has the same
  signature, and `inline_code_theme or code_theme` still decides the cell colors
  (`rich/markdown.py:582`). The `rich-markdown` command takes the same flags as before (`-h` diff
  empty).
- **Repeated rendering / notebooks.** The header style is applied to `column.content.copy()`
  (`rich/markdown.py:261-266`), so printing the same `Markdown` object twice gives the same output
  (checked: the second print's first frame equals the first print exactly).
- **A deliberate rule change to know about.** Because header code spans now win over
  `markdown.table.header`, a theme that recolors header text no longer recolors a *highlighted*
  snippet inside a header cell. Measured with a custom `markdown.table.header`
  (red, bold, italic): old rendered `` `print(1)` `` as `1;3;31;40`; new renders it as the code theme
  while ` plain` after it still gets `1;3;31`. Non-code header words, and header code with no lexer,
  are unaffected. This is what "colors survive" asks for, but it is a visible precedence change.
- **Edge behaviour users might poke at.** Empty cells, partial tables, tables without code, control
  characters (`be\x07llo`), square brackets and `%` in cells all render identically before and after,
  even though the string branch of `TableDataElement.on_text` changed from `Text()` + `stylize` +
  `append_text` to `append(text, style)` (`rich/markdown.py:338-340`).
- **Reading the docs.** A reader now finds an "Inline code" section in
  `docs/source/markdown.rst:23-46` that explains the lexer, the theme fallback, and states in words
  that snippets keep their colors in both the heading row and body rows — none of that was written
  down before. `CHANGELOG.md` gained a Fixed line for issue 4038. Two nits remain in that section:
  the CLI paragraph now nests under it, and the example passes the default theme.

VERDICT: approve
