# I cannot say which sign-in style I want, and the old switch is accepted with no user name at all

## What happens now

To send a request with digest sign-in, I have to add a simple on/off switch called `--digest` (short form `-d`). It only turns something on, it never names a style, and the tool lets me use it even when I gave no user name and password at all. In that case the sign-in information is never used and my request goes out unsigned, with no warning. The single-letter short form `-d` also sits right next to my other short options, so I can hit it by accident.

## What should happen

I should be able to name the sign-in style I want directly on the command line, and the tool should stop with a clear message if I name a style without also giving a user name and password.

## About this project

This project is a command line tool for sending HTTP requests from the terminal. I type in a web address, and it shows me what it sent and what came back, with the response body colored and formatted. It also lets me add headers, send data, and sign in to sites that ask for a user name and password.

## Problem this solves

The on/off switch gives me no way to say which sign-in style my script needs beyond a bare "use digest", and it is accepted without a user name and password without any complaint, so a mistake in my command line goes unnoticed. Naming the style and checking it against the user name and password removes both rough edges.

## What changed

The on/off switch for digest sign-in is gone, along with its single-letter short form. In its place there is a named option where I choose the sign-in style, with two choices: basic sign-in and digest sign-in. Basic sign-in is used when I say nothing, so a plain user name and password on their own keeps working exactly as before. The single-letter short form is free again. If I pick a sign-in style but leave out the user name and password, the tool stops and tells me that the style option can only be used together with the user name and password option.

## Impact

This is a change in usability and correctness. Commands that use the user name and password option on its own are unaffected, while commands that used the old on/off switch need to name the sign-in style instead.

## User experience

Before: I add `--digest` on its own, get no warning, and my request arrives at the site without any sign-in, so it answers with an error page I did not expect. After: I name the digest style together with my user name and password, and the request comes back signed in. If I name a style and forget the user name and password, the tool stops right away and tells me what is missing.

## Hints

- /workspace/httpie/cli.py
- /workspace/httpie/__main__.py
- /workspace/tests/tests.py
