# Dated note 1 beside README.md (Fri 6 Nov 2026, week 45): kit v4's one-kernel option under card 0's alarm, and its wall time at the cap

*This note sits beside [`README.md`](README.md) and edits nothing in this directory: every file `SHA256SUMS` lists stays as
committed (`f64ab6cd`). It adds to section 5 ("Before a card uses it") what the dip lane's verifier found missing, and corrects one
figure of section 1. It is an option, dry pass only: there is no kit v4, no card has run it, and its A/B check is owed. Its time is
its commit's. Desk only: no card was touched.*

## Builds on

- **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 03:50 PST. Public rows read: P01, H07, H28. The ids are opaque
  pointers into a private inventory.
- **Used:** [`onekernel.py`](onekernel.py), imported unchanged (`iters_for`, `wall_at`, `CPO`, `HOST_TIMEOUT_S`); card 0's alarm
  as the lab measured it, `docs/findings/14-card-behaviour.md` lines 238 and 466 (E84): a 300 MHz safe state, and over a
  sustained run the work samples 31-32% at 300 MHz, 32-34% at 600, 25% at 700 and 10-11% at 800 MHz, with the kernel's own
  effective clock at 0.475-0.479 GHz; the host's timeout, `workloads/sparsity/host/main.cpp` at `27dce7f0` lines 237-246
  (`timeoutS` 6; "kernel did not finish within 6 s, aborting the stream").
- **Tiers:** public only.

## 1. Under card 0's alarm, a one-kernel burst overruns the host's 6 s timeout

`onekernel.py` sizes the one kernel to end in 5.5 s at 600 MHz (`FLOOR_MHZ`, "the lowest point the governor sets"). That is right
for the governor's operating points at BL2 0.22.0 (600, 700 and 800 MHz). It is not right under **card 0's PMIC alarm**, whose
safe state is 300 MHz. The 3.30 G-cycle kernel then lasts ([`sizing-check-alarm.txt`](sizing-check-alarm.txt)):

| clock | wall | against the 6 s timeout |
|---|---|---|
| 600 MHz, the sizing's worst case | 5.50 s | under |
| E84's sampled mix under the alarm (551 MHz) | 5.98 s | 0.02 s under: at the limit |
| E84's kernel effective clock under the alarm (0.475-0.479 GHz) | 6.89-6.95 s | **over** |
| the 300 MHz safe state | 11.0 s | **over** |

So under the alarm the host aborts the stream. No v3 launch reaches that path: a v3 launch is about 0.37 s. **Added to
section 5:**
- A kit that uses the option keeps every burst clear of card 0's alarm, by its admission and its stops. That already binds every
  card 0 run: its 65.9 W one-sample stop, far from the 75 W alarm.
- The kit's stop-path tests also cover a kernel the host timed out: the abort, the collection, and the scorer's handling of a
  launch with `ok` false.
- A burst whose kernel timed out is set aside by a rule registered before the session.

## 2. The kernel's wall at the cap, corrected

Section 1 says the kernel lasts **4.30-4.43 s** at the cap. That covers a first heartbeat inside the kernel 0.5-1.0 s after its
start. The heartbeat can come at any time in the first second, so the full range is **4.18-4.43 s** (4.179 s with the first
heartbeat at 0 s; `onekernel.wall_at`, aifoundry2's climb). With the first launch about 0.15 s after the process's start, the
burst window (from 1.5 s to the end) is then about 2.8-3.1 s; section 3's "about 2.95 s" is its middle.

## 3. What the records say

"Kit v4 runs bursts as one kernel by default, which removes the dips" overstates. The records quote: **an option for kit v4,
dry pass only**. A kit that uses it still needs everything section 5 lists, and the two items above.

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| [`sizing_check_alarm.py`](sizing_check_alarm.py) | the check: the one kernel's wall at the cap and at the clocks under the alarm, from `onekernel.py` unchanged |
| [`sizing-check-alarm.txt`](sizing-check-alarm.txt) | its output: `python3 -I -B sizing_check_alarm.py` |
| [`SHA256SUMS-1`](SHA256SUMS-1) | the files above, plus every file `SHA256SUMS` lists and `SHA256SUMS` itself, all unchanged |

SPDX-License-Identifier: Apache-2.0
