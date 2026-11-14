# Colors in the pager turn themselves on for the wrong reasons, and pager options are dropped on Windows

## What happens now

When Click pages text, it decides whether to keep colors by joining the value of the LESS setting together with the options you gave and then searching that whole blob of text for the letter r or R anywhere in it. A setting such as a resume prompt, or a file name like README.md, is enough to trigger it, even though nothing asked for raw control characters. On Windows the pager is started from a temporary file and it is given only the file name, so any options you set in PAGER are dropped on the way; a pager named less.exe is also not recognised as less, because the whole file name is compared.

## What should happen

Colors in the pager should be turned on only when the invocation genuinely asks for raw control characters, such as a short r or R flag, a group of short flags containing one of those letters, or the spelled-out long option. Your PAGER options should reach the pager on every platform, including Windows, and a pager file with a suffix should count as less there.

## About this project

Click is a Python library for building command line programs. It gives you commands, groups, options and arguments, plus help pages, prompts, progress bars and a pager that opens long text in your terminal's pager.

## Problem this solves

I page long command output through my own pager settings, and on Windows the options I set are ignored, so my colors and prompts never reach the pager. On every platform, a file name or a prompt string that happens to contain the letter r silently changes the output I see, which is confusing and hard to explain.

## What changed

The temporary file pager now starts the pager with your PAGER options in front of the file name instead of the file name alone, so settings such as PAGER="less -R" are honoured on Windows. The check for raw control characters now looks at whole options rather than at raw letters anywhere in text, so file names, spelled-out long options with attached values, and option terminators no longer count, while a short flag, a group of short flags, and the bare long option still do. A pager file named less.exe is recognised as less, with letter case ignored on Windows and respected elsewhere. An unbalanced quote in the LESS setting no longer stops the check; it falls back to splitting on spaces. Nothing that worked before is taken away.

## Impact

Correctness and compatibility of the pager on Windows and with custom PAGER settings.

## User experience

Before: on Windows I set PAGER="less -R" and my output still arrives without colors, because the option never reaches the pager. On Linux, paging a file called README.md or setting a resume prompt in LESS turns on raw control characters on its own, which shows stray escape codes. After: my PAGER options reach the pager on every platform, so less -R gives me colors on Windows too, and only a real raw-character request turns them on.

## Hints

- /workspace/src/click/_termui_impl.py
- /workspace/tests/test_termui.py
- /workspace/CHANGES.md