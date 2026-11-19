# E214 session a1c1-S1's data README, dated note 1 (Wed 18 Nov 2026; after the data verifier): the checker's reproduce line needs the claim's planning line, `--plan-w 57.3`; the die reference reads 45.4 C; check K's reproduce lines (post hoc)

*Written on aifoundry2 from about 21:50 PST on Wed 18 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e214d` of round Q220, after this directory's data verifier, `verify-e214d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived all seven committed E214 sessions, 622 of 622 runs, from their raw files: 183,450 numeric leaves bit-equal and 0 mismatches). It found one low README fix and one nit, both in this directory (its findings 1 and 2); and it noted that no E214 README gives a reproduce line for check K (its finding 3, information), which this note gives. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `f7f3257c`, 17:28:54 PST Wed 18 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E214.md`](../../../../tools/claims-v3/e214/E214.md)), **measured** (the session's records), **desk check** (this lane's runs of the committed code on the committed files) and **REPORTED** (verify-e214d's, not re-run here).*

## 1. The correction: the checker's line needs `--plan-w 57.3` (verify-e214d's finding 1, low)

**What README.md says** (its section "Reproduce", line 81), verbatim:

```
python3 -I -B check_session_e214.py session a1c1 ../../../../tools/claims-v3/e214/proposal/src --out checks.json --txt checks.txt
```

**So the line should read:**

```
python3 -I -B check_session_e214.py session a1c1 ../../../../tools/claims-v3/e214/proposal/src --plan-w 57.3 --out checks.json --txt checks.txt
```

**Why.** Check C9 compares every scheduled run's and smoke arm's planned peak with the planning line that the claim names for its own session. The checker's only built-in line for aifoundry1 card 1 is E212's 66.6 W (`check_session_e214.py` lines 28-29 and 50), and `--plan-w` sets the claim's own line. This session's claim, #12.3 (16:46:16 PST), names 57.3 W: "every arm planned at or under 57.3 W with the 75 W live stop" (README note 2). The data lane passed that line as `--plan-w 57.3`, read from its record of the claim (committed here as `meta-e214-a1c1-S1.json`, `plan.plan_w`), so the committed `checks-e214-a1c1-S1.json` and `.txt` read 57.3. The README's line was printed without the flag. E214's other sessions reproduce as printed because their claims' lines equal the checker's built-in ones: 52 W on card 0, and 66.6 W in a1c1-S2 and a1c1-S4. a1c1-S3 (63.7 W) has the same fix in its own dated note 1.

**What this lane ran** (desk check, in a copy of GitHub main's tree at `0e95201d`, with outputs written outside the copy):

- The line as printed: rc 0. Its C9 reads `line_w 66.6`, still labelled `line_from the claims' planning line`, though 66.6 W is E212's line and not this claim's. So its outputs differ from the committed files in that value alone: one line of the JSON (`"line_w"`) and one line of the `.txt` (the C9 line).
- The line with `--plan-w 57.3`: rc 0. Both outputs equal `checks-e214-a1c1-S1.json` and `checks-e214-a1c1-S1.txt` byte for byte.
- C9 passes either way: the highest planned peak of the 89 read is 57.3 W, and the measured board peak 53.95 W. The verdict "ALL PASS (C0-C9)" stands.

## 2. The die reference reads 45.4 C (verify-e214d's finding 2, nit)

**What README.md says** (its section "The reduction", line 53): "die reference 45.38428571428572 C". **It should read: "die reference 45.4 C".**

**Why.** By the registered rule (the docstring of `reduce_mms.py`, "THE DIE-START CORRECTION"), the die reference is the session's median start die over the runs read for energy. Here 86 runs are read. Their middle two start dies are 45.34 C and 45.43 C (45.42857142857143 in floating point), and the mean of the two is 45.38428571428572 C in floating point. That is the value `data-e214-a1c1-S1.json` holds as `die_ref_c`, unchanged. The reducer's own table, `reduce-e214-a1c1-S1.txt`, prints it as "die ref 45.4 C"; the README printed the raw float. The other six READMEs show one decimal only because their medians are short floats (43.0, 43.0, 44.0, 46.0, 46.1 and 47.0 C). Desk check: this lane's own median of the 86 start dies, read from `data-e214-a1c1-S1.json` by the rule's words, equals `die_ref_c` exactly.

## 3. Check K's reproduce lines (verify-e214d's finding 3, information)

The README's check K row ("K the kit's records and the claim": ALL PASS) has no line under "Reproduce", because `kit_e214.py` reads the data lane's work layout and not this directory. The layout is `<work>/<label>/session/`, `<work>/<label>/kit/build/BUILD-mms.json` (the kit's build record), `<work>/<label>/kit/run/preflight-load.txt` (its load record), `<work>/meta/<label>.json` for every E214 claim posted by then (the data lane's meta records), and the build records copied at the earlier releases (`<work>/<earlier label>/kit/build/BUILD-mms.json`). Every one of these is committed: `session/`, `build-record-aifoundry1.json`, `preflight-load-aifoundry1.txt` and `meta-e214-<label>.json` in each session's directory. For this session the claims posted by its data commit are #12.2 (a1c0-S1) and #12.3 (this one), and the one earlier release is a1c0-S1's. The sets matter for byte equality, because K4 lists the claims and the build records it read. From this directory:

```
K=$(mktemp -d)
mkdir -p "$K/meta" "$K/a1c1-S1/kit/build" "$K/a1c1-S1/kit/run"
ln -s "$PWD/session" "$K/a1c1-S1/session"
cp build-record-aifoundry1.json "$K/a1c1-S1/kit/build/BUILD-mms.json"
cp preflight-load-aifoundry1.txt "$K/a1c1-S1/kit/run/preflight-load.txt"
for t in a1c0-S1 a1c1-S1; do cp ../2026-11-18-e214-mmsweep3-$t/meta-e214-$t.json "$K/meta/$t.json"; done
for t in a1c0-S1; do mkdir -p "$K/$t/kit/build" && cp ../2026-11-18-e214-mmsweep3-$t/build-record-aifoundry1.json "$K/$t/kit/build/BUILD-mms.json"; done
python3 -I -B kit_e214.py "$K" a1c1-S1 ../../../../tools/claims-v3/e214/proposal/src --out kit.json --txt kit.txt
```

`kit.json` and `kit.txt` then equal `kit-e214-a1c1-S1.json` and `kit-e214-a1c1-S1.txt` byte for byte (desk check: this lane ran the layout for all seven sessions, 7 of 7 byte for byte, as verify-e214d had).

## 4. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B check_session_e214.py session a1c1 ../../../../tools/claims-v3/e214/proposal/src --plan-w 57.3 --out checks.json --txt checks.txt
```

Then the lines of section 3. The checker's outputs equal `checks-e214-a1c1-S1.json` and `.txt`, and check K's equal `kit-e214-a1c1-S1.json` and `.txt`, byte for byte when `python3` is `/usr/bin/python3` 3.12.3 (both JSON files name the interpreter and its version).

**What stays as it was:** every other line of the README. Its reproduce lines other than the checker's reproduce as printed: the registered reducer, `spot_time_e208.py`, `window_e214.py`, `box_e214.py` and `never_e214.py` (verify-e214d's record, REPORTED).

SPDX-License-Identifier: Apache-2.0
