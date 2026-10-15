# I cannot ask for just the pure-Python wheel tags

## What happens now

There is no way to ask only for the tags that work everywhere, without also being told about the machine I am on. The one helper that hands out those tags also checks the running computer and gives back entries tied to that computer. It is not listed on the tags page of the documentation either, and nothing in the tests mentions it.

## What should happen

I can ask for only the pure-Python tags, meaning the ones built from a Python version plus the none and any parts. I get the same answer on every computer, and I can give it a version I choose or let it use the version of the running Python. If I give it a version with nothing in it, I get a clear message telling me the version must have at least one item instead of an unclear failure.

## About this project

This is a library that reads and works out Python compatibility tags. A tag is the three-part label in a wheel filename that says which Python, which ABI, and which operating system the wheel works with. Tools use it to decide which wheel files can be installed on a given computer.

## Problem this solves

People who build or check wheels that work everywhere only care about the portable tags, but today they get a mix that also depends on the computer they happen to be running on, so they have to pick the portable ones out by hand every time.

## What changed

The new version offers a way to ask for just the portable tags, and the tags page of the documentation now shows it next to the other low-level helpers. The wider helper that also looks at the running computer now gets its portable part from this same place, so the two stay in step. Nothing was taken away.

## Impact

Ease of use and correctness: a smaller, computer-independent answer plus a clear message when the given version is empty.

## User experience

Before: I want only the portable tags, so I call the wider helper and get a long list where many entries name my computer's operating system; I then sift out the portable ones myself.

After: I ask for the portable tags and get only the short list of py plus none plus any entries, the same on every computer, and the page that lists the helpers shows me this one.

## Hints

- /workspace/src/packaging/tags.py
- /workspace/docs/tags.rst
- /workspace/tests/test_tags.py