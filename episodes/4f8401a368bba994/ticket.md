# Paging output can keep colour codes when I asked for none, can close my terminal output, and can fail on non-English text

## What happens now

When I ask Click to send my long output through a pager, the colour cleanup only happens when a pager program is really running. If no pager is found, or my output is not going to a terminal, Click writes the text out as-is and the colour codes stay in the text, even though I asked for plain text. The same page-through helper also hands me back a stream that sits on top of my normal output, so if that stream gets closed, my usual output is closed with it and later prints fail. On Windows, and on the no-pager path everywhere, the text is written to a temporary file using whatever character set the machine happens to use, so text my terminal can display can still raise an encoding error there.

## What should happen

Asking for plain output means plain output on every paging path, including the fallback that writes straight to the terminal. Closing what the pager gives me must never close my own output stream. The temporary-file path should write text the same way the pipe path does, using the encoding that matches my output and swapping out characters it cannot represent instead of failing.

## About this project

Click is a Python library for building command line programs. It gives you commands, options, prompts, progress bars, and helpers such as sending long output to a pager like less or more. The pager helper is what makes long help text or long reports easy to scroll through.

## Problem this solves

I build tools that print long reports, and I need the output to stay readable when it is piped into a file or a log. Right now I get stray colour codes in my saved files, and on Windows my script can crash on text that works everywhere else, so I have to keep text ASCII-only as a workaround.

## What changed

Colour codes are now removed on the no-pager path too, matching the running-pager path, so the colour setting is honoured everywhere. The stream the pager hands back no longer closes the output underneath it when it is closed itself. The temporary-file path now writes with the same encoding as the pipe path and replaces characters it cannot encode rather than raising an error.

## Impact

Correctness and reliability: plain output is guaranteed on every paging path, my own output stream is safe from being closed, and non-English text no longer fails on Windows.

## User experience

Before: I run my program with colours turned off and redirect the output to a file. The file contains stray escape sequences that make it look messy, and on Windows the same run can stop with an encoding error on accented or non-Latin characters. After: the saved file is clean plain text, my program's normal output keeps working after the pager finishes, and the same accented or non-Latin text is written out fine on Windows.

## Hints

- /workspace/src/click/_termui_impl.py
- /workspace/src/click/_compat.py
- /workspace/src/click/utils.py
- /workspace/tests/test_termui.py
- /workspace/tests/test_utils/test_echo_via_pager.py
- /workspace/CHANGES.md