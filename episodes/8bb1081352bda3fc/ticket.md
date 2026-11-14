# No way to ask for a UUID option, so my command gets raw text and I check it myself

## What happens now

There is no way to tell a command that an option holds a UUID like `821592c1-c50e-4971-9cd6-e89dc6832f86`. I ran the current version and asking for a UUID value gives an error saying there is no such attribute. Every UUID my command receives is the plain text the user typed, so my command has to check each value by hand and write its own message when the text is wrong. The help text also never mentions UUID, so users have no idea what shape the value should take.

## What should happen

I should be able to say that one of my options takes a UUID, in the same way I already say an option takes a string, a number, or a true-or-false value. Then the value that reaches my command is a real UUID, and text that is not a valid UUID is turned away at once with a message that names the option and shows the bad text.

## About this project

Click is a Python library for writing command line programs. You describe the commands and the options they take, and Click reads what the user typed, turns it into the right Python values, and shows help text and error messages for you.

## Problem this solves

Without this, every command that takes a UUID must repeat the same check and the same error message for each option it has. I want the checking and the message to come from the same place that already handles strings, numbers, and booleans, so my command only receives values that are already correct.

## What changed

A value called UUID is now available next to the ready-made values for text, whole numbers, decimal numbers, and true-or-false. An option that uses it gives the command a real UUID instead of a line of text. Input that is not a valid UUID is refused with a message such as `Invalid value for "--u": bar is not a valid UUID value`. The help text names the value `uuid`, in the same style as `integer`, `floating point`, and `boolean`. Nothing was taken away: the existing values and their messages stay the same. The two documentation pages that list the available values now mention the UUID one, and the test file now checks that a UUID option accepts a good value, accepts one typed on the command line, and turns away a bad one.

## Impact

Ease of use and correctness: fewer lines of checking in each command, values arrive ready to use, and bad input is reported the same way as every other option.

## User experience

Today I write an option, run my program, and whatever the user typed arrives as text, so my own check decides whether the program continues or prints an error that only my code knows about. After the change I mark that option as a UUID, the value reaches my command as a UUID ready to use, and if someone types `bar` the program stops before my command runs and says `Invalid value for "--u": bar is not a valid UUID value`, the same way a bad number is reported today.

## Hints

- /workspace/click/types.py
- /workspace/click/__init__.py
- /workspace/docs/api.rst
- /workspace/docs/parameters.rst
- /workspace/tests/test_basic.py
