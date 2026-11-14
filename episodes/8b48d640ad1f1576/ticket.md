# I can only check keys and values together, not just one of them

## What happens now
When I check a dictionary, I have to give both a check for the keys and a check for the values. If I only care about the keys, or only about the values, the tool still makes me supply the other one. Leaving the other one out stops me right away with an error, so I cannot get past it.

## What should happen
I should be able to give just a check for the keys, or just a check for the values. When I give only one, the dictionary is checked with that one. Only when I leave out both should I get a clear message telling me to provide at least one of them.

## About this project
This project is a Python library that helps people describe the data their programs use. It lets you attach checks to the data so bad values are caught early instead of causing trouble later. One of those checks looks inside a dictionary and checks its keys and its values.

## Problem this solves
When I only care about one side of a dictionary, I am forced to write a throwaway check for the other side just to keep the tool happy. That is extra work and extra noise for something I do not need.

## What changed
The check for the keys and the check for the values can now each be left out on their own. Giving only one of them works and the dictionary is checked with it. Giving neither gives a clear error. Before, both were required every time.

## Impact
Ease of use and less busywork.

## User experience
Before, if I wanted to check only that the keys of a dictionary are text, I also had to write a check for the values, even though I did not care about them. After, I give just the key check, and the dictionary is checked with no extra work on my part.

## Hints
- /workspace/src/attr/validators.py
- /workspace/src/attr/validators.pyi
- /workspace/tests/test_validators.py
- /workspace/tests/typing_example.py