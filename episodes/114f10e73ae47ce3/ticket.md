# I cannot put my own check first or second when I join it with a ready-made retry rule

## What happens now
Joining a ready-made retry rule with my own check only works in one order. When my own check comes first and the ready-made rule comes second, the join works. When the ready-made rule comes first and my own check comes second, the library passes the work to the other side and expects that side to know how to deal with it. My own check does not know how to do that, so the join does not work. The same thing happens for both kinds of join, the one that means "both must agree" and the one that means "either one is enough".

## What should happen
I should be able to join a ready-made retry rule with my own check in either order, using both kinds of join, and get the same behavior. The order I write them in should not decide whether it works.

## About this project
Tenacity is a small helper for Python programs that repeats an operation when it fails. It lets people say how many times to try, how long to wait between tries, and which failures count as worth another try. It also comes with ready-made rules for common situations, and people can add rules of their own.

## Problem this solves
People who already have their own way of deciding when to try again cannot freely mix it with the ready-made rules, because one order works and the other does not. That forces them to rearrange their code or write extra code of their own just to get the two rules to work together.

## What changed
The new version lets a ready-made retry rule be joined with my own check in both orders, for the join that means "both must agree" and for the join that means "either one is enough". Everything that worked before still works the same way, and nothing was taken away.

## Impact
Ease of use and consistent behavior.

## User experience
Before: I write my own check first and the ready-made rule second, and my code runs. When I swap the two around, it breaks and I have to work out why. After: I can write the ready-made rule first or my own check first, and my code runs and behaves the same either way.

## Hints
- /workspace/tenacity/retry.py
- /workspace/tests/test_tenacity.py
