# E216 amendment 1: verify-e216's findings answered before any E216 datum (Q227, lane fix-e216)

*Dated Thu 19 Nov 2026 (week 47), written 14:30-15:30 PST at the desk on aifoundry2 by Q227's lane `fix-e216`, **before any E216 datum**: no
booking of aifoundry2 for E216, no card-e216 folder, no `tools/claims-v3/e216/` path and no `docs/reports/data/` folder naming e216 in any ref of
GitHub's main. It answers verify-e216's findings (HOLDS WITH FIXES, its result written 14:24 PST). This amendment is part of the registration
commit, so E216's freeze line (that commit's push) covers it.*

**What did not change.** No forecast: `forecast-e216.json`, `.csv` and `.txt`, `points-e216.json` and `.csv`, `plan-e216.json` and `.txt`,
`kernel-e216.json`, `POINT-RULE-e216.md` (hashed at 10:25:10 PST), `desk/` and `terms/` are byte for byte as reg-e216 made them and verify-e216
checked them. No band, tie, threshold, head-to-head, minimum of a head-to-head, card time, stop or order changed.

**What changed.** One registered rule, A1, for the fault the verifier named. One registered reading, A3, is now written down: the kit's. Every
other item below is REPORTED (A2, A4) or a correction of words (A5, A9, A10, the nits). This lane opened no E215 datum and read no E215 result:
its scratch clone keeps every `docs/reports/data/*e215*` folder out of its working tree, and no file of E215's card lanes was opened.

## A1 (verify-e216's F1, a rule defect): the pair rule P1 needs at least 5 decided pairs, RE-FROZEN

The registered minimum was 4. But 4 of 4 pairs ordered right gives a one-sided exact binomial p of 1/16 = 0.0625, which is over 0.05. So at
exactly 4 decided pairs P1 could only read **FAIL**, the same word as 0 of 4. PASS first becomes possible at 5 decided pairs (5 of 5: p 0.031).

**Re-frozen:** `rules_e216.py` sets `PAIR_MIN = 5`, and `rules-e216.json` is re-made by it. **4 or fewer decided pairs now read TOO FEW.** PASS
and FAIL are as registered for 5 or more: PASS when more than half are ordered right and p <= 0.05 (5 decided: 5 right; 6: 6 right; 7: 7 right;
8: 7 or more), FAIL otherwise.

- `rules-e216.json` is re-made by its own maker (seed and draws unchanged): `ca96812c...` becomes `c6a8f10c88445b2cca72ece73168d247e5fd10e40d02e7de4cd721f070c1806e`.
  A field-by-field comparison with the verified file finds exactly two registered fields changed: `pair_rule.min_decided` 4 to 5, and the pair
  rule's REPORTED power with truth = MM1-v3.1 (FAIL 0.001 to 0.0; TOO FEW stays 1.0). With truth = contention, PASS 0.913 / FAIL 0.087 is
  unchanged, and with truth = contention x 3, PASS 0.911 / FAIL 0.089 is unchanged: those days always decide at least 5 pairs. Every other
  field is as verified, and the only additions are A4's REPORTED fields.
- `score_e216.py` is re-pinned to the new `rules-e216.json`. Its PINS line and one comment line are the only changes, so its sha256 is now
  `9c61d06cbb6d11ec00a6d7f26d25da48160857d0ddfefe5b403dd89fba3d3c4e`. The scorer reads the minimum from `rules-e216.json` (`pair_rule.min_decided`).
- **Checks (desk):** the scorer's own self-test on its ten stand-in days is re-run, and `selftest-standins.json` is byte for byte as verified.
  `report_e216.py --selftest` drives the frozen scorer on new stand-in days. Pairs moved 1% apart each way read:
  - 4 decided, all ordered right: **TOO FEW**;
  - 5 decided, all ordered right: **PASS** (p 0.03125);
  - 5 decided, 4 ordered right: **FAIL**;
  - 6 decided (5 ordered right and a control separated): **FAIL**.

## A2 (F2): what E1-E4 read if the gemmLnc term is right, and a REPORTED reading without family G

Family G's 10 points are a quarter of the 40 registered points that T1-T3 and E1-E4 score. At those points the registration's own frozen
gemmLnc term puts MM1-v3.1's W over idle 16-23% low (at 799.0 MHz: g01 38.02 against 30.96 W, g02-g06 37.68 against 30.71 W, g07-g10 37.15
against 32.07 W). E211's and E213's measurements of gemmLnc's excess, made on other cards, pointed the same way.

**Stated before the data:** if the term is right at G, **E1, E2 and E3 read FAIL at 30 of 40, and E4 reads FAIL at 34 of 40** (36 needed).
That comes from family G alone, whatever MM1-v3.1 does at Gt, Y and F. The registered P(PASS) of 0.97-0.99 for E1-E4 assumes MM1-v3.1's
held-out error at every point, so it does not hold if the term is right.

The stand-in day `lnc_at_G` in `reported-selftest-e216.json` checks this: G's W over idle is set at 'v3.1 + gemmLnc term' and every other
figure at MM1-v3.1. It reads:

| rule | over the 40 registered points | over the 30 outside G | over G alone |
|---|---|---|---|
| T1 | PASS 40 of 40 | | |
| E1 | FAIL 30 of 40 | PASS 30 of 30 | FAIL 0 of 10 |
| E2 | FAIL 30 of 40 | PASS 30 of 30 | |
| E3 | FAIL 30 of 40 | PASS 30 of 30 | |
| E4 | FAIL 34 of 40 | PASS 30 of 30 | FAIL 4 of 10 |

H2w reads 'v3.1+lnc BETTER' on that day.

- **The registered rules are unchanged:** E1-E4 and T1-T3 are scored over the 40 registered points. Re-registering them over the 30 points
  outside G is the orchestrator's call, before any datum; this lane did not make it.
- **REPORTED beside them:** `report_e216.py` reads the scorer's own output (`scored-e216.json`). It REPORTS T1-T3 and E1-E4 over the 30
  registered points outside G and over G's 10 alone, from the scorer's own cells and by the scorer's own `verdict()`. First it re-makes the
  registered verdicts over all 40 from those cells and checks that they equal the scorer's; if they do not, it writes MISMATCH and nothing else.
  Runbook step 13 runs it after the scorer (the kit, `rb/s24_score_e216.sh`), into `RB_OUT/score/reported-e216.json` and `reported.out`.
- **How to read the day:** suppose E1-E4 FAIL over the 40, H2w reads 'v3.1+lnc BETTER', and the REPORTED lines without G PASS. That reads as
  the term right at G with MM1-v3.1 holding elsewhere. It is not, by itself, a fault of MM1-v3.1 outside family G.

## A3 (F3): the never-run reading, registered (the kit's)

Section 4's rule counts a hit "in a folder naming aifoundry2 or a2c0, or naming no card". Read literally over today's lane folders, it now
removes **9 of the 46 points**: y08a, y08b and f01-f07. verify-e216 finds every one of those hits in E217's registration copy under
`W/out/data-e217/work/reg-tree/` (`configs-e217.json`, `scan-e217.json`, `arms.json`, written 13:14-13:17 PST). That copy is the model
session's plan for aifoundry1, written after this registration's scan, and none of its hits is a run on any card.

**The registered reading (adopted here, before any datum):** a point ran on aifoundry2 card 0 only on **evidence of a run on this card**, dated
before E216's freeze line or undated. Evidence is one of:

- a measured point of MM1-v3's or MM1-v3.1's on this card;
- a committed lab file counted for this card (a data folder naming aifoundry2 or a2c0, or naming no card);
- a lane file in a folder naming aifoundry2 or a2c0;
- a lane file in a folder naming no card that is a **session record** by its name: `queue.json`, `run.json`, `status.json`, `session.log`,
  `smoke.json`, `telemetry.jsonl[.gz]`, `launches.jsonl[.gz]`, `proc*.out`, `proc*.err`, `data-*.json` or `reduce-*.txt`.

A hit only in a lane file whose folder names no card, and which is not a session record (an arm list, a schedule copy, a plan, a registration
copy, a desk scan), is REPORTED with its file and dates and never labels a point. A point whose every counted file is dated after the freeze
line is REPORTED ('ran after') and kept.

This is KIT.md section 4 item 12's reading, and `desk/neverrun_card_e216.py`'s code (runbook step 6n), unchanged. The registration's own scan
(`desk/scan-e216.json`, run before the point rule) is unchanged and found no hit either way. **The orchestrator confirms this reading**: an open
question to it in fix-e216's result.

## A4 (F4): REPORTED: the power with errors shared by configuration, and the head-to-heads by distinct configuration

Family G's 10 points carry 3 distinct per-op forecasts. The Y pairs y01-y03 are one mask pair at three shapes, and 5 of the 6 card-transfer
twins share one forecast. So a sign test over points counts near-duplicates as independent.

`rules-e216.json > power_shared_REPORTED` is made by `rules_e216.py`'s new `power_shared()`, from a generator of its own (seed 20261120), so
every registered simulation draws exactly as before. It is the registered power simulation, with every case's ln error shared by its distinct
configuration. A configuration is the two forecasters' frozen per-op values at 799.0 MHz (wall cycles an op; W over idle for the energy rules),
rounded to 6 decimals.

| rule | cases / configurations | P(first BETTER \| truth first): independent -> shared | P(a winner \| the midpoint): independent -> shared |
|---|---|---|---|
| H1t | 40 / 17 | 0.041 -> 0.132 | 0.022 -> 0.205 |
| H2w | 10 / 3 | 0.915 -> 0.866 | 0.028 -> **0.437** |
| H2f | 10 / 3 | 0.889 -> 0.849 | 0.022 -> **0.450** |
| H3 | 16 / 12 | 0.018 -> 0.037 | 0.014 -> 0.027 |
| H4 | 40 / 22 | 0.636 -> 0.660 | 0.026 -> **0.224** |

**So, with errors shared by configuration, a 'winner' of H2w or H2f at the midpoint truth comes on about 44% of simulated days, and of H4 on
about 22%** (verify-e216's own simulation: 43% and 23%). A winner of those rules speaks for 3 configurations, or for H4's 12 decidable ones,
not for 10 or 20 independent points.

`report_e216.py` REPORTS each head-to-head's tallies by distinct configuration beside its point-level verdict. Those tallies are first
closer / second closer / ties over the configurations (a configuration's d is the mean of its cases' d), with the exact two-sided sign p over
the decided ones. They are never a verdict: with 3 configurations, no sign test can reach 0.05.

The cases are the scorer's own. They are re-made from its output, and their point-level tallies must equal the scorer's (checked on every
stand-in day). The distinct configurations counted on a full stand-in day equal `power_shared_REPORTED`'s `n_configurations` (17, 3, 3, 12, 22).

## A5 (F5): D3's basis corrected (the 64.0 W line stays)

D3, and POINT-RULE-e216.md's disclosure and planning line, say every E212 session on this card was planned at or under 64.0 W, and that a point
over 64 W would be capped by the governor, voiding its 799 MHz forecast. **The committed record says otherwise** (re-read by this lane from the
committed files):

- the planned peaks (`est_peak_w` in the committed schedules): E208's a2c0-S1 and a2c0-S2 were planned to 73.3 W; E212's a2c0-S2 to 73.3 W
  and a2c0-S3 to 65.6 W (S1 and S4 to 64.0 W); E209 planned e44 at 69.21 W;
- E209's e44 then held 799.2 MHz in its win view (`mhz_min` 800) at a 68.27 W board mean, on route c and not capped.

So the governor did not cap this card's matmul runs at 64-69 W. **The 64.0 W line stays as registered.** It is a conservative planning choice
against the 70 W x 3 board stop (the highest planning peak is 63.21 W). verify-e216 counts 138 NB3 and 72 NB56 G candidates that it removed.
Only its stated basis was wrong. POINT-RULE-e216.md stays as hashed (10:25:10 PST): this note corrects its words and changes nothing it chose.

## A9 (F9): section 8's words on verify-lay's reading

Section 8 says "a FAIL of P1 or H3 agrees with verify-lay's reading, a PASS contradicts it". That is not what the rules read under
verify-lay's count-only reading. Then the card shows no within-pair difference at equal shire counts, so P1 reads **TOO FEW**: the registered
simulation gives TOO FEW 1.0 when the truth is MM1-v3.1, at the minimum 4 and at 5 alike. H3 reads NOT DECIDED, or 'MM1-v3.1 BETTER'.

**Corrected:**

- a **TOO FEW** of P1 agrees with verify-lay's reading;
- a **PASS** contradicts it;
- a **FAIL** (pairs separated but ordered wrong, or a control separated) contradicts both the contention term and verify-lay's reading: it
  means a layout effect that the term misorders;
- H3's expected reading is NOT DECIDED either way (its registered power is about 2%).

## A10 (F10): the freeze line's timing

GitHub's main took E215 arm A's data (`8355db15`, 13:00:32 PST) and since then E215 arm B's data (`4f648f24`), both before E216's
registration push. So E216's public, timed freeze line (the land lane's push of this commit) now postdates E215's data.

E216 stays blind to E215:

- every forecast re-makes byte for byte from frozen code and inputs that were public before any E215 datum (verify-e216:
  `forecast-e216.csv` byte-identical; the term files equal posts #1.29 and #1.29.1, 09:32 PST);
- the points come from the rule hashed at 10:25:10 PST over committed inputs;
- this amendment changed no forecast and no point;
- its one rule change (A1) is the verifier's mechanical fix of a minimum, made by a lane that opened no E215 datum and read no E215 result.

The same statement belongs in `W/out/q227-freeze-e216.txt`, beside the push's sha and time (the land lane writes it).

## Notes on words (verify-e216's nits)

- **nit 2:** g02 runs after g03-g06 because its planning peak is about 9.4e-10 W higher (a float difference), not because of its id.
- **nit 3:** the point rule's text passes L2's unfilled quota "to the next in the order NB3, NB56, L2, then back to NB3", while its code shared
  it round-robin (NB3 +2, NB56 +1, giving G = NB3 6, NB56 4). The text and the code were hashed together at 10:25:10 PST. The draw is the
  code's, as hashed and kept by the orchestrator's answer 1 (`W/out/orch/e216-answers.txt`).
- **The kit's items** (verify-e216's F6, F7, F8 and nits 1, 4, 5 and 6) are answered in KIT.md's section "fix-e216" and CARD-LANE-BRIEF.md:
  - THE ORDER's markers when an E215 card lane books again (F6);
  - step 0's S1 on an unreadable record and an upper-case seal (F7);
  - a load gate at steps 7 and 9 for THE CPU RULE (F8);
  - the runbook test's counts in its two forms (nit 1);
  - step 1's 00:00:00 Friday (nit 4);
  - the brief's step-0 row (nit 5);
  - G8 reading step 7's words (nit 6).

## Files this amendment changed or added (under `tools/claims-v3/e216/`; all are new files to GitHub's main)

| file | change | sha256 |
|---|---|---|
| `rules_e216.py` | A1 (`PAIR_MIN = 5`, its docstring) and A4 (`config_key()`, `power_shared()`, the new REPORTED field) | listed in `SHA256SUMS-e216-registration` |
| `rules-e216.json` | re-made by it (A1, A4) | `c6a8f10c88445b2cca72ece73168d247e5fd10e40d02e7de4cd721f070c1806e` |
| `score_e216.py` | its PINS line re-pinned to the new rules, and one comment line (A1) | `9c61d06cbb6d11ec00a6d7f26d25da48160857d0ddfefe5b403dd89fba3d3c4e` |
| `report_e216.py` | new: A2's and A4's REPORTED readings from the scorer's output, with its self-test | listed in `SHA256SUMS-e216-registration` |
| `reported-selftest-e216.json` | new: its self-test (16 cases: the scorer's ten days, the configurations, lnc_at_G, p1_4, p1_5, p1_5w, p1_ctrl), PASS | listed in `SHA256SUMS-e216-registration` |
| `E216-amendment-1.md` | this note | listed in `SHA256SUMS-e216-registration` |
| `E216.md` | markers in place at D3, sections 1, 4, 7 and 8; section 0's and 10's tables; the Amendments section | listed in `SHA256SUMS-e216-registration` |
| `SHA256SUMS-e216-registration` | re-made: every file but itself | (the kit pins it) |

**Desk checks of this amendment** (aifoundry2, `/usr/bin/python3` 3.12.3 `-I -B`, single-threaded in the round's slots):

- `rules_e216.py` re-run, with the field-by-field comparison above;
- `score_e216.py --selftest-standins` (bytes as verified) and `--forecasts` (only the pins line differs);
- `desk/realbytes_e216.py` (`selftest-real.json` bytes as verified);
- `report_e216.py --selftest`: SELFTEST-REPORT-E216 PASS, its output byte-identical on a second run;
- `sha256sum -c SHA256SUMS-e216-registration`.
