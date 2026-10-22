# Saved version answers get thrown away when rules are tidied

## What happens now

When I give a group of version rules and then ask for it as text, the tool tidies the rules by removing repeats and putting them in order. While tidying, it also clears two answers it had already worked out: the answer to "can any version ever match this group" and the answer to "which version ranges does this group cover". The next time I ask whether a version matches, the tool has to work both answers out again from scratch. So a simple request for the text of my rules quietly undoes work the tool had already done.

## What should happen

After the tool tidies my group of version rules, the answers it already worked out should stay in place. Asking for the text of the group should not clear them. When I then check a version, or repeatedly check versions against the same group, the tool should reuse the answers it already has instead of working them out again.

## About this project

This project is a Python library that helps people work with version numbers and version requirements, such as the ones written in a package file. It can compare versions, read the rules that describe which versions are allowed, and tell you whether a given version fits those rules. Many other tools depend on it, so it needs to give fast and consistent answers.

## Problem this solves

When the tool throws away answers it already worked out, every later version check on the same group of rules costs extra time and effort for no reason. People who check many versions against the same rules pay that cost again and again, and they get no benefit from it.

## What changed

The step that tidies a group of version rules no longer clears the two saved answers. Nothing was removed from what I can do: the rules are still made free of repeats and still put in order, and the text I get back is the same. The only difference is that the answers about never-matching groups and about version ranges survive the tidying instead of being wiped out.

## Impact

Speed and consistent answers.

## User experience

Before: I build a group of version rules, check a version against it, then ask for the group as text, and check another version. The text request wipes out the saved answers, so the second check works everything out again. After: I do the same steps, and the second check reuses the answers that were already worked out, so it is faster and gives the same result.

## Hints

- /workspace/src/packaging/specifiers.py
- /workspace/tests/test_specifiers.py