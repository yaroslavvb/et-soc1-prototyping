# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 17:2x PST: which runbook a later step runs (Q141(r)'s fix pass)

*Written beside [`README.md`](README.md) and not inside it: the README stays as committed in `efaaa726`. It corrects one bullet, which
the records' verifier found (Wed 4 Nov 2026, about 16:42–17:15 PST). Desk only: nothing registered, frozen or measured changes, no
device command is involved, and no run's result is in it.*

**The correction.** The README's section "Q141(k), the bounded runbook" ends: *"For the card day: E167's collection should run with
v2's `s22_collect.sh e167` (fault 4); every other remaining step may stay on v1."* The first half is right; the second is not. The
runbook's own dated note, committed with v2 in `16771f36` (15:34:42 PST), says
([`tools/claims-v3/q141k-runbook/README.md.dated-note.md`](../../../../tools/claims-v3/q141k-runbook/README.md.dated-note.md)):

> **For any later step or card day, use [`v2/`](../../../../tools/claims-v3/q141k-runbook/v2/README.md)**: the same steps, arguments and exit codes, called as
> `bash tools/claims-v3/q141k-runbook/v2/<script>`. It reads the same state on the boxes and takes what was written that day, so a lane
> can switch at any step.

So the bullet should read: **for every step after v2's commit, and on any later card day, use v2**; E167's collection is one such
step, not the only one. Two of v2's fixes, besides E167's collection, still bore on steps after this report was written (16:14 PST),
both among the nits the runbook's dated note lists:

- **E163's plan must end by the last end.** Under v1, `s11_a3_session.sh e163` has no end check: a full E163 launched with less than
  its 70 card-minutes left starts and is then cut by E163's own deadline. It is not refused, though v1's README says "each launch
  refuses otherwise".
- **Box state counts only when written that day.** Under v1, the state the runbook leaves on a box (the jobs' exit-status
  files, E166's log offset) carries no date, so a second card day would take the first day's dry-pass verdicts and E166's session
  end as its own.

The runbook's own note records which of its other findings did not bite on 4 Nov: faults 1 and 2, fault 5's boot rule (step 14 read
aifoundry2's boot inside it both times), and the step-9 nit (step 9 ran before E166's session).

**Where the records carry it.** The Q141 section of [`05-claims.md`](../../../findings/05-claims.md) ("The runbook (Q141(k)) and the
card half") and the Q141 row of [`02-requests.md`](../../../findings/02-requests.md), each in a dated clause, every earlier word kept;
and the Horace Hub's Fix entry of this time.

SPDX-License-Identifier: Apache-2.0
