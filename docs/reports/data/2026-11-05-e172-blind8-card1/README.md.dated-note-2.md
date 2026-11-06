# E172's data README, dated note 2: E172's C checked again from a fresh reference cache. All 3,470 C records re-derived, the four passes' 3,410 and the smoke's 60, equal the committed check byte for byte. P8-KC's own count is 1,900 of 1,900, where the README's P8-KC row quotes the check's 3,470 (no number, rule or verdict changes)

*Written Thu 5 Nov 2026 (week 45), about 16:35-17:00 PST, on the Intel, desk only (no card, no device command, no lab box, no post in
the lab's channel, no Modal, no archive). It answers the pool-8 card day's critic, `next` **rank 7**: "E172's four passes checked for C
again from a fresh cache (3,410 launches)", because "P8-KC on card 1 is the one data claim of the day that no verifier re-derived in full".
The critic itself had checked a sample, 320 of p17210's 860 launches, identical to the committed check. [`README.md`](README.md) (lab
`b3255af1`) and [dated note 1](README.md.dated-note-1.md) (`04159d14`) stay as committed, and this note sits beside them. Everything here is
**post hoc**. **No number, rule, line or verdict changes**, and no data file is touched. The evidence is
[`posthoc-note2-e172.txt`](posthoc-note2-e172.txt), written by [`posthoc_note2_e172.py`](posthoc_note2_e172.py), which reads this
directory as committed and the re-check's output. The run answers item 6 of the kinds page's section 11
([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), with items 8
and 9, as the README says.*

## 1. What ran

- **The registered checker, unchanged, as [`collect_e172.sh`](../../../../tools/claims-v3/e172/collect_e172.sh) step 1 runs it.**
  - The checker is Q139(k)'s [`ccheck.py`](../../../../tools/claims-v3/ccheck/ccheck.py) `check`, sha256 `2f806fe6…`. That is the file
    this directory's `code.sha256` records and the one E163's collection recorded.
  - It ran with `--jobs 2` and a **new, empty `--cache`** (0 entries before, 1,255 after). The engine it pins,
    `rtl-sim/fma_toggle_v2/accum.c` (sha256 `dc47efbc…`), was built afresh into that cache, and every reference C was computed from
    nothing.
- **Its input** was the C log of every session that `ccsessions_p8.listed_sessions` lists for E172. Each was decompressed from this
  directory's committed `c-log.jsonl.gz` as `c-log-<session>.jsonl`, in the list's order:
  - the smoke `p17201`, 60 C records;
  - then `p17210` (860), `p17211` (850), `p17212` (840) and `p17213` (860).

  The four passes are rank 7's 3,410. The smoke's 60 ran in the same call, so the whole committed check could be compared with its
  re-derivation, file against file.
- **Where and when:** a clean clone of the lab's main at `04159d14`, with `/usr/bin/python3` 3.9.6. It was one local job at nice 10 with
  the checker's two worker threads (two of the round's CPU slots held for them), **16:35:35-16:48:03 PST (748 s)**, rc 0. The comparison
  ran at 16:48:17-16:48:18.

## 2. What it re-derives

| | the committed check (`ccheck/ccheck-session.json.gz`, `ccheck-session.txt`) | re-derived from a fresh cache | the same? |
|---|---|---|---|
| **the four passes**, p17210-p17213 | 3,410 C records, PASS 3,410 (860 / 850 / 840 / 860; fp32 1,420, fp16 990, int8 1,000) | 3,410, PASS 3,410 | **every record identical in all 22 fields** (66 distinct tiles) |
| the smoke, p17201 | 60, PASS 60 (fp32 36, fp16 12, int8 12) | 60, PASS 60 | every record identical (7 distinct tiles) |
| **the whole check**, five logs | 3,470, PASS 3,470 (fp32 1,456, fp16 1,002, int8 1,012); no ROUNDING, UNMODELLED or FAIL; no broken record | the same summary | **the `--out` file byte-identical**: 3,523,730 bytes, sha256 `089ff1d0…` both. The printed output is byte-identical too (3,471 lines) |
| **P8-KC** (`score_p8_600.c_status` and `score_p8_600_v2.kc_of`, unchanged, on the re-check) | `scored.json` › `primary.rules.P8-KC`: PASS, **1,900 of 1,900**, none excluded, none unmeasured | PASS, 1,900 of 1,900, none excluded, none unmeasured | equal |
| the C-session gate (`ccsessions_p8.check`, unchanged, no `--since`) | `scored.json` › `c_sessions`: ok, 5 of 5 sessions OK, stop-path test OK | CCHECK-DONE; 5 of 5 CCSESSION-OK, each judging every launch its log holds; STOPTEST-OK; FINISHED | equal, 5 of 5 records |

**So E172's check of C holds in full from a fresh cache.** Its references depend on no cache entry, and the critic's sample (320 of
p17210's 860) is now the whole set.

## 3. What each count counts

The two counts the records quote are not the same set ([`posthoc-note2-e172.txt`](posthoc-note2-e172.txt) part 5; every runs-table launch
record matched to its C record by `t_start_ms` and `t_end_ms`):

| session | C records | runs-table launch records | C records outside the runs tables | runs-table records of pool 8's 64 tiles | of other items |
|---|---:|---:|---:|---:|---:|
| smoke p17201 | 60 | 60 | 0 | 30 | 30 |
| p17210 (kept) | 860 | 840 | 20 | 640 | 200 |
| p17211 (kept) | 850 | 830 | 20 | 640 | 190 |
| p17212 (kept) | 840 | 820 | 20 | 620 | 200 |
| p17213 (set aside by E78's pass gate) | 860 | 840 | 20 | 640 | 200 |
| **all** | **3,470** | **3,390** | **80** | **2,570** | **820** |

- **The check's 3,470** is every C record in the five logs, and P8-KC's set is far narrower. It includes:
  - the 80 launches of the two burn-in runs of `anchor_pi` that each pass makes before its runs table opens (`run.log`'s "burn-in 1/2"
    and "2/2"), which no runs table lists;
  - E78's six items: 710 records over the four passes, 120 each, except `fp16.zeros` 110, whose run p17211 #27 E78's launch rule skipped;
  - `anchor_pi`'s 80 runs-table launches and the smoke's 30 other records;
  - pool 8's 2,570, of which 640 are in the set-aside pass 17213 and 30 in the smoke.
- **P8-KC's 1,900** counts only pool 8's 64 tiles in the registered primary's kept passes 17210-17212: 640 + 640 + 620. p17212's two
  skipped runs, #39 and #52, were pool-8 tiles. Pool 8's own 12 anchors (its scale, check and zeros anchors, all among the 64) are in
  it. E78's `fp32.randn` and `fp16.randn`, two of the six float-scale anchors, are not. Their C status is read by `scale-c.md` (all six
  anchors C all PASS) and by M11's reader (90 of 90 each in the kept passes).
- Reported beside, never a rule: pool 8's tiles over all four passes (17213 included), 2,540 of 2,540 PASS.

**So the README's row "P8-KC | every launch of every pool-8 tile in a kept pass | 3,470 of 3,470 bit-exact in the session" puts the
check's count beside P8-KC's set.** P8-KC's own block reads **1,900 of 1,900**. Both are PASS, and the verdict stands. The README's other
uses of 3,470 give the check's count, which is right for what they say:
- the title's "every launch's C bit-exact (3,470 of 3,470)";
- "Every launch's C is bit-exact: 3,470 of 3,470 PASS";
- the C-check row of "Registered against what happened".

E171's README reads the same way. Its P8-KC row gives the check's 3,490 of 3,490, while E171's own P8-KC block reads 2,550 of 2,550 (the
four kept passes; [`../2026-11-05-q143c-m11-hc1b-i8pb/m11-hc1b-i8pb.json`](../2026-11-05-q143c-m11-hc1b-i8pb/m11-hc1b-i8pb.json) ›
`sessions` › `E171` › `P8-KC`).

## 4. What the records take from this note

- Quote: "E172's C re-derived in full from a fresh reference cache by the registered checker, unchanged (post hoc, 5 Nov 2026): 3,410 of
  3,410 C records in the four passes and 60 of 60 in the smoke equal the committed check, its file byte for byte; P8-KC re-read from it
  is 1,900 of 1,900 PASS, as scored."
- Where a record says "P8-KC 3,470 of 3,470" (this README's table, the card day critic's E172 verdict), read: **P8-KC 1,900 of 1,900**
  (pool 8's tiles in the three kept passes), and **the check of C 3,470 of 3,470** (every C record). For E171, read P8-KC 2,550 of 2,550,
  and the check 3,490 of 3,490.

## 5. How to reproduce

From the top of a clone of the lab's main at `04159d14` or later, with `<dir>` a new, empty directory outside the tree:

```bash
D=docs/reports/data/2026-11-05-e172-blind8-card1
mkdir -p <dir>/cache
for s in e172-smoke/p17201 e172/p17210 e172/p17211 e172/p17212 e172/p17213; do
  gzip -dc $D/aifoundry1-c1/$s/c-log.jsonl.gz > <dir>/c-log-$(basename $s).jsonl
done
nice -n 10 python3 -B tools/claims-v3/ccheck/ccheck.py check <dir>/c-log-p17201.jsonl <dir>/c-log-p17210.jsonl \
  <dir>/c-log-p17211.jsonl <dir>/c-log-p17212.jsonl <dir>/c-log-p17213.jsonl --out <dir>/ccheck-session.json --jobs 2 \
  --cache <dir>/cache > <dir>/ccheck-session.txt
cmp <(gzip -dc $D/ccheck/ccheck-session.json.gz) <dir>/ccheck-session.json && cmp $D/ccheck/ccheck-session.txt <dir>/ccheck-session.txt
python3 -B $D/posthoc_note2_e172.py <dir>/ccheck-session.json     # parts 1-7; exit 0 as committed
```

The check takes about 12-13 minutes at two workers on the Intel. Its reference cache is the only thing the call writes besides `--out`.

SPDX-License-Identifier: Apache-2.0
