# Errors from dependency groups and metadata break when they are copied

## What happens now

Two of the errors this library raises keep useful details inside them. The cyclic dependency group error keeps the group that was asked for, the group it was found in, and the group it pointed to. The invalid metadata error keeps the name of the field that was wrong. But when one of these errors is saved away and read back — for example written to a file, sent to another program, or stored in a cache — the saved copy cannot be turned back into the same error. The details are dropped and reloading fails.

## What should happen

A person who saves one of these errors and reads it back should get the same error again. The group names and the field name should still be there, and the message should read exactly the same as before. This should work the same way for both errors.

## About this project

This project is a library that helps other tools read and check information about Python packages. It knows how to read package version numbers, requirements, dependency groups, and package metadata, and it tells the caller when something is wrong by raising errors. People building packaging tools use it so they do not have to write all of that checking themselves.

## Problem this solves

When an error is passed between programs or kept for later, it has to survive being copied. Today it does not, so people lose the reason the error happened and cannot show the original message or the group and field details to whoever needs them. This makes it hard to log errors properly or hand them from a worker to the main program.

## What changed

Both errors now come back whole after being saved and read again. The cyclic dependency group error keeps its three group names, and the invalid metadata error keeps the field name it was raised for. The messages stay the same. Two new checks were added, one for each error, that save the error out, read it back, and compare the details and the message.

## Impact

Correctness and ease of use when errors are copied.

## User experience

Before: a person catches the cyclic dependency group error, saves it, reads it back, and the restored error no longer knows which groups were involved, so they cannot re-show the original message. After: they do the same thing and the restored error has the same three group names and the same message as the one they caught. The same holds for the invalid metadata error and its field name.

## Hints

- /workspace/src/packaging/dependency_groups.py
- /workspace/src/packaging/metadata.py