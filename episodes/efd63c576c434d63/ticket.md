# Version numbers written in the usual loose styles are turned away

## What happens now

Today the version reader accepts only one narrow spelling of a release name. It insists on a dot before the word dev and insists on a number after it, so the version one point zero with dev right after the zero is refused. It insists on a number after a pre-release letter, so one point zero followed straight by the letter a is refused, and so is one point zero followed by the letters r and c. The letter must sit right next to its number with nothing in between, so a version with a dot, the letter a, another dot, and the number one is refused as well. The long words alpha and beta are not known, and capital letters are refused, so a version with the word alpha spelled out is turned away, and so is one with capital r and capital c. The same narrow rules apply inside requirement lines, so asking for at least one point zero with dev after it fails. A label after a plus sign must be all lower case, so one point zero plus a single capital letter is refused too.

## What should happen

I should be able to hand it any of the spellings people really write and get back the same version in its plain short form. A missing number after dev or after a pre-release letter should count as zero. Capital letters and the long words alpha and beta should be accepted, and a label after a plus sign should be accepted whether it is written with capital letters or small ones. Requirement lines that use these looser spellings should pass as well.

## About this project

This is a small helper library that reads version numbers and answers questions about them, such as whether one version is at least another. It also checks version requirement lines the way PyPI does, and it can show you a version it read in a plain, readable form.

## Problem this solves

Real projects write their version numbers in many different styles, and every one of those styles that gets turned away stops a release script when nobody is watching. I want the version numbers already sitting in my own files to be read as they are, without me having to rewrite them first.

## What changed

The reader now allows a dot or a dash before the word dev, and a dot, a dash, or nothing at all before a pre-release letter. When a number is missing after dev or after a pre-release letter, it counts as zero, so a version written with the letter a and no number after it comes back with a zero in that place. Capital letters are understood, and the long words alpha and beta are understood as well. A label after a plus sign no longer cares about upper or lower case, so a mixed-case label is read as a small-letter label. Requirement lines are read with the same loose rules and ignore capital letters. One thing stops being refused: a single capital letter used as the whole label after a plus sign is now accepted.

## Impact

Ease of use and correctness. Far fewer version numbers are turned away, and nothing runs slower.

## User experience

Today I write a version with a dot, the letter a, another dot, and the number one, and I get an invalid version error, so I have to edit my own files to work around it. After this, the same text is accepted and comes back in the short plain form, and the same goes for the capital-letter and long-word spellings in my requirement lines.

## Hints

- /workspace/packaging/version.py
- /workspace/tests/test_version.py
