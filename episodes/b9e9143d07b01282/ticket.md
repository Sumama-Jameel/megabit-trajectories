# Version numbers lose their trailing zeros when shown

## What happens now
When I read a version written as one point zero and print it, I get back just
one. The trailing zero is gone. The same shortening happens to a version that
ends with a full release number and then an alpha tag or a release tag, so the
text I see is shorter than the text I typed. The version I wrote is not the
version I see.

## What should happen
The version I print should keep the numbers exactly as I wrote them. If I
write a trailing zero, it stays. If I write a full release number followed by
an alpha tag or a release tag, that full release number stays with it. At the
same time, the short form and the long form of the same release should still
count as the same version when they are compared.

## About this project
This project is a small library for working with the version numbers of
software packages. It reads a version written as text, compares two versions,
and prints a version back. People use it to check and sort the versions listed
in their project files.

## Problem this solves
When a version is printed in a shortened form, I cannot match it against the
version I wrote in my project file, so I cannot be sure the tool read the right
thing. Keeping the numbers as written removes that confusion.

## What changed
The release part of a version now keeps every number the user typed instead of
dropping the trailing zeros, and the plain part of a version keeps those zeros
too. The examples in the docs and the expected values in the tests now keep
those zeros as well. Comparing versions still treats the short form and the
long form of the same release as equal.

## Impact
Correctness and ease of use of the version text shown to people, with no
change to how versions are compared or sorted.

## User experience
Before: I print a version written as one point zero and the tool shows just
one, which does not match my file. After: I print the same version and the
tool shows one point zero, exactly as written.

## Hints
- packaging/version.py
- tests/test_version.py
- docs/version.rst
