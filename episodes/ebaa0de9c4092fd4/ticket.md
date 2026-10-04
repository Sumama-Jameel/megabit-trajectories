# Version words and capital letters are not cleaned up, so the same release looks like two different ones

## What happens now

When I turn a version string into a version object, most of the spelling gets tidied up, but some does not. The long words alpha and beta are left as they were written, so "1.0alpha1" prints back as "1.0alpha1" instead of "1.0a1", and "1.0beta1" prints back as "1.0beta1" instead of "1.0b1". Capital letters are also kept, so "1.0ALPHA1" prints as "1.0ALPHA1" and "1.0+AbC" prints as "1.0+AbC" instead of "1.0+abc". Because of this, two spellings of the same release are not treated as the same thing: "1.0RC1" does not equal "1.0c1", and "1.0+AbC" does not equal "1.0+abc", so a sorted list of versions ends up with duplicates and in the wrong order.

## What should happen

Every accepted way of writing a version should come back in one short, standard spelling: alpha, beta and rc become a, b and c, and letters are always lowercase, including the part after the plus sign. Versions written in different ways should then compare as equal and sort next to each other instead of being kept apart.

## About this project

This is a small library for working with version numbers written as text, such as "1.0", "2.1.3a1" or "1.0+ubuntu-1". It reads a version string, pulls it apart into its parts, and then lets you compare and sort versions the way software releases are really ordered, and check them against requirements such as "at least 2.0".

## Problem this solves

My versions come from several places, and different places spell the same release differently: some write "alpha", some write "ALPHA", some write "a". Today the library treats those as different releases, so my sorted list shows the same release twice, requirement checks match the wrong entry, and versions I believed were identical turn out not to be.

## What changed

The long words alpha and beta are now shortened to a and b, the release-candidate word rc is shortened to c, and all letters in a version are put in lowercase, including the trailing part after the plus sign. Nothing that worked before stops working: every spelling that was accepted before is still accepted, and versions written as short letters and lowercase words come out exactly as they did. What no longer happens is a version string being handed back in a spelling the user did not write.

## Impact

Correctness and consistency. Versions written in different ways are recognised as the same release, so comparisons, sorting and requirement checks all give the right answer.

## User experience

Before: I write two versions as "1.0RC1" and "1.0c1", sort them, and I get two different entries in the wrong order because the first spelling keeps its letters. After: both print as "1.0c1", they compare as equal, and they land in one place in my sorted list.

## Hints

- /workspace/packaging/version.py
- /workspace/tests/test_version.py
