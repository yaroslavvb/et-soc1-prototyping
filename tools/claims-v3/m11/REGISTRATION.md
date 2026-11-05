# Q142(h): M11's heat registration - heat over minutes as a session level against a gain (HM-LG, its power stated), the hold design on aifoundry3 and aifoundry2, a heat scale for card 1 alone and a paired-anchor int8 term for card 1, each term's entry and not-wanted rules as numbers, written before any hold and any fit

*Thu 5 Nov 2026 (week 45), on the Intel, desk only: no card, no device command, no lab box, no post in the lab's channel, no Modal,
no archive. Read from about 07:00 PST, written from about 07:30 PST, committed at the time git records. It answers the pool-8
readiness critic's `next` **rank 3** ("M11's heat registration before any hold. It tests a session level against a gain over
minutes, with two or more rise levels per session and one hold like E144's, and states its power the way LG does. A heat scale for
card 1 alone and a paired-anchor int8 term go beside it."), with the Q142 critics' heat findings (§ 0), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **items 9 and 8** (heat over minutes,
the heat path between sessions) and **item 6** (the power model, for term (d)). The owner's goal, in his words of 2 November 2026: to
predict the power requirement and heat generation of numeric computations as accurately as possible.*

**Written and committed before:** any M11 hold (none has run, none has a run number or a claim); any M11 fit (no fit code exists, and
no candidate term below has been computed on any committed row); any data of pool 8's card day, E171-E174 (no E171-E174 data
directory or reduction exists in any ref at this commit: `git log --all`). Everything below is fixed now. A departure is a dated
amendment file beside this one, committed before the output it touches. [`SHA256SUMS`](SHA256SUMS) holds the sha256 of the 58
committed files this registration names, as read at this commit; every later M11 lane checks them before it reads anything.

**Nothing frozen changes.** M10 (`e9367b66`, `6829c9ba`, with `ef74dd0d`, `d1581099`, `c996d135`), M9 (`1f244140`, `8dfafae3`), Q138(t)'s
chain (`f5473428`, `c2f9920d`), pool 8's registration and freeze (`3e97f583`, `4576fb90`, `dfe226f1`) and E171-E174's registrations
(`4441083f`, `c8064454`) stay as committed. M11 is M10 plus whichever of the candidates below enter by their rules; every other part of
M11 is M10's, unchanged.

## 0. What was already seen (post hoc, disclosed)

None of these is a registered result, and none is re-scored as one here. The candidates were named from them.

1. **The chain's misses given the watts.** On the 14 fitted holds of six sessions (`heldout-m10.json` › `heat_d_chain_gain.holds`, the
   frozen chain on each hold's measured board, arm A), the nine large rises (R ≥ 10 °C) read 1.83-5.60% low, except E144's `H_H`
   (fp32 random duty-cycled, R 15.00 °C), read to +0.10% (e +0.015 °C). E144's other hold, `H_L` (int8 −1s, R 4.25 °C), read
   −0.032 °C.
2. **A level in one session, a gain in another** (Q142's round critic, re-derived in E166's dated note 2 by
   [`posthoc_heat_level_gain.py`](../../../docs/reports/data/2026-11-04-e166-heat-replicate-aifoundry3/posthoc_heat_level_gain.py)):
   E154's misses grow with the rise (e = −0.229 °C + 5.72% of R; a gain alone fits better than a level alone, 0.110 against
   0.204 °C), E166's are flat or falling (e = +0.395 °C − 1.43% of R; a level alone fits better, 0.079 against 0.155 °C). Regressed on
   the chain's rise P instead of R (as § 2 registers), the same holds give E154 −0.238 °C + 6.01% and E166 +0.392 °C − 1.44%
   (`design-power-heat.txt` § 1).
3. **M10's term (d).** One γ = 0.03199 (the ×1.032 arm) passed M10's § 6; § 7's second clause was met by E144 (`H_H` 0.015 → 0.547 °C
   with its fold's γ 0.0375), so M10's primary is the chain unscaled and the gain a reported arm (`m10-s7.json`). Per card kind, γ is
   0.02349 (aifoundry3) and 0.04515 (aifoundry2). Over the nine large rises the chain unscaled reads 0.493 °C rms given the watts, the
   arm 0.294 °C (held out).
4. **Card 1's 4.5 s heat scale (M10's c1).** Held out, the session heat scale takes card 1's heat rms from 0.2855 to 0.1731 °C
   (d −0.112 °C, interval −0.137 to −0.085, resolved) and leaves aifoundry3's at 0.1717 → 0.1737 °C (+0.002, not resolved), so c1 failed
   M10's "< 0 on each card" (`heldout-m10.json` › `heat_c1.per_card`). Card 1's 16 session scales run 0.629-1.101 (sd 0.136, 6.2 times
   the 0.022 their own errors give); aifoundry3's 13 run 0.842-1.007 (sd 0.042, 3.0 times). **So term (c)'s pooled held-out entry on
   card 1 is already known to pass**; its new clauses and its blind reading (§ 8) are not.
5. **Card 1's int8.** E164-X2 read the int8 card ratio 0.9418 (interval 0.9367-0.9467) against M10's and M9's 0.9616; RK4 read the
   E163/E164 pair's int8 anchors at 0.9368 against the pool's 0.9418. Scaling M9 by card 1's own int8 anchors (0.9766) over-corrected
   pool 7's int8 on card 1 (bias −0.076 → +0.061 W; the card-half critic). Scaling M10's card-1 int8 by 0.9418 / 0.9616 = 0.9794 takes
   pool 7's priority-1 bias from −0.081 to +0.039 W and every card-1 int8 row from 0.185 to 0.210 W rms (Q142's round critic). M10's int8
   session scales from each session's int8 random anchors (`int8.full`, with the pools' where they ran) read 0.969-0.987 on card 1 and
   0.973-1.000 on aifoundry3: the anchors read about 2% under the model on both cards. **By RK4's numbers, term (d)'s k for the
   E163/E164 pair would be about 0.9368 / 0.9616 = 0.974 at equal rates, a size that over-corrects pool 7's card-1 int8 as the tile
   ratio did.** I expect (d) not to be wanted (§ 9).
6. **Pool 8's day** (E171-E174) is registered and kitted, waiting on his word; nothing of it has run.
7. **What this lane read before writing:** Q138(t)'s README, chain code and frozen files; E144's, E144b's, E154's, E161's, E166's and
   E167's READMEs, dated notes and scored files; Q140(e)'s registration; M10's registration with A2-A4, `heldout-m10.json`'s heat and
   int8 blocks, `section7-m10.json`'s (c1) and (d), `m10-s7.json`; POOL8-REGISTRATION's §§ 1, 3, 7 and 8 and `design_power_groups.py`;
   E171's, E172's, E173's and E174's registrations (their plans, sets and windows); E164's README (X1, X2, RK4) and dated note 2; pool 8's
   `blind8.json` roles and set sizes; the Q142 critics' heat and int8 post hoc readings; run_hpl.py's run options.
8. **What it computed before writing** (design only, committed beside this file): [`design_power_heat.py`](design_power_heat.py) →
   [`design-power-heat.txt`](design-power-heat.txt) and [`.json`](design-power-heat.json): the noise by P8-LG's rule, the planned rises
   by Q138(t)'s frozen chain, and the power of every rule below. Nothing else was computed on any row.

## 1. What is read per hold

- **The chain:** Q138(t)'s frozen chain per card kind (`model-q138t.json`: aifoundry3 R 0.8695 °C per board W, aifoundry2 0.663), open
  loop on the hold session's **measured** board trace (arm A), anchored over the last 120 s of the rest before each hold
  (`heat_q138t.anchor_value`): exactly as `score_e166.read_one` / `arm_a_error` compute it on aifoundry3 and `score_e167.read_hold` on
  aifoundry2, unchanged.
- **The windows** (Q140(e) R3): t0 = the start of the hold's first process, b = the end of its last process; the plateau = the mean over
  [b − 300 s, b). aifoundry3's die is the 34-sensor mean; aifoundry2's is the firmware's whole-degree reading (`minshire[0]`) on the 0.2 s
  grid, as E167 read it.
- **Per hold h:** R = the measured plateau's rise over the anchor; P = the chain's rise read the same way; **e = R − P**. These are the
  quantities M10's (d) rows hold for the committed sessions.
- **A hold is scored** if it is complete by E166's X1 (b − t0 ≥ 570 s; the anchor and plateau windows covered at ≥ 5 samples a second)
  and, on aifoundry2, in the 800 MHz regime (at least 90% of its window's samples at ≥ 790 MHz, E167's carried clock share). A hold
  that is not scored is named, with its reason, and leaves every rule's set.

## 2. (a) Heat over minutes: the two forms, and how each is fitted

For each M11 hold session σ (one card kind, one day):
- **LEVEL**, a session level added to the chain's rise: e = a_σ, so R = P + a_σ.
- **GAIN**, a gain multiplying it: e = g_σ P, so R = (1 + g_σ) P.
- **BOTH**: e = a_σ + g_σ P. **The null:** e = 0.

Each form is fitted to σ's own scored holds by ordinary least squares. **Nothing is shared between sessions**, and the two card kinds
never share a parameter (each has its own chain). P is the regressor, not R, so the regressor carries no measurement error of R.

What each would mean. A gain is the session's heat path (its °C per board W) or its board-W scale off by g, so every hold misses in
proportion to its rise. A level is an excess the same for every hold whatever its rise: a room that drifts by a fixed amount over a
hold's ten minutes, or an anchor read off the chain's state. (A fixed offset of the absolute die cancels in a rise read over the hold's
own anchor, so it is not a level.)

## 3. The statistic that separates them, its threshold, and the readings beside it

**HM-LG, P8-LG's test with holds for tiles.** The groups are a card kind's M11 hold sessions. A session counts if it has **at least 4
scored holds spanning at least 6.0 °C of P**. With k sessions and n holds:
- F_slope = [(RSS_LEVEL − RSS_BOTH) / k] / [RSS_BOTH / (n − 2k)] tests every g_σ = 0;
- F_level = [(RSS_GAIN − RSS_BOTH) / k] / [RSS_BOTH / (n − 2k)] tests every a_σ = 0;
- each against **F(k, n − 2k)'s 95% point** (5%). The null model (e = 0) is tested beside with (2k, n − 2k) degrees of freedom.
- **n − 2k must be at least 3, else NOT SCORED.** (P8-LG asks 4. Three lets one session of five holds be scored, at F(1, 3)'s point
  of 10.13; § 4 states what that costs.)

**Verdicts:** **GAIN** if F_slope rejects and F_level does not; **LEVEL** if F_level rejects and F_slope does not; **BOTH** if both
reject; **NOT SEPARATED** if neither, with the null reading beside: "the chain's misses are zero in these sessions" or "they differ
from zero, the form unresolved". The code is `design_power_groups.lg_test(groups, min_tiles=4, min_span_w=6.0, min_df=3)`,
unchanged: its argument names count tiles and watts, and here they count holds and °C of P.
- **HM-LG-A3**, over aifoundry3's M11 sessions, is the **primary**. **HM-LG-A2**, over aifoundry2's, is registered beside it with its
  own (low) power. A pooled reading over both card kinds, each hold's e and P divided by its card kind's σ of § 4, is reported only.
- **HM-AG, do the sessions share one gain (one level)?** Read when HM-LG gives GAIN, LEVEL or BOTH and k ≥ 2, with
  s² = RSS_BOTH / (n − 2k): for GAIN, F_AG = [(RSS_one gain − RSS_GAIN) / (k − 1)] / s² against F(k − 1, n − 2k)'s 95% point, where
  the one-gain model is e = γ P over all the card kind's holds; for LEVEL, the same with e = ā and RSS_LEVEL; for BOTH, the one
  two-term model e = ā + γ P over all the holds against RSS_BOTH, [(RSS_one − RSS_BOTH) / (2(k − 1))] / s² against
  F(2(k − 1), n − 2k). "They share one" if it does not reject. (The power file computes the first two; the third's power is not
  computed.)
- **HM-E144, does E144's reading repeat?** On each session's E144-like hold H_E (§ 5): |e| / R ≤ 0.015 (RK3-c's line). "REPEATS" if
  inside in every session that ran H_E, else "DOES NOT REPEAT"; each session's reading reported.
- **HM-HE, is the miss specific to H_E?** e(H_E) against the 95% prediction interval of the two-term fit on the session's other scored
  holds (t at n_σ − 3 degrees of freedom): "DEPARTS" if outside. It is reported beside HM-LG and never changes its verdict. A departure
  in every session means the misses depend on the hold (its kind or its duty pattern), not on P alone.
- **Reported per session:** a_σ and g_σ with 95% intervals (t at n_σ − 2); the level-alone and gain-alone residuals; each hold's
  carried-in tail (the chain's) and its place in the order; the room's drift over R0 (the 34-sensor mean's least-squares slope over R0's
  last 240 s).

## 4. The test's power at the planned design (computed by committed code from the committed sessions' noise, as LG's was)

[`design_power_heat.py`](design_power_heat.py) (standard library, plus numpy only through Q138(t)'s frozen chain; it checks its ten
inputs against [`SHA256SUMS`](SHA256SUMS)) → [`design-power-heat.txt`](design-power-heat.txt), [`design-power-heat.json`](design-power-heat.json).
It imports `design_power_groups.lg_test` and `f_ppf` unchanged, and draws 5,000 sessions a cell from seeded strings.

**The noise of one hold's miss within a session, by P8-LG's rule** (`noise_from_reruns`' rule, line for line: a two-term fit where a
session holds at least 4 holds spanning more than 2 °C of P, else the session's mean; residuals scaled to their degrees of freedom):
- **aifoundry3: σ = 0.0884 °C**, over the 11 fitted holds of E144 (mean), E154 and E166 (two-term), M10's own set (E166's `K_OL_long`
  left out as M10 left it).
- **aifoundry2: σ = 0.2296 °C**, from the only committed aifoundry2 sessions with two holds of one kind in the 800 MHz regime: E111's
  and E133's int8 −1s holds, each day read by the chain fitted on the other day (`cv-q138t.json` › `a2`; each session's mean). Their
  holds ran 340-345 s and 1,596-1,597 s, so this estimate carries a length difference and is on the high side. The frozen chain's own
  aifoundry2 sessions (E144b, E161, E167) hold one 800 MHz hold each and add nothing. A readout floor is printed beside: 0.302 °C,
  aifoundry3's σ with a whole-degree anchor's uniform ±0.5 °C added.

**HM-LG's verdict shares at the plan** (§ 5: two aifoundry3 sessions of five holds, P per session 14.21 / 0.73 / 9.67 / 3.46 / 8.36 °C
and 11.86 / 0.97 / 9.78 / 3.47 / 8.44 °C, rooms 51.2 and 52.0 °C; F(2, 6)'s point 5.143), in % (GAIN / LEVEL / BOTH / NOT SEPARATED):

| truth (every session) | at σ = 0.0884 °C | at 1.5 σ |
|---|---|---|
| none | 1.7 / 1.9 / 3.3 / **93.1** | 2.0 / 1.7 / 3.2 / **93.1** |
| gain 2.35% (M10's aifoundry3 γ) | **68.3** / 0.4 / 4.3 / 27.1 | **34.9** / 1.1 / 3.8 / 60.2 |
| gain 3.20% (the ×1.032 arm) | **88.2** / 0.1 / 5.1 / 6.6 | **58.2** / 0.8 / 4.3 / 36.7 |
| gain 4.52% (M10's aifoundry2 γ) | **95.3** / 0 / 4.4 / 0.2 | **85.8** / 0.2 / 4.5 / 9.6 |
| level 0.15 °C | 1.1 / **44.9** / 3.6 / 50.4 | 1.5 / **20.7** / 3.5 / 74.3 |
| level 0.27 °C (E154's and E166's level alone) | 0 / **89.3** / 4.9 / 5.8 | 0.8 / **59.9** / 4.4 / 35.0 |
| level 0.40 °C (E166's two-term level) | 0 / **95.1** / 4.9 / 0.1 | 0.1 / **87.8** / 4.7 / 7.4 |
| E154's fit, −0.229 °C + 5.72% | 14.9 / 0 / **85.1** / 0 | 48.4 / 0 / **50.0** / 1.7 |
| E166's fit, +0.395 °C − 1.43% | 0 / 66.2 / **33.7** / 0 | 0 / 76.0 / **16.7** / 7.3 |
| E154's fit in one session, E166's in the other | 1.2 / 0.1 / **98.6** / 0.1 | 14.6 / 2.0 / **74.6** / 8.7 |

- **One aifoundry3 session** (df (1, 3), point 10.13): GAIN 67.1% at the arm's 3.2%, LEVEL 64.6% at 0.27 °C, 88-89% at 4.5% or
  0.40 °C; no effect reads NOT SEPARATED 93.1%. **Three sessions:** 94.3% and 94.3%.
- E166's own fit reads LEVEL more often than BOTH because its −1.43% gain is small: the test then reports the level it can resolve.
- **aifoundry2** (§ 5's masked design, P 3.05 / 12.20 / 3.05 / 12.20 °C a session; σ 0.2296): two sessions read GAIN 29.1% at M10's
  aifoundry2 γ (4.52%) and LEVEL 27.6% at 0.40 °C (NOT SEPARATED 93.6% with no effect); four sessions 51.4% and 51.9%; at the readout
  floor, two sessions 17.7% and 16.1%. **Without the mask**, every aifoundry2 hold at 800 MHz rises at least about 10.5 °C (int8 zeros:
  33.7 W board at a 47 °C rest against an idle 22.6 W, from pool 8's frozen aifoundry2 zeros prediction), so the rises span under 6 °C
  and HM-LG-A2 reads NOT SCORED in every draw.

**S7-W's rates** (§ 7; at the plan; the share of draws in which a held-out session reads worse): a gain or a level fitted on no effect
11.6% and 10.9% (11.3% and 10.8% at 1.5 σ); the right form carried 0-0.5% (2.4% for a 0.15 °C level); a wrong form carried 0-3.1%
(7.5% at 1.5 σ, a gain carried on a 0.15 °C level). **S7-W guards against a term that hurts a held-out session; it does not tell the
form, which is HM-LG's job.**

**HM-AG's rates** (two sessions, F(1, 6)'s point 5.987): 4.6-8.9% say "they differ" when the sessions share one form (the 5% the test
allows); when they differ as E154 and E166 did, 13.5% (gains) and 37.3% (levels). **With two sessions HM-AG rarely sees a difference
that HM-LG reads as BOTH (98.6%)**; a BOTH verdict with HM-AG "share" is read as § 6 says.

**H_E's readings** (one session): with no effect, HM-E144 reads inside ±1.5% in 98.5% of draws and HM-HE departs 4.8% (the 5%
allowed). A gain of 3.2% puts H_E inside 0.2%, a level of 0.27 °C 27.3%, a level of 0.15 °C 76.5%. A hold-specific miss of 0.3 °C makes
HM-HE depart 22-24%, of 0.5 °C 46-48%. **One session's HM-HE is weak; HM-E144 separates "the chain reads H_E" from a 3% gain well.**

## 5. (b) The hold design

### aifoundry3 card 0 (the primary): two sessions, on different days

E166's harness (`run_e166.py`: E97's natural chain, E89's 10 Hz 34-sensor sampler, the C-logging host on every launch), **600 MHz
pinned, nothing set** (TDP 0 W, threshold 65 °C as read at both ends). Each session on a rested card:

| step | min | item (E78's S) | pattern | P planned at a 51.2 °C room (52.0 °C) | carried-in tail | in-launch peak, 34-sensor mean |
|---|---|---|---|---|---|---|
| R0 | 5.0 | rest: the room | G0: holds run only if the room (34-sensor mean, last 120 s) ≤ 53.0 °C | — | — | — |
| **H_E** | 10 | `fp32.randn` (26.70 W) | **E144's H_H** (A1.1): `--seconds 3.20` (7 dispatches, 3.456 s) every 7.56 s, share 0.4571, if the room ≤ 51.5 °C; `--seconds 2.60` (2.965 s) every 7.98 s, share 0.3716, in (51.5, 53.0] | 14.21 (11.86) | 0 | 67.79 (66.27) °C |
| R1 | 6.0 | rest | | | | |
| **Z** | 10 | `fp32.zeros` (1.99 W) | natural chain | 0.73 (0.97) | 1.43 °C | 53.4 °C |
| R2 | 2.0 | rest | | | | |
| **L1** | 10 | `int8.full` (9.65 W; E97's H1, E154's H_M) | natural chain | 9.67 (9.78) | 1.21 | 62.5 |
| R3 | 6.0 | rest | | | | |
| **S** | 10 | `int8.neg_ones` (4.18 W; E144's H_L) | natural chain | 3.46 (3.47) | 1.09 | 55.9 |
| R4 | 2.0 | rest | | | | |
| **L2** | 10 | `int8.full` | natural chain | 8.36 (8.44) | 2.58 | 62.5 |
| R5 | 2.5 | rest: the last cool-down | | | | |

- **Why this shape.** Three rise levels and a replicate: the small holds (Z, S) hold P near 1 and 3.5 °C, the large ones (L1, L2, H_E)
  8.4-14.2 °C, so both the level (P near 0) and the slope are pinned. H_E is first, from the room, as E144's H_H was, so it repeats the
  one hold the chain read to 0.1%. The six-minute rests after the large holds keep the small holds' carried-in tails near 1 °C, so their
  P is mostly their own rise. The four other holds share one pattern, E97's natural chain (three int8 holds and fp32 zeros), so H_E
  alone is duty-cycled and the only fp32 hold that switches; HM-HE reads that difference.
- **Card-minutes per session: 74.7** (73.3 of plan plus the smoke with its five stop tests, 1.4 as in E154 and E166), inside a
  **76-card-minute envelope**. A hold does not start with less than its length + 30 s left; a rest is cut at the deadline.
- **Stops (E166's), on live samples, tested in the smoke:** no launch starts at a firmware reading ≥ 70 °C; a hold ends at any sample
  ≥ 72 °C (firmware or 34-sensor mean) or a board reading ≥ 65 W; the pass ends at ≥ 74 °C; E97's guards (a stale sampler, another user
  on the card, a clock off 600 MHz in 5 samples, three failed launches). **H_E's planned in-launch peak of 67.79 °C at a 51.2 °C room is
  E144's own envelope** (E144 measured 68.14 °C, firmware 67 °C, at a 51.22 °C rest): 3.8 °C under the hold line, the firmware about
  1 °C lower under the launch gate. Every other hold peaks at or under 64.7 °C at a 53.0 °C room. The highest board is H_E's bursts, as
  E144's (56.69 W there), under 65 W.
- **Device commands:** E166's chain, unchanged in what it sends: every command a READ, the two PMIC voltage-register reads the owner
  allowed on 2 November 2026; no statistics reset, no firmware-revisions query, no set of any kind. The kit's preflight runs
  `tools/claims-v3/dmcmd_audit.py` and must read GO.

### aifoundry2 card 0 (registered, optional: its power is low)

E167's harness (`run_e167.py` over E80's `run_kspeed.py` and E64's `run_hpl.py`, E98's 15-minute rest, the C-logging host), **its own
governor, 65 W / 65 °C as read, nothing set**. Each hold is three blocks, as E167's G1Q: REST (cool gate at 49 °C, waiting at most
240 s, then the 120 s anchor), HOLD (72 back-to-back 8 s processes, about 10.1 minutes), END (120 s); E98's 15-minute rest between holds.

| hold | item | P planned |
|---|---|---|
| **Z_m** | `int8.neg_ones` on shires mask `0x11111111` (8 of 32: every fourth shire by number, run_hpl.py's `mask`; the kit states where they sit on the die) | about 3.05 °C (a quarter of G1E's: an assumption, bracketed at 6 °C in the power file) |
| **G1E** | `int8.neg_ones` on every shire: **E144b's G1 again** (E144's aifoundry2 half), 10 minutes instead of 13 | 12.20 °C (E144b's G1) |
| Z_m2, G1E2 | the same again | |

- **The 800 MHz regime:** the 49 °C gate (E167's G1) puts G1E's plateau near 61 °C, about 4.7 °C under the governor's trip at its
  65 °C threshold; a hold read below that regime leaves HM-LG's set (§ 1).
- **The mask is a departure from every committed hold**, which all switched every shire. It is the one way, without a harness change,
  to get a small rise at 800 MHz, because int8 zeros on every shire already rise about 10.5 °C. A masked hold heats a quarter of the
  shires, a placement the chain never saw, so its miss may carry a placement effect that would read as a level on aifoundry2; that is
  one more reason HM-LG-A2 is not the primary. The kit must show that the check of C covers a masked launch; if it cannot, Z_m and
  Z_m2 are dropped and HM-LG-A2 reads NOT SCORED.
- **Card-minutes:** about **58** a session on E161's accounting (each hold about 14.3: REST 2, HOLD 10.1, END 2; the smoke and two stop
  tests 0.8), up to 74 if every gate waits its 240 s; about 105-120 minutes held, with the 15-minute rests.
- **Stops (E167's):** a die reading ≥ 72 °C on one live sample (the minion shires' mean or the hottest sensor) or a board reading over
  80 W on 3 consecutive live samples, tested in the smoke; every hold's predicted peak under section 22's 82 W admission (G1E about
  40 W, Z_m about 27 W). Device commands as E167's: every one a READ; no residency read, no statistics reset, no firmware-revisions query.
- **What it buys:** HM-LG-A2 at about 29% with two sessions and 51% with four (§ 4). Its whole-degree reading and the narrow span
  between the zeros level and the trip set that. **I recommend no aifoundry2 card time for HM-LG unless he wants four sessions**; the
  replicate of E144b's G1 (HM-E144 on G1E, reported) is the one thing two sessions would add.

### Card 0 and card 1 of aifoundry1: not designed

A hold there adds no power: **no frozen heat chain exists for either card** (Q138(t) froze aifoundry3's and aifoundry2's only), so a
hold there has no chain miss to test, and a chain fitted on the same session would be in sample. Card 0's 6 s burst coefficient (M10's
c2) gets its second session on pool 8's day (E174's C0-H1 and C0-HK), not here.

## 6. (a)'s entry rule: what each verdict puts in M11's heat over minutes

Per card kind, from HM-LG on that card kind's M11 sessions. **Only M11's own hold sessions decide it**; no committed session enters
the verdict or the constants.

| HM-LG | HM-AG | what M11 carries |
|---|---|---|
| GAIN | the sessions share one gain | γ_c = Σ e P / Σ P² over the card kind's scored M11 holds, as a factor (1 + γ_c) on the chain, **if \|γ_c\| ≥ 0.010 and its 95% interval (t at n − 1) excludes 0, and S7-W is not met** |
| LEVEL | they share one level | ā_c = the mean e over those holds, added to every hold's rise, **if \|ā_c\| ≥ 0.10 °C and its 95% interval (t at n − 1) excludes 0, and S7-W is not met** |
| BOTH | they share both | both, fitted jointly (e = ā_c + γ_c P over those holds), each by its own numbers above |
| GAIN, LEVEL or BOTH | they differ | **nothing enters**: the next registration reads the term from each session itself (a calibration hold first) |
| NOT SEPARATED or NOT SCORED | — | **nothing enters**: the chain unscaled stays M11's primary, as M10's |

- **The ×1.032 arm** stays a reported arm unless HM-LG-A3's GAIN carries γ_c on aifoundry3, which then replaces it. With LEVEL, or NOT
  SEPARATED with the null not rejected, the arm is retired from M11's readings.
- With one session (k = 1), neither HM-AG nor S7-W can be read, so **nothing enters M11's primary**: the verdict and the session's
  constant are reported as a candidate, labelled "one session", for the next session to test.

## 7. What would show a heat term is not wanted (beyond failing its rule)

- **S7-W, a held-out session reads worse.** Each M11 session of the card kind held out in turn, the carried term fitted on the card
  kind's other M11 sessions: the held-out session's rms over its scored holds, with the term minus without, exceeds **σ_c / √n_σ**
  (σ_c = 0.0884 °C on aifoundry3, 0.2296 °C on aifoundry2). Met in any held-out session: the term is not wanted. Its rates are in § 4.
- **HM-HE departs in every session** that ran H_E: the misses belong to the hold, not to the session, so no session term is wanted.
- **The sign differs between card kinds** for a term carried on both (M10's (d) clause 1).

## 8. (c) A heat scale for card 1 alone (HC1)

- **Form.** On aifoundry1 card 1 only: a kinds item's 4.5 s rise dT_win = h₁(σ) × M10's 4.5 s law (`m10.json` › `heat_4p5s`, the form
  `H2_per_card_runlength`: dT = g S + h S (T_run − 4.5), refitted in each fold as M10's `base_refit_loko`) at the item's measured S and
  run length. **h₁(σ) = the median, over the session's random anchors, of measured dT_win / the law** at the anchor's measured S and
  run length. The anchors are M10's REGISTRATION § 3a set (E78's `fp32.randn`, `fp16.randn`, `int8.full`; pool 6's and pool 7's random
  anchors where the session ran them), both families together, plus pool 8's six scale anchors in a pool-8 session; **never a check
  anchor or a zeros anchor**. aifoundry3 keeps h = 1.
- **Rows.** M10's heat rows (`fit_m7.heat_rows`' rule, with E141, E142, E153, E157, E163 and E164): **card 1's 448 rows** in 16
  sessions are judged; aifoundry3's 484 are reported, unscaled.
- **Held out:** leave one kind out, as M10's (c1): the law refitted without the kind, and the anchors of the held-out kind left out of
  every session's h₁ in its own fold.
- **Entry rule (all of):** card 1's pooled held-out heat rms with h₁ minus without **≤ −0.010 °C, with the 95% paired-bootstrap interval
  (over kinds, 2,000 draws, seed 142) below 0** (§ 0.4: already known to hold); the difference **≤ 0 in at least two thirds of card 1's
  sessions with at least 10 heat rows**; and card 1's heat bias **does not change sign and grow in size**.
- **Not wanted (any of):** HC1-B reads WORSE; h₁ over-corrects on a new card-1 session's N1 (its bias changes sign and grows in size).
- **HC1-B, the blind reading.** On **E172** (pool 8 on card 1), **counted blind only if this commit precedes E172's first launch record**
  (checked by git and the launch records' times), else reported as post hoc; if E172 never runs, on the next card-1 session that runs
  random anchors. The set: E172's N1 (31 tiles), C-gated as P8-KC. Per tile, dT_win (the mean over kept passes) against h₁(E172) × the
  law (`m10.json`'s coefficients, no refit) at the measured S and run length, and against the law unscaled: **paired bootstrap over the
  tiles, 20,000 draws, seed 80,000 + the sum of the character codes of `M11-HC1-B`: BETTER if the interval's upper end < 0, WORSE if its
  lower end > 0, else NOT RESOLVED.** Reported beside: the same at M10's primary D (as P8-H1-H3 read it); the check anchors' errors with
  and without h₁; h₃(E171) computed the same way on aifoundry3 and **not applied** (a control). These are M11's readings: they change no
  E172 rule, line or verdict, and are computed from E172's committed files after its own scoring.
- **Precision.** M10's card-1 interval (half-width 0.026 °C over 315 kinds) scaled to N1's 31 tiles gives a half-width of about
  **0.082 °C**: M10's held-out effect, −0.112 °C, would read BETTER; an effect under about 0.08 °C would not resolve.

## 9. (d) A paired-anchor int8 term for card 1 (I8P)

- **Form, the anchors' measured over predicted D, paired across the cards.** For a card-1 session σ and its paired aifoundry3 session ρ
  (one that ran the same int8 random anchor tiles, by bytes):
  k(σ, ρ) = the median, over those int8 anchors a, of [D_σ(a) / D̂_σ(a)] / [D_ρ(a) / D̂_ρ(a)],
  with D measured on Q139(u)'s footing and D̂ = M10's int8 prediction (its B form, card term 0.9616 on card 1) at each session's measured
  rate. Card 1's int8 prediction in σ is k × M10's. The pairing cancels each anchor's own miss, which § 0.5 shows is common to both
  cards; it is RK4's anchor scale relative to M10's card term. The check anchor never enters k.
- **Rows.** The card-1 int8 rows of the nine committed pairs, each a card-1 session that ran an aifoundry3 session's tiles: E82 / E78,
  E91 / E86, E131 / E95, E93 / E121, E108 / E122, E94 / E123, E142 / E141, E157 / E153, E164 / E163 (every one of them runs `int8.full`;
  the pools' pairs add their own int8 anchors). Card 1's other int8 rows keep M10's prediction and are reported.
- **Held out:** leave one kind out, as M10's B: in each fold the int8 prices and the card term refitted without the kind, D̂ and k from
  the fold's, and no anchor of the held-out kind read.
- **Entry rule (all of):** over the paired sessions' card-1 int8 rows, the held-out rms with k minus without **≤ −0.010 W, with the 95%
  paired-bootstrap interval (over kinds, 2,000 draws, seed 142) below 0**; E164's priority-1 int8 bias **falls in size and keeps its
  sign**; the rms over **every** card-1 int8 row rises by **no more than 0.001 W**.
- **Not wanted (any of):** k over-corrects (the bias changes sign and grows in size) on E164's int8 rows or over the paired sessions'
  card-1 int8 rows; the pairs' k agree with 1 within the anchors' own errors (the sd of k over the pairs no larger than the sd that
  drawing each anchor's D as D + se × N(0, 1), 2,000 draws, seed 142, gives), so M10's constant card term suffices; I8P-B reads WORSE.
- **I8P-B, the blind reading.** On **E172 paired with E171** (pool 8's 600 MHz pair), **counted blind only if this commit precedes both
  first launch records**, else post hoc. k from `int8.full`, `int8.anchor8_full_a_4aac84` and `int8.anchor8_full_b_935710` in both
  sessions' registered primary reductions (C-gated); the int8 check anchor `int8.anchor8_check_full_d8b6c8` never in k. On I1 (12
  tiles): the paired bootstrap of rms(D − k × M10 primary) − rms(D − M10 primary), as HC1-B's, seed 80,000 + the sum of the character codes
  of `M11-I8P-B`. Reported beside: the check anchor's |e| with and without k (better if smaller with k and inside M10's int8 band), and I1's
  bias with and without k ("over-corrects" if its sign changes and its size grows).
- **Precision.** M10's card-1 int8 interval for term a (half-width 0.0077 W over 93 kinds), scaled to I1's 12 tiles: about **0.021 W**.
- **What I expect, frozen so it can be wrong:** (d) does not enter, or enters and is not wanted by over-correction (§ 0.5); I8P-B NOT
  RESOLVED. A "second int8 anchor the model reads well" (the Q142 critic's other suggestion) needs a tile no session has run; it is named
  as remaining, not registered here.

## 10. Every term's entry and not-wanted rules, as numbers (M10's § 6 / § 7 form)

| term | it enters if ALL of these hold | rows it is judged on | it is not wanted if ANY of these holds |
|---|---|---|---|
| **(a) heat over minutes, aifoundry3** | HM-LG-A3 reads GAIN, LEVEL or BOTH; HM-AG "share"; \|γ_c\| ≥ 0.010 or \|ā_c\| ≥ 0.10 °C with its 95% interval excluding 0 | aifoundry3's M11 hold sessions (§ 5) | S7-W: a held-out session's rms rises by more than 0.0884 °C / √n_σ; HM-HE departs in every session; the sign differs from aifoundry2's carried term |
| **(a) heat over minutes, aifoundry2** | the same, on HM-LG-A2 | aifoundry2's M11 sessions | the same, with 0.2296 °C |
| **(c) HC1, card 1's heat scale** | card 1's pooled held-out d ≤ −0.010 °C, interval below 0; d ≤ 0 in ≥ 2/3 of card 1's sessions with ≥ 10 rows; no sign change with growth of card 1's bias | card 1's 448 heat rows (aifoundry3's 484 reported) | HC1-B WORSE; over-correction on a new card-1 session's N1 |
| **(d) I8P, card 1's paired int8 anchors** | pooled held-out d ≤ −0.010 W, interval below 0; E164's priority-1 int8 bias falls and keeps its sign; every card-1 int8 row's rms up by no more than 0.001 W | the nine pairs' card-1 int8 rows | over-correction on E164's or the pairs' rows; the pairs' k within their anchors' noise of 1; I8P-B WORSE |

**One way only:** a not-wanted clause never brings in a term that failed its entry rule; a term that enters and meets a clause is
carried as a reported arm, never as the primary (M10's A2-1).

## 11. Pool 8's day: no collision

- **Never beside it.** M11's sessions run after pool 8's card day, never beside E171-E174 on a card or a box they use, and never on their
  claims, locks, queues, build directories or post clauses. Each M11 session gets its own run number, claim and clause in the day's one
  post when he gives the card time.
- **(c) and (d)'s blind readings** read only E171's and E172's committed files, after their own scoring; they change no P8 rule, line,
  set or verdict, and nothing of E173 or E174.
- **Precedence.** Each blind reading counts as blind only if this registration's commit precedes the first launch record of every
  session it reads; the scorer checks that by git and by the launch records' times, and otherwise labels the reading post hoc.

## 12. The card time it needs (waits on his word)

| card | sessions | card-minutes | what it buys |
|---|---|---|---|
| **aifoundry3 card 0** | **2, on different days**, each on a rested card | **74.7 each, 149.4 in all** (cap 76 each) | HM-LG-A3 at 88% (a 3.2% gain) and 89% (a 0.27 °C level); HM-E144 twice |
| (the least) | 1 | 74.7 | HM-LG-A3 at df (1, 3): 67% and 65% |
| aifoundry2 card 0 (optional) | 2 (or 4) | about 58 each (up to 74 with the gate waits; 105-120 minutes held each) | HM-LG-A2 at 29% (51% with four); G1E, E144b's G1 again |
| aifoundry1 card 0, card 1 | 0 | 0 | — |

## 13. The order of the work after this registration

1. **The kits** (new files): aifoundry3's from E166's, aifoundry2's from E167's, with § 5's designs; each with `dmcmd_audit` GO, a dry
   pass on the Intel and the parent's stop tests in its smoke. **The scorer** (new files): § 1's readings through `score_e166`'s and
   `score_e167`'s functions unchanged, HM-LG through `lg_test` unchanged, § 3's readings and § 6-7's rules. Its self-test reproduces
   M10's committed per-hold e and R for E154's five and E166's four fitted holds within 0.001 °C, and prints, labelled post hoc, what
   HM-LG would read on E154 and E166 as two sessions.
2. **On his word:** the sessions of § 12, each pre-checked by git against this commit.
3. **M11's refit** (a later lane): (c) and (d)'s held-out entry rules on the committed rows (M10's 959 power rows and 932 heat rows,
   with their 62 extra inputs, `POOL8-SHA256SUMS-62`), and (a)'s constants from the M11 sessions only; frozen with a hash list; a critic.
4. **HC1-B and I8P-B** after E171's and E172's own scoring is committed.

## 14. What does not change

M10, M9, Q138(t)'s chain, pool 8 and every earlier frozen file and registered verdict stay as committed. This lane adds new files only
(`tools/claims-v3/m11/`). After it these lists still pass: M10's registration's 174 and M10's 68 and `SHA256SUMS-a2` (10),
`POOL8-SHA256SUMS` (209) and `-62` (62), `blind8/SHA256SUMS` (89), `blind7/SHA256SUMS` (91), and this registration's
`SHA256SUMS` (58).

## 15. Compute

Desk only, on the Intel: the power file is a local job of 54 s on one core through the round's slot. The committed printout and JSON
come from the run of 07:38:09-07:39:03 PST, made after a one-line change to the script's docstring; the runs of 07:28:07-07:29:01 and
07:36:18-07:37:13 gave the same bytes. Before them, a few development runs of 3 s each with 200 draws a cell, written only to the
lane's scratch. Plus git, `shasum` and sub-second reads of committed JSON. No lab box, no remote host, no card.
[`SHA256SUMS-m11`](SHA256SUMS-m11) pins this directory's other files as committed.
