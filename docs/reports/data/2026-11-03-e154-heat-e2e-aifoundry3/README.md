# E154: heat over minutes predicted from the bits on aifoundry3 card 0 - four 10-minute holds of new kinds, every plateau rise inside its registered band, 0.37 °C rms from the bits against 0.34 °C given the measured watts

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 9** (heat over minutes: a steady state for heat), **item 8** (the heat path between sessions) and **item 6** (the power model). It
answers **rank 4 of Q138's final critic**, "Heat over minutes predicted end to end from the computation's description ... The
bits-to-M7-power-to-chain path for a new kind has never been scored", its aifoundry3 half (E161 is aifoundry2's). Tue 3 Nov 2026 (week 45),
Q139. The owner's mandate: his words of 2 November 2026 ("settle any unanswered questions regarding horace's power model"), with his goal "to be
able to predict the power requirement and heat generation of various kinds of numeric computations as accurately as possible".*

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 19:50-20:30 PST; desk only: no card, no device command, nothing re-run).
An independent verifier re-derived every registered number and verdict of E154 from the committed data, with the registered code and with
its own. It re-ran the check of C and the device-command audit, and re-hashed the box's data read-only. All of it stands: **no registered
verdict and no measured, frozen or registered number changes.** It found two major faults and ten minor ones in what this README and the
lane's result say about the numbers; the fix pass found two more (C13, C14).*
- ***C1 (major): the critic's per-hold test is met by 1 of 4 holds, not 2.*** *Its rule is the plateau and the checkpoints' rms within the
  hold's scale. Only K_L meets both. Rank 4's aifoundry3 half has its first blind score, not its answer.*
- ***C2 (major): the heat path's miss is not an fp32 term.*** *Given the watts, the chain reads all three large rises 3.1-4.6% low, H_M's
  int8 included, and the two small int8 rises within 0.07 °C. The early deficit on K_S is mostly the power path's; the heat path's part is
  the late growth. The ±0.4 °C quote is one session's.*
- *C3-C14: "rise" where a rise is meant, with the absolute die beside it (0.39 °C rms, post hoc, on which footing M8 ranks last); all four
  tails; the S at work kept off the tiles; the cancellation; the no-reset code path; the firmware caveat for all ten commands; K_O's tile
  named; the registration's times; the (c) readings listed; launches and dispatches counted apart; E97's 0.3-0.8 °C as a move within one
  session (E144's C3); and the box's draft copy of the registration README.*

*Each passage is marked "corrected after verification, C<n>" where it stands. The old wording is in
[§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026). Every new number is printed by
[`corrections_e154.py`](corrections_e154.py) → [`corrections.txt`](corrections.txt) ([`corrections.json`](corrections.json)), post hoc.*

- **Frozen first:** Q139(e)'s predictions, `predictions-q139e.json` (`455c46c1`, 06:00:48 PST) and amendment A1 (`e224a3f8`, 06:51:54 PST),
  [`../2026-11-03-q139e-heat-end-to-end/`](../2026-11-03-q139e-heat-end-to-end/README.md): M8's watts from the bits for pool 6's four hold
  candidates through Q138(t)'s frozen chain, with the bands and rules. Nothing was fitted here.
- **Pre-registered** in `8c23853c` (written about 17:30-17:51 PST, committed 17:51:30, pushed 17:51:32; corrected after verification, C10),
  before the claim (17:52:43) and before any device access (17:52:59):
  [`tools/claims-v3/e154/README.md`](../../../../tools/claims-v3/e154/README.md). The post hoc script `posthoc_e154.py` was committed in
  `64aa95ee` (17:56) during R0, before any hold's data. The box ran from a copy of `tools/claims-v3/e154/` made before the commit (added
  after verification, C14). Its 12 code files, as the pass recorded them (`aifoundry3/e154/p15420/code.sha256`), match `8c23853c` byte for
  byte. Its copy of the registration README (written 17:49:03, sha256 `7aec97fb…`) is a draft. It differs from the committed one (`bf2c9fc9…`)
  only in three time stamps and the closing section on the session script's dry run
  ([`logs/registration-readme-box-copy.diff`](logs/registration-readme-box-copy.diff)): no rule, prediction, stop or design line.
- **Card:** aifoundry3 card 0, 600 MHz in all 44,259 samples. `ettelem config` read at the session's start (17:52:59), at both ends of both
  blocks and at the session's end (19:06:50): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV every time. Nothing was set.
- **Card session** 17:52:59-19:06:50 PST, **73.9 card-minutes**, inside the 76: the smoke with its five stop tests (block 15401), then **the
  full design** in one measured pass, 15420 (17:54:12-19:06:50).
- **Every device-management command sent was a read** (ten kinds, two of them PMIC voltage-register reads, which the owner's rule of 2 November
  2026 allows). Each is classified from et-platform `836a4ab`'s public handlers, under aifoundry3's non-public-build caveat (corrected after
  verification, C8; [§ Device commands sent](#device-commands-sent)).
- **No statistics reset was sent.** The evidence is the code path (corrected after verification, C7):
  - no file the session runs sends `DM_CMD_SET_STATS_RUN_CONTROL`;
  - `start_sampler`, the one path that forwards `--reset-ms` (lib.sh:154), is never called;
  - E128's guard refuses `--reset-ms`;
  - lib.sh's drain is replaced by a refusal.

  The samples' `since_reset_ms` is no evidence either way, because `pvt_sample.py` writes −1 on every tick (line 208).
- **Every dispatch's C is bit-exact:** 6,346 of 6,346 dispatches read PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`), so every hold
  ran the computation it was meant to. They came in 481 process launches: the smoke's 58 dispatches in 7 and the pass's 6,288 in 474
  (corrected after verification, C12).

**In plain words.** Before today, every check of this chip's heat over minutes was given measured watts: the board's, or E78's for the same
kinds (corrected after verification, C13). Here the watts came from the numbers alone. A model (M8) read each tile's bits and said how many
watts it would draw, and a frozen heat model (Q138(t)'s chain) turned those watts into a die temperature over ten minutes. Four kinds the
models had never seen ran for ten minutes each:
- a real attention block in fp32 (a causal softmax times V);
- a real int8 W8A8 projection;
- an int8 kind whose B lines flip between all-zero and all-one bytes;
- an fp32 kind in which one A bit (bit 5) toggles between rows on a 1/3 base word, with B all ones (corrected after verification, C9).

**Each plateau's rise over the die just before its hold landed within 0.02-0.49 °C of the rise predicted from the bits, 0.37 °C rms, all four
inside their registered 95% bands.** These are rises (corrected after verification, C3). The die's own level over the last 300 s, predicted
from the room at the session's start, reads 0.39 °C rms (post hoc).

Given the measured watts instead, the same heat model reads the same holds to 0.34 °C rms. The two totals are close because two errors of about
the same size partly cancel (corrected after verification, C6 and C2):
- **the power path:** on its own it moves the plateaus by 0.37 °C rms (E − A). On the two fp32 holds its error is opposite to the heat
  model's.
- **the heat path:** given the watts, the heat model reads the three large rises 0.35-0.54 °C low. They are 11-12 °C each: both fp32 holds,
  and H_M, an int8 hold from a rested die. It reads the two small int8 rises (4-6 °C) within 0.07 °C, so on those two the error is the power
  model's (about 0.4-0.5 W).

## Results

**The registered verdicts** (`scored.json` › `verdicts`, the registered scorer `score_e154.py` on pass 15420):

| hold | kind | arm E, end to end from the bits (the primary) | arm A, given the measured watts (the comparison arm) |
|---|---|---|---|
| **K_S** | `fp32.real_smol_softmax_v_causal`, 3.20 s every 4.37 s | **PASS** | **PASS** |
| **K_Q** | `int8.real_qwen_w8a8_v`, back to back | **PASS** | **PASS** |
| **K_L** | `int8.b_line_zero_ff`, back to back | **PASS** | **PASS** |
| **K_O** | `fp32.a_onebit_b5_third`, back to back | **PASS** | **PASS** |
| **H_M** | `int8.full` (E97's H1 again; not end to end) | (b) from E78's watts **PASS**; (c) the replicate **PASS** | **PASS** |

**The numbers** (`scored.json` › `holds`; rises are over each hold's anchor, the last 120 s of the rest before it, read the same way in the
measurement and the prediction; the plateau is the last 300 s):

| hold | rest die before (34-sensor mean, last 120 s) | share / period | measured plateau rise | arm E predicted (M8), over the carried-in tail | **arm E error** | checkpoints' rms (60 s to the end) | band / FAIL beyond | arm A rms / plateau error | **E − A** |
|---|---|---|---|---|---|---|---|---|---|
| **K_S** | 54.653 °C | 0.7891 / 4.37 s | 11.792 °C | 11.768 (tail 3.21) | **+0.024** | 0.372 | 0.599 / 1.30 | 0.330 / +0.418 | −0.394 |
| **K_Q** | 56.066 | 0.9615 | 5.673 | 6.091 (tail 4.43) | **−0.418** | 0.401 | 0.941 / 1.882 | 0.058 / +0.005 | −0.423 |
| **K_L** | 54.583 | 0.9616 | 4.024 | 3.532 (tail 3.07) | **+0.492** | 0.450 | 1.446 / 2.892 | 0.107 / +0.073 | +0.419 |
| **K_O** | 53.383 | 0.9610 | 11.546 | 11.186 (tail 1.89) | **+0.360** | 0.344 | 0.688 / 1.376 | 0.406 / +0.536 | −0.176 |
| **session** (4 holds) | R0: 51.410 °C (the room; K_S at the plan period) | | | | **0.370 rms**, mean +0.115 | | | **0.342 rms**, mean +0.258 | 0.37 rms |

**H_M, E97's H1 again (item 8, a third session):** from a rested die (51.410 °C), its rise per board W at 570-630 s is **0.884 °C/W, 0.984 of
E97's H1** (PASS inside [0.94, 1.06]); from E78's measured watts the plateau error is **+0.194 °C** with the checkpoints at 0.180 rms (PASS
±1.30, and inside the tight 0.361 °C); arm A rms 0.345, plateau +0.352 (PASS).

**The arms beside** (registered as reported; `scored.json` › `holds` › `M7_through_the_chain`, `M6_through_the_chain`,
`E153_through_the_chain`; the plateau errors in °C):

| hold | M8 S (W) → error | M7 S → error | M6 S → error | **E153's measured S** (4.5 s runs this afternoon) → error | E − E153 |
|---|---|---|---|---|---|
| K_S | 15.674 → +0.024 | 15.605 → +0.095 | 15.528 → +0.177 | 15.298 → +0.417 | −0.393 |
| K_Q | 9.241 → −0.418 | 9.239 → −0.437 | 9.250 → −0.475 | 9.043 → −0.299 | −0.119 |
| K_L | 5.935 → +0.492 | 6.250 → +0.130 | 6.649 → −0.324 | 6.378 → −0.087 | +0.579 |
| K_O | 11.427 → +0.360 | 11.373 → +0.529 | 11.317 → +0.730 | 11.463 → +0.459 | −0.099 |
| **rms** | **0.370** | **0.352** | **0.473** | **0.347** | |

- **Against the critic's decisive scale** (Q139(e)'s `critic_scale_C`, reported by the rule: √(0.18² + (0.87 σ_S)²) per hold; corrected
  after verification, C1; `corrections.txt` C1). The critic's rule for rank 4 is the checkpoints' rms **and** the plateau within that scale.
  - **With both conditions, 1 of 4 holds passes: K_L** (plateau 0.492 and checkpoints 0.450, within 0.574 °C).
  - K_S's plateau (0.024) is within its 0.278 °C, but its checkpoints (0.372) are not.
  - K_Q (0.418 / 0.401 over 0.369) and K_O (0.360 / 0.344 over 0.277) are outside on both.
  - On the plateau alone 2 of 4 pass (K_S, K_L). At the critic's flat "about 0.35 °C" none passes both, and only K_S passes on the plateau.

  The session's 0.370 °C rms sits at the critic's "about 0.35 °C", and every registered band passes. **But the critic's per-hold test is not
  met, so rank 4's aifoundry3 half has its first blind score, not its answer.** The registered bands (D4 of Q139(e)) are 1.7-4.1 times wider.
- **M6's frozen step response on the measured trace** (`a_M6`, no leakage loop) reads the four plateaus 0.95-1.39 °C low and H_M 0.28 °C low,
  rms 0.70-1.42 °C: as in E144, the leakage loop is what makes the chain right.
- **The plan readings:** the measured rises against amendment A1's table (the registered machinery on the plan's records at a 51.2 °C room) are
  +0.07 (K_S), −0.42 (K_Q), +0.48 (K_L) and +0.34 °C (K_O); against the frozen session table +0.43, −0.53, +0.48, +0.34 (A1's C1: the table ran
  K_S at a rounded duty).
- **(c) for every hold and H_M's t63** (registered as "reported beside, never a verdict"; added after verification, C11; `scored.json` ›
  `holds` › `c_per_board_W_last300s` and `H_M_c_t63`). The rise per board W over the last 300 s, in °C/W:

  | H_M | K_S | K_Q | K_L | K_O |
  |---|---|---|---|---|
  | 0.873 [0.742, 1.004] | 0.719 [0.673, 0.764] | 0.540 [0.468, 0.611] | 0.558 [0.473, 0.642] | 0.769 [0.617, 0.920] |

  H_M's t63 is 111.0 s, against the closed loop's 119.2 s (0.931). `scored.json` also carries `score_e144`'s verdicts on these readings, by
  E144's rule: H_M PASS, K_S and K_O INCONCLUSIVE, K_Q and K_L FAIL, and the t63 PASS. Those verdicts are not E154's rules and not results.
  E144's band was set for holds anchored on a rested die, and the four pool-6 holds start on tails, so their readings are not comparable with
  E97's or E144's.

**Post hoc** ([`posthoc.json`](posthoc.json), [`tools/claims-v3/e154/posthoc_e154.py`](../../../../tools/claims-v3/e154/posthoc_e154.py),
committed before any hold's data; never a verdict):

| hold | board over R0's P_ref, last 300 s: measured / M8's loop / E153's loop (W) | S at work over the last 300 s, after the leakage law (W) | M8's S | E153's S |
|---|---|---|---|---|
| H_M | 12.85 / 12.98 / — | 9.43 | 9.648 (E78's) | — |
| K_S | 17.38 / 17.72 / 17.25 | 15.21 | 15.674 | 15.298 |
| K_Q | 11.90 / 12.39 / 12.11 | 8.81 | 9.241 | 9.043 |
| K_L | 8.15 / 7.74 / 8.35 | 6.14 | 5.935 | 6.378 |
| K_O | 15.60 / 15.54 / 15.59 | 11.29 | 11.427 | 11.463 |

- **The power path over minutes:** M8's loop reads the board 0.34 W high on K_S, 0.49 W high on K_Q, 0.41 W low on K_L and 0.06 W low on K_O.
  On the first three that is the E − A column (−0.39, −0.42, +0.42 °C at the chain's ~1 °C per W). K_O's −0.18 °C comes with a +0.06 W board
  error in the hold, so most of it is carried in, consistent with K_L's under-read board leaving arm E a smaller tail at K_O's start (E − A
  counts the power errors of the holds before, through the tail, as well as the hold's own).
- **The S at work after ten minutes** is 0.09-0.24 W below E153's 4.5 s measurement on all four tiles (mean −0.18 W). This reading divides by the
  leakage law, E97's pooled quadratic, which is not E153's footing, so the offset is as much the two leakage corrections as the tiles. It is
  not a tile effect until it is redone on one footing (corrected after verification, C5).
- **The carried tail is not optional:** restarting the loop at each hold's own rest die, as if that warm die were the room, reads K_S, K_Q, K_L and
  K_O 3.8, 5.4, 2.8 and 1.8 °C too high (errors −3.79, −5.39, −2.75, −1.83 °C; H_M, from rest, unchanged at +0.19).
- **The room:** R0's rest die moved ±0.25 °C moves every arm E plateau error by at most 0.04 °C.
- **The absolute die** (added after verification, C3; `corrections.txt` C3). The rises above are read over each hold's own anchor, the last
  120 s of the rest before it. That also takes out the chain's error at the anchor: there the carried tail reads 0.03-0.22 °C low.
  - The die's own level over each hold's last 300 s, predicted from R0's room on the realized records, against the measured one: K_S +0.05,
    K_Q −0.19, K_L +0.60 and K_O +0.45 °C, **0.39 °C rms** (mean +0.23). H_M, from rest, reads +0.19.
  - On that footing M7 reads 0.30, M6 0.34 and E153's measured S 0.30 °C rms. So M8 is the worst of the four there. On the rises it is third
    of four (E153 0.347, M7 0.352, M8 0.370, M6 0.473).
  - The ranking depends on the footing and stays unresolved.

**Trajectories** (corrected after verification, C2). On the two fp32 holds arm E's die rose slower than predicted in the first three minutes
(K_S −0.40 to −0.51 °C at 60-180 s, K_O −0.20 to −0.28) and was still rising at the end (+0.24 and +0.49 °C at the hold's end). Arm A, read at
arm E's own checkpoints and windows, splits that shape (`corrections.txt` C2; `scored.json` keeps no arm A checkpoints). Each cell is the
measured minus the predicted rise, in °C:

| hold (measured rise) | arm | 60 s | 120 s | 180 s | 300 s | 450 s | 600 s | end | plateau | plateau / rise |
|---|---|---|---|---|---|---|---|---|---|---|
| **H_M**, int8.full from a rested die (11.21) | A | +0.23 | +0.31 | +0.30 | +0.39 | +0.31 | +0.40 | +0.31 | **+0.352** | 3.1% |
| **K_S**, fp32 (11.79) | A | −0.14 | −0.05 | +0.05 | +0.23 | +0.47 | | +0.38 | **+0.418** | 3.5% |
| | E − A | −0.26 | −0.45 | −0.57 | −0.54 | −0.39 | | −0.14 | −0.394 | |
| **K_O**, fp32 (11.55) | A | +0.03 | +0.06 | +0.14 | +0.32 | +0.61 | +0.43 | +0.49 | **+0.536** | 4.6% |
| | E − A | −0.23 | −0.34 | −0.34 | −0.36 | −0.17 | +0.05 | +0.00 | −0.176 | |
| **K_Q**, int8 (5.67) | A | −0.09 | −0.06 | −0.05 | +0.03 | +0.01 | | −0.02 | **+0.005** | 0.1% |
| **K_L**, int8 (4.02) | A | +0.09 | +0.12 | +0.15 | +0.07 | +0.07 | | +0.05 | **+0.073** | 1.8% |

- **The early deficit on the fp32 holds is mostly the power path's.** At 60-180 s arm A reads K_S −0.14 to +0.05 °C and K_O +0.03 to +0.14 °C,
  while E − A reads −0.26 to −0.57 and −0.23 to −0.34.
- **The late growth is the heat path's.** Arm A reads K_S +0.23 to +0.47 °C and K_O +0.32 to +0.61 °C at 300-450 s.
- **H_M misses the same way.** It is int8, from a rested die, and given the watts it reads +0.23 °C at 60 s and a flat +0.30 to +0.40 °C from
  two minutes on.
- **On the two small int8 rises arm E's error is a level** from two minutes on (K_Q −0.37 to −0.48, K_L +0.41 to +0.51). Arm A is within
  0.16 °C at every checkpoint there (0.05-0.10 °C rms), so that level is the power model's.

**So, given the watts, the chain reads the three large rises 0.35-0.54 °C low, 3.1-4.6% of each rise, H_M's int8 included. It reads the two
small int8 rises within 0.07 °C (0.1-1.8%).** The heat path's miss tracks the size of the rise at least as well as the format. These cannot be
told apart here:
- the size of the rise;
- a gain that moved since 2 Nov;
- a slow stage the chain lacks;
- a room that drifted during the holds (there is no inlet thermometer);
- the format.

On 2 Nov (E144) the same chain, given the watts, read a 15.0 °C rise on this card (fp32 random, duty-cycled, from a rested die) to +0.015 °C,
and a 4.25 °C int8 rise to −0.032 °C. So the 3-5% belongs to this session; it is not a fixed function of the rise.

## What this does to predicting power and heat

**The term tested** is the whole path from a computation's description to its die over minutes on a pinned card: the tile's bits, then M8's
switching watts, then Q138(t)'s closed chain from watts to the die, carried through the tails of the holds before.

**Out-of-sample error of heat over 10 minutes for a new kind on aifoundry3, before:**
- from the bits: **never scored**. Q139(e)'s expected 95% sizes were 0.60-0.69 °C (floats) and 0.94-1.45 °C (int8); the critic's scale about
  0.35 °C;
- given the measured board watts: 0.04-0.18 °C rms on E144's two holds (2 Nov), plateaus +0.015 / −0.032 °C;
- from the bits over a 4.5 s run: 0.10-0.13 °C (E153, M8, today).

**After (this session, four new kinds, registered unless marked post hoc):**
- **from the bits: 0.370 °C rms on the plateau rises** (largest 0.49 °C, K_L), **trajectories 0.34-0.45 °C rms**, every hold inside its
  registered band. **1 of 4 holds is inside the critic's per-hold rule** (corrected after verification, C1). The absolute die, from the room,
  reads 0.39 °C rms (post hoc, C3).
- given the measured watts (arm A), the same holds read 0.342 °C rms, mean +0.258 °C (corrected after verification, C2). **The heat path alone
  reads the three large rises 0.35-0.54 °C low, 3-5% of each rise, H_M's int8 included, and the two small int8 rises within 0.07 °C.** This is
  the second session of this card; on the first (E144, 2 Nov) the chain read its two holds to +0.015 and −0.032 °C.
- the power path's share (E − A): 0.37 °C rms, with M8's in-hold board errors −0.49 to +0.41 W (post hoc);
- from E153's measured watts for the same tiles: 0.347 °C rms on the rises and 0.30 °C on the absolute die, where M8 reads 0.39 (post hoc,
  C3). On the rises the bits are within 0.02 °C rms of having measured the tiles first, at n = 4. On the absolute die they are 0.08 °C worse.

**What it changes:** heat over minutes from a computation's description can now be quoted on aifoundry3 at about **±0.4 °C on a 10-minute
plateau rise, from one session (rms 0.37 °C over n = 4 new kinds; 95% interval for the 1σ 0.22-1.06 °C, χ² with 4 degrees of freedom)**, with
the power model and the heat model contributing about equally.
- **One session's figure** (corrected after verification, C2 and C13). Another session can add a move that is not yet measured below the
  0.3-0.8 °C by which E97's plateau moved within its one session (E144's C3).
- **Not the critic's test passed** (1 of 4 holds, C1).
- **The model ranking is not resolved at n = 4, and it depends on the footing** (C3). On the rises M8 reads 0.370, M7 0.352 and M6 0.473 °C
  rms; on the absolute die M8 0.39, M7 0.30 and M6 0.34.
- **K_L again shows M8's int8 near-whole-byte discount over-correcting** (M8 +0.49 °C, M7 +0.13, M6 −0.32), as E153 found over 4.5 s. The S
  at work, 6.14 W, lies between M8's 5.94 and M7's 6.25.
- **The next heat term (item 9) is the chain's gain or a slow stage on large rises** (corrected after verification, C2), not an fp32 term:
  the three 11-12 °C rises read 3-5% low given the watts, H_M's int8 included. This session cannot tell it from a room that drifted during the
  holds, because there is no inlet thermometer.

## Registered against what happened

| registered | what happened |
|---|---|
| the full design if the session's anchor is at or before 20:40 PST, budget 76 card-minutes | T0 17:52:59 PST: the full design; 73.9 card-minutes |
| the room rule (R0's rest die) sets K_S's period | 51.410 °C ≤ 51.5 °C: the plan period, 4.37 s; K_S ran 137 cycles, the median period 4.37 s, share 0.7891 (plan 0.7908) |
| natural chain holds | 90 (H_M) and 81-84 launches (the pool-6 holds), share 0.9610-0.9616 (plan 0.9655; the C log and the wrapper's hash sums take about 0.4%) |
| stops: gate 70 °C, hold 72 °C / 65 W, session 74 °C, on live samples | none fired in the pass: highest board 45.34 W (K_S), highest `minshire[0]` 66 °C, highest 34-sensor mean 67.54 °C (K_S) |
| every planned in-launch peak at or under 67.5 °C | K_S's peaked at 67.54 °C, 0.04 °C over the design line (A1 put it at 67.40 °C at a 51.5 °C room), 4.5 °C under the hold stop |
| the five stop tests in the smoke | all passed (`logs/smoke-gate.json`): no launch at a 1 °C gate; the hold's die and board lines ended a hold with no launch; a board line 4 W over the idle (27.57 W) ended the launch in flight 1 s in, at a live sample of 38.90 W; the session line ended the block with exit 6 |
| the smoke gate | GO (block ok, every stop test, each tile launched, a sound C log, the 34 raw codes in every line, 600 MHz, both config reads) |
| the C check, a validity label | 6,346 of 6,346 dispatches PASS, in 481 process launches (corrected after verification, C12): every hold "C verified" |
| no hold dropped, no departure after the data | none |

## Device commands sent

As registered ([`tools/claims-v3/e154/README.md`](../../../../tools/claims-v3/e154/README.md#device-commands-sent)); the preflight read GO on the
box at the session's start (`logs/dmcmd-preflight.txt`: 38 send sites, 0 disallowed, the one reviewed exception lib.sh:154):

| command | sent by | class |
|---|---|---|
| `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25), `…_TEMPERATURE_THRESHOLDS` (21), `…_POWER_STATE` (23) | `ettelem config` through E128's guard: the session's start and end, each block's start and end | READ (RAM copies; et-platform `836a4ab` thermal_pwr_mgmt.c:613-617, 665-669, 551-555) |
| `DM_CMD_GET_ASIC_FREQUENCIES` (53) | `ettelem config`, `pvt_sample.py` (10 Hz), lib.sh's `die_c` | READ (PLL register reads) |
| `DM_CMD_GET_ASIC_VOLTAGE` (32) | `ettelem config`, `pvt_sample.py`, `die_c` | READ (two PMIC voltage-register reads; allowed by the owner's rule of 2 November 2026) |
| `DM_CMD_GET_MODULE_POWER` (33), `DM_CMD_GET_SP_STATS` (60), `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | `pvt_sample.py`, `die_c` | READ (RAM copies; PVT register reads) |
| `DM_CMD_GET_MODULE_VOLTAGE` (31) | lib.sh's `die_c` at each block's start and end | READ (nine PMIC voltage-register reads; allowed) |
| `DM_CMD_GET_ASIC_PVT_SAMPLES` (74), group 0 only | `pvt_sample.py` at 10 Hz | READ, from the held patch source (E144's classification and residual) |
| the C-logging host (`sparsity_ccheck.sh` → `build/ccheck/b/host/sparsity_host`, E78's kernel) | every launch | no device-management command (ops node: code load, DMA, launches) |
| **not sent** | — | the statistics reset (`--reset-ms`), command 74's group 6, the firmware-revisions query, any residency read, any set, any reset, `dev_mngt_service` |

*Added after verification, C8.* The registration says these were classified "from the firmware source of the running build". For aifoundry3
that is not quite so:
- aifoundry3 runs a non-public BL2 0.22.0 build, the thermal firmware build flashed there on 7 Oct 2026.
- So every class above is read from et-platform `836a4ab`'s public handlers, plus the lab's held command-74 patch for command 74.
- A command present in both is classified from `836a4ab`'s handler, which that build may not share.

The table's caveat (`tools/claims-v3/e144/dmcmd_table_e144.json` › `source.caveat`) therefore binds all ten commands here, not command 74
only. The classes themselves check out at `836a4ab`: the verifier read every handler.

## The day's post

Tue 3 Nov's one `#community-lab` post, message `1567332504330051616`, under the discord lock with `EXPECT_TEXT`, dry run, save and read back:
- **claim, 17:52:43 PST:** from `<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~17:54 PST [doc](<…/horace-kinds-of-numbers>) — released`
  to `<ai> **Claude says:** using aifoundry3 for 1.5 h, until ~19:22 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`;
- **release, 19:07:58 PST:** the same text with ` — released` appended (the only card held), every word kept.

Mon 2 Nov's post was not touched, and no other post was made.

## What this cannot say

- **One session, one card, four kinds.** A 1σ from n = 4 has a wide interval: 0.37 °C rms gives 0.22-1.06 °C at 95% (χ², 4 degrees of
  freedom). The plateau moved 0.3-0.8 °C within E97's one session on this card with nothing changed, cause not established. The move between
  sessions is not yet measured below that scale (E144's C3; corrected after verification, C13). The room's only proxy is the rest die; there
  is no inlet thermometer.
- **The 10-minute holds read 92-95% of their fixed points**, like for like in prediction and score, not a steady state. All four pool-6 holds
  started on tails of 1.9-4.4 °C (corrected after verification, C4). The chain carries them; restarting it at the rest die instead would have
  been 1.8-5.4 °C wrong.
- **The bands do not separate the models** (Q139(e)'s D4): M8, M7 and M6 all PASS by the same rule on three or four holds.
- **The critic's per-hold rule is met by 1 of 4 holds** (added after verification, C1), so this does not close rank 4's aifoundry3 half on
  the critic's own test.
- **The S-at-work reading is post hoc** and rests on E97's pooled leakage law at 53-67 °C.

## How to reproduce

```bash
# the C check (Q139(k)), on the two C logs, then the registered scorer and the post hoc readings (numpy 1.26.4, Python 3.9)
gunzip -k docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/ccheck/c-log-p154*.jsonl.gz
python3 tools/claims-v3/ccheck/ccheck.py check docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/ccheck/c-log-p15401.jsonl \
  docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/ccheck/c-log-p15420.jsonl --out /tmp/ccheck-all.json --jobs 6
python3 tools/claims-v3/e154/score_e154.py docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420 --json scored.json
python3 tools/claims-v3/e154/posthoc_e154.py docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420 --json posthoc.json
python3 tools/claims-v3/e154/score_e154.py --self-test
# the corrections after verification (post hoc; writes corrections.txt and corrections.json beside it)
python3 docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/corrections_e154.py
```

## Files

| file | what |
|---|---|
| `scored.json` | the registered scorer's output: every arm per hold, the verdicts, the session figure |
| `posthoc.json` | the post hoc readings (power over minutes, S at work, the tail, the room) |
| `aifoundry3/e154/p15420/` | the measured pass: `telemetry.jsonl.gz` (the 10 Hz sampler with the 34 raw codes), `marks.jsonl` (rests, holds, launches, `rest_die`, `room`), `runs.jsonl` (one record per dispatch), `run.log`, `configs.json`, the config reads, `block.json`, `gen.sha256`, `binaries.sha256`, `manifest.txt` |
| `aifoundry3/e154-smoke/p15401/` | the smoke and the five stop tests, in the same layout |
| `ccheck/` | the two C logs (`c-log-p15401.jsonl.gz`, `c-log-p15420.jsonl.gz`; moved here from the pass directories, byte-identical) and `ccheck.py`'s output (`ccheck-all.json`, `ccheck.txt`) |
| `logs/` | the session log, the session's config reads with their times, the device-command preflight, the smoke gate; `registration-readme-box-copy.diff`, the committed registration README against the box's draft copy (C14) |
| `corrections_e154.py`, `corrections.txt`, `corrections.json` | the corrections after verification, C0-C14 (post hoc; no verdict uses them): the script imports the registered scorer, which checks its 13 frozen inputs, and first reproduces `scored.json`'s plateau errors and session figure (C0) |

## Corrections after verification (Tue 3 Nov 2026)

*Written Tue 3 Nov 2026, about 19:50-20:30 PST, by the fix pass, after the data, the post hoc readings and the verifier's report. Desk
only: no card, no device command, nothing re-run. It took two read-only looks: at aifoundry3 (`et-who` at 19:57:58 PST: the card free, no
process of ours) and at the day's post (19:57: it ends "— released"). No measured, frozen or registered number, rule, prediction or verdict
changed. The registration (`tools/claims-v3/e154/`, `8c23853c`) keeps its text, with a dated note under its header.*

*Every number here is printed by [`corrections_e154.py`](corrections_e154.py) → [`corrections.txt`](corrections.txt)
([`corrections.json`](corrections.json)). The script imports the registered scorer, which checks the sha256 of its 13 frozen inputs. It first
re-runs that scorer in memory, and it gives `scored.json`'s plateau errors and session figure exactly (C0). So every reading below stands on
the registered footing.*

### C1 (major): the critic's per-hold test is met by 1 of 4 holds

**What the text said.** "Against the critic's decisive scale (Q139(e)'s `critic_scale_C`, reported by the rule: √(0.18² + (0.87 σ_S)²) per
hold): K_S 0.024 within 0.278 °C, K_L 0.492 within 0.574, K_Q 0.418 over 0.369 and K_O 0.360 over 0.277. The session's 0.370 °C rms sits at
the critic's "about 0.35 °C". Two of four holds pass that tighter test; the registered bands (D4 of Q139(e)) are 1.7-4.1 times wider."

**The rule.** Q138's final critic, rank 4: "rms and plateau within √(chain² + (R × power rms)²), about 0.35 °C on aifoundry3". The text
compared the plateau only.

| hold | plateau error (°C) | checkpoints' rms (°C) | the hold's scale (°C) | both within |
|---|---|---|---|---|
| K_S | +0.024 | 0.372 | 0.278 | no: the rms is outside |
| K_Q | −0.418 | 0.401 | 0.369 | no |
| K_L | +0.492 | 0.450 | 0.574 | **yes** |
| K_O | +0.360 | 0.344 | 0.277 | no |

- With both conditions, 1 of 4 passes.
- On the plateau alone, 2 of 4 pass.
- At the flat 0.35 °C, none passes both.

So rank 4's aifoundry3 half has its first blind score, not its answer. It is not closed on the critic's own test.

### C2 (major): the heat path's miss tracks the size of the rise, H_M included

**What the text said** (each passage's old wording):
- Trajectories: "On the int8 holds the error is flat from two minutes on (K_Q −0.37 to −0.48, K_L +0.41 to +0.51): a level, which is the power
  model's (A is 0.06-0.11 °C rms there). The fp32 holds' shape is the heat path's: given the watts, A's plateau errors are +0.42 and +0.54 °C on
  K_S and K_O, against E144's +0.015 and −0.032 °C on this card on 2 Nov."
- After: "given the measured watts (arm A), the same holds: 0.342 °C rms, mean +0.258 °C, so the heat path alone is now **0.3-0.5 °C on hot fp32
  holds** on a second session of this card, not 0.04-0.18".
- What it changes: "heat over minutes from a computation's description can now be quoted on aifoundry3 at about ±0.4 °C on a 10-minute plateau
  (rms 0.37 °C over n = 4 new kinds; …), with the power model and the heat model contributing about equally. … The heat path's +0.4-0.5 °C on
  the fp32 holds is the next term to correct (item 9: a slow stage or a between-session move; E97's moves were 0.3-0.8 °C)."
- In plain words: "on the two int8 holds the heat model given watts is nearly exact (+0.005 and +0.073 °C), so the error there is the power
  model's (±0.4 W)."

**What it left out.** H_M is int8 (`int8.full`). It started from a rested die in the same session, and arm A reads its plateau +0.352 °C (rms
0.345).
- Arm A at arm E's own checkpoints (the table under Trajectories, `corrections.txt` C2) shows the early deficit on K_S is mostly the power
  path's: arm A reads −0.14 to +0.05 °C at 60-180 s.
- The heat path's part is the late growth (K_S +0.23 to +0.47, K_O +0.32 to +0.61 °C at 300-450 s), plus H_M's flat +0.30 to +0.40.
- Given the watts, the chain reads the three large rises 3.1-4.6% low and the two small ones 0.1-1.8% off.
- On 2 Nov (E144) the same chain read a 15.0 °C rise to +0.015 °C.

So the next heat term is the chain's gain or a slow stage on large rises, or the room's drift, which this session cannot tell apart. It is not
an fp32 term, and the ±0.4 °C quote is one session's.

### C3: the plateaus are rises; the absolute die beside them

**What the text said.** "Each plateau landed within 0.02-0.49 °C of the prediction from the bits, 0.37 °C rms, all four inside their
registered 95% bands" (In plain words). The title read "every plateau inside its registered band".

**What they are.** They are rises over each hold's anchor, read the same way in the measurement and the prediction. That form also cancels the
chain's error at each anchor, where M8's carried tail reads 0.03-0.22 °C low. The absolute die over the last 300 s, predicted from R0's room
on the realized records (post hoc, `corrections.txt` C3), in °C:

| S through the chain | K_S | K_Q | K_L | K_O | rms (mean) |
|---|---|---|---|---|---|
| **M8 (arm E)** | +0.055 | −0.193 | +0.598 | +0.446 | **0.386** (+0.226) |
| M7 | +0.127 | −0.189 | +0.237 | +0.508 | 0.303 (+0.171) |
| M6 | +0.208 | −0.202 | −0.221 | +0.572 | 0.339 (+0.089) |
| E153's measured S | +0.448 | +0.051 | +0.093 | +0.395 | 0.303 (+0.247) |

Best first, the absolute die ranks M7 and E153 (0.303), then M6, then M8. The rises rank E153, M7, M8, M6. So the ranking depends on the
footing.

### C4: all four pool-6 holds started on tails

**What the text said.** "Three holds started on tails of 1.9-4.4 °C" (What this cannot say).

**The count is four.** The chain's tails are K_S 3.21, K_Q 4.43, K_L 3.07 and K_O 1.89 °C. The measured rest die before each sits 3.24, 4.66,
3.17 and 1.97 °C above R0 (`corrections.txt` C4). The registration's "K_S and K_Q start on tails of 3.2 and 4.4 °C" names two, while its own
plan table gives tails for all four (3.21, 4.44, 3.06 and 1.88 °C).

### C5: the S at work after ten minutes is not a tile effect

**What the text said.** "… so the offset is as much the two leakage corrections as the tiles." The sentence now adds that it is not a tile
effect until it is redone on one footing. The lane's result had made the offset a blog point; the corrected result drops it.

### C6: the cancellation

**What the text said.** "So composing the power model in front of the heat model costs almost nothing in the total here: on the two fp32 holds
its errors partly cancel the heat model's, …".

**What it now says.** On its own the power path moves the plateaus by 0.37 °C rms (E − A: −0.394, −0.423, +0.419, −0.176 °C). The two totals
(0.370 and 0.342 °C) are close only because the two errors partly cancel on the fp32 holds.

### C7: the no-reset evidence is the code path

**What the text said.** "no statistics reset (`since_reset_ms` −1 in every sample)". `pvt_sample.py` writes `rec["since_reset_ms"] = -1` on
every tick (line 208), whatever was sent. The evidence is the code path, which the bullet now gives. The conclusion stands.

### C8: the firmware caveat binds all ten commands

This is an addition, under Device commands sent. aifoundry3 runs a non-public 0.22.0 build, so every class is read from `836a4ab`'s public
handlers plus the held command-74 patch, under the table's caveat. The E154 READMEs had carried the residual for command 74 only.

### C9: K_O's tile

**What the text said.** "an fp32 kind with one walking bit".

**What the tile is.** Its rule (`tools/claims-v3/kinds/blind6/blind6.json` › `fp32.a_onebit_b5_third`): "A every word 1/3 (0x3EAAAAAB) with
bit 5 set in the odd rows: each step down an A column flips that one bit (the recoded operand, a new base word); B every element 1.0". One bit
toggles at a fixed position, and nothing walks.

### C10: the registration's times

**What the text said.** "Pre-registered in `8c23853c` (pushed 17:51:30 PST)". 17:51:30 is the commit time; the push was at 17:51:32 (the Intel
clone's reflog of `origin/main`). The registration says it was "written … about 17:30-18:00 PST" and dates its departures "17:30-18:00 PST".
Both run past its own commit: it was written about 17:30-17:51, before the claim (17:52:43).

### C11: the (c) readings

This is an addition, under Results. The registered "reported beside" readings were missing: (c)'s rise per board W for every hold, and H_M's
t63. The lane's result said this README "reports only their numbers"; it reported none. `scored.json`'s verdicts on them are `score_e144`'s, by
E144's rule, and are not E154's.

### C12: launches and dispatches

**What the text said.** "**Every launch's C is bit-exact:** 6,346 of 6,346 dispatches (the smoke's 58 and the pass's 6,288)". The table read
"6,346 of 6,346 PASS".

**The counts.** There were 6,346 dispatches in 481 process launches: 474 launch marks in the pass and 7 in the smoke, against `runs.jsonl`'s
6,288 + 58 (`corrections.txt` C12). `ccheck-all.json`'s `launches` field counts dispatches.

### C13 (found by the fix pass): E97's 0.3-0.8 °C, and the watts earlier checks were given

**What the text said.**
- What this cannot say: "The plateau moves 0.3-0.8 °C between sessions on this card with nothing changed (E97)".
- What it changes: "(item 9: a slow stage or a between-session move; E97's moves were 0.3-0.8 °C)".
- In plain words: "every check of this chip's heat over minutes was given the board's measured watts".

**What is so.**
- E144's verified correction C3 (3 Nov) reads: "The 0.3–0.8 °C is how far the plateau moved within E97's one session, cause not established,
  not a move between sessions."
- E144's (b) was given E78's measured watts for the same kinds, not the board's. The critic's rank 4 says "given the measured board watts, or
  E78's measured watts for the same kinds".
- The verifier's report repeats "E97's between-session moves". Q139(e)'s README also says "between-session plateau moves of 0.3-0.8 °C", which
  is outside this lane's files.

### C14 (found by the fix pass): the box's copy of the registration README

The pass's `code.sha256` records the registration README as `7aec97fb…`; the committed registration is `bf2c9fc9…`. The box's copy, read back
read-only at 19:58 PST (file time 17:49:03), is a draft. It differs only in two things
([`logs/registration-readme-box-copy.diff`](logs/registration-readme-box-copy.diff)):
- three time stamps: the draft has 17:40, 17:45 and 17:45 where the commit has 17:48, 17:50 and 17:50, for the self-test, the dry run and the
  box's audit;
- the closing section, "The session script's dry run".

The other 12 files `code.sha256` records match `8c23853c` byte for byte. The README is documentation, not code the session runs, so the
registration of record is the commit, which preceded the claim.
