# Dated note 5 beside REGISTRATION.md (Fri 6 Nov 2026, week 45): dated note 2's Builds-on block, the registration's block completed, and the wording the records quote

*This note sits beside [`REGISTRATION.md`](REGISTRATION.md) and its dated notes 1-4, and edits none of them. Every file of
[`SHA256SUMS-4`](SHA256SUMS-4) stays as committed (`3002edaf`). It adds no rule and changes no number, parameter, line or
verdict. It gives what the dip lane's verifier found missing or overstated in the registration's records, before any governed
session. Its time is its commit's.*

## 1. Dated note 2's Builds-on block

[Dated note 2](REGISTRATION.md.dated-note-2.md) (`17c18e89`) added a term (K_GC = 0.67, a governed pass's deficits scaled by
it) and a rule (seq-gc's promotion if it reads a lower DT-G rms than seq on the blind session) without the block the stock-take's
rule asks for. A missing block makes such an amendment not ready, not a wording fault. This is its block, given late. No governed
session has run since note 2, so seq-gc has scored nothing, and its standing (REPORTED, never a verdict) is unchanged.

1. **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 03:50 PST. Public rows read: P01, P02, H23, H26, L22. The ids are
   opaque pointers into a private inventory.
2. **Used:**
   - **The post hoc study** ([`2026-11-06-q145b-dips-posthoc/`](../../../docs/reports/data/2026-11-06-q145b-dips-posthoc/README.md),
     `006c85eb`, results 3 and 4). Taken: E175's three governed falls cost 24.23, 21.73 and 26.97 MHz against the term's 32.36,
     37.50 and 39.24 MHz (`posthoc-dips.json` > `sessions.E175.fall_costs`), ratios 0.749, 0.579 and 0.687, mean 0.67.
   - **E175's committed data** (`9f13d7c3`; `results.json` > `run_rows` and `score.reported.tiles`). Taken: each tile's counted
     passes and its governed set, as the run's registered rules read them.
   - **E64's governor model** ([`../hpl/surface_hpl.py`](../hpl/surface_hpl.py), a first-order average of the board's power
     compared with the TDP once per pass; [`2026-10-23-e64-horace-power-limit/README.md`](../../../docs/reports/data/2026-10-23-e64-horace-power-limit/README.md)
     line 103). Taken: the catch-up's mechanism only. After a dip the filtered power is lower, so the power arm holds 800 MHz
     longer. No figure is taken.
   - **The check against an earlier measurement of the same quantity:** none exists at the same operating point. The pinned falls
     of E173 and E174 cost what the term says (study, result 4), so the factor is the governed passes' alone.
3. **Not used:**
   - **E173's `fp16.u8_tdist_93475b` governed fall** (25.6 against 38.67 MHz, ratio 0.66). It is close to K_GC, but the tile has
     no governed prediction: its f_ref is 800 MHz, so its ratio is not comparable.
   - **A catch-up model from `surface_hpl.py`'s filter** (simulating the power arm after a dip). It is owed before K_GC could be
     anything but a reported arm.
4. **Tiers:** public only.
5. **Readiness:** the block was missing from `17c18e89` until this note.

**Under amendment A1** ([dated note 4](REGISTRATION.md.dated-note-4.md)), E175's `BURST-68` fall, the 0.749 of the three, is not
counted: its run's ring shows the power arm stepping to 600 MHz three times. On A1's two governed falls the ratio is 0.579 and
0.687, mean 0.63 (post hoc, n 2). K_GC stays 0.67 as committed, and seq-gc stays REPORTED.

## 2. The registration's Builds-on block, completed

- **P03 and H28 were listed as checked but as neither used nor not used.** Both are **not used**:
  - P03, the public PMIC firmware's board meter and its one-second average: the meter's dated notes beside
    `docs/energy-manual/09-method.md` treat it. The term takes only a lag for the board's deficit (A1-6 adds its sensitivity arm).
  - H28, the kits' meter and stops: the term reads the sampler's board only through the registered reduction's tile means, and
    takes no parameter from the kits.
- **E100's corrections commit is `2e2dea21`** (Sun 1 Nov 2026, 02:24 PST, "E100: corrections after verification"). The
  registration's "corrections `9b93e3e9`" names Q132(o)'s cross-link pass (09:56 PST), which touched E100's README only to link it.
- **The board's lag was mis-sourced.** `BOARD_LAG_S` 0.24 s cites "E58, published one SP pass late; E64's pass 0.24 s". E58's "one
  pass late" is the **rails** on aifoundry3, whose pass is 0.255 s under the 10 Hz sampler; E58 read `board_avg_w` as current
  (`docs/findings/05-claims.md` lines 770 and 773). `board_w`, the instantaneous reading the sampler takes, is refreshed once per SP
  pass: every 156 ms on aifoundry2 under the 10 Hz sampler (`docs/findings/14-card-behaviour.md` line 794). E64's 0.24 s is the
  pass its model fitted. The registered 0.24 s stays; A1-6 reports the seq arm's board at 0.17 s beside it.

## 3. Wording the records quote

- **DT-N is a rate check.** It tests how many falls a session's gaps allow, not which bursts dip. Random placements of the same falls
  pass it too, and at 4-8 expected falls its band is wide (1-14 at E173's 7.0). DT-L is what tests the phase. Quote DT-N's PASS as
  "the count matches the gaps", never as "the dips are predicted".
- **The period from a session's falls includes the card's prior.** The post hoc study's 1000.0104 ± 0.0006, 1000.0194 ± 0.0007 and
  1000.0097 ± 0.0009 ms are the lattice fitted with the prior (`fit_lattice` adds it). Quote them as "with the card's prior". The
  figures without it are in the post hoc study's dated note 1.
- **Card 0's fall is over-stated, one-sidedly.** The term's P + c7 = 1.13 s is longer than E174's measured 1.062 s (median of four
  falls that recovered). On the four full falls the term reads 45.1, 49.8, 45.0 and 49.5 MHz against 44.9, 46.0, 42.0 and 44.9 MHz
  measured. Dated note 2's and the post hoc README's "within 0.2-4.6 MHz on six falls" hides that the term is never low on a full
  fall. A1-5 re-reads card 0's climb after a fall.
- **Dated note 3's own header** says 03:03 PST. It was committed at **03:01:40 PST** (`5dba20fd`). The records quote commit times.
- **Kit v4's one-kernel bursts are an option, dry pass only.** "Kit v4 runs bursts as one kernel by default, which removes the dips"
  states as done what has only a desk test and a dry pass: there is no kit v4, no card run, and the A/B check is owed. "Removes
  the dips" rests on E100's N arm (0 falls in 126 heartbeats inside its kernels, which alone does not separate N from A0; E100's
  README line 13) and on E100's 0 of 234 heartbeats inside kernels. Quote it as "an option for kit v4 (dry pass only)".

## Files

| file | what |
|---|---|
| `REGISTRATION.md.dated-note-5.md` | this note |
| [`SHA256SUMS-5`](SHA256SUMS-5) | this note, plus every file `SHA256SUMS-4` lists and `SHA256SUMS-4` itself, all unchanged |

SPDX-License-Identifier: Apache-2.0
