# ADR 0013 — An import is told which dataset it writes to, and refuses when it is not

**Status:** accepted

## Decision

Every import names its target dataset. The caller supplies it. When no dataset is supplied the
import raises immediately and writes nothing.

Nothing guesses. The previous behaviour, taking whichever dataset happened to be first in the table,
is removed from both import resources.

One consequence is accepted deliberately: the Django admin's import wizards have no way to name a
target dataset, so both of them now raise on every use. They stay that way until a dataset-selection
surface exists.

## Why

Writing to the wrong dataset is silent and expensive to undo. A heat flow determination filed under
somebody else's dataset is indistinguishable from one filed correctly, and the error surfaces
whenever somebody notices records they did not contribute — which may be never.

The fallback read as a convenience but was never a correct behaviour. It did not choose the right
dataset; it chose an arbitrary one that happened to be right whenever exactly one dataset existed,
which is the condition under which the bug is invisible. Failing loudly is strictly better than a
silent wrong write, and there is no capability lost, because no route through the admin ever reliably
chose the right target.

Removing it broke a large number of tests that had been relying on it without saying so. That is the
same defect in another form: a test that never names its target is not testing the behaviour it
appears to test.

## Revisit if

Never for the guessing itself. The admin's refusal ends as soon as its import page can name a
dataset, at which point it supplies one and the route becomes usable again.
