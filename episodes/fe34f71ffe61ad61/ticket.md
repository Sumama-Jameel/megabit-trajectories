# Paging on Windows hides the real error behind a "file in use" message

## What happens now

When a command sends its output through a pager, the text is first written into a temporary file, and that file is handed to the pager program. The temporary file is only closed after the writing has finished successfully. If anything goes wrong along the way, the cleanup step goes straight to deleting the temporary file without closing it first. Windows refuses to delete a file that a program still holds open, so that deletion fails with a permission error about the file being in use, and that cleanup error is what the user ends up seeing instead of the actual problem.

## What should happen

When something goes wrong during a paging session, the real error should reach the user, and the temporary file should still be cleaned up. On Windows this means the temporary file is always closed before it is removed, whether the writing finished normally or not.

## About this project

Click is a Python library for building command line programs. It handles the everyday parts of a terminal program: parsing the options people type, printing help text, asking questions, showing progress bars, and sending long output to a pager such as less.

## Problem this solves

On Windows, a failure inside a command that pages its output is reported as a permission error about a file being in use, which tells the user nothing about what actually went wrong. That makes real bugs in a command very hard to diagnose, because the user is sent looking at a file problem instead of the error in their own code.

## What changed

The temporary file used for paging is now closed as part of the cleanup step, before it is removed. Previously it was closed only on the happy path, after all the text had been written. Nothing that worked before stops working: paging output still works the same way, and nothing is removed from the set of available features. The only difference is in what the user sees when something fails.

## Impact

Correctness on Windows, and clearer error messages for everyone.

## User experience

Before: a user on Windows runs a command that pages its output, and the command raises an error while the text is being written. The user gets a permission error saying a file is in use, and never sees the error their command actually produced. After: the same user runs the same command and gets their own error message, clearly and on its own, with no leftover temporary file left behind.

## Hints

- /workspace/src/click/_termui_impl.py
- /workspace/tests/test_termui.py
- /workspace/CHANGES.md