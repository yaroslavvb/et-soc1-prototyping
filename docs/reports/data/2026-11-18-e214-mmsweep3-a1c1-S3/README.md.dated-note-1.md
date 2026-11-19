# E214 session a1c1-S3's data README, dated note 1 (Wed 18 Nov 2026; after the data verifier): the checker's reproduce line needs the claim's planning line, `--plan-w 63.7`; check K's reproduce lines (post hoc)

*Written on aifoundry2 from about 21:50 PST on Wed 18 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e214d` of round Q220, after this directory's data verifier, `verify-e214d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived all seven committed E214 sessions, 622 of 622 runs, from their raw files: 183,450 numeric leaves bit-equal and 0 mismatches). It found one low README fix, in this directory and in a1c1-S1 (its finding 1), and one nit, in a1c1-S1 alone (its finding 2); and it noted that no E214 README gives a reproduce line for check K (its finding 3, information), which this note gives. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `9ac3c338`, 20:19:53 PST Wed 18 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E214.md`](../../../../tools/claims-v3/e214/E214.md)), **measured** (the session's records), **desk check** (this lane's runs of the committed code on the committed files) and **REPORTED** (verify-e214d's, not re-run here).*

## 1. The correction: the checker's line needs `--plan-w 63.7` (verify-e214d's finding 1, low)

**What README.md says** (its section "Reproduce", line 81), verbatim:

```
python3 -I -B check_session_e214.py session a1c1 ../../../../tools/claims-v3/e214/proposal/src --out checks.json --txt checks.txt
```

**So the line should read:**

```
python3 -I -B check_session_e214.py session a1c1 ../../../../tools/claims-v3/e214/proposal/src --plan-w 63.7 --out checks.json --txt checks.txt
```

**Why.** Check C9 compares every scheduled run's and smoke arm's planned peak with the planning line that the claim names for its own session. The checker's only built-in line for aifoundry1 card 1 is E212's 66.6 W (`check_session_e214.py` lines 28-29 and 50), and `--plan-w` sets the claim's own line. This session's claim, #12.7 (19:37:13 PST), names 63.7 W: "every run planned at or under 63.7 W with the 75 W live stop" (README note 2). The data lane passed that line as `--plan-w 63.7`, read from its record of the claim (committed here as `meta-e214-a1c1-S3.json`, `plan.plan_w`), so the committed `checks-e214-a1c1-S3.json` and `.txt` read 63.7. The README's line was printed without the flag. E214's other sessions reproduce as printed because their claims' lines equal the checker's built-in ones: 52 W on card 0, and 66.6 W in a1c1-S2 and a1c1-S4. a1c1-S1 (57.3 W) has the same fix in its own dated note 1.

**What this lane ran** (desk check, in a copy of GitHub main's tree at `0e95201d`, with outputs written outside the copy):

- The line as printed: rc 0. Its C9 reads `line_w 66.6`, still labelled `line_from the claims' planning line`, though 66.6 W is E212's line and not this claim's. So its outputs differ from the committed files in that value alone: one line of the JSON (`"line_w"`) and one line of the `.txt` (the C9 line).
- The line with `--plan-w 63.7`: rc 0. Both outputs equal `checks-e214-a1c1-S3.json` and `checks-e214-a1c1-S3.txt` byte for byte.
- C9 passes either way: the highest planned peak of the 94 read is 63.7 W, and the measured board peak 59.48 W. The verdict "ALL PASS (C0-C9)" stands.

## 2. Check K's reproduce lines (verify-e214d's finding 3, information)

The README's check K row ("K the kit's records and the claim": ALL PASS) has no line under "Reproduce", because `kit_e214.py` reads the data lane's work layout and not this directory. The layout is `<work>/<label>/session/`, `<work>/<label>/kit/build/BUILD-mms.json` (the kit's build record), `<work>/<label>/kit/run/preflight-load.txt` (its load record), `<work>/meta/<label>.json` for every E214 claim posted by then (the data lane's meta records), and the build records copied at the earlier releases (`<work>/<earlier label>/kit/build/BUILD-mms.json`). Every one of these is committed: `session/`, `build-record-aifoundry1.json`, `preflight-load-aifoundry1.txt` and `meta-e214-<label>.json` in each session's directory. For this session the claims posted by its data commit are #12.2 (a1c0-S1), #12.3 (a1c1-S1), #12.4 (a1c0-S2), #12.5 (a1c1-S2), #12.6 (a1c0-S3) and #12.7 (this one), and the earlier releases are those of a1c0-S1, a1c1-S1, a1c0-S2, a1c1-S2 and a1c0-S3. The sets matter for byte equality, because K4 lists the claims and the build records it read. From this directory:

```
K=$(mktemp -d)
mkdir -p "$K/meta" "$K/a1c1-S3/kit/build" "$K/a1c1-S3/kit/run"
ln -s "$PWD/session" "$K/a1c1-S3/session"
cp build-record-aifoundry1.json "$K/a1c1-S3/kit/build/BUILD-mms.json"
cp preflight-load-aifoundry1.txt "$K/a1c1-S3/kit/run/preflight-load.txt"
for t in a1c0-S1 a1c1-S1 a1c0-S2 a1c1-S2 a1c0-S3 a1c1-S3; do cp ../2026-11-18-e214-mmsweep3-$t/meta-e214-$t.json "$K/meta/$t.json"; done
for t in a1c0-S1 a1c1-S1 a1c0-S2 a1c1-S2 a1c0-S3; do mkdir -p "$K/$t/kit/build" && cp ../2026-11-18-e214-mmsweep3-$t/build-record-aifoundry1.json "$K/$t/kit/build/BUILD-mms.json"; done
python3 -I -B kit_e214.py "$K" a1c1-S3 ../../../../tools/claims-v3/e214/proposal/src --out kit.json --txt kit.txt
```

`kit.json` and `kit.txt` then equal `kit-e214-a1c1-S3.json` and `kit-e214-a1c1-S3.txt` byte for byte (desk check: this lane ran the layout for all seven sessions, 7 of 7 byte for byte, as verify-e214d had).

## 3. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B check_session_e214.py session a1c1 ../../../../tools/claims-v3/e214/proposal/src --plan-w 63.7 --out checks.json --txt checks.txt
```

Then the lines of section 2. The checker's outputs equal `checks-e214-a1c1-S3.json` and `.txt`, and check K's equal `kit-e214-a1c1-S3.json` and `.txt`, byte for byte when `python3` is `/usr/bin/python3` 3.12.3 (both JSON files name the interpreter and its version).

**What stays as it was:** every other line of the README. Its reproduce lines other than the checker's reproduce as printed: the registered reducer, `spot_time_e208.py`, `window_e214.py`, `box_e214.py` and `never_e214.py` (verify-e214d's record, REPORTED).

SPDX-License-Identifier: Apache-2.0
