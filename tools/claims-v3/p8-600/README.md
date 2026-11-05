# Pool 8's P8 scorer at 600 MHz, for E171 and E172 (Q142(k6); registered, not yet run)

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only (Q142(k6), lane `desk-q142k6-kits`): no card was claimed, no device command was
sent, no lab box was reached. It is step 2 of [`../e171/E171.md`](../e171/E171.md) and [`../e172/E172.md`](../e172/E172.md) ("The order
of the freeze"), committed after them (`4441083f`, 03:38:53 PST) and before either kit. It answers item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) (with items 8 and 9) and the
Q142(r)/(p)/(d) critic's `next` rank 2: "a scorer that imports predict_pool8_a2's lines and is self-tested on committed data". Before this,
E163-E170's scorers scored blind7's rules, never P8's.*

## What it does to predicting power and heat

It makes pool 8's blind test of M10 scorable as registered on both 600 MHz cards: M10's power per format (P1-P3), its bias (B1, B2), its
bands (C1), M10 against M9 (M1, M1f, M1i), term a against its a-priori arm (A1) and on the held-out check anchors (KA), the 4.5 s heat
(H1-H4) and the re-runs' level or gain (LG). Every line is the frozen predictor's, at the scored n. Nothing is predicted or fitted here;
no number of M10, M9 or the pool changes.

## Files

| file | what |
|---|---|
| `score_p8_600.py` | the scorer: `score --run E171\|E172 --reduction <primary> --raw <raw copy> --ccheck <check of C> [--arm name=<reduction> ...]`, and `ka-pooled <E171 scored.json> <E172 scored.json>` |
| `ccsessions_p8.py` | the check that every session that must carry a C log carries one, checked to its end (the registrations' list; the Q142 critic's fault 3); the runbook's `cc_gate` calls it, and so does the scorer |
| `selftest_score_p8_600.py` → `selftest-score-p8-600.json`, `.txt` | the self-test (below), run after the last code change, 03:53:51-03:54:56 PST, one slot job |
| `SHA256SUMS` | the five files above |

## How it scores (the registrations' words, in code)

1. The predictor's hash lists (`predict_pool8_a2.check_lists`, then `predict_pool8.check_inputs`, 209 files) and the freeze's sha256 of
   this card's predictions file and of `intervals-pool8.json` (Q142(x)'s `SHA256SUMS`); anything else exits 9.
2. The sessions that must carry a C log (`ccsessions_p8.check`): any listed session without a finished check exits 4, nothing written.
3. The frozen `predict_pool8.scale` on the reduction's anchor items, then the scale's anchors are checked: a check anchor, a zeros anchor
   or a tile that is neither M10's float anchor nor pool 8's scale anchor exits 5, nothing written.
4. The frozen `predict_pool8.primary`; E163's `measured` (copied); E163's `c_status` (copied) for P8-KC and the scored sets.
5. The rules: `boot_range` / `mix_range` lines at the scored n with seed 80000 + the rule id's character codes (P1-P3, B1, B2, H1-H3);
   `binom_low` (C1, H4); the paired form, E163's `compare_rule` with 20,000 draws (M1, M1f, M1i, A1); KA per session and pooled;
   `design_power_groups.lg_test` (LG); G from its parts; HM NOT SCORED. Fewer than 2 kept passes: every rule NOT SCORED.

## The self-test: all six parts PASS

| part | what | result |
|---|---|---|
| S1 | the rule functions on each card's frozen sets give `intervals-pool8.json`'s lines | 11 of 11 lines per card identical (P1-P3, B1, B2, H1-H3, C1 and H4's coverage line, LG's F point) |
| S2 | E163's committed figures, with the scorer's functions configured as E163 registered them (seed base 16300, 20,000 draws, paired 5,000, M9's references) on E163's committed reduction | 13 of 13 rules reproduced, every reading, interval and verdict to 1e-12: P1 FAIL 0.3886 W, P2 PASS 0.1917, P3 PASS 0.1913, B1 FAIL LOW +0.1507, B2 FAIL LOW +0.0509, C1 PASS 42 of 48, M1 BETTER −0.0982, M2 BETTER −0.1427, M3 BETTER −0.1012, H1-H3 PASS 0.2257 / 0.1632 / 0.1244 °C, H4 PASS 46; the copied `c_status` equals E163's committed one for all 77 tiles (2,310 launches, all PASS); `ccsessions_p8` lists E163's 7 C-logged sessions (the smoke, three kinds passes, three E151 blocks; 72, 990 × 3 and 340 × 3 launches) and finds each checked to its end |
| S3 | the same for E164 (seed base 16400, paired 5,000, card-1 references) | 12 of 12 rules reproduced: P1 FAIL 0.3765, P2 PASS 0.1754, P3 PASS 0.2000, B1 FAIL LOW +0.1636, B2 FAIL HIGH −0.0765, C1 FAIL 41 of 48, M1 NOT RESOLVED −0.0485, M2 BETTER −0.1175, H1 PASS 0.3343, H2 PASS 0.3517, H3 FAIL 0.2122, H4 PASS 44; `c_status` all PASS over 2,550 launches; 5 sessions listed, each checked to its end |
| S4 | end to end through the frozen predictor: pool 7's ten T9 tiles predicted for both cards, then scale, its check and primary on M10's committed footing reductions of E163 and E164 | every M10 primary equals `rows-m10.json`'s in-sample prediction within 7.1e-15 W; the scale equals M10's committed session scale (1.00991 / 1.01024); the scorer's per-format rms equals the rms from `rows-m10.json` within 1.5e-15 W |
| S5 | a synthetic session with known answers on each card (rates at the stated rate, the scale anchors at s = 1.004, designed errors) | every designed verdict and reading (P1 PASS at 0.100 W, P3 FAIL at 0.300, B1 PASS, B2 FAIL LOW, H3 FAIL, H4 and C1 counted against the frozen bands, KA PASS, LG GAIN, G FAIL, HM NOT SCORED), s = 1.004; the command line gives the same verdicts; with every fp16 N1 tile C-excluded P2 and H2 read NOT SCORED and the all-tiles block appears; one kept pass: every rule NOT SCORED; no scale anchor measured: s = 1, KA NOT SCORED; a missing C log, a check that skipped one session's log, and a launched stop-path test: exit 4 and no file; a check anchor, a zeros anchor or a non-anchor in the scale: exit 5; a predictions hash that is not the freeze's: exit 9; `ka-pooled` over the two cards: PASS, n 4 |
| S6 | the paired interval against an independent re-implementation from the registration's words | identical for M1, M1f, M1i and A1 |

## Compute

The Intel, every Python run through the round's local slot, one at a time, at nice 10: two development runs of the self-test (the first
failed S2, on a field `c_status` had dropped from E163's copy, and S5, on the test's own design of the no-scale case; both fixed; the
second passed), a third that passed into this directory at 03:51:10 and was overwritten after one more change (the variable `ROOT`
renamed `TOP` in the three files, for the public-text scan's fixed list; nothing else), and the committed fourth, about 55-65 s each on
one core; the slot wrapper's own lock message, which its redirect put on the output's first line, was removed from the `.txt`; before them a facts script (once) and the registrations'
generator (three times), about a second each. No lab box, no mini job, no card.

SPDX-License-Identifier: Apache-2.0
