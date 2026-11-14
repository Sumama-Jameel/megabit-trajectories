# Feedback report

## Tests

The harness ran the suite three times with the command `python -m pytest` from
`/workspace`. I did not run any test myself.

- Run 1 of 3: exit_code=0, 18 collected, 18 passed, 0 failed.
  Output excerpt: `collected 18 items` / `tests/test_dunders.py .................. [100%]` / `18 passed in 0.04s`.
- Run 2 of 3: exit_code=0, 18 collected, 18 passed, 0 failed.
  Output excerpt: `collected 18 items` / `tests/test_dunders.py .................. [100%]` / `18 passed in 0.03s`.
- Run 3 of 3: exit_code=0, 18 collected, 18 passed, 0 failed.
  Output excerpt: `collected 18 items` / `tests/test_dunders.py .................. [100%]` / `18 passed in 0.04s`.

Total: 54 collected across the three runs, 54 passed, 0 failed. The covering test
is `tests/test_dunders.py:250 test_validator`, whose docstring reads "If a
validator is passed, call it with the Attribute and the argument."

## What is missing

The behaviour the ticket asks for is implemented. What is not there is the
surrounding material the ticket also mentions.

- Breaking change is not recorded. `docs/changelog.rst` still only has
  "15.0.0 (UNRELEASED)" with the single line "- Initial release.". The file
  even says "strict backwards-compatibility policy". Every check function in
  user code breaks at this change and nothing tells the user so.
- The new calling convention is not documented anywhere. `attr/_make.py:83-86`,
  the `:param validator:` text of `_make_attr`, still only says the validator
  "is called on the attribute". It never says it now receives two arguments, or
  what order. A user reads this docstring to learn how to write a check
  function, and it does not answer that.
- No new test was added for this change. `tests/test_dunders.py:250` already
  existed and already expects the two-argument order, so the contract is
  covered, but nothing in the test suite names the breaking change or checks a
  validator that returns a value, or one on a field that also has a default.
- Pre-existing gap, not caused by this diff, but it blocks the ticket's promise
  that you can "write one function, use it on many fields":
  `attr/_make.py:97` passes `validator=None` hardcoded, so `attr.ib()` can never
  carry a validator. Only the internal `Attribute` constructor can. Through the
  public API the feature is unreachable today.
- Only `tests/test_dunders.py` exists as a test module. Nothing under `tests/`
  covers `attr/_make.py`, `attr/_funcs.py`, or `attr/__init__.py`, so a change
  like this one is only checked by one assertion.

## Why it fails

Nothing fails. All three runs are 18/18 green, and the reason is visible in the
code, not luck.

The change is two lines in `attr/_dunders.py:182-184`. The old line was:

```
lines.append("attr_dict['{name}'].validator({name})".format(name=a.name))
```

The new line is:

```
lines.append("attr_dict['{name}'].validator(attr_dict['{name}'], "
             "{name})".format(name=a.name))
```

I printed the generated script through the repo's own interpreter and the
emitted line is `attr_dict['a'].validator(attr_dict['a'], a)`. The attribute
object comes first and the value second, which is the order the ticket asks for
and the order `tests/test_dunders.py:272` asserts with
`assert ((a, 42),) == e.value.args`.

Two details make the test pass for the right reason. The test's validator is
`def raiser(*args)` at `tests/test_dunders.py:257`, so it takes any arity and
cannot catch a wrong argument count by itself; the exactness comes from the
`==` comparison on `e.value.args`, which pins the order. And `attr/_dunders.py:159`
builds `attr_dict` from the same `attrs` list that produced the script, so the
object handed to the validator is the very `Attribute` the test created, which
is why identity and equality in that assertion hold.

Non-validator fields are untouched: the new `attr_dict[...]` lookup is inside
the `if a.validator is not None:` branch, so the default-value and
default-factory branches at `attr/_dunders.py:186-198` are byte-for-byte the
same. Fields without a validator therefore cost no extra work and cannot break.

The only failure risk I can see in the code is a validator with a fixed
one-argument signature, but no such validator exists in the repo; `grep -rn
"validator" tests/ attr/ docs/ README.rst` shows the only executable validator in
the tree is `raiser(*args)`.

## Verdict

VERDICT: approve

## Experience difference

- Signature seen by a user's check function. Before, the generated
  `__init__` called `validator(value)`. Now it calls
  `validator(attribute, value)`. That is exactly what the ticket asked for, and
  `attr/_dunders.py:182-184` is the only place that had to change.
- What the first argument is. It is the real `Attribute` object taken from
  `attr_dict`, which is built once per class at `attr/_dunders.py:159`. So the
  object a check receives is the same object exposed as `__attrs_attrs__`. A
  user can read `attribute.name`, `attribute.type` if set, or `attribute.default`
  and write one check function and reuse it across fields, instead of
  hardcoding a field name. That reuse is the main payoff and it works.
- What a user's existing check function does. It breaks. A `def check(x)`
  validator now raises `TypeError: check() takes 1 positional argument but 2 were
  given` on the first instantiation, not at decoration or import time. The
  failure is at first use, so it is not caught early. Nothing in
  `docs/changelog.rst` warns about this, which is the biggest gap in the
  product as it stands: the change is breaking and silent.
- Docs a user reads. `attr.ib`'s `:param validator:` text in
  `attr/_make.py:83-86` describes a one-argument call, so someone using the
  generated docs will write the wrong signature. `docs/api.rst:43` only shows
  `validator=None` in an `Attribute` repr, so it neither helps nor hurts.
- Reachability from the public API. Unchanged by this diff, but worth stating
  plainly: `attr/_make.py:97` hardcodes `validator=None` in `_CountingAttr`, so
  `attr.ib(validator=...)` is silently dropped. A user following the ticket and
  writing `x = attr.ib(validator=my_check)` gets no error and no validation.
  The two-argument calling convention is real and tested, but only through the
  internal `Attribute` path that `tests/test_dunders.py:250` uses. Until
  `attr.ib` can carry a validator, the ticket's "write one function, use it on
  many fields" story cannot actually be exercised by an end user.
- How the change is proven. The behaviour is pinned by a single assertion in a
  single pre-existing test. There is no test that a returned value is ignored,
  no test for a validator on a field that also has a default or a factory, and
  no test covering `attr/_make.py` or `attr/_funcs.py` at all. The suite is 18
  tests in one file, so a green run says the one contract holds, not that the
  library is sound.
- What did not change for good or bad. Attribute ordering, defaults, factories,
  the generated `__init__` signature, and `__attrs_attrs__` are all identical.
  The diff is 2 insertions and 2 deletions in one file, with no other file
  touched (`git diff --cached --stat` reports `attr/_dunders.py | 4 ++--`), so
  the blast radius of the change is as small as it can be.
