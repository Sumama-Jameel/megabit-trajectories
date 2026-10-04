# Feedback report

## Tests

Repo state under review: `git diff --stat HEAD` → `CHANGELOG.md | 1 +`, `rich/markdown.py | 7 ++++---` (2 files, 5 insertions, 3 deletions). `tests/test_markdown.py` is byte-identical to `HEAD` (`git diff --name-only HEAD` lists only the two files above).

Whole suite, run myself in `/workspace`:

```
$ cd /workspace && python -m pytest -q -p no:cacheprovider
956 passed, 24 skipped, 1 warning in 6.00s
$ python -m pytest --collect-only -q -p no:cacheprovider
980 tests collected in 0.41s
$ TERM=unknown python -m pytest tests/ -q -p no:cacheprovider     # project's test-no-cov target
956 passed, 24 skipped, 1 warning in 6.16s
```

So: 980 collected, **956 passed, 0 failed, 24 skipped**. The warning is pre-existing (`tests/test_panel.py::test_render_panel`, pytest deprecation, unrelated to this change). Skips are also unrelated: `-rs` puts them all in `test_windows_renderer.py`, `test_inspect.py`, `test_tree.py`, `test_traceback.py`, `test_pretty.py`; `tests/test_markdown.py` has no skips (`7 passed`).

Markdown-only run:

```
$ python -m pytest tests/test_markdown.py tests/test_markdown_no_hyperlinks.py -v
tests/test_markdown.py::test_markdown_render PASSED
tests/test_markdown.py::test_inline_code PASSED
tests/test_markdown.py::test_markdown_table PASSED
tests/test_markdown.py::test_inline_styles_in_table PASSED
tests/test_markdown.py::test_inline_styles_with_justification PASSED
tests/test_markdown.py::test_partial_table PASSED
tests/test_markdown.py::test_table_with_empty_cells PASSED
tests/test_markdown_no_hyperlinks.py::test_markdown_render PASSED
8 passed in 0.18s
```

Nothing fails. That is the headline test result, and it is also the problem: the suite is blind to the ticket. Proof — I copied the tree to `/tmp/base`, restored the pre-patch `rich/markdown.py` from `HEAD` (verified: `335:        text.stylize(context.current_style)` present, `git show HEAD:rich/markdown.py` diff empty), and ran everything again:

```
=== FULL SUITE WITH PATCH REVERTED ===
956 passed, 24 skipped, 1 warning in 6.40s
```

Identical numbers. **Not one existing test notices the bug this change fixes.**

I then wrote a throw-away probe test (kept outside the repo, in `/tmp/regress/`, nothing in `/workspace` touched) that compares the colour set of a snippet in a paragraph against the same snippet in a table cell:

```
=== WITH PATCH (/workspace rich) ===        1 passed in 0.13s
=== WITHOUT PATCH (/tmp/base rich) ===      1 failed
E         Extra items in the right set:
E         '38;2;248;248;242;48;2;39;40;34'
E         '38;2;174;129;255;48;2;39;40;34'
```

That confirms two things: the body-cell fix is real, and the shipped suite has zero coverage for it.

`make test` as written cannot run here — `make` is absent and `pytest-cov`, `black` and `mypy` are not installed (`python -m black --check rich/markdown.py` → `No module named black`; `python -m mypy --version` → `No module named mypy`), so `--cov` is rejected. I ran the plain and `TERM=unknown` pytest equivalents above instead. Style was spot-checked by eye against the surrounding code: the new block matches the existing `TextElement.on_text` shape at `rich/markdown.py:100-101`.

## What is missing

1. **No regression test — the ticket names `tests/test_markdown.py` as a hint and it was not touched.** The diff has no test file. Evidence: `git diff --name-only HEAD` → `CHANGELOG.md`, `rich/markdown.py`; and the reverted-baseline run above passes 956/24 exactly like the patched run. Today's suite would let the bug come straight back. The five table tests that do exist (`test_markdown_table`, `test_inline_styles_in_table`, `test_inline_styles_with_justification`, `test_partial_table`, `test_table_with_empty_cells`) all build `Markdown(...)` **without** `inline_code_lexer`, so none of them ever reaches the coloured-code path; the one test that does set a lexer (`test_inline_code`) has no table in it.

2. **The heading row is only half done.** Ticket, "What changed": colours keep their look "in both the heading row and the body rows". Body rows deliver; the heading row does not. Real renders (patched, truecolor, `inline_code_lexer="python"`):

   ```
   #### header_with_code   | `Function` | `len(str)` | header row + body row
        header: [('36;48;2;39;40;34','Function'), ('36;48;2;39;40;34','len'),
                 ('36;48;2;39;40;34','('), ('36;48;2;39;40;34','str'), ('36;48;2;39;40;34',')')]
        body:   [('38;2;248;248;242;48;2;39;40;34','print'), ('38;2;174;129;255;48;2;39;40;34','1'), ...]
   ```

   Every header token still carries the one same foreground `36` (cyan) — the only change over baseline (`36;40`) is the background, which now comes from the code theme. Keyword, string and number are still indistinguishable from each other in the top row, so "colors stop being flattened anywhere in a markdown table" is not yet true.

3. **A stale artifact worth clearing.** `tests/.pytest_cache/v/cache/lastfailed` contains `"test_markdown.py::test_inline_code_in_table_cells": true`, and the same name appears in `.../cache/nodeids`. No test of that name exists in the suite (`grep -rn "inline_code_in_table" tests/` matches only those two cache files). The directory is gitignored (`.gitignore:59:.pytest_cache/`), so it is not part of the change; I report it only because it shows a test with exactly the right name was collected and failed at some point, and it does not exist now.

4. **Docs untouched.** `docs/source/markdown.rst` (28 lines) is listed in the hints; `grep -n "inline_code\|table\|lexer"` on it returns nothing, so the feature this fixes is still undocumented there — no mention of `inline_code_lexer` at all, in a table or elsewhere. Low weight, but the hint file saw no edit.

5. **Wording nit** in the changelog line added at `CHANGELOG.md:20`: "Fixed inline code in Markdown tables cells" (reads "tables cells").

6. **Met: no settings added or removed.** `python -m rich.markdown --help` lists exactly the same flags before and after (`-c/--force-color`, `-t/--code-theme`, `-i/--inline-code-lexer`, `-y/--hyperlinks`, `-w/--width`, `-j/--justify`, `-p/--page`), and the command runs clean (`EXIT=0`).

## Why it fails

No test fails, so there is no failing-test cause to list. `pytest -q` → `956 passed, 24 skipped`, exit 0. The causes below are for the two gaps.

**Gap A — no test.** The suite simply never combines `inline_code_lexer` with a table. Measured, not assumed: patched run and reverted run both report `956 passed, 24 skipped`, and my `/tmp/regress` probe is what first makes the difference visible (`1 passed` patched, `1 failed` reverted, with the missing items named as the two `38;2;...` theme colours).

**Gap B — the heading row.** The mechanism is the same flattening the patch removed from body cells, still alive one level up. Old `TableDataElement.on_text` appended a whole-range style over text that already carried per-token pygments spans, and a full-range span added last wins at render time, so every token was painted `markdown.code` (`rich/default_styles.py:147` = `bold=True, color="cyan", bgcolor="black"`) — exactly the flat `1;36;40` seen in the reverted renders. The new code at `rich/markdown.py:333-337` stops doing that for cells, and body rows now match a paragraph byte for byte:

```
$ python /tmp/parity.py
PARA snippet styles: ['38;2;174;129;255;48;2;39;40;34', '38;2;230;219;116;48;2;39;40;34', '38;2;248;248;242;48;2;39;40;34']
CELL snippet styles: ['38;2;174;129;255;48;2;39;40;34', '38;2;230;219;116;48;2;39;40;34', '38;2;248;248;242;48;2;39;40;34']
PARA==CELL: True
```

Header cells go through the same `TableDataElement`, so they gain the theme background — but the table is then built at `rich/markdown.py:260-262`, where each heading cell is copied and stamped with one style over its whole length (`heading.stylize("markdown.table.header")`), and `markdown.table.header` is `Style(color="cyan", bold=False)` (`rich/default_styles.py:167`). A whole-length style applied after the fact sets the foreground for the whole run and overrides the token colours, which is the `36;48;2;39;40;34` output observed above. Note this same stamping is long-standing for headers — the committed expectation in `tests/test_markdown.py::test_inline_styles_in_table` already shows header `**column**` rendered without bold while body bold survives — so it is a pre-existing design, not damage from this patch. As the ticket is written, though, the heading row item is still unmet.

**No collateral damage found.** Baseline-vs-patched diff over 13 rendered documents produced 10 changed lines, every one of them an inline-code span inside a table with a lexer set:

```
$ diff /tmp/b.txt /tmp/a.txt | grep -c '^[<>]'
10
```

Byte-identical before and after: plain-word tables, tables with no lexer (`` `print(1)` `` still `1;36;40`), empty cells, partial/unfinished table, right-align/centre alignments, headings, fenced code blocks, lists and quotes. The four edge cases I expected to be risky are also unchanged: a whole-document `style="italic bright_red"` on plain cells, and a `nested_list_cell` diff clean; and where a `style="bold underline"` document *does* change a code cell (from `1;4;36;40` to theme colours), the paragraph output is byte-identical before and after and carries no `1;4` either — so the cell now agrees with the sentence, which is the stated goal:

```
=== PATCHED ===  PARA: '...tail...'  (identical in both trees)
  PARA: '\x1b[1;4mtext \x1b[0m\x1b[38;2;248;248;242;48;2;39;40;34mc\x1b[0m...'
  CELL: '...\x1b[36m \x1b[0m\x1b[38;2;248;248;242;48;2;39;40;34mc\x1b[0m...'   # now matches PARA
  (baseline CELL was '\x1b[1;4;36;40mc\x1b[0m\x1b[1;4;36;40m(\x1b[0m...')
```

The `rich-markdown` CLI was exercised end to end and shows the fix in real user terms — patched cell: `^[[97;40mprint` / `^[[93;40m"hi"` (two colours), reverted baseline cell: `^[[1;36;40mprint^[[0m^[[1;36;40m(^[[0m^[[1;36;40m"^[[0m^[[1;36;40mhi^[[0m` (one flat colour throughout).

## Verdict

VERDICT: changes_needed

## Experience difference

**What got better, and where it stops.** The ticket's example is a `print` call in back ticks inside a cell. Before this change, opening such a note gave two different readings of one identical snippet: the sentence above the table was multi-colour (token colours on the code background), and the cell was one flat tone — measured as `1;36;40` bold cyan on black for every character of `print("hi", 1)`, keyword, string, number, brackets and all. That is the "wall of one tone" the ticket complains about, and it is gone from body rows: the cell now emits exactly the same escape sequences as the paragraph (`PARA==CELL: True`), so in a cheat sheet the code words in the table stand out as much as the code words above it, and the eye can pick out a string from a number from a name without re-reading.

**The top row of the table is the remaining gap, and it is the first thing you read.** Ticket asks for both rows; only body rows arrive. With `| \`Function\` | \`len(str)\` |`, the header letters are still one cyan tone (`36`) for every token; the strip behind them now matches a code block's background instead of black, so the header looks like code but still reads like code with one colour. Net effect on a real page: the header band and the body rows no longer match each other, and a header that is a list of function signatures is still flat. Because `markdown.table.header` also strips bold, the header row loses emphasis generally, so the gap is not only about colours.

**Readability and trust.** The specific complaint — a table looking broken next to the paragraph above it — is resolved for the common case of a table full of snippets in the body. The layout itself never moved: column widths, borders, alignment markers (`---:`, `:---:`, `:---`), padding and the rule line come out byte-identical, so nothing shifts on screen while you read.

**Default, no-colour users are untouched.** Opening notes with plain `Markdown(text)` (no lexer) renders exactly as before: the cell with `` `print(1)` `` is still `1;36;40` in both trees. Only people who opted into inline code colouring see any change, and they see strictly more colour, never less.

**Everything else you could reasonably expect to stay put, does.** Plain words, links (still hyperlink-underline blue, with only the randomised link `id=` differing between runs), bold, italic, strikethrough, empty cells, a half-typed table, headings with code in them, fenced code blocks, lists and block quotes, and a whole-document `style=`: all byte-identical before and after. No document needs editing, no flag is added, none is taken away, and `rich-markdown` still takes the same choices as today. There is nothing new to learn and nothing to turn on to get this.

**What is still missing for the user in the longer term.** With no test in `tests/test_markdown.py` that combines a table with a lexer — and with the whole suite passing unchanged when the fix is backed out — the flat-colour cells can silently return and nobody's checks would notice. And the feature that makes any of this visible, `inline_code_lexer`, is not described anywhere in `docs/source/markdown.rst`, so a reader who notices dull colours in a table has nothing in the docs telling them the switch exists.

---

VERDICT: changes_needed
