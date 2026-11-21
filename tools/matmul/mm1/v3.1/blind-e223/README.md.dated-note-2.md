# blind-e223: dated note 2, dated amendment 1 as landed and verify-blind-e223's findings on it

*Sat 21 Nov 2026, Pacific time. Written by the lab's lane land-blind-e223 (round Q239) at 08:46 PST for this folder's second commit, after verify-blind-e223 held the lab's blind test of E223, with this amendment, WITH FIXES (07:55-08:31 PST). This folder's `README.md` is decl-e223's, written before the amendment, so this note is also the amendment's README. Desk only: no card, no device, no simulator. Interpreter `/usr/bin/python3` 3.12.3 (-I -B), standard library only, single-threaded. This note changes no file of the folder and no number, forecast, rule or verdict; nothing in it is a measurement.*

## What amendment 1 is

decl-e223 froze the lab's blind test of E223 at 02:22:09 PST without two of Q238's mask candidates, because neither had a matching posted freeze line when it read them. By the declaration's own rule, a candidate qualifying after that read joins only by a dated amendment hashed and posted before E223's first datum. amend-e223 (round Q239a) wrote that amendment. Its files sit beside the declaration and edit none of its files. It adds three REPORTED columns that decide nothing:

- **'MM1-v3.2 + mesh'**: Q238's mask-mesh, FROZEN.txt `487188c7...`, whose freeze line was posted at 02:23:42 PST;
- **'MM1-v3.2 + AF4 + mesh'**: the same term with AF4, by construction and with no refit. It equals mesh at every E223 case, because AF4 acts only on gemmLnc points and E223 runs none;
- **'MM1-v3.2 + mask-ceiling'**: a REPORTED reference, never a model candidate. It is Q238's mask-ceiling at its posted FROZEN.txt `1649ba5b...` (02:21:44 PST).

They are scored exactly as the declaration scores 'MM1-v3.2 + posimb-mask':
- on the placement class (PLACE, 421 cases), each against MM1-v3.2 on H1, H2, H3 and H5 by the exact sign test, per card and pooled;
- the subset cases (513), blind-e221's MASK class (MASKE221, 353) and each held-out set, REPORTED.

Some parts read NO DATA by construction, as the amendment declares. The reference forecasts no counter mean, so its H2 is MM1-v3.2's. E1 (W given t) is MM1-v3.2's for all three columns.

## What is committed here

- **The amendment's land, byte for byte**: 12 files and `SHA256SUMS-amend1` (sha256 `21a6b1a5e8cfe970...`, 12 of 12 OK). It was written at 02:40:01 PST on Sat 21 Nov, after the amendment (hashed 02:36:29), its nominal forecasts (made 02:36:41-02:37:56, written 02:38:24, hashed 02:39:02) and its FROZEN.txt (02:39:02, landed here as `FROZEN-amend1.txt`), and before its post and any E223 session.
  - The files: `DECLARED-blind-e223-amendment-1.md` and `.json`, `forecasts-nominal-e223-amend1.csv` and `.json`, `FROZEN-amend1.txt`, and its 7 scripts under `scripts/amend1/`, byte-equal to the scripts as run.
  - No path collides with the declaration's files, committed just before.
- **The verification.** verify-blind-e223 checked the amendment beside the declaration:
  - its FROZEN.txt equals the posted line, its 9 file lines re-hash 9 of 9, every listed file was written before the post, and its inputs re-hash 33 of 33;
  - the work copy its forecasts were made from equals GitHub main blob for blob, 3,270 of 3,270 files;
  - its own caller re-made the amendment's nominal forecasts bit for bit, within the 82,705 nominal fields equal to the frozen files; the scopes at the nominal footing are as declared (mesh 513 cases, the reference 454);
  - the twin keys it re-derived from the landed point records equal `twin-keys-amend1.json`;
  - the land is new files only. Its fix to it is finding 1, below.
- **This note adds seven new files**, and `SHA256SUMS-note2` lists the sha256 of six. It edits no file:
  - `README.md.dated-note-2.md`, this note;
  - `SHA256SUMS-note2`;
  - the five files that FROZEN-amend1.txt names and the land left out, byte for byte from amend-e223's lane folder (finding 1).

## The freeze line, checked on this folder

Posted on the coordination Discussion as #16.1.1.1.1 (2026-11-21 02:40:33 PST in the round's record; 02:40:33.134 PST by the post's own stamp) as E223's go, the reply to the declaration's #16.1.1.1. E223's three aifoundry2 card 0 sessions sent their first card commands 10.103, 50.092 and 87.981 minutes after it, each under a claim posted after both freeze posts. So all three are BLIND for the amendment's columns too.

- `FROZEN-amend1.txt` `ab32a8d5364ed7a3416162b2e2d23343807c74e24bda79e4c9f2d040035050b2`: the posted FROZEN.txt sha256, equal here.
- The post names the four frozen files by their first 8 hex digits, and FROZEN-amend1.txt gives each in full. Both agree with the file here:
  - `DECLARED-blind-e223-amendment-1.md` `2c204ce441405dc7305a1c25421be51b099d2cb01a3f2c030ed9e936123f788f`;
  - `DECLARED-blind-e223-amendment-1.json` `5f5f69bfd6f838ccd380b5cd4e6a5781fffff4a1132e25e2f93c53daadb7151f`;
  - `forecasts-nominal-e223-amend1.csv` `938869054af4efdf50f13c1504351134edfa59089ecda0d514d6eab74119c481`;
  - `forecasts-nominal-e223-amend1.json` `d9a9074eb6558488cf91f15e95dadc2af8b2e411c62a66d8272ec21a8ba6bf80`.

## Each line of FROZEN-amend1.txt and where it is here

FROZEN-amend1.txt names 9 files by sha256, under amend-e223's own folder names. Their places here follow the declaration's map (`work/stepN/` is `inputs/stepN/`) and the amendment's own `scripts/amend1/`:
- `work/stepN/` is `inputs/amend1/stepN/`;
- `logs/` is `logs/amend1/`. The declaration's `logs/step2-sha256.txt` is decl-e223's own step log, another file.

| line | sha256 | listed as | here | check |
|---|---|---|---|---|
| 3 | `2c204ce441405dc7...` | `DECLARED-blind-e223-amendment-1.md` | `DECLARED-blind-e223-amendment-1.md` | byte-equal |
| 4 | `5f5f69bfd6f838cc...` | `DECLARED-blind-e223-amendment-1.json` | `DECLARED-blind-e223-amendment-1.json` | byte-equal |
| 5 | `938869054af4efdf...` | `forecasts-nominal-e223-amend1.csv` | `forecasts-nominal-e223-amend1.csv` | byte-equal |
| 6 | `d9a9074eb6558488...` | `forecasts-nominal-e223-amend1.json` | `forecasts-nominal-e223-amend1.json` | byte-equal |
| 8 | `85e94dfaf156ce09...` | `logs/step2-sha256.txt` | `logs/amend1/step2-sha256.txt` | byte-equal, added by this note |
| 9 | `cbb265eaa0b47718...` | `logs/step3-sha256.txt` | `logs/amend1/step3-sha256.txt` | byte-equal, added by this note |
| 10 | `a6627d8815f05e15...` | `work/step3/fc-amend1.json` | `inputs/amend1/step3/fc-amend1.json` | byte-equal, added by this note |
| 11 | `b69ba1fe730dfb0c...` | `work/step2/twin-keys-amend1.json` | `inputs/amend1/step2/twin-keys-amend1.json` | byte-equal, added by this note |
| 12 | `80b4b03f7f2cfe19...` | `work/step1/frozen-checks.json` | `inputs/amend1/step1/frozen-checks.json` | byte-equal, added by this note |

- **All 9 hold their listed bytes here**, and in amend-e223's lane folder all 9 still equal their lines. The five added files were last written from 02:29:01 to 02:39:02 PST, by the freeze.
- **The two step logs**, now at `logs/amend1/`, name the amendment's md and json (step 2) and its nominal forecasts (step 3). All 4 lines equal the files here.
- **The freeze records named in the comment lines** are equal to files already in the lab:
  - line 1 names decl-e223's FROZEN.txt `5551c2d7...`, which is this folder's `FROZEN.txt`;
  - line 13 names mask-mesh's `487188c7...` and mask-ceiling's posted `1649ba5b...` and on-disk `bf6e2d96...`. All three are on main: `tools/matmul/mm1/v3.4-cands/mesh/FROZEN.txt`, `tools/matmul/mm1/v3.4-cands/mask-ceiling/FROZEN.txt.superseded-022113` and `.../mask-ceiling/FROZEN.txt`. The amendment's own copies of them, which FROZEN-amend1.txt does not name, are not landed.

## verify-blind-e223's findings on this folder, answered

1. **Five frozen files missing (finding 1, low).** The land carried 4 of the 9 files its FROZEN.txt names. So 5 freeze lines could not be re-hashed from the landed tree, and the amended columns' twin keys, a declared input, were not in it.
   - The five are here now, byte for byte, at the paths in the table, and `sha256sum -c SHA256SUMS-note2` checks them there.
   - `inputs/amend1/step2/twin-keys-amend1.json` holds the amended columns' twin keys.
   - `inputs/amend1/step3/fc-amend1.json` is the full record of the amendment's nominal forecasts.
   - `inputs/amend1/step1/frozen-checks.json` is the amendment's check of every frozen file it read before writing.
   - This note is the short README for the amendment that the verifier asked for.
2. **The round's strict public-text scan (finding 2, low).** The scan (`pubscan_strict.py`, sha256 `76ea74d9...`) finds 2 hits in the amendment's land. Both are false positives: a common word for a folder's top level (said of the lane folder), which the scan's pattern for the administrator account also matches, in `scripts/amend1/s02_amend.py` line 3 and `scripts/amend1/s04_write.py` line 4.
   - Beside them, `DECLARED-blind-e223-amendment-1.json` lines 41 and 42 quote the same two posts as the declaration: E223's proposal (#16) and the kit's push to aifoundry2 (#16.1.1). They hold the model session's kit folder by its home-relative name, the prefix `eb5478f6` of its sealed forecast's digest and the model session's own two-word name for its box. All three are already public in E223's registration on main (`tools/claims-v3/e223/E223.md`), and no number of the sealed forecast appears here.
   - They stay as they are. The amendment is frozen and posted, and its scripts are the bytes as run.
   - This note and the five added files add no hit of that scan.

## The amendment's own gap, for the record

amend-e223 returned FROZEN WITH GAPS for one reason: mask-ceiling's two freeze files.
- The line posted for it at 02:21:44 PST (`1649ba5b...`) names that lane's 02:21:13 write, and that lane rewrote its FROZEN.txt at 02:22:21 (`bf6e2d96...`).
- The amendment names the posted line. Every file its reference forecasts call is equal under both records, so its forecasts are the same under either line. `inputs/amend1/step1/frozen-checks.json` lists the five called files: `mask_ceiling.py`, `params-mask-ceiling.json`, `scripts/r_common.py`, `scripts/rf_core.py` and `scripts/f01_features.py`.
- The round's record says the corrected line (`bf6e2d96...`) was posted before any E223 datum.

## What the verifier did not check

- The Discussion posts' own text. It read the round's records and the watcher's stamps.
- **NOT RUN:** any reading of the model session's sealed forecast.

SPDX-License-Identifier: Apache-2.0
