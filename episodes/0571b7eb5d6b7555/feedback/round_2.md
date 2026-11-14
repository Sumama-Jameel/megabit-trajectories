# Feedback report

## Tests

I did not run the tests myself. The results below are the pipeline's Diff2 suite runs, quoted as given.

Command run by the pipeline: `python -m pytest` (3 runs, rootdir `/workspace`, Python 3.11.16, pytest 9.1.1).

- Run 1 of 3: exit_code=0 — `collected 8 items`, `tests/test_funcs.py ........ [100%]`, `8 passed in 0.03s`
- Run 2 of 3: exit_code=0 — `collected 8 items`, `tests/test_funcs.py ........ [100%]`, `8 passed in 0.03s`
- Run 3 of 3: exit_code=0 — `collected 8 items`, `tests/test_funcs.py ........ [100%]`, `8 passed in 0.03s`

Totals: 24 test executions across 3 runs, 8 unique tests per run, 24 passed, 0 failed, 0 skipped, 0 errors. Stable across all three runs.

Scope note: the suite only covers `tests/test_funcs.py`. `ls -la tests/` shows `tests/` contains only `__init__.py` and `test_funcs.py`, so `attr/_make.py` (where `Attribute`, `ib`, `s` live) has no tests at all. The doctest examples added in `attr/_funcs.py` and `attr/_make.py` are not collected by `python -m pytest`, so the green run says nothing about them.

## What is missing

Against the ticket, the behaviour changes are in place:

- `attr.ls` in `attr/_funcs.py` no longer silently walks up to `cl.__class__`; it raises `TypeError("Passed object must be a class.")` when passed an instance.
- `attr.ls` raises a separate, clear error for a plain class with no attrs fields (`ValueError`, "is not an attrs-decorated class"), instead of conflating it with the instance case.
- `attr.has` in `attr/_funcs.py` follows the same class-only rule and only catches the "not an attrs class" error, so `has(object) is False` and `has(some_instance)` raises `TypeError`; its docstring documents that `:raises TypeError:`.
- `attr.to_dict` recurses into nested attrs values and keeps working on instances because it now lists the instance's class.
- `attr.Attribute` is imported in `attr/__init__.py` and is in `__all__`, so it is public.
- Docstrings were filled in for `ls`, `to_dict`, `has`, `Attribute` (including `name`, `default_value`, `default_factory`), `Attribute.from_counting_attr`, `_make_attr`/`ib`, `_get_attrs`, `_add_methods`/`s`.
- `docs/api.rst` changed from a title-only page to `autofunction`/`autoclass` entries for `attr.s`, `attr.ib`, `attr.Attribute`, `attr.ls`, `attr.to_dict`, `attr.has`.
- `docs/conf.py` adds `doctest_global_setup = 'import attr'`, which is what lets the `attr.`-qualified examples in those docstrings run at all.

Still missing or not finished:

1. **The doctest in `attr.ls` cannot produce the output it claims.** The `ls` docstring shows `>>> attr.ls(C)` returning a list of `Attribute(name='x', default_value=NOTHING, default_factory=NOTHING)`. Grepping `attr/_make.py` for `__repr__`, `def `, and `^class ` shows `class Attribute` defining `__init__` and `from_counting_attr` only; the single `__repr__` hit in that file is prose inside the `add_repr` docstring text, not a method on `Attribute`. So `repr()` of a returned attribute is the default object form, and the example is wrong. The same block also relies on a trailing `\` line join inside a `.. doctest::` block, which doctest does not do.
2. **No test for the instance case in `has`.** The diff touches no test file, and the passing suite contains no case where `has` is given an instance, so the new raise-instead-of-return-a-bool contract is unproven by the run.
3. **`_get_attrs` docstring** names the count-bearing attribute class `_CountingAttr`; I could not confirm in this round that this is the class actually used, since the definition lives outside the files I read.
4. **`_add_methods` docstring claims `add_cmp` adds `__lt__`/`__le__`/`__gt__`/`__ge__`.** I did not read `_dunders.py` far enough to confirm that, so it is currently an unverified statement in shipped documentation.
5. **Coverage of "every helper, argument, switch, and returned field" is partial.** `attr.NOTHING` has no entry in `docs/api.rst` and no explanation of what "no default" means; the `default_value` versus `default_factory` *behaviour* of `ib` is stated only as `:ivar` prose, not shown by an example; the count-bearing attribute class is left unnamed in the public docs.
6. `docs/api.rst` has no page entry for `attr.NOTHING`, and no example anywhere showing `to_dict` on a nested structure, which is the behaviour the ticket highlights.

## Why it fails

No test fails: 8 passed, 0 failed, in all three pipeline runs. So there is no failing-test reason to report.

The real gap is untested and unrun documentation. Because `python -m pytest` does not collect doctests, the incorrect `attr.ls` example is invisible to the suite that was run; `tox.ini` is what wires `sphinx-build -b doctest` into the docs environment, and that was not part of the harness runs. So a green suite coexists with a broken example: the change is "tested" only where the old tests already agreed with the new behaviour.

The one place I expect real breakage outside pytest is item 1 above: `attr.ls` returns objects whose printed form is the default `<attr._make.Attribute object at 0x...>`, not `Attribute(name='x', default_value=NOTHING, default_factory=NOTHING)`, so the expected-output block does not match actual output and is non-deterministic (memory address) on top of that.

## Verdict

VERDICT: changes_needed

## Experience difference

What the ticket describes:

- A user asking "what fields does this class have?" gets a straight list of fields with names and their default situation (`NOTHING` means none, a value means that value, a factory means built per call). Passing an instance gets a clear, specific complaint instead of a misleading answer; passing a non-attrs class gets a different, specific complaint that names the class.
- `attr.has` is a yes/no question about a class: `False` for a plain class, `True` for a decorated one, and a clear error when the question itself does not make sense (an instance was passed).
- `attr.to_dict` handles the common nested case on its own, so `to_dict(outer_instance)` returns a dict whose nested values are already dicts.
- `attr.Attribute` is something a user can import from `attr`, with its fields (`name`, `default_value`, `default_factory`) documented.
- The documentation is a real reference: a browsable page per public name, and examples that a reader can copy and that are checked, so they do not drift.

What exists now:

- The three behaviour changes work as described. That is the substance of the ticket and it is done.
- The documentation page now has entries for the six public names instead of being empty, and `doctest_global_setup` in `docs/conf.py` is the right enabling piece.
- But the examples are not trustworthy yet. The main `attr.ls` example shows output the code cannot produce, so a reader who follows it sees something different from what is written, and it is not reproducible run to run because of the object address. The ticket's promise of verified, runnable examples is not met for `ls`.
- The `has` and `to_dict` stories are told only in prose. Nothing in the suite exercises `has` on an instance, so the documented "raises `TypeError`" is a claim, not a checked fact.
- The field-level detail the ticket asked for is partial. `name`, `default_value`, and `default_factory` are listed as `:ivar` lines, but the reader gets no example of the difference between "no default" and "a default", and `NOTHING` — which appears inside the documented output — is not documented anywhere. The internal count-bearing attribute class appears in a `_get_attrs` docstring by name without being defined in the docs, which is confusing rather than helpful.
- Two factual statements in the new docstrings (`_add_attrs`/`_add_methods` behaviour and the `_CountingAttr` name) are unconfirmed against `_dunders.py` and `_make.py` in this review; if either is wrong, users get wrong information from the reference page, which is the opposite of the ticket's goal.

Net: the product behaviour asked for is in place and the empty API page is filled in, but the documentation promise — complete, correct, runnable — is only partly delivered, and the wrong `ls` example would be caught the moment the docs doctest run that `tox.ini` already defines.