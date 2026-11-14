# Version numbers with an exclamation mark are rejected as invalid

## What happens now

Today the only mark this project accepts between an epoch number and the rest of a version is a colon. So a version written as `1!1.0` is treated as an invalid version and cannot be read at all. The same goes for requirements: a requirement such as `==1!1.0` is refused, because the colon is the only separator understood. Everything else, including printing, sorting, pre-release words like `a` and `rc`, and requirement checks, works as before.

## What should happen

A version written with an exclamation mark before the release numbers should be a normal, valid version. I should be able to read it, print it back, sort it against other versions, and write requirements that use the same mark, and have all of that work the same way it does for a version with no epoch at all.

## About this project

This project is a small helper library for working with software version numbers and with rules about which versions are allowed, such as "at least this version" or "exactly this version". It reads version numbers as text, tells you whether a version is allowed by a given rule, sorts versions from oldest to newest, and writes versions back out in a normal form.

## Problem this solves

I keep real version numbers that already use the exclamation mark to mark an epoch, and this library refuses every one of them as invalid. That stops me from comparing those versions, sorting them, and checking them against the rules my projects depend on, so I have no way to work with version data I actually have.

## What changed

The mark between an epoch number and the release numbers is now an exclamation mark instead of a colon. Versions written as `1!1.0` or `0100!0.0` are accepted, `1!1.0` is printed back unchanged, and `00!1.2` still shortens to `1.2`. Requirements accept the same mark, so `~=2!1.0` and `==2!1.*` are valid rules. The colon form is no longer accepted, so `1:1.0` and `~=2:1.0` now count as invalid. Nothing else about reading, printing, sorting, or checking versions moves.

## Impact

Compatibility and correctness: the library now reads the version numbers that other tools produce, and it stops accepting the older colon form.

## User experience

Before: I read a version string `1!1.0` and the library tells me it is not a valid version, and the same happens when I try to use `==1!1.0` as a rule, so I cannot compare or sort that data at all.

After: I read `1!1.0` and get a version back, it prints as `1!1.0`, it sorts in the right place next to my other versions, and the rule `==1!1.0` is accepted and matches that version. A string with a colon in that spot is now rejected, so any data I already stored with a colon needs to be read the other way.

## Hints

- packaging/version.py
- tests/test_version.py
