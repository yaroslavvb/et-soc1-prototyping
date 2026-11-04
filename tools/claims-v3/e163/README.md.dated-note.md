# Dated note on E163's kit README `README.md` (Wed 4 Nov 2026, week 45, PST, after Q141(a)'s verifier; before any E163 data and before the claim)

Written beside the README and not inside it. [`README.md`](README.md) (`1c47ce62`) stays as committed. Nothing here changes a rule of
`E163.md`, a file the box runs, or the order of the box steps. It makes the network commands exact, settles one figure, and adds one line
on the day's post. The registration's own amendment is [`E163.md.dated-note.md`](E163.md.dated-note.md) (A1). No E163 data exists, and
no card has been claimed.

## Every network step carries the options (Q141(a)'s verifier, fault 3)

Box step 1 says every ssh runs with `-o BatchMode=yes -o ConnectTimeout=10`, so a step that would wait at a prompt fails at once instead.
But the commands in step 4 (the rsync), step 10 (the ssh) and step 11 (the copy back) name no options. An rsync without `-e` opens a plain
ssh, which can wait at a prompt on the operator's side.

The exact commands are below. Run each from the Intel, in the lab clone, after `git pull --ff-only`, and with
`git status --short tools/claims-v3/` printing nothing for the paths synced.

**Step 4.** `-R` keeps each path's place under `aifoundry/`. This shape was tried on the Intel as a local dry run (rsync 3.5.1, no ssh):
every file landed at its own path, and no `__pycache__` was copied.

```
rsync -a -c -R --exclude __pycache__ -e 'ssh -o BatchMode=yes -o ConnectTimeout=10' \
  tools/claims-v3/e163/ tools/claims-v3/kinds/blind7/ tools/claims-v3/kinds/blind5/ tools/claims-v3/kinds/e130/ \
  tools/claims-v3/e152/ tools/claims-v3/e151/ tools/claims-v3/ccheck/ tools/claims-v3/dmcmd_audit.py tools/claims-v3/dmcmd_table.json \
  aifoundry3:aifoundry/
```

**Steps 3, 5-9 and 10.** Each runs on the box as a script file:

```
ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry3 'bash -s' < <file>
```

For step 10, `<file>` holds README step 10's `setsid nohup … session_e163.sh …` line.

**Step 11.** First the copy back, into a fresh `<raw copy>` directory on the Intel, in the layout `collect_e163.sh` reads (`e163/`,
`e163-smoke/`, `e163-stoptest/`, `logs/`):

```
rsync -a -e 'ssh -o BatchMode=yes -o ConnectTimeout=10' aifoundry3:aifoundry/build/claims-v3/aifoundry3/e163 \
  aifoundry3:aifoundry/build/claims-v3/aifoundry3/e163-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e163-stoptest <raw copy>/
rsync -a -e 'ssh -o BatchMode=yes -o ConnectTimeout=10' aifoundry3:aifoundry/build/e163/ <raw copy>/logs/
```

Then the collector, with Q141(t)'s committed arm as its second argument (amendment A1-5; committed in `67d5e44f`):

```
PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e163/collect_e163.sh <raw copy> \
  docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry3.json
```

If any ssh prints a sign-in link instead of connecting, stop that step at once and wait for a fresh approval, as step 1 says.

## 70 or 75 minutes (Q141(a)'s verifier, fault 7)

The two files give different figures for FULL:

- README § The order on aifoundry3 says to run FULL "if 75 minutes are free".
- E163.md gives FULL a window of at least 70 card-minutes and caps it at 70 (§ What runs, § Card budget).

**The binding numbers are E163.md's, and the queue enforces them:** the budget rule allows 4,200 s from `E163_T0`, with 60 s of it
reserved for the closing read, and the session also stops at `E163_DEADLINE`. README's 75 minutes is advice for choosing the plan, 5
minutes over the cap. No code reads it.

## One reservation for E166 and E163

E163 runs after E166 on aifoundry3. If both run in one reservation, the day's post needs a single aifoundry3 clause that covers both
sessions. Its hours are E166's cap of 76 card-minutes plus E163's 70, with the gap between them and a margin, rounded up to the half hour:
`for 3 h`. README's `for 1.5 h` is E163's alone.

SPDX-License-Identifier: Apache-2.0
