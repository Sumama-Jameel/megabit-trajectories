# Colored Bits of Inline Code Go Flat Inside Table Cells

## What happens now

Rich can color the short pieces of code you write between back ticks inside a
markdown document, once you switch that coloring on when you create the
markdown. It works fine in ordinary sentences and in headings: a word like
print comes out in one color, quoted text in another, and the whole thing sits
on a light background so it clearly reads as code.

It does not work the same way inside a table cell. The very same piece of code
in a table row comes back with exactly one flat color. Every word, every
number and every quoted piece looks the same as every other piece, and the
plain code background wins over everything else. The usual colors for code are
simply gone, only in tables.

## What should happen

A piece of code inside a table cell should look the same as that same piece
inside a sentence. The colors picked for keywords, words and quoted text should
survive the trip into the table, so a table full of code snippets is just as
easy to read as the paragraph above it. Tables with plain words keep looking
exactly as they do today.

## About this project

Rich is a Python library for writing nice looking things in the terminal:
colors, tables, progress bars, logs and syntax colored source. It also draws
markdown for you, which is how the command rich-markdown turns a notes file
into something readable in a terminal window. Markdown documents hold both
tables and little snippets of code, and Rich is meant to show them side by
side, in color.

## Problem this solves

People write notes, cheat sheets and command references where the important
part lives inside a table cell. When those cells lose their colors, the table
turns into a wall of one tone and the eye can no longer pick out the words that
matter, which is exactly the job you bought a colored terminal writer for.

## What changed

Colored short pieces of code keep their colors when they land inside a table
cell, in both the heading row and the body rows. Colors stop being flattened
anywhere in a markdown table. Nothing else about tables changes: plain words,
links, bold, italics, headings, code blocks and whole-document colors look the
same as before, and the rich-markdown command keeps taking the same choices it
takes today.

## Impact

Ease of use and correctness of what you see. The colors you asked for now
arrive in tables the same way they arrive in sentences. No setting is added and
none is taken away, so documents and tables written today keep working.

## User experience

Here is a small example of the difference.

Before: I put the word for a print call, written between back ticks, in a cell
of a table in my notes, and I show the file in the terminal. The cell shows
that word in a single dull color, with a gray block behind it, while the same
word in the sentence above the table shows up in several colors. The table
looks broken next to the sentence.

After: I do the same thing and the cell shows that word with the same several
colors as the sentence, so my notes read evenly top to bottom and the code
words in the table stand out just as much as everywhere else.

## Hints

- rich/markdown.py
- tests/test_markdown.py
- rich/text.py
- rich/syntax.py
- docs/source/markdown.rst
