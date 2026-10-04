# I cannot pin one exact release name that is not a numbered version

## What happens now
Today the only signs a version requirement can start with are: two equals signs, two equals signs with a bang, one or two tildes, one or two bang-less comparison signs, and the signs for less than, less than or equal, more than, and more than or equal. There is no way to say "install this one exact name, character for character". Every one of those signs also insists on a numbered version on the right side, so a name such as `lolwat` is refused with an error the moment you ask whether it matches.

## What should happen
I want to be able to write a requirement that starts with three equals signs and then any text at all, for example a requirement meaning "only this exact archive". The text after the three equals signs should be compared letter by letter, and upper and lower case should be treated as the same. I also want to be able to ask about a name such as `lolwat` without getting an error: the answer should simply be yes or no.

## About this project
This project is a small helper library for working with software version numbers and version requirements in Python. It reads a version written as text, sorts versions so older ones come first, and answers questions about whether a given version satisfies a requirement such as "at least 2.0".

## Problem this solves
Some projects publish releases under a name that is not a numbered version, for example a word, a date, or a build stamp. With the requirement signs available today there is no supported way to say "use this one exact release and nothing else", so such a project cannot describe its own pinning at all and has to bend its name into a numbered form or give up on pinning.

## What changed
A new sign made of three equals signs joins the list of accepted requirement signs. It accepts any text after it, it appears in the printed form of a requirement, and it can be combined with the other signs and with the ampersand form. A name that cannot be read as a numbered version is now handed straight to that comparison instead of being turned into a numbered version, and asking about such a name no longer raises an error: it answers no match unless every sign in that same requirement is the new exact-match sign.

## Impact
Ease of use and compatibility. The seven existing requirement signs keep the meaning they have today, and the new sign is the only one that accepts text which is not a numbered version.

## User experience
Before: I write a requirement that starts with three equals signs and I am told the requirement is invalid, and asking whether the word `lolwat` matches gives me an error instead of an answer. After: the requirement is accepted, the word `lolwat` matches `lolwat` and also `Lolwat`, a different word does not match, `1.0.0` does not match a requirement of `1.0`, and a requirement that mixes the new sign with a numbered rule such as "new sign 1.0.0 combined with equals 1 times anything" answers no match for the word rather than raising.

## Hints
- /workspace/packaging/version.py
- /workspace/tests/test_version.py
- /workspace/packaging/_compat.py
- /workspace/packaging/_structures.py
- /workspace/packaging/__about__.py
- /workspace/docs/index.rst
- /workspace/README.rst
