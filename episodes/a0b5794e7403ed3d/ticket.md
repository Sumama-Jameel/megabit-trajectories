# An empty list of platforms is ignored when building wheel tags

## What happens now
When I ask for wheel tags and hand in an empty list of platforms, the empty list is treated as if I had not given any platforms at all. The tool then quietly fills in the platforms of the computer I am running on, so I get tags for my own machine even though I asked for none.

## What should happen
If I hand in an empty list of platforms, I should get no platform tags back. If I leave the platforms out completely, I should still get the platforms of the computer I am running on, exactly as before.

## About this project
This project is a library for dealing with Python package names, version numbers, and wheel tags. A wheel is a ready-to-install package file, and a wheel tag is the short label that says which computers and which Python versions that file fits. The library works out these tags so the right package file can be picked for the computer that needs it.

## Problem this solves
I sometimes work out tags for a target that has no platforms at all, and I get back unrelated tags for my own computer instead. That makes the answer wrong and can lead a tool to pick package files that do not belong to the target I care about.

## What changed
An empty list of platforms now means an empty list, so no platform tags are produced from it. Leaving the platforms out still means "use this computer", and the tags I get in that case are the same as before. All of the platform names and tag labels that were there before are still there.

## Impact
Correctness and predictability of the tags you get back.

## User experience
Before: I hand in an empty list of platforms and I get back tags for the computer I am running on, even though I asked for none. After: I hand in the same empty list and I get back no platform tags at all, while leaving the platforms out still gives me the tags for my own computer.

## Hints
- /workspace/src/packaging/tags.py
- /workspace/tests/test_tags.py