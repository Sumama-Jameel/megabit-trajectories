# No way to get an option's short name text when the option is hidden

## What happens now

If I mark an option as hidden, there is no way to ask that option for its own short name text, the part that reads like "-c, --config TEXT" on a normal help screen. The only way to build that text is the help record call, and that call gives nothing back at all for a hidden option, so the left column is lost too.

## What should happen

I should be able to ask any option, hidden or not, for just its name text, without also asking for the description beside it. That name text should match what a normal help screen shows for that option.

## About this project

Click is a Python library for writing command line programs. You describe your options and arguments in a script, and Click turns them into a working program with help screens, prompts and error messages that look the same on every operating system.

## Problem this solves

I am writing a wrapper that lists a command's options in my own help screen, and some of those options are hidden so they stay out of the standard help. I still need to name them in my own screen, so today I have to copy the name-building logic out of the library into my program, which gives different text from the real help screen and breaks again whenever the library changes.

## What changed

A new way to ask a single option for its name text was added. It returns the option's spellings together with its value placeholder, and it works even when the option is hidden. The existing help record call now gets that text from the same place, so it gives back exactly the same name text as before and still gives nothing for a hidden option. Nothing was removed.

## Impact

Ease of use, and correctness of help output. Ordinary help screens look exactly the same as before.

## User experience

Today: I mark my config option as hidden, ask it for its name text, get nothing back, and copy the name-building logic into my own code so I can print something. After: I mark it as hidden, ask it for its name text, and get back the same "-c, --config TEXT" text that a normal help screen would show, with nothing copied into my code.

## Hints

- /workspace/src/click/core.py
- /workspace/tests/test_options.py
- /workspace/CHANGES.md