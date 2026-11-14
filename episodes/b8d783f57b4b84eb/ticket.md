# Post releases written without a dot, or without a number, are rejected

## What happens now

If a version ends with a post release, the word post has to be written with a
dot in front of it and a number after it. A version where the word post is
joined straight onto the release numbers, or where it is preceded by a dash,
or where no number follows the word, is turned down with an "Invalid version"
error. The same restriction applies when the post release appears inside a
requirement, so a rule that mentions such a post release is refused as well.

## What should happen

Every spelling people actually use for a post release should be accepted: the
word post attached to the numbers, the word post after a dot, the word post
after a dash, the word in capitals, and the word with no number after it at
all. When the number is left out, it should count as zero, and the version
should be shown back in the standard form with the dot and the number filled
in. Rules that mention a post release should accept the same spellings.

## About this project

This project is a small library for working with version numbers. It reads a
version that you give it, tells you whether the version is valid, sorts
versions, and checks a version against a requirement such as a minimum or an
exact match.

## Problem this solves

A lot of projects name their post releases without a dot before the word post,
with a dash instead, or with no number at all. Right now those real releases
cannot be read at all, so a project that uses such a name cannot be installed,
listed, or compared with others.

## What changed

Post releases are read in all the usual spellings instead of only the one
spelling with a dot and a number. A post release with no number is treated as
having a number of zero, and it is printed back with the dot and the number
added. Requirements that mention a post release accept the same spellings.
How versions are ordered against each other, and every other part of a version
such as the pre-release part, the development part and the local part, behave
exactly as before. Nothing was taken away.

## Impact

This is about compatibility and ease of use: version names that people
already use stop being rejected, and nothing that worked before changes.

## User experience

Before: I ask the library about a post release where the word post is joined
straight to the numbers, or written after a dash, and I get an "Invalid
version" error even though that name is used by a real project. After: the
same name is accepted, and when I print the version back I get the standard
form with the dot and, where the number was missing, a zero.

## Hints

- /workspace/packaging/version.py
- /workspace/tests/test_version.py
