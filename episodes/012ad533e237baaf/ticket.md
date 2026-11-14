# No way to get the ABI part of the tag for the interpreter I am running

## What happens now
The library gives me a helper for the name of the running interpreter and a helper for its version, and both are listed in the module's list of names. There is no matching helper for the ABI part. The two internal helpers that do know about ABIs are marked with a leading underscore and are not written up anywhere, so I have to reach into those hidden names and work out the answer myself.

## What should happen
I should be able to ask the library for the ABI label of the interpreter I am running and get back the same text that appears in a full tag, so I can build or compare tags without any guesswork.

## About this project
This project is a small library of helpers that Python people use to work with package names, version numbers, environment markers, and the tags that describe which Python builds a package can be installed on. The tags part in particular is what tools read to decide which wheels are usable on the machine they are standing on.

## Problem this solves
A tag has three parts: interpreter, platform, and ABI. Two of the three are easy to get today, so anyone who needs the third one has to dig through hidden helpers or read the interpreter configuration themselves. That is extra work and easy to get wrong, especially on interpreters other than CPython.

## What changed
A new helper, called interpreter_abi, is now part of the public names of the tags module, sitting next to interpreter_name and interpreter_version. It reports the ABI label of the running interpreter: on CPython it is the name and version joined together, and on other interpreters such as PyPy it is derived from the interpreter's own extension suffix. The tags documentation page now lists it in the same way the other helpers are listed, and there is a check that covers both the CPython case and the PyPy case. Nothing was taken away; the existing helpers behave exactly as before.

## Impact
Ease of use, and a small step towards completeness of the public helper set.

## User experience
Before: to learn the ABI label of my own interpreter I had to reach for a hidden helper with an underscore in its name, work out which of the two internal generators applied to my interpreter, and assemble the answer by hand. After: I ask the module for the ABI of the running interpreter and get the ready-made label back, the same value that shows up in the ABI slot of a full tag.

## Hints
- /workspace/src/packaging/tags.py
- /workspace/docs/tags.rst
- /workspace/tests/test_tags.py
