# Turning retries off does not work when I run my retry object directly

## What happens now

I can turn retrying off with the off switch when I use the decorator or when I step through the retry object myself. But if I build a retry object and call it with my own function, the off switch is ignored. It keeps trying the function again and again, and when it finally gives up I get the library's own "too many retries" error instead of the error my function raised. The same thing happens with the version for async code. The current tests only cover the decorator and the step-by-step way, so this gap is not caught today.

## What should happen

When the off switch is set to off, calling a retry object directly with my function should run my function exactly one time. If my function returns a value, I should get that value back. If my function raises an error, I should get that same error back, not a wrapped retry error. A single call should happen for both plain functions and async functions.

## About this project

This is a Python library that helps people run a piece of work again when it fails, for example when a network call or a file read does not work on the first try. It lets people set how many times to try, how long to wait between tries, and which errors are worth trying again. It also has an on/off switch so retrying can be turned off, for example while learning or while running somewhere retries are not wanted.

## Problem this solves

People who write their own loop around the retry object expect the off switch to mean "just run it once". Today the switch silently does nothing in that case, so their program sits and waits through repeated tries and then shows a confusing error that hides the real failure.

## What changed

The off switch is now respected when a retry object is called directly with a function. With the switch off, the function runs one time, its own result comes back, and its own error comes back as is. The async retry object does the same and waits for the async function once. Nothing else is different: the decorator and the step-by-step way work as they did before, and with the switch on, retrying works as usual.

## Impact

Correctness and ease of use.

## User experience

Before: I turn the switch off, call my retry object with a function that fails, and it tries several times, waits between tries, and raises a "too many retries" error. After: with the switch off, the function runs once, and I see the exact error my own function raised, straight away.

## Hints

- /workspace/tenacity/__init__.py
- /workspace/tenacity/asyncio/__init__.py
- /workspace/tests/test_tenacity.py
- /workspace/tests/test_asyncio.py