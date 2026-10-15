# Removing colors and measuring text width miss some terminal codes

## What happens now
When colored text comes from another tool, Click does not always recognize the marks that carry the color. Some of those marks are left in the text when a user asks for plain text, so stray characters show up on screen. The same marks are also counted as real characters when Click decides how wide a line is, so styled help text wraps earlier than it should and can split in the middle of a word.

## What should happen
Click should treat the whole family of these terminal control marks as one unit. When a user asks to remove colors, none of the marks should remain. When Click measures how wide styled text is, the hidden marks should not count, so lines wrap by the number of characters a person actually sees.

## About this project
Click is a library that people use to build command-line programs in Python. It draws colored text in the terminal and wraps help text so it fits the width of the window. To do that well it has to know which characters a person can see and which are only marks that tell the terminal to change color or position.

## Problem this solves
Many tools color their output with marks that Click does not recognize, so a user who copies or pipes that text into a Click program sees leftover junk or lines that break in the wrong place. The user needs the colors gone no matter which tool wrote them, and the text laid out by what is actually visible.

## What changed
The set of marks the program recognizes is now the full family of terminal control sequences instead of just the simple color forms. Every mark that was removed before is still removed, so nothing that used to work stops working. Nothing a person can see on screen is treated as a hidden mark.

## Impact
Correctness and ease of use of colored output and wrapped help text.

## User experience
Before: a user prints a line that another tool colored with the newer colon style, and leftover bracket characters appear on screen while the line wraps sooner than it should. After: the same line shows as plain text with no leftover characters, and it wraps by the number of characters a person actually sees.

## Hints
- /workspace/src/click/_compat.py
- /workspace/src/click/_textwrap.py
- /workspace/tests/test_compat.py
- /workspace/tests/test_utils/test_style.py
- /workspace/tests/test_formatting.py