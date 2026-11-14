# Long command descriptions are dropped from the command list instead of being shortened

## What happens now
When a tool has a command whose description has no short version, the command list shows nothing next to that command. If the opening part of the description is longer than the allowed limit, the text is thrown away, so the command appears with a blank line beside it. If there is no full stop in the opening part, the same thing happens and the command still shows nothing.

## What should happen
The command list should always show a short line for each command. When the description is long, the list should show the first part of it, cut off cleanly, with a small marker at the end to show the text continues.

## About this project
This project is a toolkit for building command line tools in Python. It helps people describe commands, options, and arguments, and it prints the help text that users see. The command list is the part of that help text that names each command along with a short line about what it does.

## Problem this solves
A person running a tool with several commands cannot tell what the commands do when the short lines are missing. They have to open the full help for each command one by one to find the one they want, which is slow and confusing.

## What changed
Commands that used to appear in the list with a blank short line now show a shortened line instead. Long descriptions get cut off and end with a small marker showing there is more text. Descriptions that end within the limit are shown in full, keeping their final full stop. Nothing that used to work stops working.

## Impact
This is a ease of use change. It improves how readable the command list is and how quickly a person can pick the right command.

## User experience
Before: a person runs a tool with several commands and sees the command names with empty short lines beside some of them, so they cannot tell which command does what. After: the same person runs the tool and sees a short, readable line beside every command, with long ones cut off and marked, so they can spot the command they need right away.

## Hints
- /workspace/click/core.py
- /workspace/click/utils.py
- /workspace/tests/test_commands.py
