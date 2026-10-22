# My help option names come back in a mixed-up order

## What happens now
When I give my command more than one name for the help option, the names come back in
a mixed-up order instead of the order I wrote them. If I write the names as short one
first and long one second, the program may show them the other way around. The order
can be different from what I asked for, so I cannot rely on it.

## What should happen
The help option names should stay in the same order I wrote them. If I write the same
name twice, only the first one should be kept. Names that another option already uses
should still be left out. I should be able to set the names and then see them exactly
as I arranged them.

## About this project
This project is a tool for people who build command-line programs in Python. It takes
care of reading the options a user types, printing the help text, and showing errors.
People use it so they do not have to write all of that themselves.

## Problem this solves
People who pick their own short and long names for the help option get them back in a
random order, so the help text can look wrong and confuse the people using their
program. This matters most when a name they chose clashes with another option and the
leftover names come out shuffled.

## What changed
The help option names now keep the order in which they were given. Names that appear
more than once are trimmed so the first one stays. Names that another option already
uses are still removed. Before, the order was lost; now it is kept.

## Impact
Ease of use and correctness.

## User experience
Before: I set the help names as the short one first and the long one second, and the
program sometimes shows them swapped. After: I set the same two names and they show up
exactly in that order every time.

## Hints
- /workspace/src/click/core.py
- /workspace/tests/test_commands.py
- /workspace/CHANGES.md