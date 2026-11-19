# E214 session a1c0-S1's data README, dated note 1 (Wed 18 Nov 2026; after the data verifier): check K's reproduce lines (post hoc)

*Written on aifoundry2 from about 21:50 PST on Wed 18 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e214d` of round Q220, after this directory's data verifier, `verify-e214d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived all seven committed E214 sessions, 622 of 622 runs, from their raw files: 183,450 numeric leaves bit-equal and 0 mismatches). It found one low README fix and one nit, in a1c1-S1 and a1c1-S3 (each answered by that directory's dated note 1) and none in this directory; and it noted that no E214 README gives a reproduce line for check K (its finding 3, information), which this note gives. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `3b3e4182`, 16:44:33 PST Wed 18 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E214.md`](../../../../tools/claims-v3/e214/E214.md)), **measured** (the session's records), **desk check** (this lane's runs of the committed code on the committed files) and **REPORTED** (verify-e214d's, not re-run here).*

## 1. Check K's reproduce lines (verify-e214d's finding 3, information)

The README's check K row ("K the kit's records and the claim": ALL PASS) has no line under "Reproduce", because `kit_e214.py` reads the data lane's work layout and not this directory. The layout is `<work>/<label>/session/`, `<work>/<label>/kit/build/BUILD-mms.json` (the kit's build record), `<work>/<label>/kit/run/preflight-load.txt` (its load record), `<work>/meta/<label>.json` for every E214 claim posted by then (the data lane's meta records), and the build records copied at the earlier releases (`<work>/<earlier label>/kit/build/BUILD-mms.json`). Every one of these is committed: `session/`, `build-record-aifoundry1.json`, `preflight-load-aifoundry1.txt` and `meta-e214-<label>.json` in each session's directory. For this session the only claim posted by its data commit is #12.2 (this one), and there is no earlier release (this is E214's first session). The sets matter for byte equality, because K4 lists the claims and the build records it read. From this directory:

```
K=$(mktemp -d)
mkdir -p "$K/meta" "$K/a1c0-S1/kit/build" "$K/a1c0-S1/kit/run"
ln -s "$PWD/session" "$K/a1c0-S1/session"
cp build-record-aifoundry1.json "$K/a1c0-S1/kit/build/BUILD-mms.json"
cp preflight-load-aifoundry1.txt "$K/a1c0-S1/kit/run/preflight-load.txt"
for t in a1c0-S1; do cp ../2026-11-18-e214-mmsweep3-$t/meta-e214-$t.json "$K/meta/$t.json"; done
python3 -I -B kit_e214.py "$K" a1c0-S1 ../../../../tools/claims-v3/e214/proposal/src --out kit.json --txt kit.txt
```

`kit.json` and `kit.txt` then equal `kit-e214-a1c0-S1.json` and `kit-e214-a1c0-S1.txt` byte for byte (desk check: this lane ran the layout for all seven sessions, 7 of 7 byte for byte, as verify-e214d had).

## 2. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
```

Then the lines of section 1. Check K's outputs equal `kit-e214-a1c0-S1.json` and `.txt` byte for byte when `python3` is `/usr/bin/python3` 3.12.3 (the JSON names the interpreter and its version).

**What stays as it was:** every line of the README. Its reproduce lines reproduce as printed: the checker (this claim's planning line, 52 W, equals the checker's built-in line for this card), the registered reducer, `spot_time_e208.py`, `window_e214.py`, `box_e214.py` and `never_e214.py` (verify-e214d's record, REPORTED).

SPDX-License-Identifier: Apache-2.0
