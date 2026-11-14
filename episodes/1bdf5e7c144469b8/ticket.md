# Turning off the wait, or joining waits together, makes a retry blow up

## What happens now

When I tell my retry not to wait between attempts, my code blows up with a type error. This happens when I pass nothing at all for the wait, when I pass the number zero, and when I build the wait from an empty list of waits. The unhappy part is the timing: my code runs fine through the first attempt, and the error only appears the first time a retry actually happens. The same trouble hits the async version of the helper.

There is a second problem. When I try to join a plain wait function with a wait setting and put the plain function first, it errors instead of joining them. The number zero is allowed in that spot, but a plain function is not.

There is a third problem with joining. When waits are joined together, each piece is asked for the retry state using a name. A plain wait function is only promised to take that value in the first position, so a function whose label is named differently fails.

## What should happen

A wait value that means "nothing" should simply mean "retry straight away". This should hold for nothing at all, for zero, and for an empty list of waits, in both the normal and the async retry helpers. A plain wait function should join with a wait setting from either side, not just one. When waits are joined, each piece should be asked for the retry state by position, so functions with differently named labels work.

## About this project

This project is a small helper library for Python that runs a piece of code again when it fails. It lets people say how many times to try, how long to wait between tries, and what to do when a try gives up. It is used wherever a network call or a file operation can fail for a moment and work on the next try.

## Problem this solves

People who deliberately want no delay between tries get a crash at the exact moment a retry finally fires, so their code looks healthy until they need it most. Joining waits is how people build up their own delay plan, and today that path breaks for plain wait functions, which pushes people away from a feature they need.

## What changed

A wait value that means nothing is now honored as no wait, for both the normal and the async retry helpers. A plain wait function can now be joined with a wait setting from either side. When waits are joined, each piece is now asked for the retry state by position rather than by name.

## Impact

Correctness and ease of use, with no new demand on the person using the library.

## User experience

Before: I set my retry to not wait, my first attempt fails, and the first retry stops with a type error. After: I set the same retry to not wait, my first attempt fails, and the retry runs straight away with no delay and no error.

## Hints

- /workspace/tenacity/wait.py
- /workspace/tenacity/__init__.py
- /workspace/tenacity/asyncio/__init__.py
- /workspace/tests/test_tenacity.py
- /workspace/tests/test_asyncio.py
