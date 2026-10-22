# The positional arguments list in the help page leaves out arguments that have no description

## What happens now

When a command takes several positional arguments and only one of them has a description, the help page shows only that one argument under "Positional arguments". The other positional arguments are missing from the list, even though they still show up in the usage line at the top of the help page. So the list and the usage line do not match, and a person reading the help cannot see every positional argument the command takes in one place.

## What should happen

As soon as one positional argument has a description, the "Positional arguments" list should show every positional argument the command takes. The ones without a description should still appear, with a blank description next to them. If none of the positional arguments has a description, the list should stay hidden, just as it does today.

## About this project

This project is a toolkit for building command line programs in Python. It lets a programmer describe the options and arguments a command takes, and it then builds the built-in help text, parses what the person typed, and reports errors. People who use those programs see this help text every time they run the program with the help flag.

## Problem this solves

A person reading the help page cannot see all the positional arguments a command accepts, so they have to guess the missing ones from the usage line. That makes the help text feel incomplete and forces people to look elsewhere for what the command needs.

## What changed

The "Positional arguments" list now matches the usage line. Once any one positional argument has a description, all of them are listed, and the ones without a description show a blank space next to them. When no positional argument has a description, no list appears, the same as before.

## Impact

Ease of use and a correct, complete help page.

## User experience

Before: a command takes three positional arguments and only the middle one has a description. The help page lists one argument, and the person using the program wonders what the other two are for.

After: the same command's help page lists all three positional arguments, with the two undescribed ones shown as blank, so the list lines up with the usage line above it.

## Hints

- /workspace/src/click/core.py
- /workspace/docs/arguments.md
- /workspace/docs/documentation.md
- /workspace/tests/test_arguments.py