# E190's data README, dated note 1 (Sat 14 Nov 2026): the frozen scorer's output and note 1's report, each run on the data commit `a6fafba4`, committed beside it - R0 PASS, S1 PASS, S2 FAIL, S3 FAIL, S4 PASS, S5 PASS, S6 PASS, S7 DIFFERS, S8 NONE; the data verifier's own re-derivation agrees

*Beside [`README.md`](README.md), which stays as committed in `a6fafba4` (19,675 bytes, sha256 `bb79abaf...`), as does every file
[`SHA256SUMS`](SHA256SUMS) lists. Written on aifoundry2, desk only, by Q175's lane `scores-e190` on Sat 14 Nov 2026 (week 46), PST, after
E190's data verifier `verify-e190d` (Sat 14 Nov 2026, 14:43-15:06 PST), which found that the day holds as committed. The kit's step 13
([`KIT.md`](../../../../tools/claims-v3/e190/KIT.md), section 3) and the card-lane brief's dated note 1
([`CARD-LANE-BRIEF.md.dated-note-1.md`](../../../../tools/claims-v3/e190/CARD-LANE-BRIEF.md.dated-note-1.md), step 13) run the frozen scorer and
note 1's report only after the data commit and leave their outputs to a later commit. This note commits them byte for byte, with the scorer's
printed lines, and sets the data verifier's figures beside the scorer's. **No number, rule, verdict, forecast, band, threshold or gate reading
changes.***

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e190.json`](scores-e190.json) | the frozen scorer's output ([`score_e190.py`](../../../../tools/claims-v3/e190/score_e190.py), registered in `508d48d9`, unchanged): R0 and S1-S8, each cell's figures, errors and words, the ledger arm (reported) and the headline | 17,975 | `b819d885...` |
| [`scores-e190.txt`](scores-e190.txt) | the scorer's printed lines, copied byte for byte from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 770 | `d1e7e94b...` |
| [`report-e190-n1.txt`](report-e190-n1.txt) | note 1's REPORTED readings ([`report_e190_n1.py`](../../../../tools/claims-v3/e190/report_e190_n1.py) `day`): fp16's S1 and S4 also against the same-size reading, and the minion clock inside each cell's counted launches | 1,982 | `afbded8c...` |
| `README.md.dated-note-1.md` | this note | | |

[`SHA256SUMS-note1`](SHA256SUMS-note1) pins these four. With `SHA256SUMS` (432 files, unchanged), every file here is pinned but `README.md`
(its sha256 is above), `SHA256SUMS` and `SHA256SUMS-note1` themselves.

## 2. When, where and on which commit each ran

From the runbook's log and its capture of each call (kept outside the repository, in the card lane's runbook folder RB_OUT), and from the lab
clone's own log of its HEAD:

- **Step 13, the frozen scorer** ([`rb/s24_score_e190.sh`](../../../../tools/claims-v3/e190/rb/s24_score_e190.sh), the kit's): Fri 13 Nov 2026 at
  **16:33:24 PST**, on aifoundry2, in the lab clone with its HEAD at **`a6fafba4`**, the data commit (made at 16:33:10 PST), which stayed the
  clone's HEAD until the next commit (E183's data) at 16:43:38 PST. Its gates, each rc 0: the data directory committed (the last commit naming
  it: `a6fafba4`); the directory clean (no line); `SHA256SUMS` 432 of 432 entries OK; the history check, `HISTORY OK` (HEAD descends from the
  registration `508d48d9`, its subtree `4d4f7440`; 78 additions and nothing else under `tools/claims-v3/e190` since; no shadowing addition).
  Then `/usr/bin/python3 -I -B tools/claims-v3/e190/score_e190.py docs/reports/data/2026-11-13-e190-large-gemm/data-e190.json --out
  RB_OUT/scores-e190.json`: rc 0 in 0.1 s. `scores-e190.json` was last written at 16:33:24.453, the same instant as the runbook's capture of
  the scorer's printed lines. The scorer refuses unless `forecast-e190.json` is the registered one; its record's `forecast_sha256` is `7875c153...`,
  the registered sha256, and so is the file's at `a6fafba4`.
- **Step 13b, note 1's report** ([`rb/s25_report_e190_n1.sh`](../../../../tools/claims-v3/e190/rb/s25_report_e190_n1.sh), the kit's dated
  note 1): **16:33:46-16:33:48 PST**, the same clone at the same HEAD (its own first check printed `a6fafba4`):
  `/usr/bin/python3 -I -B tools/claims-v3/e190/report_e190_n1.py day --data docs/reports/data/2026-11-13-e190-large-gemm --scores
  RB_OUT/scores-e190.json --out RB_OUT/report-e190-n1.txt`: rc 0 in 2.1 s. The file was last written at 16:33:48 and is byte-equal to the
  call's capture.
- **The interpreter**, for both: `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`).
- **Re-run since, at the desk, on the committed bytes** (desk checks of code; each output byte-equal to the files above, and the printed
  lines to `scores-e190.txt`): by `verify-e190d`, in its own clone at `a6fafba4` (Sat 14 Nov 2026, 15:02 PST); and by this lane (15:15 PST)
  on the files the two programs read, taken from `a6fafba4` itself: the E190 tool folder and this directory, then the scorer's import chain
  (E136's, E119's and the kinds' module folders, the ledger v2's, and 12 more folders and files the run named: two module folders and ten
  committed data or desk files), each program run as the runbook ran it, in the round's CPU slot with no device node reachable.

## 3. The verdicts and the headline, as printed

[`scores-e190.txt`](scores-e190.txt), verbatim (the order S6 before S5 is the scorer's own):

```
R0 PASS
S1 PASS
S2 FAIL
S3 FAIL
S4 PASS
S6 PASS
S5 PASS
S7 DIFFERS
S8 NONE
A.fp32: t 0.2947 s (frozen 0.3878); J over idle 8.943 (frozen 10.002); J with the card at rest 15.911 (frozen 18.898)
A.fp16: t 0.1403 s (frozen 0.1411); J over idle 4.243 (frozen 4.068); J with the card at rest 7.579 (frozen 7.303)
A.int8: t 0.0691 s (frozen 0.0680); J over idle 1.304 (frozen 1.247); J with the card at rest 2.950 (frozen 2.807)
B.fp32: t 0.3177 s (frozen 0.4121); J over idle 5.332 (frozen 5.154); J with the card at rest 15.205 (frozen 18.792)
B.fp16: t 0.1527 s (frozen 0.1535); J over idle 2.512 (frozen 2.156); J with the card at rest 7.266 (frozen 7.235)
B.int8: t 0.0752 s (frozen 0.0736); J over idle 0.726 (frozen 0.530); J with the card at rest 3.070 (frozen 2.964)
```

Behind the words (`scores-e190.json`): S1 passes in 12 of 12 cells, S2 in 4 of 12, S3 in 4 of 12, S4 in 12 of 12 and S6 in 12 of 12; S5 in 3
of 3 arm A bursts; S7 reads SAME in fp16 only (below); S8 is a reading. The headline's measured figures are the README's first table; its
frozen ones are the registered points.

## 4. Beside verify-e190d's independent re-derivation

`verify-e190d` re-derived every figure from this directory's committed raw files with its own code: it imports nothing from the kit, and it
read `forecast-e190.json` at `508d48d9` (sha256 as registered). Each pair below is **the scorer / verify-e190d**, generated from
`scores-e190.json` and from the verifier's own output, not typed. They agree in every figure, at the precision shown and to 1e-9 beneath it,
except S7 int8's X and its t error (4.1).

| cell | runs | seconds a GEMM | J over idle | J with the card at rest | S2: J over idle against given | S3: J at rest against given | S1, S2, S3, S4, S6 |
|---|---|---|---|---|---|---|---|
| A fp32 burst | 4 | 0.2947 / 0.2947 | 8.943 / 8.943 | 15.911 / 15.911 | +17.68% / +17.68% | +9.22% / +9.22% | PASS FAIL FAIL PASS PASS / PASS FAIL FAIL PASS PASS |
| A fp16 burst | 4 | 0.1403 / 0.1403 | 4.243 / 4.243 | 7.579 / 7.579 | +4.85% / +4.85% | +2.66% / +2.66% | PASS PASS PASS PASS PASS / PASS PASS PASS PASS PASS |
| A int8 burst | 4 | 0.0691 / 0.0691 | 1.304 / 1.304 | 2.950 / 2.950 | +3.00% / +3.00% | +1.30% / +1.30% | PASS PASS PASS PASS PASS / PASS PASS PASS PASS PASS |
| B fp32 burst | 4 | 0.3177 / 0.3177 | 5.332 / 5.332 | 15.205 / 15.205 | +34.18% / +34.18% | +9.81% / +9.81% | PASS FAIL FAIL PASS PASS / PASS FAIL FAIL PASS PASS |
| B fp16 burst | 4 | 0.1527 / 0.1527 | 2.512 / 2.512 | 7.266 / 7.266 | +17.08% / +17.08% | +5.31% / +5.31% | PASS FAIL FAIL PASS PASS / PASS FAIL FAIL PASS PASS |
| B int8 burst | 4 | 0.0752 / 0.0752 | 0.726 / 0.726 | 3.070 / 3.070 | +33.90% / +33.90% | +6.37% / +6.37% | PASS FAIL FAIL PASS PASS / PASS FAIL FAIL PASS PASS |
| A fp32 sustained | 2 | 0.2940 / 0.2940 | 9.984 / 9.984 | 16.832 / 16.832 | +17.86% / +17.86% | +9.88% / +9.88% | PASS FAIL FAIL PASS PASS / PASS FAIL FAIL PASS PASS |
| A fp16 sustained | 2 | 0.1404 / 0.1404 | 4.723 / 4.723 | 8.155 / 8.155 | +5.73% / +5.73% | +3.24% / +3.24% | PASS PASS PASS PASS PASS / PASS PASS PASS PASS PASS |
| A int8 sustained | 2 | 0.0690 / 0.0690 | 1.388 / 1.388 | 3.068 / 3.068 | +4.77% / +4.77% | +2.10% / +2.10% | PASS PASS PASS PASS PASS / PASS PASS PASS PASS PASS |
| B fp32 sustained | 2 | 0.3184 / 0.3184 | 6.505 / 6.505 | 16.404 / 16.404 | +36.39% / +36.39% | +11.83% / +11.83% | PASS FAIL FAIL PASS PASS / PASS FAIL FAIL PASS PASS |
| B fp16 sustained | 2 | 0.1525 / 0.1525 | 3.023 / 3.023 | 7.830 / 7.830 | +17.81% / +17.81% | +6.20% / +6.20% | PASS FAIL FAIL PASS PASS / PASS FAIL FAIL PASS PASS |
| B int8 sustained | 2 | 0.0751 / 0.0751 | 0.824 / 0.824 | 3.185 / 3.185 | +27.04% / +27.04% | +5.83% / +5.83% | PASS FAIL FAIL PASS PASS / PASS FAIL FAIL PASS PASS |

J with the card at rest against its frozen band (reported, not a rule): INSIDE in all 12 cells, by both.

| S5, arm A bursts | die start, °C | die maximum, °C | E136's law, °C | error, °C | verdict |
|---|---|---|---|---|---|
| fp32 | 52.20 / 52.20 | 58.00 / 58.00 | 56.236 / 56.236 | +1.764 / +1.764 | PASS / PASS |
| fp16 | 52.87 / 52.87 | 58.00 / 58.00 | 57.362 / 57.362 | +0.638 / +0.638 | PASS / PASS |
| int8 | 52.98 / 52.98 | 56.00 / 56.00 | 55.965 / 55.965 | +0.035 / +0.035 | PASS / PASS |

| S7, per format | X | t error | J over idle error | verdict |
|---|---|---|---|---|
| fp32 | 1.0779171 / 1.0779171 | +0.0265% / +0.0265% | +15.695% / +15.695% | DIFFERS / DIFFERS |
| fp16 | 1.0846187 / 1.0846187 | +0.3188% / +0.3188% | +11.666% / +11.666% | SAME / SAME |
| int8 | 1.0888228 / 1.0888421 | -0.0785% / -0.0803% | +30.844% / +30.844% | DIFFERS / DIFFERS |

- **S8**: h 0.1353 / 0.1353; q 1.0499 / 1.0499 (q_N 0.9991 and q_S 1.3747, by both): NONE / NONE.
- **R0**: PASS / PASS. Every check of C read exact or approx: the scorer's 18 check results (12 approx, 6 exact), and the verifier's own count
  over every check line, 174 (116 approx, 58 exact); the smoke's cycles an op 0.756-1.012 of the point (inside 50-250%), by both.
- **The ledger arm, reported, never a rule** (`scores-e190.json`, `ledger_arm_reported`: card 1's bursts priced by the ledger v2 at their
  measured seconds and starting die): J over idle fp32 -49.8%, fp16 -24.8%, int8 -26.7%; J with the card at rest -25.8%, -10.2%, -7.9%. The
  verifier re-checked the scorer's arithmetic on it only; it did not re-run the ledger v2 (NOT RUN).
- **Note 1's report** (`report-e190-n1.txt`; REPORTED, never a verdict): every fp16 cell is INSIDE the same-size reading as well as its
  frozen band, and the highest clock in the counted launches is 800 MHz in every arm A cell and 600 MHz in every arm B cell, with 0 arm B
  samples outside 590-610 MHz. The verifier checked its 4 fp16 lines and 12 clock lines against its own figures: the same.

### 4.1 The differences, each a reading choice that changes no verdict

1. **S7 int8's X** (X = T600 / T800, from arm A's own launches at 600 and at 800 MHz). The kit's reducer, for the scorer, takes each T as
   the mean over the launches of each launch's wall time per iteration (launch index 0 or more, check ok, wall at least 0.1 s); the verifier
   pools the wall over the iterations of the same launches: X 1.0888228 / 1.0888421, so the t error -0.0785% / -0.0803%. With arm A's calibration launches counted too, X 1.0901848 and -0.2033%. E190.md section 6
   says "X arm A's own T600 / T800" and names no estimator. Every reading leaves int8's S7 line DIFFERS (its J over idle error, +30.844% by
   both, decides it); fp32 and fp16 do not move.
2. **The rest window.** The scorer reads the 5 s before a run's first process; the verifier, the last 5 s of the rest read, which ends 0-1 ms
   earlier. One run differs, arm A's `04-S1-sus-fp32`: 49 samples / 50. Its p_rest and die start are the same.

### 4.2 A reading of the registration's words beside the frozen code (this lane's; post hoc)

E190.md section 6 says its rules are "scored on the bursts unless named", and it reports "each sustained cell's errors" beside them; the frozen
scorer (and the verifier with it) counts S1, S2 and S3 over all 12 cells. Over the six bursts alone the words are the same: S1 6 of 6, S2 2 of
6, S3 2 of 6.

## 5. Erratum in README.md's prose

- [`README.md`](README.md) lines 61-62 (its tables are exact): "16.5 W over idle" for arm B fp16 reads **16.4 W** (47.5825 − 31.135 = 16.4475 W), its frozen "14.1" reads **14.0** (14.0483 W), and "30.4 W over idle" for arm A fp32 reads **30.3 W** (53.9925 − 23.64375 = 30.34875 W): each was rounded twice, and the README stays as committed.

## 6. Post hoc context: arm B's closing power state (the README's departure 5)

The verifier's count over the lab's committed config reads (Sat 14 Nov 2026; post hoc, not re-counted here): of the 420 reads named for
aifoundry1's card 1 (499-500 mV), 376 read `managed_power`; 17 earlier card-1 experiments (E104-E172, 1-5 Nov 2026) read `low_power` at a
start and `managed_power` at an end; and E184, card 1's previous session (Sun 8 Nov 2026), read `managed_power` in all 6 of its reads. The
power state is read, never set: nothing was set on the day.

## 7. Labels

**Measured**: the sessions' figures and every cell value. **Registered**: E190.md, `forecast-e190.json`, the rules, the bands and the
points. The verdicts are the frozen scorer's own output on the committed data; note 1's readings are REPORTED. The verifier's figures and
both re-runs are **desk checks of code**. Section 4.2 and section 6 are **post hoc**. This lane reached no box, opened no device and changed
no committed file.
