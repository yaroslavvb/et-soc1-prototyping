# E133 data: E111's two heat holds again on aifoundry2, a second session per kind, and a cool probe (Q136, Mon 2 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): item 9, "A
steady state for heat", and item 8, "The heat path drifts between sessions" (Q134's final critic, item 6).*

*Pre-registered in [`tools/claims-v3/e133/E133.md`](../../../../tools/claims-v3/e133/E133.md) with
[`predictions-e133.json`](../../../../tools/claims-v3/e133/predictions-e133.json), the scorer, its self-test and a dry queue. It was committed as
**`9723d79b`** at 09:00:48 PST and was on origin at 09:00:52. The first lane was then blocked by the lab's Tailscale lapse (08:40–10:04 PST) and never
reached the card; it had only looked at the box, 08:21–08:26 PST, before the lapse (corrected after verification,
[C4](#corrections-after-verification-mon-2-nov-2026)). **Amendment A1** (`f842cc39`, 10:12:24 PST, on origin 10:12:27) was written for this second
session before the claim and before any E133 data: it was final at that commit, before the box access at 10:12:41 (C4). It says the first
session never ran (0 card-minutes, nothing to join), moves the smoke's latest start to 11:30, scores R2 as frozen beside R2w (keyed at the
governor's whole degree), adds a hash guard on the audited chain and corrects two labels.*

*The session:*
- *Claimed at 10:14:18 PST by rewriting the day's one `#community-lab` post (message `1566837317765963987`).*
- *First device access at 10:14:32 PST: the session-start `ettelem config`.*
- *Card runs 10:14:32–12:40:40 PST on aifoundry2 card 0 only: **80.81 card-minutes of 110**.*
- *TDP 65 W and threshold 65 °C at all 42 config reads, from the session-start read (10:14:32) to the session-end read (14:05:44), which came
  after the release (D5). Nothing was set, and **no WRITE command of any kind** was sent, not even the statistics reset. The residency read was
  answered unsent 30 times and never sent.*
- *The card's clause was dropped from the post at 12:41:01 PST. The session-end read (14:05:44) came after it, outside the claim: a READ on a free
  card ([D5](#departures-dated), added after verification).*
- ***W3, the optional afternoon probe, did not run, by its registered rule.** At 14:05:07 PST the free card's 10-minute idle die read 44.925 °C,
  under the rule's 45.0 (W2's REST idle, 44.0, plus 1.0). `SKIP-W3` was touched at 14:05:29, and the queue ended at 14:05:40.*

*Corrected after an independent verification, Mon 2 Nov 2026 (§ [Corrections after verification](#corrections-after-verification-mon-2-nov-2026),
C1–C6). The governor trips at a whole-degree reading of 66, which the plateau's own readings and the SP trace show directly. R2w's agreement is a
weak test, because the idle's whole-degree reading cannot place the die on either side of its key. The session-end read came after the release
(D5). The first lane never reached the card, though it looked at the box. A1 was final at its commit. Item 9 is given per kind. Desk only, no card
touched. No registered rule, prediction, number or verdict changed.*

## Results first

**22 registered verdicts: 4 PASS, 8 FAIL, 1 INCONCLUSIVE, 1 AT THE TRIP, 1 OK, 2 ABOVE_TARGET, 2 SUPPORTS, 1 PARTLY, 1 POSITIVE_BELOW_TARGET,
1 BELOW_TARGET** ([`results.json`](results.json) `tally`, [`reduce.txt`](reduce.txt)). Seventeen of the 22 have a registered side, and **15 of
those came out as predicted, all eight FAILs among them. Two did not:**
- **E133-R1 on H-I8**: INCONCLUSIVE where PASS was predicted;
- **E133-R2**: AT THE TRIP where AT THE FLOOR was predicted.

Amendment A1's **E133-R2w**, keyed before any data at the governor's whole degree, predicted AT THE TRIP and came out as predicted
([`a1_readings.json`](a1_readings.json) `R2w_amendment_A1`). *(Added after verification, [C2](#corrections-after-verification-mon-2-nov-2026):
that is a weak test. W2's REST idle read 44 in every sample, a whole degree, so it cannot place the die on either side of R2w's 44.54 °C key. The
direct evidence that the trip comes at a reading of 66 is the plateau's own readings and the SP trace, in result 2.)* Before scoring anything, the
scorer reproduced E98's and E111's committed results key for key (`regression`).

**1. Item 9: a second session per kind.** By R1 the coefficient replicates for fp32 random (PASS, ratio 0.966), though for that kind R1 compares
Sunday's hold at the governor's floor with Monday's at its trip, two regimes *(added after verification,
[C5](#corrections-after-verification-mon-2-nov-2026))*. It nearly replicates for int8 −1s (R1 INCONCLUSIVE, 1.042 [1.005, 1.111], the range's
top 0.001 past the band). Four holds over two sessions put aifoundry2's steady coefficient at **0.65–0.70 °C per board W** ([`results.json`](results.json) `A`, `R1`; [`a1_readings.json`](a1_readings.json) `holds`):

| hold | kind, clock (share at it) | start | idle before → after: die, W | plateau, last 300 s: die, W | rise | over idle | **c, per board W** [range] | E111's c (1 Nov) | R1: ratio [range] | slope, last 10 min: fine W (A1's reading), die beside | registered |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **H-I8** (W1B) | int8 neg_ones, 800 MHz (0.960) | from rest, 26.5 min, 190 of 190 processes | 44.0, 21.527 → 44.0, 21.552 | **56.36 °C, 39.20 W** | 12.36 °C | 17.67 W | **0.700** [0.699, 0.719] | 0.672 [0.647, 0.696] | 1.042 [1.005, 1.111] **INCONCLUSIVE** | −0.101 °C/min (se 0.015); die −0.096 (se 0.016) | A1 **FAIL**; A2 prior PASS, lab model, E97 and 76 s line FAIL; R1 predicted PASS |
| **H-F32** (W2) | fp32 randn, **at the governor's trip**: 600 MHz in 0.889 of samples, mean 612.7 MHz | after E98's probe and its hold of 39, 27.0 min, 190 of 190 | 44.0, 21.413 → 44.0, 21.447 | **65.91 °C, 55.23 W** | 21.91 °C | 33.80 W | **0.648** [0.648, 0.664] | 0.671 [0.651, 0.685] | 0.966 [0.947, 1.019] **PASS** | +0.303 °C/min (se 0.048); die −0.008 (se 0.0025) | A1 **FAIL**; A2 as H-I8; R1 PASS as predicted |

- **E133-A3 PASS, near its low edge.** c(H-F32) / c(H-I8) = 0.927 [0.901, 0.949], inside [0.90, 1.11] (E111's was 0.999). In this session fp32's c sits
  7% below int8's, but fp32 sat at the trip, so its c is the governor's operating point. The registration flagged this under "What this cannot
  say".
- **Four holds, two sessions, one heat path.**
  - The four c's: 0.672 and 0.671 (E111, Sunday afternoon, idle 45–47 °C), 0.700 and 0.648 (E133, Monday late morning, idle 44.0 °C). Mean 0.673,
    range 0.648–0.700.
  - All four sit inside aifoundry2's band [0.62, 0.82]: A2 prior PASS on both of E133's holds.
  - All four sit wholly outside the lab's September model (1.25–1.70), E97's aifoundry3 plateau (0.86–0.95) and the 76 s line (0.40–0.52): FAIL ×6,
    as predicted.
- **Why R1 on H-I8 is not a PASS.** H-I8's c depends on the window here, because the die wandered (result 3). Over 5-minute windows from minute 5 it
  reads 0.672–0.719. The window from minute 5 reads 0.672, E111's value. The registered last 300 s catch the die coming back down from 57 to about
  56.2 °C. So the ratio's range reaches 1.111, past the band's 1.11 by 0.001: INCONCLUSIVE, not a FAIL.
- **The frozen point predictions.**
  - H-I8: predicted 55.8 °C at 39.9 W from a 43.25 °C idle. It read **56.36 °C at 39.20 W from a 44.0 °C idle**. The rise was 12.36 °C (predicted
    12.50) and the board 17.67 W over idle (predicted 18.61).
  - H-F32: predicted at 65.0 °C if at the floor. It read 65.91 °C, at the trip (result 2).
  - Against E111's, H-I8's plateau sits 2.64 °C lower, at 1.42 W less, from an idle 2.5 °C cooler (E111's idles around its hold: 46.0 and 47.0 °C).

**2. E133-R2: fp32 random sat at the governor's trip, not at its floor. The frozen key missed by the governor's whole degree; A1's key did not**
([`results.json`](results.json) `R2`, `beside.H-F32.minutes`; [`a1_readings.json`](a1_readings.json)). *(Added after verification: A1's key agreed
on an idle reading too coarse to test it, [C2](#corrections-after-verification-mon-2-nov-2026).)*
- **The die was pinned.** The minute bins read 65.88–66.01 °C from minute 1 to the end (from minute 8 the range is 0.097 °C). The clock left the
  600 MHz floor in 11.1% of the plateau's in-kernel samples, the ones the scorer reads. In the raw telemetry of the same 300 s (2,998 rows) it read
  700 MHz in 9.9% and 800 in 1.5% (desk count, not a registered reading). It left the floor in 5.7% of the 300 s before, and in 4–13% minute by
  minute from minute 2. The board read 55.23 W.
- **Why the frozen key missed.** W2's REST idle read 44.0 °C in all 600 samples. That is above the frozen key's 43.5 °C, so R2 predicted AT THE
  FLOOR, and below A1's 44.54 °C, so R2w predicted AT THE TRIP. At the floor the plateau would sit near idle + 21.5–21.8 °C = 65.5–65.8 °C. The
  governor's whole-degree mean reads that as 65, which is not above the threshold. So the governor lets the clock up, the die rises to read 66, the
  governor steps down, and it holds the die at the 65/66 boundary.
- ***The trip, read directly*** *(dated note, [C1](#corrections-after-verification-mon-2-nov-2026) and C2, Mon 2 Nov 2026, after verification; post
  hoc, from committed files: [`corrections_e133.txt`](corrections_e133.txt)).*
  - **The rule.** The governor steps the clock down only when the whole-degree mean of the minion-shire sensors reads above its 65 °C threshold,
    so at 66. That mean is an integer division (et-platform `836a4ab`: `pvt_controller.c`'s minion average, `thermal_pwr_mgmt.c:884`; A1 §4).
  - **The plateau read 66.** Over the scorer's 300 s window, H-F32's 2,998 raw rows read **66 in 86.6%**, 65 in 12.0% and 67 in 1.4%. What reads 65
    is the floor plateau that did not happen, near 65.5–65.8 °C.
  - **The SP's own trace logged the trip at 66.** Its 30 dumps carry 89 thermal throttle-down lines. Each dump is 8 KiB and holds only the
    buffer's last 44–45 entries, so later dumps repeat earlier entries. Told apart by their timestamps, the lines are **20 distinct events**: the
    last ten of the probe's fp32 randn run and the last ten of H-F32. **Every one reads "current temperature: 66, threshold: 65".**
  - **So R2w's agreement is a weak test.** W2's REST idle read 44 in all 1,212 raw rows (all 600 of the scorer's samples): a whole degree with no
    dither. The reading places the die somewhere in the degree from 44 to 45 °C, and A1's 44.54 °C key lies inside it, so the reading cannot put the
    die on either side of the key. A die near a whole-degree edge dithers: the smoke's rest at 10:14 read 43 in 189 of its 213 rows and 44 in 24.
    W2's REST never did. R2w stays as scored, AT THE TRIP as predicted, but it does not confirm the key. The plateau's readings and the trace above
    are the direct evidence for the whole-degree trip.
- **Sunday was different.** E111's idle was 45.0 °C, which put the floor's plateau at 67.3 °C, above the trip, so its clock stayed at the floor.
  **A 1 °C cooler idle moved fp32 random from the governor's floor to its trip.**
- **A1 on H-F32 reads the fine W, and FAILs (as predicted) while the die stood still.** The clock was held at 600 MHz in 89% of the window (≥ 70%),
  so A1 reads the fine W. That rose 0.134 W/min as the clock's share moved between 0.87 and 0.96 from minute to minute, so A1 FAILs. The die's own
  slope was −0.008 °C/min (se 0.0025), inside the 0.02 bar: at the trip the governor, not the cooling, held the die still. E133.md's "What this
  cannot say" expected A1 to read the die at the trip. The scorer reads the fine W whenever the clock is held in ≥ 70% of the window, and the
  scorer is the rule, so the verdict stays FAIL.

**3. E133-A1, steadiness: FAIL on both holds again, as predicted, and int8's wander repeated** ([`reduce.txt`](reduce.txt) PART A minute rows;
[`results.json`](results.json) `beside.H-I8.minutes.wander`).
- **H-I8's die by the minute.** 56.0 °C from minute 5 to minute 12; 56.5–57.0 from minute 13 to minute 20; back to 56.1–56.7 from minute 21 to
  minute 26. From minute 8 the wander spans 1.05 °C.
- **The same size as Sunday's, the other way round.** E111's H-I8 wander was also about 1 °C, but it went down first (59.0 → 58.0 → 59.0) where
  this one went up first.
- **The cause is not established.** The A4 proxies are coarse and moved by under a degree, and the camera phone's battery read 29.4 °C throughout.
  With no inlet thermometer, the inlet stays unread.

**4. Item 8: the cool probe fell further on the line than either reading predicted, and its hold followed the room's reading.** E133-W2 sat 2.8 °C
below the night's baseline on the W-derived rest die. The scorer counts eight probes and puts six on the line and the hold: E98's P1, P3, P6 and
P7, E111-W2 and E133-W2 ([`results.json`](results.json) `B`):

| rule | verdict | what the data say |
|---|---|---|
| E133-B0, the gate (E98-R0's) | **OK** | six probes for the line, rest-die range 3.68 °C (E111's five: 1.54) |
| E133-B1 = E98-R1 on all, the 76 s line on the rest die | **ABOVE_TARGET** (as predicted) | **0.756** [0.584, 0.929] on 4 df (E111's five: 0.472 [0.371, 0.573]) |
| E133-B2 = E98-R2 on all, the hold's die on the rest die | **SUPPORTS** (no side predicted) | 0.946 [0.396, 1.496] (E111: 1.48 [−0.03, 2.98], INCONCLUSIVE) |
| E133-BV = E98-V | **PARTLY** | B1 above target, B2 supports |
| **E133-B3c line**, the cool probe against the night's baseline | **ABOVE_TARGET** (as predicted) | **0.808 [0.736, 0.880] per °C**: dx −2.80 °C, line 37.08 °C against 38.12 (E111's fit, 0.47) and 38.69 (the room's 0.25) |
| E133-B3c hold | **SUPPORTS** (no side predicted: the registered question) | **0.732 [0.429, 1.035] per °C**: hold 56.39 °C against 55.48 (the room's 1.12), 54.84 (E111's fit) and 52.94 (a changed path's 2.08) |
| E133-B4 = E98-S4, fp16 ones at the trip | **POSITIVE_BELOW_TARGET** (MHz), **BELOW_TARGET** (W) | −6.5 MHz/°C [−11.2, −1.8]; −0.36 W/°C [−0.92, +0.21]. E133-W2's fp16 ones ran at 800 MHz, under the trip, which E98-S4 does not model |

- **By the registration's own refutation clauses, this probe refutes both readings of the 76 s line.**
  - The room's reading (0.25) is refuted at this leverage: B3c line is ABOVE_TARGET.
  - E111's fit (0.47) is refuted too: B3c's line interval excludes 0.47.
  - The line moved 0.81 °C per °C of rest die. That is one probe, and the interval comes from E98's frozen per-probe scatter (0.089 °C), not from
    this probe's own.
  - With E133-W2 counted, the six-probe B1 slope steepens from 0.47 to 0.76.
- **The hold, the registered question, followed the room's reading at its low edge.** It moved 0.73 °C per °C. That reaches E98-R2's band and
  excludes the 0.25 floor (SUPPORTS), and it excludes a changed path's 2.08. The hold of 39 read 0.91 °C above the room's prediction.
- **Beside the rules**, E98's side readings: S1 1.44 W/W [0.86, 2.03] (ABOVE_TARGET); S2 1.70 [0.58, 2.82] (INCONCLUSIVE); S3, the run from rest
  on eight probes, line 0.74 [0.39, 1.09] and fine W 1.24 [0.69, 1.79] ([`results.json`](results.json) `B.S1`, `B.S2`, `B.S3`).

**5. The room: the idle die did not move a whole degree in two hours.** All four REST readings, from 10:35 to 12:40 PST, read 44.0 °C in every
sample, at 21.41, 21.45, 21.53 and 21.55 W ([`results.json`](results.json) `A.idles`).
- **Against E111.** E111's idles read 45 → 47 °C at 21.70–22.09 W over its afternoon. Like for like, before any hold, this session's idle was 1.0 °C
  and 0.29 W below E111's W2 (45.0 °C, 21.705 W).
- **Before E126.** From 06:52 to 07:32 PST, before E126 held the card, the idle read 43.25 °C at 21.30 W (A1 §6).
- **The proxies.** There is no inlet thermometer. The idle die is the proxy, and it also carries the card's own recent heat (E111's idles after its
  holds read 46–47 °C; this card's read 44.0 after both holds).

**6. The session** ([`queue.jsonl`](queue.jsonl), [`queue.out`](queue.out)). Every step exited 0. Nobody else was logged in at any of 573 checks
([`idle_logins.jsonl`](idle_logins.jsonl), counts only):

| step | start → end (PST) | rest before (min) | card-min | exit |
|---|---|---|---|---|
| SMOKE | 10:14:32 → 10:15:14 | — | 0.70 | 0 |
| W2 (E98's probe, then H-F32) | 10:35:14 → 11:22:39 | 20.0 | 47.40 | 0 |
| END | 11:37:58 → 11:40:00 | 15.0 | 2.03 | 0 |
| W1B (REST, then H-I8 from rest) | 11:55:00 → 12:23:38 | 15.0 | 28.64 | 0 |
| END2 | 12:38:38 → 12:40:40 | 15.0 | 2.03 | 0 |
| W3 (optional) | **not run**: the W3 rule at 14:05:07 (10-minute idle die 44.925 °C < 45.0); `SKIP-W3` 14:05:29; the queue ended 14:05:40 | — | 0 | — |

**The W3 rule's reading.** The reading was taken at 14:05:07 PST from aifoundry2's own 5 s history: 120 rows, none held, die mean 44.925 °C, board
21.626 W. It is reproducible from [`history/aifoundry2-2026-11-02.jsonl.gz`](history/aifoundry2-2026-11-02.jsonl.gz), 13:55:07–14:05:07. The
budget would have held W3 (80.81 + 24 ≤ 110), and nobody else held the card. Only the idle rule failed, by 0.075 °C. The afternoon warmed the idle
from 44.0 °C (the 10-minute mean at 12:49 and at 13:28) to about 44.9 °C by 14:05, not the full degree.

**The peaks and the stops.** W2 peaked at **88.65 W** during H-F32 (10:59:16 PST, at 700 MHz: the governor stepping up from the floor at the trip)
and at 88.62 W in the probe's own fp32 randn run. It had 372 samples over 85 W: 322 in H-F32, 306 of those at 700 MHz. None was over 93 W. Its die
mean peaked at 67 °C, and the hottest sensor's running maximum read 69 °C, carried from before the session. W1B peaked at 40.31 W, die 57 °C. The stops,
80 °C and 93 W on three samples, never came near ([`results.json`](results.json) `peaks`).

## What it changes

- **Kinds page, item 9.** A second session per kind ran *(corrected after verification, [C5](#corrections-after-verification-mon-2-nov-2026):
  this said "The heat path's coefficient has a replicate")*. R1 is PASS for fp32 random (0.966), with Sunday's hold at the governor's floor and
  Monday's at its trip, and INCONCLUSIVE for int8 −1s, by 0.001 (1.042 [1.005, 1.111]). Four holds over two sessions and two kinds read 0.648–0.700
  °C per board W. Still open:
  - no hold is steady by the registered test (A1 FAIL on all four holds of the two sessions);
  - int8's 1 °C wander repeated, cause unknown;
  - no inlet thermometer exists.
- **Kinds page, item 8.** One cool probe, 2.8 °C below the night's on E98's W-derived rest die *(the scale named after verification,
  [C6](#corrections-after-verification-mon-2-nov-2026))*, refutes both readings of the 76 s line's drift: the line moved 0.81 °C per °C of
  rest die, against the room's 0.25 and E111's fit of 0.47. The hold followed the room's reading (0.73 per °C, SUPPORTS on E98-R2's partition). Still
  open: a warm probe (W3 did not run: the idle reached 44.9 °C, not 45.0) and an inlet thermometer.
- **The governor (the speed half).** On this card fp32 random sits at the 600 MHz floor or at the governor's trip, a whole-degree reading of 66
  against its 65 °C threshold, depending on a 1 °C change in the idle. At the trip the clock leaves the floor in about 11% of samples (mean 612.7
  MHz), and the die is pinned to within 0.1 °C at the 65/66 boundary of the whole-degree mean the governor reads *(corrected after verification,
  [C1](#corrections-after-verification-mon-2-nov-2026): this said "the 65 °C trip" and "Under the trip")*.

## Registered against what happened

| registered ([`E133.md`](../../../../tools/claims-v3/e133/E133.md)) | happened |
|---|---|
| registration, predictions, scorer and self-test on origin before the claim and any device access | `9723d79b` on origin 09:00:52; first session blocked (Tailscale), nothing ran; A1 `f842cc39` on origin 10:12:27; claim 10:14:18; first device access 10:14:32 |
| the smoke by 11:00 (A1: by 11:30) | 10:14:32, exit 0 |
| SMOKE, W2, END, W1B, END2 in order, E98's rest rule | as such, every step exit 0; rests 20.0, 15.0, 15.0, 15.0 min |
| nothing set; config at both ends of every step and session | 42 reads, all TDP 65 W, threshold 65 °C, 600 MHz idle |
| no WRITE of any kind; the residency read never sent | none sent; 30 residency reads answered unsent (`*/e133-not-sent.jsonl`); 0 drains |
| at most 110 card-minutes (less the first session's 0); no step after 15:00; hard stop 16:00 | 80.81 card-minutes; the last step ended 12:40:40; the queue ended 14:05:40 |
| W3 only if the idle reaches W2's REST idle + 1.0 °C at about 14:05, and the post first | 44.925 °C < 45.0 at 14:05:07: not run, not claimed (`SKIP-W3`) |
| predicted c 0.672 (H-I8), 0.671 (H-F32); R1 PASS ×2 | 0.700, 0.648; R1 INCONCLUSIVE (H-I8), PASS (H-F32) |
| predicted R2 AT THE FLOOR (the idle read 44.0 ≥ 43.5) | AT THE TRIP: **not as predicted**; A1's R2w (44.54) predicted it, a weak test: the idle's whole-degree reading cannot place the die on either side of 44.54 ([C2](#corrections-after-verification-mon-2-nov-2026)) |
| predicted A1 FAIL ×2, A2 prior PASS ×2 and FAIL ×6, A3 PASS | as predicted |
| predicted B0 OK, B1 ABOVE_TARGET, B3c line ABOVE_TARGET (about 0.47) | OK; ABOVE_TARGET (0.756); ABOVE_TARGET at 0.808 (it also excludes 0.47) |

## Device commands sent

The classification is E133.md's table, from et-platform `836a4ab` (BL2 0.22.0, the build aifoundry2 runs). It was re-checked before the claim by
Q136(w)'s checker at HEAD: GO, 37 send sites, 0 disallowed, with the two reviewed exceptions
([`amendment-a1-check.txt`](../../../../tools/claims-v3/e133/amendment-a1-check.txt) §4). The counts below come from the collected records
([`commands_sent.json`](commands_sent.json), [`count_commands_e133.py`](count_commands_e133.py)):

| program | command(s) | class | sent in this session |
|---|---|---|---|
| `ettelem sample --every-ms 100` (no `--reset-ms`), one sampler per run | `DM_CMD_GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE` (2 PMIC voltage-register reads), `GET_MODULE_VOLTAGE` (9 PMIC voltage-register reads), `GET_ASIC_FREQUENCIES` | READ (the voltage reads are the owner's allowed ones, 2 Nov 2026) | 48,401 sample rows from 20 sampler processes, so about 48,401 rounds of the six GETs |
| `ettelem config`: after every run and at each session's ends (`run_hpl.py`), at both ends of every step (the queue), at the session's start and end (`run_e133.sh config`) | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` | READ | 30 + 10 + 2 = 42 |
| `ettelem sptrace` after every run | no SP command: the driver's trace ioctls and an MMIO read | READ | 30 |
| `ettelem residency 2 3 4 5 6` (`run_hpl.py:622`) | — | **NOT SENT** (A1's guard on the chain; `run_e133.py`'s wrapper) | 0 sent; 30 answered unsent |
| `dev_mngt_service -m DM_CMD_GET_MODULE_POWER` (run_hpl's drain) | `GET_MODULE_POWER` | READ | 0 |
| `sparsity_host` (`build/sparsity_t2`) | no device-management command: ops node only | — | 503 launch processes |
| `et-who`, `et-lab-manifest`, `sensors -j`, `uptime`, `who`, `flock`, `curl` to the camera phone | none (sysfs, `/proc`, `fuser`, host hwmon) | — | — |
| any WRITE: the statistics reset, a set of any kind, the firmware-revisions query, a reset | — | — | **none** |

## Departures (dated)

- **A1** is the registration's amendment for this session (E133.md § Amendments). It was written before the claim and before any E133 data.
  *Dated note ([C4](#corrections-after-verification-mon-2-nov-2026), Mon 2 Nov 2026, after verification): A1's date line reads "written
  10:08–10:15 PST", a window that contains the claim (10:14:18) and the first device access (10:14:32). A1 was final at its commit, 10:12:24 PST,
  and on origin at 10:12:27, before the box access (10:12:41), the claim and any data. A1 itself is not edited.*
- **D1: the box's checkout was not pulled (Mon 2 Nov, 10:12 PST).** `git pull --ff-only` in aifoundry2's lab checkout (at `0c187e12`) refused,
  because other lanes' rsynced files, untracked there and since committed, would have been overwritten. Nothing of theirs was touched. E133's own
  directory was rsynced from the Intel's clone at origin/main `f842cc39`, and the sha256 of 38 files was compared on both sides: the chain, the
  kinds table, the 8 tiles and every E133 file. All were equal, and A1's guard checks the chain again at every session.
- **D2: a first collection, and a first look (11:40 PST).** Between END and W1B, while the card rested, `collect_e133.sh` ran once for a first look.
  The scorer refused to score without W1B: its "beside" reading needs every hold. So the first look called the scorer's own Part A and R2 functions
  in scratch, and nothing of it is committed. The data here come from the collection at 12:41, after END2, and again at 14:06, after the queue
  ended. Only the queue's records changed (W3's skip and the queue's end, `results.json` `queue`); every number and verdict is the same.
- **D3: "the morning".** The holds ran from 10:35 to 12:24 PST, late morning and midday (A1 §3). R2 is keyed on the idle die, not the hour.
- **D4: two small corrections to A1's text (Mon 2 Nov, ~13:00 PST, from the first lane's fix pass; A1 itself is not edited).** Neither changes a
  number used anywhere.
  - A1 §6 gives E111's W2 idle as 21.71 W. It is 21.70 W (E111 `results.json` `A.idles.W2.w`, 21.7048).
  - A1 §6 says the morning range does not come from the minutes after E126's release. That holds for the range's ends, which come from 06:46–07:32,
    but the first lane's own 08:16–08:26 bin (43.31 °C, 21.29 W) also lies inside the range.
  - The first lane's blocked window had 26 attempts from 08:40:44 to 09:29:34: the first ssh, 14 probes by hand and the 11 in its `probes.log`.
    A1 §1's "11 logged probes … plus unlogged attempts from 08:40:44" counts the same attempts.
- **D5: the session-end config read came after the release (Mon 2 Nov, 14:05:44 PST; written after verification,
  [C3](#corrections-after-verification-mon-2-nov-2026)).** The queue's END2 end snapshot read the config at 12:40:40, inside the claim, and this
  session's clause left the post at 12:41:01. W3 did not run, so the card was never claimed again, and from 13:02:58 the post read fully released
  (the aifoundry3 lane's " — released"). The session's last `ettelem config` (`run_e133.sh config session-end`, 14:05:44) then opened aifoundry2's
  management node 85 minutes after the clause was dropped, when no clause named the card.
  - It was a READ (A1's five GETs), under `flock -n` and `timeout 10`, on a free card: `et-who` read nothing held, and the 120 history rows the W3
    rule read up to 14:05:07 show nothing held.
  - It did no harm and changes no number.
  - Later designs take the session-end read before the clause is dropped, or put the clause back for it.

## How it ran

The first lane was blocked by the Tailscale lapse and never reached the card; it had only looked at the box, 08:21–08:26 PST, before the lapse (A1
§1; corrected after verification, [C4](#corrections-after-verification-mon-2-nov-2026): it said "never reached the box"). This session ran from
the Intel, each box step in a script file run by `ssh aifoundry2 'bash -s' < file`:

```bash
# 10:12:24 amendment A1 committed (f842cc39), on origin 10:12:27
# 10:12:41 aifoundry2: et-who "No process holds an ET-SoC-1 device node or card lock", the lock free, no other user logged in
rsync -a --exclude=__pycache__ tools/claims-v3/e133/ aifoundry2:claude/et-soc1-prototyping/tools/claims-v3/e133/   # then 38 hashes compared: equal
bash tools/claims-v3/e133/run_e133.sh check                  # 10:13:20: idle-login rule 0 blocking; binaries and chain as audited
# 10:14:18 the day's #community-lab post rewritten with this card's clause (message 1566837317765963987)
bash tools/claims-v3/e133/run_e133.sh config session-start   # 10:14:32: TDP 65 W, threshold 65 C, 600 MHz
bash tools/claims-v3/e133/run_e133.sh go 10:14               # 10:14:32: the queue, detached (smoke latest 11:30 by A1)
# 12:41:01 the card's clause dropped from the post (another lane's aifoundry3 clause kept)
# 14:05:07 the W3 rule read on the box's own history: 10-minute idle die 44.925 C < 45.0, so W3 not claimed
bash tools/claims-v3/e133/run_e133.sh skip-w3                # 14:05:29; the queue skipped W3 and ended at 14:05:40 ("done")
bash tools/claims-v3/e133/run_e133.sh config session-end     # 14:05:44: TDP 65 W, threshold 65 C, 600 MHz; et-who: nothing held (after the release: D5)
```

Then on the Intel, from the top of the repository:

```bash
bash tools/claims-v3/e133/collect_e133.sh docs/reports/data/2026-11-02-e133-heat-holds 1793643240 <to>
python3 tools/claims-v3/e133/reduce_e133.py docs/reports/data/2026-11-02-e133-heat-holds \
    --out docs/reports/data/2026-11-02-e133-heat-holds/results.json > docs/reports/data/2026-11-02-e133-heat-holds/reduce.txt
python3 docs/reports/data/2026-11-02-e133-heat-holds/a1_readings_e133.py docs/reports/data/2026-11-02-e133-heat-holds/results.json \
    docs/reports/data/2026-11-01-e111-heat-steady/results.json > docs/reports/data/2026-11-02-e133-heat-holds/a1_readings.json
python3 docs/reports/data/2026-11-02-e133-heat-holds/count_commands_e133.py docs/reports/data/2026-11-02-e133-heat-holds \
    > docs/reports/data/2026-11-02-e133-heat-holds/commands_sent.json
```

## Joins and traps

- **Per board W, open loop.** c has the leakage's climb in its watts, as in E111. It is not per W of switching. The die is the firmware's
  whole-degree 34-sensor mean. Over 300 s its readings dither enough to read to about 0.1 °C, except at the trip, where the governor pins it.
- **At the trip, c is the governor's operating point.** H-F32's 0.648 is a steady die at a time-averaged 55.23 W, with the clock dithering above the
  floor. E111's 0.671 was read at the floor. R1 compares them as registered.
- **The two holds started differently, as in E111.** H-I8 started from rest (W1B). H-F32 started straight after E98's probe series and its hold of 39,
  from 53 °C.
- **Every idle read 44.0 °C**, so each c's idle-before/after range adds nothing from the idle. The range comes from the plateau against the window
  before it.
- **E133-W2 is the only new probe in Part B, and it is cool.** B3c rests on one probe and E98's frozen scatter. B1's six-probe interval rests on 4 df.
- **The proxies are coarse.** The NIC and NVMe sensors heat with their own hosts, a card is a proxy only while free, and the camera phone's battery
  did not move.

## Corrections after verification (Mon 2 Nov 2026)

An independent verifier read the registration and A1, this data, the source of the box's `ettelem` binary and the firmware handlers at `836a4ab`, the
same afternoon.
- **The write lens passes: no WRITE of any kind.** `since_reset_ms` is −1 in all 48,401 sample rows, and the SP's running board maximum never fell.
  All 42 config reads read 65 W / 65 °C. The residency read was never sent, no drain ran, and the 30 SP trace dumps hold only the governor's events.
- **It recomputed the registered rules** (R1, A3, R2, B1, B3c and the tally), reproduced the W3 rule's reading from the committed history, and checked
  the amendment's timing against the Intel clone's reflog and the day's one post.

What it found is wording, here and in the lane's own result: C1–C6, made above as marked edits and dated notes. The registration, the scorer's outputs
([`results.json`](results.json), [`reduce.txt`](reduce.txt), [`a1_readings.json`](a1_readings.json)) and every registered number and verdict are
unchanged. The new counts are post hoc: [`corrections_e133.py`](corrections_e133.py) → [`corrections_e133.txt`](corrections_e133.txt), from
committed files only. They refine one of the verifier's counts: its 89 throttle-down lines are 20 distinct events.

| | what was wrong | what changed |
|---|---|---|
| C1 | **Where the governor trips.** The lane's result said a plateau at 65.9 °C "reads 65, which is not above its 65 C threshold", and that the floor would have settled the die "just under the governor's 65 C trip". The plateau mostly read 66, above the threshold. What reads 65 is the floor plateau that did not happen, near 65.5–65.8 °C; result 2 had this right. What it changes said "the 65 °C trip" and "Under the trip" | A dated note under result 2 gives the direct evidence. The plateau's 2,998 raw rows read 66 in 86.6%, 65 in 12.0% and 67 in 1.4%. All 20 distinct thermal throttle-down events in the SP trace (89 lines in 30 dumps that repeat entries) read "current temperature: 66, threshold: 65". What it changes now says "the governor's trip, a whole-degree reading of 66 against its 65 °C threshold". The result's blog points 2 and 3 are rewritten from result 2 |
| C2 | **R2w's agreement was read as a confirmation.** W2's REST idle read 44 in every sample, a whole degree with no dither. That places the die somewhere from 44 to 45 °C, and R2w's 44.54 °C key lies inside that degree | Dated notes in Results first, under result 2 and in the registered-against table. R2w stays as scored, AT THE TRIP as predicted, but it is a weak test; the trip's direct evidence is C1's readings and trace |
| C3 | **One card access fell outside the claim**: the session-end `ettelem config` at 14:05:44, 85 minutes after the clause was dropped (12:41:01). The post had read fully released since 13:02:58 | Departure D5: a READ under the lock on a free card, with no harm done. Later designs take the read before the release, or claim again for it |
| C4 | **Two timeline slips.** The header and How it ran said the first lane "never reached the box". It looked at the box from 08:21 to 08:26 (A1 §1), and the registration's "Before the freeze" numbers come from that look. A1's date line, "written 10:08–10:15 PST", contains the claim (10:14:18) and the first device access (10:14:32) | "Never reached the card" in both places, and a dated note on Departures' A1: final at its commit, 10:12:24 PST, on origin at 10:12:27, before the box access (10:12:41), the claim and any data. A1 itself is not edited |
| C5 | **Item 9's "replicate" was given whole.** By R1 it holds for fp32 random only, and that PASS compares Sunday's floor with Monday's trip. For int8 −1s, R1 is INCONCLUSIVE | Result 1 and What it changes give item 9 per kind, with the two regimes named |
| C6 | **Blog-point wording** in the lane's result. "A one-degree cooler room": no inlet thermometer exists, and the idle die also carries the card's recent heat. "700 MHz in about 10%", cited to `results.json` `R2`: it is result 2's desk count. "Steady to about 1 C, not 0.1 C": H-F32 was held within 0.1 °C at the trip. "2.8 C cooler": that is on E98's W-derived rest-die scale, not the die reading | Rewritten in the result. Here, What it changes' item 8 names the W-derived rest die |

## Files

| file | what |
|---|---|
| `README.md` | this file |
| `results.json`, `reduce.txt` | `reduce_e133.py`: Parts A and B, R1, R2, B3c, the verdicts, the regression (E98's and E111's results reproduced) |
| `a1_readings_e133.py`, `a1_readings.json` | amendment A1's R2w from the scorer's own R2 output, and the two sessions per kind side by side (E111's committed `results.json` against this one) |
| `count_commands_e133.py`, `commands_sent.json` | every device command the session sent, counted from the records |
| `corrections_e133.py`, `corrections_e133.txt` | added after verification, post hoc, from committed files only: H-F32's plateau readings and clock, the REST blocks' readings, the SP trace's throttle-down events told apart by timestamp, the minute wander and the cool probe's W-derived lead |
| `SMOKE/`, `W2/`, `END/`, `W1B/`, `END2/` | raw `run_e133.py` sessions: `e133.json` (the chain's hashes), `session.json`, `kspeed.json`, `runs.jsonl`, `launches.jsonl.gz`, `queries.jsonl`, `marks.jsonl`, `e133-not-sent.jsonl`, `tel/*.jsonl.gz` (10 Hz), `sp/`, `logs/`, `manifest.txt`, `run.out`, `run.log`, the queue's `snapshot-*.json`, `sensors-*.json`, `config-*.txt` |
| `config-session-start.txt`, `config-session-end.txt` | the session's first and last `ettelem config` (10:14:32 and 14:05:44 PST) |
| `queue.jsonl`, `queue.out`, `status.json`, `schedule.json` | the queue's records and schedule (A1's smoke latest 11:30) |
| `idle_logins.jsonl` | the idle-login rule's decisions at every check, counts only |
| `phone.jsonl` | the camera phone's `/health`, once a minute (descriptive) |
| `history/<box>-<UTC date>.jsonl.gz` | the three boxes' own 5 s history over the session, numbers only |
