# My field helper cannot tell an automatic name from one I picked myself

## What happens now

When I write a helper that looks at each field of my class, the fields I get do not yet have their automatic names filled in. The name slot is empty for any field whose name I did not set by hand. Because the slot is empty, I cannot tell a field that got its name automatically apart from a field that simply has no name yet. There is also no simple flag on a field that tells me whether its name was chosen for me or chosen by me.

## What should happen

When my helper looks at each field, every field should already have its name filled in, whether I set it myself or it was chosen for me. Each field should also carry a clear flag that is true when the name was chosen automatically and false when I set it myself. That way my helper can make decisions based on that flag instead of guessing from an empty value.

## About this project

This project is a library that helps people write small classes that mostly hold data. Instead of writing lots of repetitive setup code by hand, a person describes the fields they want and the library writes the boring parts for them. It is used widely in Python programs to keep data-holding classes short and clear.

## Problem this solves

People who write helpers that adjust fields need to know which names were picked automatically, so they can replace or keep them without touching the names they chose themselves. Today they cannot tell the two apart, so they either overwrite names they wanted to keep or miss names they wanted to replace.

## What changed

Fields now arrive at a person's field helper with their automatic names already in place, instead of arriving empty. Each field also gains a flag that says whether its name was chosen automatically or set by hand. The old habit of checking for an empty name to detect an automatic one no longer matches how the fields arrive.

## Impact

Ease of use and correctness for people who write field helpers.

## User experience

Before: I write a helper that checks whether a field's name is empty to decide it was chosen automatically, but fields I named by hand and fields named for me both look the same in some cases, so my helper gets it wrong. After: I read the new flag on each field, and it plainly tells me whether the name was chosen for me, so my helper does the right thing every time.

## Hints

- /workspace/src/attr/_make.py
- /workspace/docs/extending.md
- /workspace/tests/test_functional.py
- /workspace/tests/test_hooks.py
- /workspace/tests/test_make.py
- /workspace/tests/utils.py
