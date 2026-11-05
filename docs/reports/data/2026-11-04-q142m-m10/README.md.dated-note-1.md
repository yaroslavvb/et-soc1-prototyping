# Dated note 1 beside README.md (Wed 4 Nov 2026, about 21:25-21:45 PST; Q142(m)'s fix pass) - section 7 read for every term: term (d) is not wanted, so M10's primary carries Q138(t)'s chain unscaled and the +3.2% gain as a reported arm; every power figure stands

*README.md, `m10.json` and every other file of `6829c9ba` (20:24:58 PST) stay as committed. This note follows:*
- *the lane's verifier, which read the four commits adversarially, about 20:30-21:00 PST;*
- *dated amendment A2, [`../../../../tools/claims-v3/m10/REGISTRATION.md.dated-note-2.md`](../../../../tools/claims-v3/m10/REGISTRATION.md.dated-note-2.md)
  (`ef74dd0d`, 21:23:36 PST). A2 was committed before any section 7 output, and it says how § 7 binds and how each clause is
  read.*

*Where this note and README.md differ, this note governs. On the kinds page,
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 6, 8 and 9.*

## 1. Section 7, read for every term

Every reading below comes from [`section7-m10.json`](section7-m10.json), written by [`section7_m10.py`](section7_m10.py). That
script first re-ran `fit_m10.py`, unchanged, and every committed output reproduced:
- `heldout-m10.json` within 8.5e-14;
- `rows-m10.json` within 2.1e-13 W;
- `m10.json` within 2.2e-9 relative, at a covariance element;
- no other value differed. `fit-output.txt` differs in one line, its self-test's last digits.

The readings use M10's committed held-out errors (leave one kind out; for c2 and e one tile, for d one session).

| term | entered by § 6 | § 7's clause | reading | met? |
|---|---|---|---|---|
| (a) floats | yes | the scales agree within their own noise | the sd of s over a card's sessions is 0.00201 on aifoundry3 (14 sessions) and 0.00248 on card 1 (16). The anchors' own errors alone would give 0.00070 and 0.00112, so the spread is 2.9 and 2.2 times their noise. | no |
| | | pool 7's bias moves toward 0 on both cards | B → B+a, pool 7's 28 float kinds: +0.178 → +0.090 W (aifoundry3) and +0.192 → +0.101 W (card 1). Priority 1: +0.188 → +0.101 and +0.201 → +0.111 W. | no |
| | | the scale over-corrects | no family cell changes sign and grows (every row, pool 7's 52, priority 1; each card) | no |
| (b) | yes | the S rows move the wrong way | the S rows' rms, B → B+b: 0.497 → 0.287 W (aifoundry3) and 0.507 → 0.223 W (card 1) | no |
| | | counting is not what misses | 4 of the 13 S tiles have \|3pt − N\| ≤ e(N): `b9_one`, `a_onebit_b16_half`, `a_onebit_b5_third` and `b12_third` | no |
| (c2) | yes | the leave-one-tile-out k includes 0.14004 | k runs 0.2407-0.2433 | no |
| **(d)** | **yes (one γ)** | γ's sign differs by card kind | γ 0.0235 (aifoundry3) and 0.0451 (aifoundry2). Every per-card-kind fold's γ is positive (0.015-0.031 and 0.037-0.058). | no |
| | | **a held-out session's large rises read worse with γ** | **E144: 0.015 → 0.547 °C.** Its one large rise, `H_H` (R 15.00 °C), was read by the chain to 0.1%. With its fold's γ (0.0375) it reads −0.547 °C, 0.53 °C worse. The other five sessions improve: E144b 0.724 → 0.367, E154 0.442 → 0.121, E161 0.367 → 0.152, E166 0.238 → 0.162 and E167 0.910 → 0.475 °C. | **yes** |
| (a) int8 | no | (reported) | Card 1's scales lie within their noise (0.0054 against 0.0068). On aifoundry3 the scale over-corrects pool 7: +0.047 → −0.055 W. | (yes) |
| (c1) | no | (reported) | the heat scales' sd is 0.042 on aifoundry3 (13 sessions; E115's single-pass anchors have no se, so E115 is left out) and 0.136 on card 1 (16), against 0.014 and 0.022 from the window rise's own errors. The gain is not resolved on aifoundry3 (+0.002 [−0.003, +0.007] °C). | (the gain clause) |
| (e) | no | (reported) | κ runs 0.9602-0.9671 for floats and 0.9160-0.9218 for int8, so κ0 0.9463 is outside both. The board error is not resolved (−0.096 [−0.180, +0.016] W). | (the board clause) |

**So, by A2-1, term (d) is not wanted.** M10's primary entries are (a) floats, (b) and (c2), and (d) is out. The terms that
failed § 6 stay out, and § 7 changes nothing for them.

## 2. What supersedes what

- **M10's primary entries.** [`m10-s7.json`](m10-s7.json) supersedes `m10.json`'s `entered` and `heat_chain_gain` as the
  primary, and nothing else. `m10.json` stays the frozen form for every other parameter (sha256 `37b7fa86…`, as listed in
  [`SHA256SUMS`](SHA256SUMS)).
- **The predictor.** [`predict_m10_s7.py`](predict_m10_s7.py) carries predict_m10.py's functions, plus:
  - `chain_gain_primary` = 1: Q138(t)'s chain unscaled;
  - `chain_gain_arm` = 1.032: the reported arm.

  `predict_m10.chain_gain()` returns the arm's factor, never the primary's. Its self-test passes
  ([`selftest-predict-m10-s7.txt`](selftest-predict-m10-s7.txt): the hashes, both factors, and predict_m10's own self-test,
  104 rows within 1.4e-14 W).
- **Heat over minutes, M10's primary: Q138(t)'s chain unscaled.**
  - Over the nine large-rise holds (six sessions) the chain reads 0.493 °C rms. Q138(t) froze the chain before E144, the
    first of those sessions, so it is blind on all nine.
  - The 1.032 arm reads 0.294 °C, held out by session. It is reported, not used.
  - Pool 8's registration names the chain unscaled as its primary, with the arm beside it.

## 3. README.md's sentences, as corrected

- **The title.** "the heat chain's gain of +3.2% enters" becomes: the heat chain's gain of +3.2% passes § 6, but § 7 shows it
  is not wanted (E144). So M10 carries the chain unscaled, with the gain as a reported arm (A2).
- **"In plain words".** "Over minutes, Q138(t)'s chain reads large rises 3.2% low on both card kinds; a gain of 1.032 takes the
  large-rise plateaus from 0.49 to 0.29 °C rms, held out by session" becomes:
  - Fitted on every non-trip hold, the chain reads rises 2.3% low on aifoundry3 and 4.5% low on aifoundry2 (one common γ:
    3.2%).
  - On aifoundry3 the large rises improve by only 0.085 °C rms with it.
  - A gain of 1.032 takes the nine large-rise plateaus from 0.49 to 0.29 °C rms, held out by session. But E144's one large
    rise, which the chain read to 0.1%, reads 0.53 °C worse with it, so § 7 keeps it out of the primary.
- **Results table 1, row (d), one γ.** "enters? yes" becomes: passes § 6; not wanted by § 7 (E144); a reported arm.
- **"M10, frozen", Heat.** "Q138(t)'s chain's rise times 1.032" becomes: Q138(t)'s chain unscaled (the primary), and times 1.032
  as a reported arm.
- **"What this does to predicting power and heat", the heat-over-minutes row.** "**0.294 °C** (rise x 1.032, leave one
  session out)" becomes: the primary stays the chain's 0.493 °C; the 1.032 arm's 0.294 °C is reported.
- **"What this cannot say".** "d rests on nine large-rise holds in six sessions" stands. Add: and its own § 7 clause is met
  by E144.
- **The dateline.** "19:20-20:45 PST" becomes: the lane ran about 19:15-20:25 PST. README.md was last written at 20:24:01 and
  committed at 20:24:58 (`6829c9ba`); 20:45 was the lane's planned end. A2-3 corrects the registration's and A1's datelines.
- **The rate.** "Pool 6's and pool 7's sessions ran 0.28-0.36% below the nominal rate" becomes, per format, each session's
  mean over the rows M10 reads, below fit_m5's nominal:
  - fp32 0.33-0.36%;
  - fp16 0.33-0.35%;
  - int8 0.23-0.28%.

  Each session's mean over all its rows is 0.29-0.32% below, and single rows 0.19-0.44%
  ([`a2-checks-m10.json`](a2-checks-m10.json) › `rate`). Pool 8's registration states its rate per format.
- **The compute ledger.** README.md's header names three kinds of fitter run beside the registered ones: the four
  development runs on the Intel, the registered runs on aifoundry1 (20:21, 20:22), and one development run on the lab host
  with term b's counts not yet complete. That last run's time was not logged, and its numbers for a, c1, c2, d and e equal
  the registered run's. The lane's result left it out.

## 4. Caveats and records the verifier asked for

- **Byte twins.** Among the 959 rows, 11 tiles carry 24 kind labels, inherited from M9's labels: E108's, E122's and E128's
  sign designs, and E115's and E127's tiles. So leaving one kind out can keep its byte twin in training. Here each twin group
  is held out as one kind ([`a2-checks-m10.json`](a2-checks-m10.json) › `byte_twins`):
  - floats B 0.2080 → 0.2082 W, and M10 (B+a+b) 0.1854 → 0.1856 W;
  - the 24 affected rows 0.179 → 0.185 W;
  - rule (a) floats −0.0063 [−0.0103, −0.0023] W and rule (b) −0.245 [−0.381, −0.110] W, both still entering;
  - int8 has no twins.

  Pool 8's designer avoids repeat tiles under new labels.
- **A1-1's sentence.** A2-3 corrects it. On pool 6's 88 rows, the frozen form's per-row errors in nested-m9.json equal B's
  machinery within the file's 1e-4 W rounding (max 5.0e-5 W, every sign agreeing).
- **§ 3a's E94.** The three random anchors are rows in E78 and E82 only.
- **The input list.** Besides the two hash lists, the re-run opened 288 data files under the tree. 62 are in neither the
  registration's 174 nor M10's 68: `docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json`,
  `tools/claims-v3/e145/predictions-e145.json` and 60 tile files of pools 6 and 7. Their sha256 as read is in
  `section7-m10.json` › `rerun.data_opened_not_in_either_hash_list`. Git shows each one unchanged between `e9367b66` and this
  note's commit, with a last change before the registration (`75802201` for 52, `d98d2e34` for 8, `e7cb1f21`, `18e5a7d2`;
  1-4 Nov). The next model's registration names them.
- **Where this fix ran.** On the Intel, as A2-3 item 5 allowed. All three lab hosts had sign-in checks pending from 21:13
  PST (retried at 21:22, 21:27 and 21:29), and the one other remote host has no numpy.
  - **The committed runs:** three local jobs of 17, 6 and 4 s at two threads, one at a time, 21:30:36-21:31:03 PST. Then
    `a2_checks_m10.py` ran once more at 21:31:41, after its twin groups' order was made deterministic (sorted); the same
    numbers, byte-identical on a repeat.
  - **Before them:** two development passes of `section7_m10.py`, one of `a2_checks_m10.py` and one predictor self-test
    (21:24-21:29), written only outside this directory. Their readings equal the committed ones.

## What this does to predicting power and heat

- **Power stands as reported, held out and not blind.**
  - floats 0.185 W over 737 rows;
  - pool 7's float rows 0.197 W (M9 as frozen, blind there, 0.358 W);
  - the S class 0.234 W;
  - int8 0.177 W;
  - pool 7's 48 kinds 0.205 / 0.187 W.

  § 7 confirms both power terms: the sessions' float levels are real (2-3 times their noise), and counting the single high
  bits is what fixes the S class.
- **Heat over minutes reverts to Q138(t)'s chain unscaled:** 0.493 °C rms on the nine large rises. The 1.032 gain (0.294 °C
  held out by session) rests on rises the chain already read well in one session, and it ruins that session's reading. It
  waits for a registered test that separates a session or day level from a gain.
- **The rest stands:** card 0's burst rise (0.2415 °C per board W) and the 4.5 s law (M7's form refitted, 0.233 °C).
- **Pool 8 is the blind test.**
