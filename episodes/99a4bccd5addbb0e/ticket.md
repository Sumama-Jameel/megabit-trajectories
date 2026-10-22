# Packages that spell the letter set for their description as small letters are turned away

## What happens now

When I read the details of a package and its description says the letter set is written as "utf-8" in small letters, the tool refuses it and reports an error saying that only UTF-8 is allowed. Only the exact spelling "UTF-8" in capital letters is let through, even though "utf-8" and "Utf-8" mean the very same thing.

## What should happen

The way the letters are capitalized should not matter. I should be able to read package details no matter whether the letter set is written as "utf-8", "Utf-8", or "UTF-8", and the value should be kept as the package wrote it.

## About this project

This project gives people a set of tools for reading and checking the information that describes a Python package, such as its name, version, and the text that explains it. It reads those details and either hands them back clearly or explains what is not allowed. People use it to look at packages before trusting or shipping them.

## Problem this solves

Many real packages write the letter set in small letters, and they are perfectly fine packages. Today the tool turns those packages away and shows an error, which blocks me from reading and using details that are actually valid.

## What changed

Now the spelling of the letter set no longer matters: small letters, mixed letters, and capital letters are all treated the same way and accepted. The old behavior of only accepting the capital-letter spelling is gone. The examples that come with the project now show "utf-8" and "Utf-8" as accepted and no longer list "utf-8" as an error.

## Impact

Correctness and ease of use.

## User experience

Before: I read a package whose description says "text/plain; charset=utf-8", and I get an error telling me that value is not allowed. After: I read the very same package and it works, with the description kept just as the package wrote it.

## Hints

- /workspace/src/packaging/metadata.py
- /workspace/tests/test_metadata.py