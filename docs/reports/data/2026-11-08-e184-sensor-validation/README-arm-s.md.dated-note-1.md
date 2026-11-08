# E184 arm S's README, dated note 1 (Sun 8 Nov 2026; after the data verifier): A3-1's post hoc pointer stands, and the dip is a second post hoc reading; the box's smoke gate and A3-1's NO-GO figure count no dip (about 0.4-0.8% at a linear meter by A2's own dip model, not 1e-6); kit note 4's step 11 can collect the gate-stopped session's own files; three records lines

*Written on the Intel from about 03:40 PST on Sun 8 Nov 2026, desk only, after the data verifier of E184's two arms (Sun 8 Nov 2026,
02:40-03:09 PST: holds with fixes, 0 critical, 0 major, 3 minor and 4 nits, none in a datum, a gate reading or a verdict).
[`README-arm-s.md`](README-arm-s.md) and [`SHA256SUMS-arm-s`](SHA256SUMS-arm-s) (lab `f8d94224`, 02:36:34 PST) stay as committed, and so
does every file of arm B (`8bf74b26`). **No number, rule, verdict or gate reading changes, and nothing is scored: E184 arm S was not run
(A3-1).** The note answers the verifier's faults that touch arm S: the README's post hoc sentence (section 1, fault 1), the gate's missing
dip term (section 2, fault 2), the session's own files left on the box (section 3, fault 3), and three records lines (section 4, faults 4, 5
and 7). Arm B's nit (fault 6) is in [`README.md.dated-note-1.md`](README.md.dated-note-1.md). The figures come from
[`posthoc_note1_e184.py`](posthoc_note1_e184.py), which reads only committed files as JSON and imports no lab module. Its output is
[`posthoc-note1-e184.json`](posthoc-note1-e184.json) ("output S1" below names its sections), the same bytes under `/usr/bin/python3` 3.9
and `python3` 3.13. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins both notes, the script and its output. For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6, as the README.*

## 1. A3-1's post hoc pointer stands; the dip is a second post hoc reading (fault 1, minor)

README-arm-s.md's post hoc section says (its line 53): *"So the stop points to a dip the box's gate keeps, not to a meter or a power reading
long at E178's operating point."* That claims too much from one quad. It also negates A3-1's registered reporting words
([`E184.md.dated-note-A3.md`](../../../../tools/claims-v3/e184/E184.md.dated-note-A3.md)): such a NO-GO is reported "with the reading,
and, post hoc, as a pointer to a meter or a power reading long at E178's operating point". **The sentence is read as:**

> *Post hoc, two readings stand side by side. A3-1's pointer: the quad read long, +0.358 W against its +0.157 W step, as a meter or a power
> reading long at E178's operating point would read. And the dip: one refresh 3.11 W below its block accounts for 0.173 W of the reading's
> 0.201 W excess over the step, and with A2-5's refresh rule the quad reads +0.185 W, 1.18 of its step. One quad at 1.18 is consistent with
> a linear meter, does not exclude a long one, and does not support E178's 0.29 at the registration's base noise.*

The records round and the hub use these words.

What the figures say (output S1 > `m16_n19`, from the committed kept refreshes in `posthoc-arms-e184.json`; the gate's reading
re-made from them is +0.35775 W, rounding aside the committed +0.35778, and A2-5's is +0.18465 W, as committed):

| one quad, A2-5's reading over the registered step: **1.177** | base noise (quad sd 0.0302 W) | twice the noise (0.0656 W) |
|---|---|---|
| the reading's sd, as a fraction of the step | 0.193 | 0.418 |
| its 95% interval | **0.80-1.55** | **0.36-2.00** |
| a linear meter, 1.0 | 0.92 sd below the reading: inside | 0.42 sd: inside |
| A3-1's long readings: 1.2 / 1.6 | 0.12 sd above it / 2.19 sd above: 1.2 inside, 1.6 just outside | 0.05 / 1.01 sd above: both inside |
| E178's 0.29 (0.2865, as A2-7 reads it) | **4.62 sd below: outside** | 2.13 sd below: just outside |

- **The dip.** The quad's first A block holds nine kept refreshes, median 29.85 W, and one at 26.74 W, 3.11 W below it. E82 amendment A2's
  dip rule keeps it (that rule sets aside a refresh more than 4 W below the lower of the two refreshes two places before and after it).
  The dip lowers the block's mean from 29.856 W to 29.510 W, by 0.346 W, and the quad's A mean by 0.173 W. So it is **0.173 W of the gate's 0.201 W excess over the step (86%)**; the other 0.028 W is A2-5's
  reading's own excess (0.18 of the step).
- **One quad keeps its drift's curve.** This is one BAAB quad, run right after the every-minion quad (44.11 W, the smoke's peak). The
  registration cancels a curved drift only across ABBA and BAAB quads. Its two B blocks differ by 0.072 W and its two A blocks (with A2-5)
  by 0.007 W, where a straight drift would make the first three times the second. One quad cannot tell a curved drift from its step.
- **The 32-shire n = 121 quad**, which also held one dip (2.43 W below its block, in its last B block of eight): the gate's reading
  0.811 of its step, A2-5's 0.964, 95% interval 0.90-1.02 at base noise (output S1 > `m32_n121`).

## 2. The box's smoke gate and A3-1's NO-GO figure count no dip (fault 2, minor; the kit's, disclosed by the card lane)

**What.** The box's gate, `check_e184_v2.py smoke` (kit note 1 section 1), reads the smoke with `check_e184.quads`, v1's reader; kit note
2's nit (f) said A2-5 governs the reducer only. A3-1's NO-GO table (about 1.1e-6 at a linear meter, base noise;
[`power-e184-a3.json`](../../../../tools/claims-v3/e184/power-e184-a3.json) > K) is one quad's Gaussian noise with no dip in it, though
A2-5 had counted such dips on E180's bursts (5 of 2,649 block refreshes, 0.72-2.34 W).

**The figure with a dip term, post hoc** (output S2). It uses A3-1's formula with A2's own contamination model (`power_e184_a2.py`'s
`contam`). A quad holds one uncaught dip with chance 1 - (1 - rate)^(4n). Its depth is one of A2-5's five depths. It may fall in an A or a B
block alike, and it moves the contrast by +- depth / 2n. The no-dip column equals A3-1's table, entry for entry.

| chance of a NO-GO at that quad, small steps read | no dip (A3-1) | A2's model as written: 7 refreshes a block, E180's rate and depths | the same at the quad's own 9 refreshes | post hoc: today's 2 set-asides pooled in, 9 refreshes |
|---|---|---|---|---|
| 1.0, base noise | 1.1e-6 | **0.0080** | **0.0035** | 0.0109 |
| 1.2, base | 1.1e-4 | 0.014 | 0.011 | 0.021 |
| 1.4, base | 0.0039 | 0.023 | 0.023 | 0.034 |
| 1.6, base | 0.053 | 0.073 | 0.076 | 0.086 |
| 1.0, twice the noise | 0.0145 | 0.023 | 0.021 | 0.028 |
| 1.2, twice | 0.044 | 0.055 | 0.054 | 0.061 |
| E178's 0.29, base | 6e-11 | 0.0012 | 0.0001 | 0.0017 |
| a quad holds a dip | | 5.2% | 6.6% | 8.7% |

- **Depth.** A dip alone takes a true +0.157 W step past +0.30 W when it is deeper than 2.00 W in a 7-refresh A block, 2.29 W in an
  8-refresh block or 2.58 W in a 9-refresh block. Of E180's five dips, one (2.34 W) is deeper than 2.00 W and none is deeper than 2.58 W.
  Today's was 3.11 W in a nine-refresh block.
- **Rate.** Today's smoke set aside 2 of its 133 kept refreshes (1.5%); E180's bursts set aside 5 of 2,649 (0.19%). That is post hoc, and
  two events.
- **So,** at a linear meter, a NO-GO like today's had a chance of about **0.35-0.8%** by A2's own model of E180's dips, and about 1.1% with
  today's dips pooled in. That is thousands of times A3-1's 1.1e-6, and still small. Between gains of 1.2 and 1.4, where E184-P would read
  HIGH, it is 1-3% at base noise instead of 0.01-0.4%.

**What it changes.** Nothing registered, and today's NO-GO stands (A3-1). Before any re-run of arm S, each as a dated note first:
1. a dated amendment and kit note: either the smoke gate reads with A2-5's rule (`check_e184_v2.py` is one of the harness's 59 box files, so
   the harness, the dry pass and the runbook's tests are re-made), or the dip risk is accepted in words at its rate; either way, A3-1's NO-GO
   figure is restated with this dip term;
2. the day's `e184-smoke/p18401` and `e184-stoptest/p18402` moved aside on aifoundry3 first: `tools/claims-v3/lib.sh` line 181 skips a pass
   directory that already holds `block.json` unless V3_FORCE is set, so the gate would read this smoke again;
3. his go, with a window that fits the arm's 8,100 s.

## 3. The session's own files are still on the box; kit note 4's step 11 can collect them (fault 3, minor; the kit's, disclosed)

**What.** Step 11 v3's first copy named `e184`, which only the queue makes. At 02:26:36 PST rsync exited 23 (rb_run 14) and the step
stopped before the session's own files, the collector and the gates (README-arm-s.md section "Step 11 v3 stopped at its first copy"). So
from this directory alone the session's T0, its 45 s, its config reads and the box's own gate line cannot be checked. They rest on the card
day's runbook output, kept outside the repository; the verifier read it, and it agrees with README-arm-s.md. The kit's tests had never
collected a gate-stopped session.

**The fix.** Kit note 4 ([`KIT.md.dated-note-4.md`](../../../../tools/claims-v3/e184/KIT.md.dated-note-4.md), lab `8092c27a`, 03:37:08
PST, written after this data and changing no rule, reader or reading). Its step 11 v4 copies the box's `build/e184/` first, then the pass
directories this T0's own log says the session made. After "smoke gate failed (...): no pass runs" that is `e184-smoke` and
`e184-stoptest`. Then come the collector, reduce v4 with A4 and score v3, all unchanged. Its desk test v4 reads 43 of 43. Case **CG**
collects a gate-stopped session: every rule NOT SCORED at the reducer's session gate, as A3-1 has it. Case **CGv** shows step 11 v3's 14 on
the same box.
- **This session can be collected on Sun 8 Nov** while aifoundry3's approval lasts (about 09:30 PST): step 2 v4, then step 11 v4, with arm
  S's runbook output directory of that day. Its files go beside these, with their own hash list and a dated note, under names that do not
  collide with arm B's committed `scored-e184-v3.*` and `reduced-e184b-v4.json`. Arm B's files stay as committed. If no lane collects them
  that day, they wait on the box in our tree's `build/e184/`.
- **The desk check, re-run here** (the verifier's S3; reduce v4 and score v3, unchanged, on a scratch copy of `raw/aifoundry3/`): arm S's
  session gate does not hold, with four reasons. There is no session log for T0 1794133299 in this copy. The smoke, checked again at the
  desk, reads `SMOKE NO-GO: m16 n19 read 0.358 W, outside -0.15-0.30`. And there is no start or end config read, with no record of an
  attempt. So E184-N, -L, -P, -J and -C are all NOT SCORED. No reduced or scored file of arm S is committed: by A3-1 there is nothing to
  score, and a collection by kit note 4 would read the session's own files.

## 4. Records lines (faults 4, 5 and 7, nits)

- **Step 10b ran after step 10 exited 16** (GATE-STOPPED), at 02:24:54-02:24:55 PST. Kit notes 2 and 3 run it "right after step 10 exits 0".
  It was the same READ through the same guard. Its own check, that this T0's log on the box ends with its end line, passed, and it read
  the card as registered: 0 W / 65 °C / max_power / 600 MHz / 523 mV. That is a departure from the table's letter; no reading changes.
- **The rail fields of `posthoc-arms-e184.json`** (`y_rail_w`, `rail_over_step`) are the minion rail's single-quad contrasts (output S5):
  - the null quad +0.740 W;
  - the n = 121 quad 0.18 of its rail step;
  - the every-minion quad 1.37;
  - the 16-shire n = 19 quad 5.45.

  The rail's average filters over about 1.06 s, longer than half a quad's 1.6 s blocks (A2-3), so a quad's rail contrast carries the
  transient of the quad before it; the 16-shire quad follows the every-minion quad. **They are not a power reading;** never quote the rail
  as reading the 16-shire step five times long.
- **f8d94224's time.** Git gives 02:36:34 PST for the commit (author and committer) and the push ended at 02:36:37; records that give
  02:37:16 are wrong. The README's own times are the card day's clock, as written.

## What does not change

README-arm-s.md, SHA256SUMS-arm-s (23 of 23 OK) and every file of `f8d94224`; arm B's README.md, SHA256SUMS-arm-b (80 of 80 OK) and every
file of `8bf74b26`. A3-1's reading stands: **E184 arm S not run**, the smoke's 16-shire n = 19 quad read +0.358 W, above +0.30 W. No rule of
arm S has a reading, and its forecasts stay untested (N NULL, L LINEAR, P LINEAR and METER EXCLUDED, J and C NONE SEEN; the governing LINEAR
powers 0.953 and 0.952). Every forecast, band, threshold and gate of E184.md, A1-A4 and kit notes 1-4 is unchanged.

## Files (new; their sha256 in [`SHA256SUMS-note1`](SHA256SUMS-note1))

| file | what |
|---|---|
| `README-arm-s.md.dated-note-1.md` | this note |
| `README.md.dated-note-1.md` | arm B's dated note 1: E184-M's bootstrap (fault 6) and arm B's records lines (fault 7) |
| `posthoc_note1_e184.py`, `posthoc-note1-e184.json` | the figures of both notes (sections S1, S2, S5 and B6) |
| `SHA256SUMS-note1` | the sha256 of the four files above |

Re-make from the top of the repository (the same bytes under `/usr/bin/python3` 3.9 and `python3` 3.13, about 25 s on one core):

```
D=docs/reports/data/2026-11-08-e184-sensor-validation
/usr/bin/python3 -B $D/posthoc_note1_e184.py $D | cmp - $D/posthoc-note1-e184.json
```

## Labels

- **Registered, blind:** the smoke gate's bands and its NO-GO, with A3-1's reporting words; every forecast and rule of arm S, untested.
- **Post hoc** (written after the data; deciding nothing): every figure of sections 1, 2 and 4.
- **Desk checks of code, not measurements:** kit note 4's tests, and section 3's desk check.

SPDX-License-Identifier: Apache-2.0
