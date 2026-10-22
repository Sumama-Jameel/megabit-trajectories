# Black as color number 0 is ignored, and other wrong colors are not reported clearly

## What happens now

When I choose a color for my text by giving the number 0, which is black, nothing happens. The text shows up with no color at all, and there is no warning that my choice was skipped. The same happens with an empty color value.

Numbers that are outside the allowed range, like 300 or a minus number, are accepted as if they were fine and end up showing nothing useful. The words true and false, when given as a color, are treated as the numbers 1 and 0 instead of being refused.

A color name that is not known does stop with a message that says the color is unknown. But a group of numbers that is the wrong shape, such as only two numbers, four numbers, or three numbers written as text, stops with a confusing internal message about too many values, too few values, or a bad format, instead of saying that the color is unknown.

## What should happen

The number 0 should show real black for both the text color and the background color.

A value should only be accepted if it is a known color name, a whole number from 0 up to 255, or three whole numbers each from 0 up to 255.

Any other value should stop with one single, clear message that says the color is unknown. That covers empty values, unknown names, text written in capital letters, true and false, minus numbers, numbers above 255, decimal numbers, groups with the wrong count of numbers, and groups that hold text instead of numbers.

## About this project

Click is a helper library for building command-line programs in Python. It gives people ready-made pieces such as options, prompts, progress bars, and colored output. One of those pieces lets a program put color and style on text it prints to a terminal.

## Problem this solves

Someone who wants black text or a black background picks the lowest color number and sees nothing happen, so their carefully chosen color is lost without a word. And when they get a color value wrong, the message they see talks about the shape of the numbers rather than telling them plainly that the color is not a real color, which sends them looking in the wrong place.

## What changed

The number 0 now shows black instead of being skipped, for both text and background.

Bad color values now all stop with the same clear message saying the color is unknown, rather than some being waved through, some being read as a number, and some failing with an internal message about the shape of the numbers.

The kind of error raised for a color that is not known is different from before, so anyone who watches for that specific error should take note.

## Impact

Ease of use and correctness: a color that was silently dropped now works, and a wrong color now gives one clear message instead of a confusing one. There is also a small compatibility effect on the kind of error raised.

## User experience

Before: I ask for black text by giving the color number 0 and the text comes out with no color, with no hint that my choice was ignored. After: the same number 0 turns the text black.

Before: I give only two numbers for an RGB color and get a message about not enough values to unpack. After: I get one plain message that tells me the color is unknown.

## Hints

- /workspace/src/click/termui.py
- /workspace/tests/test_utils/test_style.py
- /workspace/CHANGES.md
