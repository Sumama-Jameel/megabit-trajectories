# The edit helper crashes when I hand it a file path object

## What happens now

When I pass a single file path object to the `edit` helper in Click, the program
stops with a TypeError saying the path object is not iterable. That message says
nothing about file names, so it gives me no clue what went wrong. If I wrap the
same path object in a list first, the helper opens the file without any problem,
so the failure only hits the single path case.

## What should happen

I should be able to hand the `edit` helper a file path object, either on its own
or inside a list, and have the file open in my editor exactly as it does when I
pass plain text file names. The helper's own description should also say that
path objects are accepted.

## About this project

This project is Click, a Python library used to build command line programs. It
provides the pieces a program needs — arguments, options, prompts, progress
bars, and helpers such as opening a file in the user's text editor — without
having to build them from scratch each time.

## Problem this solves

I keep my file locations as path objects, not as text, so I would have to convert
them to text by hand every time I want to open one in an editor. Having the
helper accept path objects directly saves that conversion and removes a
confusing crash from the middle of my program.

## What changed

The `edit` helper now accepts file path objects as well as text file names,
whether the path object is given alone or inside a list of files. The written
description of the helper now mentions that path objects are accepted, and the
release notes list this as a new thing in the unreleased 8.5.0 section. Nothing
that worked before stops working.

## Impact

Ease of use and correctness: one broken input now works.

## User experience

Before: I call the edit helper with a single path object to a file, and the
program stops with a TypeError about the path object not being iterable, with
nothing about file names in the message. After: I call it the same way and the
file opens in my editor, just as it does when I pass the same location as text.

## Hints

- /workspace/src/click/termui.py
- /workspace/src/click/_termui_impl.py
- /workspace/tests/test_termui.py
- /workspace/tests/typing
- /workspace/CHANGES.md
