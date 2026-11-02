# E118 data: aifoundry1 card 0 at 600 MHz (static TDP 0) against its own 800 MHz — a flipped bit's price on a second card (Q133, Sun 1 Nov 2026)

Pre-registration, frozen predictions and harness: [`tools/claims-v3/e118/`](../../../../tools/claims-v3/e118/README.md),
commit `28e625c9`, pushed **14:49:42 PST**, before the claim and before any card access. The field manual's change
record, its live gates filled and committed as the GO (`f37fa285`, **14:51:51 PST**) ten seconds before the one write
at 14:52:00.933, is [`CHANGE-RECORD.md`](CHANGE-RECORD.md) (also in the tools directory). Card claimed in
`#community-lab` at **14:50:28 PST** (message `1566585247326535741`). Request Q133; it answers
[the kinds page's section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 15**'s last sentence, "E72 on a second card, which needs a governor move" (the rest of item 15 is other work,
F3), under the owner's governor OK of 1 Nov.

*Corrected after verification the same afternoon (Sun 1 Nov 2026, about 16:15 PST), at the desk: no card touched,
nothing set, nothing re-run. Wrong sentences are replaced in place below, each marked;
[Corrections after verification](#corrections-after-verification-sun-1-nov-2026) lists F1–F5, and
[`posthoc_g3_ring.txt`](posthoc_g3_ring.txt) prints F1's numbers from the committed ring dumps. No price, interval or
verdict changed. The major ones: G3's log half counted one `Power throttle up` after the restore where the ring holds
two (G3 still passes: ≥ 1 was registered), and rule 8 is PASS only for the version-matched source, UNKNOWN for the
exact running build.*

## Results first

**The pin worked as on aifoundry2, and so did the release.** All 221 smoke samples and all 11,182 samples of the
pinned passes and the probe sat at **600 MHz**; the 105 measured runs averaged **0.5183 V**; every one was kept. After TDP 65 was
written back, the return burst stepped **600 → 700 → 800 MHz** in one launch (117 / 2 / 97 samples) with no reset,
and the closing read at 15:17:33.8 equals the originals in every field (TDP 65 W, threshold 65 °C, `low_power`).
The SP trace ring adds the evidence E72 could not: **no governor event at all** while TDP 0 was set, and after the
restore **two** `Power throttle up` events, 0.21 s apart (`current pwr 23370`, then `25130` mW, against `tdp level:
65000`), each followed by its operating point, 700 then 800 MHz, and 600 MHz again at idle 10.16 s after the first:
the two-step ramp that all six complete ramps in the ring from before the pin show. *(Replaced after verification, F1:
the first version said exactly one.)*

**The price of a flipped mantissa bit follows the voltage on this card too** (`lq` h2 → h8 secant, board, per designed
flipped B mantissa bit, E60's estimator; [`verdicts.json`](verdicts.json)):

| | fJ per flipped bit | against |
|---|---:|---|
| E60, this card, **800 MHz**, 0.6039 V (20 Oct, 10 passes) | 102.49 ± 4.42 | — |
| **E118, this card, 600 MHz, 0.5183 V** (5 passes) | **71.46 ± 4.93** | registered prediction **75.71**, band 68.14–83.28 → **V1 PASS** |
| *the alternative: energy scaled with f too* | *56.78* | *band 51.10–62.46; the measurement is 3.0 SE above its centre* |

**V1m, the registered primary form** (both sides at the same leakage slope, on fixed pass sets), **PASS at both
registered slopes**: at 0 W/°C **73.27 ± 5.00** fJ against a V² prediction of 77.40 (band 69.66–85.14, −5.3 %); at
0.3273 W/°C (E60's own fit on this card) **67.57 ± 5.25** against 73.74 (band 66.37–81.12, −8.4 %). The predictions
are re-evaluated at the measured 0.5183 V, as registered.

The exponent n that reproduces each ratio as (V₆₀₀/V₈₀₀)ⁿ, with both sides' per-pass SEs propagated
([`posthoc_exponents.json`](posthoc_exponents.json), post hoc, as E72 published it):

| row | ratio 600/800 | n | n = 2 | clock alternative, n = 3.88 |
|---|---:|---:|---|---|
| registered (each side at its own fit) | 0.697 ± 0.057 | **2.36 ± 0.53** | +0.7 SE | 2.9 SE away |
| matched, 0 W/°C | 0.697 ± 0.061 | 2.36 ± 0.57 | +0.6 SE | 2.7 SE away |
| matched, 0.3273 W/°C | 0.675 ± 0.063 | 2.57 ± 0.61 | +0.9 SE | 2.1 SE away |
| minion rail (uncorrected) | 0.683 ± 0.016 | 2.50 ± 0.16 | +3.2 SE | 8.8 SE away |

So the second card says what the first said, at its own strength: **n is about 2.4–2.6, the clock-scaling reading is
excluded on the rail at 8.8 SE and disfavoured on the board at 2.1–2.9 SE**, and n = 2 sits inside every board row.
The board rows are wide because this card's 800 MHz reference has a 4.3 % SE (E60) and one of the five 600 MHz passes
reads low (per-pass secants 74.97, 77.33, 80.47, **52.53**, 71.99 fJ).

**Every registered rule:**

| | what | predicted | measured | verdict |
|---|---|---:|---:|---|
| **V1m** (primary) | secant, both sides at 0 and at 0.3273 W/°C | 77.40 / 73.74 (at 0.5183 V) | **73.27 ± 5.00 / 67.57 ± 5.25** | **PASS** at both |
| **V1** | secant at each side's own fit | 75.71 [68.14, 83.28] | **71.46 ± 4.93** | **PASS** (outside the alternative's band) |
| **V2** | the same on the minion rail | 67.90 [57.71, 78.08] | **62.77 ± 1.32** | **PASS** |
| **V3** | watts over `lq_h0`: `lq_h2`, `lq_h8` | 1.059 / 3.143 W, ±10 % | **0.889 / 2.858 W** | **FAIL**: `lq_h8` in band (−9.0 %), `lq_h2` 16.0 % low |
| **V4** | bend, full h ≥ 1 slope / secant | 1.395 [1.195, 1.595] | **1.494** | **PASS** (full ladder 106.74 ± 0.20 fJ) |
| **V5** | `lb` full slope / `lq` full slope | 1.110 [0.960, 1.260] | **1.126** | **PASS** (`lb` 120.22 ± 0.66 fJ) |
| **V6** | turn-on, `lb_h1` / `lq_h1` in watts | 3.172 [1.903, 4.441] | **3.255** | **PASS** |
| **C1** | the same-session 800 MHz control against E60's rows: `lq_h2`, `lq_h8` | 1.912 / 5.672 W, ±10 % | **0.810 ± 0.892 / 5.175 ± 0.547 W** | **FAIL**: `lq_h2` out (below), `lq_h8` in band (−8.8 %) |
| **G1** | the pin: every pinned sample at 600 MHz, and no `Power throttle up` while TDP 0 was set | 100 % and zero | **11,182 + 221 of 11,182 + 221; zero governor entries in the ring (dumps overlap)** | **PASS**, both halves |
| **G2** | pinned voltage | 0.519 [0.516, 0.522] V | **0.5183 V** | **PASS** |
| **G3** | restore read back; burst ≥ 700 MHz; ≥ 1 `Power throttle up` | all three | **65 W / 65 °C; 600 → 700 → 800 MHz; two events** (F1: first counted as one) | **PASS**, all three halves |

**Nine of the eleven registered rules pass; V3 and C1 fail as registered.** V1s (V1 against today's control instead
of E60's rows) was registered as reported only: 0.601, from a control secant of 118.9 ± 39.2 fJ on two passes, so it
says nothing (below).

- **V3 fails the way E72's did.** E72 measured `lq_h2` 12.2 % and `lq_h8` 8.9 % below the f·V² line through its own
  800 MHz rungs; here −16.0 % and −9.0 %. `lq_h2` is the smallest rung (0.89 W against a 0.46 W residual rms of the
  h ≥ 1 line), where a ±10 % band is tightest. On two cards now, the low rungs at 600 MHz draw less than f·V² predicts
  from 800 MHz.
- **C1 fails because the control is too noisy to check anything.** Of its three passes, E60's own gate set pass 2
  aside (its `anchor_pi` drifted 0.59 W, over the 0.3 W limit), and in pass 1 `lq_h2` read 0.08 W *below* its own
  `lq_h0` (44.82 against 44.90 W) — with the right operand bytes (its dumped tile is byte-identical to pass 3's and to
  E60's list, `4a694802…`). Passes 2 and 3 read `lq_h2` 1.72 and 1.70 W over `lq_h0`, near E60's 1.91. So the control
  neither confirms nor contradicts E60's rows; the frozen comparison stays the registered one, against E60. The
  control's other numbers agree with 20 Oct: 800 MHz in every kept window, **0.6038 V** (E60 0.6039), `anchor_pi`
  44.67–44.78 W (E60 45.23 W at 57 °C).

## Three cards at 600 MHz now

E118 runs at nearly E72's operating point (0.5183 V against 0.5179 V), with the same 20 items:

| | aifoundry1 card 0 (E118) | aifoundry2 (E72) | aifoundry3 (E60) |
|---|---:|---:|---:|
| `lq` full ladder, board | **106.74 ± 0.20 fJ** | 113.22 ± 0.47 | 116.75 ± 0.61 |
| `lq` full ladder, rail | 88.27 fJ | 85.07 | 87.52 |
| `lb` full ladder, board | **120.22 ± 0.66 fJ** | 125.45 ± 1.06 | 129.92 ± 0.48 |
| turn-on `lq_h1` / `lb_h1` | 0.524 ± 0.033 / 1.704 ± 0.013 W | 0.593 / 1.809 W | 0.594 / 1.954 W |
| bend (full / secant) | 1.494 | 1.430 | 1.360 |
| anchors zeros / ones / pi / randn | 22.10 / 29.83 / 29.86 / 44.69 W | 27.06 / 35.16 / 35.26 / 51.05 W | — |

On the board this card prices a flipped bit 6 % below aifoundry2 and 9 % below aifoundry3 at the same point; on the
rail the three agree within 4 %. Its anchors draw 5–6 W less than aifoundry2's, which is idle leakage, not switching.

## The session

All on aifoundry1 card 0, PST. Gates 14:50:39 (reads only) → GO commit 14:51:51 → watchdog and **TDP 65 → 0 at
14:52:00.933** → pinned smoke 14:52:02–14:52:25 → the launch-reading probe → **five 600 MHz passes 14:54:36–15:12:22**
(199–205 s each, 21 runs a pass, 105 runs, 105 kept, zero gate failures) → SP ring → **TDP 0 → 65 at 15:12:37.217**,
read back → return burst 15:12:38–15:13:01 → SP ring → **three 800 MHz control passes 15:13:02–15:17:23** → closing
read 15:17:33.8. **26.9 card-minutes** of the 45 allowed; the card was claimed 14:50:28–15:21:22.

- **The launch reading** was set by the pre-registered probe (README D7): at the pinned clock the heater brought the
  die from 47 °C only to 56 °C in its first 15 launches, so 57 °C after 58 °C (E60's card-0 gate) was not reached on
  every run; **55 °C after 56 °C** was, and every 600 MHz pass launched at 55 °C. The control launched at 57 °C after
  58 °C, as E60's 800 MHz rows did. The secant is a difference within a pass, so a different launch temperature moves
  the baseline of every rung alike.
- **Telemetry, no-PMIC-read profile** (README D1): every sample came from `ettelem-e118`; no voltage-register,
  statistics-reset or revisions request was sent. The reducer read the minion voltage from `sp.minion_mv[0]`. At
  `836a4ab` that statistic **is** the on-die PVT reading (`thermal_pwr_mgmt.c:845-848`, "voltages from PVT"), which is
  why it matches `die_mv` to 0.002 mV on E60's passes and E72's.
- **The envelope was never approached:** highest single board reading **52.75 W** (the 800 MHz control; 46.11 W while
  pinned), highest die reading **61 °C**; the guard (`session/guard.jsonl`) tripped zero times and saw no 300 MHz
  reading. Card 0's 75 W PMIC alarm stayed far away.
- **The power state after the restore.** The read within 62 ms of the restore write showed `max_power`; the closing read showed
  `low_power`. The power state is not a knob: the firmware re-derives it each pass from the SoC power against the TDP
  (`get_power_state`, `thermal_pwr_mgmt.c:403-414`, called at `:859`), and at TDP 0 any power is "over the TDP".
- **Kernel log:** card 0's `Error Event Detected` lines were **701 before and 701 after** (AER lines 21 and 21). *Post
  hoc, not registered:* by their timestamps the previous session on this card (E114, 14:18:10–14:39:48, the stock
  sampler) left 120 of them and E118 none. Two readings fit: the stock sampler's PMIC voltage-register reads, or that
  session's heavier load. This run does not separate them.
- **Card 1 was not touched:** no `et-who` line for it before or after; only the three stock-CLI calls (the vmin-LUT
  read, the set, the restore) opened its management node, each with both card locks held.

## Departures and residuals, named

- **No departure after the pre-registration.** The probe's outcome, the cut rules and the control's gate were all
  registered (README D1–D10); no item was cut and all five passes ran.
- **R1 — the board's exponent is not pinned.** n = 2.36 ± 0.53 (registered row) to 2.57 ± 0.61 (matched at 0.3273)
  holds both 2 and E72's board bracket (2.43–2.92). The rail reads 2.50 ± 0.16 here against E72's 1.60–1.72, so the
  two cards disagree on the rail: E72's caveat stands, and the rail is the PMIC's 1 s running average read one second
  after the board's window, uncorrected for leakage.
- **R2 — the control could not stand in for E60's rows** (C1 above). Its value was as a release check, which it gave:
  800 MHz in every kept window after the restore.
- **R3 — rule 8's build-identity residual**, as in E69 and E72: the card exposes no BL2 hash, so the source read
  establishes the behaviour of the version-matched source (et-platform `836a4ab`, BL2 0.22.0), on the footing E72
  accepted (CHANGE-RECORD, Rule 8). **So rule 8 reads PASS for the version-matched source and UNKNOWN for the exact
  running build:** the raw-temperature patch's second version, the boot-counter fix beneath it and the card's binary
  are unread, and neither commit is in the lab's copy of et-platform. *(Corrected after verification, F2: the change
  record labelled rule 8 PASS.)*
- **R4 — no independent reviewer saw the run, and no independent hardware recovery path exists for this fleet.** Both
  are why E118 wrote one volatile field, only downwards, armed a watchdog first and sent no clock, PMIC, reset or
  driver command.
- **R5 — a bookkeeping defect:** `session/steps.jsonl` carries each step's clock histogram in a `note` field whose
  inner quotes are not escaped, so those lines are not valid JSON. Read them as text; `session.log` carries the same
  facts.

## What it changes

- **The V² reading of a flipped bit's price is now a two-card, same-card-at-two-clocks result.** E72 alone excluded
  the clock-scaling alternative; E118 repeats it on a card with a different PMIC family and a 15 % lower 800 MHz
  price, with the matched form of the test passing at both registered slopes. On this card the two clocks are twelve
  days apart: the 800 MHz side is E60's session of 20 Oct (card 0's firmware that day is not on record), and today's
  same-session control was too noisy to confirm it (C1 FAIL, R2). *(Added after verification, F4.)* For the blog: on two cards, a flipped
  operand bit costs 0.65–0.70 of its 800 MHz energy at 600 MHz (the registered rows), where V² predicts 0.70–0.74 and "energy scales with
  the clock" predicts 0.53–0.55.
- **A third card at 600 MHz** for the full ladders: a flipped mantissa bit costs **107 fJ at the board on this card**,
  against 113 and 117 fJ on the other two; the busy partner's ladder 120 fJ against 125 and 130.
- **The governor method is proven on a third card and a second PMIC family**, with G1's and G3's log halves measured
  for the first time: TDP 0 produced no governor event at all, and the restore released the pin in two throttle-ups,
  one per step of the frequency table (600 → 700 → 800 MHz). *(Replaced after verification, F1: the first version said
  exactly one.)*
- **For the kinds page's section 11 item 15:** E118 answers its last sentence, "E72 on a second card, which needs a
  governor move" (the Horace hub's older item 5, "a second card at 600 MHz", asked the same). The rest of item 15 (the
  single-bit prices' other positions and base words, A's low bits, the sign on the rail, and why a live zero on A and a
  half-gated int8 tile cost more than priced) is other work and stays open. What stays open from E118 itself is the
  exponent's exact value: n = 2 is inside every E118 board row but 3.2 SE below this card's rail reading (2.50 ± 0.16),
  while on E72's card 2 is inside only the registered board row (outside every matched one) and the rail reads
  1.60–1.72. *(Replaced after verification, F3: the first version called item 15 answered and said 2 is inside on both
  cards.)*

## The claim

One post in `#community-lab`, message `1566585247326535741`, sent 14:50:28.709 PST: "<ai> **Claude says:** using
aifoundry1 card 0 for 1 h, until ~15:50 PST [doc](…)". Edited at **15:21:22 PST** to append " — released"; read back
as "… until ~15:50 PST doc — released (edited)".

## Corrections after verification (Sun 1 Nov 2026)

The workflow's independent verifier returned "holds with fixes". It found the governor move safe and honestly recorded,
and named two major and three minor faults, all in the write-up. It reproduced `verdicts.json` from the committed data,
and one read-only read of its own at 15:48:23 PST found card 0 at its originals (TDP 65 W, 65 °C, `low_power`,
600 MHz; [`session/verify-read-154823.out`](session/verify-read-154823.out)). Corrected at the desk the same
afternoon: no card touched, nothing set, nothing re-run. **Not changed:** every price, interval and verdict;
`results600.json`, `resultsC.json`, the runs CSVs, the matched reductions and `posthoc_exponents.json`; the frozen
registration (`tools/claims-v3/e118/README.md`, `predictions.json`, the scripts).

- **F1 (major): two throttle-ups after the restore, not one.** Between the dump after the pinned passes and the dump
  after the return burst the ring holds **eight** new entries (covered): two `Power throttle up` lines, 0.206 s apart
  (`current pwr 23370` and `25130`, `tdp level: 65000`); after each a binary power-status record and its operating
  point (700, then 800 MHz); and, 10.16 s after the first, a record and the operating point 600 MHz at idle. That is
  what 600 → 700 → 800 MHz needs at `836a4ab`, one throttle-up per step of the frequency table, and all six complete
  ramps in the dump from before the pin have the same two-step form. The return burst's 10 Hz telemetry agrees: 700 MHz
  first 0.88 s into the burst, 800 MHz 0.20 s later (SP: 0.19 s), 600 MHz again 9.71 s after that (SP: 9.89 s). The
  first count came from `score_e118.py`'s reader, `tools/claims-v3/dv2/sptrace_events.py`. Its walk from the header
  stops at the first entry that is not a printable string: here the 16-byte record written 79 ms after the first
  throttle-up. The lab already has the fix, `tools/claims-v3/hpl/sptrace_full.py` (E64 amendment A1, whose docstring
  names this defect), and [`posthoc_g3_ring.py`](posthoc_g3_ring.py) re-reads the three dumps with it. With `--apply`
  it writes the re-read ring blocks into `verdicts.json` and keeps the scorer's reading under `as_scored`, with a dated
  `corrections` entry. **G3 stays PASS** (≥ 1 was registered). **G1 is unaffected**: the dumps before the pin and after
  the pinned passes are byte-identical (`4df35ccf…`), so no reader finds an entry between them. The shared decoder is
  not edited here: the dv2, dv2v, hp and hpl tools import it (`hp/` and `hp/a2/` keep their own copies), and their
  committed outputs were made with it. Any count of ring events after an operating-point change made with it should be
  re-read with `sptrace_full.py`.
- **F2 (major): rule 8 is PASS only for the version-matched source.** At `836a4ab` the set is one assignment to a
  `volatile` `.data` field, with no flash or PMIC write on its path: PASS. For the exact build card 0 runs it is
  UNKNOWN: the raw-temperature patch's second version, the boot-counter fix beneath it and the binary are unread.
  Missing evidence is UNKNOWN, never PASS, by the change record's own rule. The GO was taken with that part unknown, on
  the footing the verified governor-preparation plan and E72 accepted; the card ended where it began (65 → 0 → 65 W).
  R3 above and the change record's dated correction now say so.
- **F3 (minor): item 15 is a bundle.** E118 answers only its last sentence, "E72 on a second card". The board exponent
  stays open, and the two cards' rails disagree. "2 is inside on both cards" is replaced too: on E72's card, 2 is
  outside every matched board row (E72's README).
- **F4 (minor): the 800 MHz side is twelve days older.** The 0.70 ratio sets today's 600 MHz price against E60's
  800 MHz price of 20 Oct. Today's control could not confirm that price (C1 FAIL, R2). "What it changes" now says so.
- **F5 (minor): the change record's missing fields.** The template asks for several fields the record left out:
  - the GO's exact time;
  - the handoff's signoff, in UTC and local time;
  - the card's asset, serial and board revision, now marked UNKNOWN;
  - the other lab user's idle login;
  - who read the maintainer's posts in full.

  They are added as a dated addendum in [`CHANGE-RECORD.md`](CHANGE-RECORD.md), in both copies.

## Files

[`verdicts.json`](verdicts.json) (every registered rule, scored by `score_e118.py`; after verification its two ring
blocks were re-read by `posthoc_g3_ring.py --apply`, with the scorer's reading kept under `as_scored`, F1),
[`posthoc_g3_ring.py`](posthoc_g3_ring.py) / `posthoc_g3_ring.json` / [`posthoc_g3_ring.txt`](posthoc_g3_ring.txt)
(F1's re-read), `results600.json` /
`runs600.csv` (the 600 MHz passes through `reduce_e118.py --pinned`, registered leak auto), `resultsC.json` /
`runsC.csv` (the control, `--free`), `m600-k*.json`, `matched600-k*.json` and their CSVs (V1m's matched reductions),
[`posthoc_exponents.py`](posthoc_exponents.py) / `posthoc_exponents.json`, [`CHANGE-RECORD.md`](CHANGE-RECORD.md),
`aifoundry1-c0/e118/p1`–`p5` (the passes: 10 Hz telemetry, runs, marks, the operand tiles as dumped, the operand
hashes, the host manifest), `e118c/p1`–`p3` (the control), `e118-smoke/p900` (the pinned smoke), `e118probe/p1007`
and `p1005` (the launch-reading probe), `e118back-smoke/p901` (the return burst), and `session/` (`gov.jsonl`,
`steps.jsonl`, `session.log`, `guard.jsonl`, the three ring dumps, the watchdog's script and log, `code.sha256`, the
gate and final reads, and the verifier's read after the release, `verify-read-154823.out`). Reproduce: `python3 tools/claims-v3/e118/score_e118.py --data
docs/reports/data/2026-11-01-e118-two-clock-card0 --gen <a dir holding E60's manifest.json> --e60pred
docs/reports/data/2026-10-20-bitflip-ladder/predictions.json --pred tools/claims-v3/e118/predictions.json --out
<verdicts.json>`, then `python3 docs/reports/data/2026-11-01-e118-two-clock-card0/posthoc_g3_ring.py --apply` (F1). The vmin-LUT binary is not committed (per-card calibration); its digest is in `gov.jsonl`.
