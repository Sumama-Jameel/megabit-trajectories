# Building an empty chain of wait steps gives a confusing error

## What happens now
In the waiting file tenacity/wait.py, the wait_chain choice lets me line up several wait times to use one after another. If I build a chain with no steps at all, nothing complains when I build it. The trouble shows up later, the first time a retry actually waits: it looks for a step that is not there and stops with an index error that does not say what is wrong.

## What should happen
When I build a chain with no wait steps, I should be told right away, in plain words, that a chain needs at least one step. The same clear message should reach me when I hand such a chain into a retry, instead of a late index error while the retry runs.

## About this project
Tenacity is a small helper library for retrying actions that can fail. It lets people say how many times to retry, which failures count, and how long to wait between tries. One of the waiting choices is a chain, which uses a list of wait times in order.

## Problem this solves
When a chain is built with no steps by mistake, the error arrives late and points at an unrelated spot, so the person spends time hunting for the real cause. A clear complaint at the moment the chain is built saves that confusion.

## What changed
Building a chain with no wait steps now stops right away with a clear message that a chain needs at least one step. Before, an empty chain was accepted quietly and only failed later during a retry. Chains with one or more steps behave the same as they did before.

## Impact
Ease of use and clearer mistakes.

## User experience
Before: I build a chain with no steps and use it in a retry, and the retry later stops with an index error that does not explain the cause. After: the moment I build the empty chain, I am told in plain words that it needs at least one step.

## Hints
- /workspace/tenacity/wait.py
- /workspace/tests/test_tenacity.py
