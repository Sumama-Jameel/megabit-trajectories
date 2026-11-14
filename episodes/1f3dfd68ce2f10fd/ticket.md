# Disabling retries

## What happens now
If I want to retry an operation, I have to set up the retry mechanism every time. There is no way to disable retries when I don't need them.

## What should happen
I should be able to disable retries when I need to, by passing enabled=False to the retry decorator or the BaseRetrying class.

## About this project
This project is a Python library that helps you retry operations that might fail. It's useful for handling temporary failures in network requests, API calls, and other operations.

## Problem this solves
Sometimes I need to test or debug operations without retries. Having the ability to disable retries makes it easier to get quick feedback on failures.

## What changed
Now I can disable retries by passing enabled=False to the retry decorator or the BaseRetrying class. This gives me more control over when retries are used.

## Impact
The new behavior improves flexibility and ease of use.

## User experience
Before: I have to set up the retry mechanism every time I want to retry an operation. After: I can disable retries when I need to by passing enabled=False to the retry decorator or the BaseRetrying class.

## Hints
- /workspace/tenacity/__init__.py
- /workspace/tenacity/asyncio/__init__.py