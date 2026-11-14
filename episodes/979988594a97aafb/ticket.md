# Asking an argument for its help line gives nothing back when it has no help text

## What happens now

When you ask a command line argument for the line that shows up in the help page, and that argument has no help text written for it, you get nothing back at all. Nothing is returned, so there is no name and no description to show. The built-in help page still lists the argument, but only because it builds that line itself as a fallback. Anything else you write that asks an argument for its help line has to build the name and the empty description on its own.

## What should happen

Asking an argument for its help line should always give something back: the argument's name, plus its help text, or an empty description when the argument has no help text. You should never have to check for a missing answer first.

## About this project

Click is a Python library for building command line programs. You describe your commands, options and arguments in Python, and Click turns them into a working command line program, including the help page users read with the help option.

## Problem this solves

If you build your own help output, a listing of a command's arguments, or a wrapper that formats them, an argument with no help text gives you nothing, and your code has to special-case it. That is the one case you should not have to worry about, and it makes every caller longer than it needs to be.

## What changed

Arguments now always hand back their name and their description, with an empty description when there is no help text. The extra fallback line that the built-in help page built on its own is gone, so the help page still reads the same but now gets every argument's line from one place. The entry about this was added to the project's list of changes.

## Impact

Ease of use and correctness for anything that reads an argument's help line.

## User experience

Before: you write a small script that prints each argument of a command with its description. One argument has no help text, so it prints an empty line, or you add your own special handling for that one case.

After: you print each argument with its description the same way for all of them, and the argument with no help text simply shows its name with an empty description.

## Hints

- /workspace/src/click/core.py
- /workspace/tests/test_arguments.py
- /workspace/CHANGES.md