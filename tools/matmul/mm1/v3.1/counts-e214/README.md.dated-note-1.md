# E214's switch counts, README dated note 1 (Thu 19 Nov 2026; after the verifier, before the commit): verify-counts-e214's three nits and one more wording slip

*Written on aifoundry2 at 11:43 PST on Thu 19 Nov 2026 (week 47) by the clock, by the lab's lane `land-e214u` of round Q225, after this
folder's verifier, `verify-counts-e214`. Desk work only: no card, no device, no simulator and no post. The verifier's verdict was HOLDS (its
record, REPORTED: its own driver over its own Verilator 5.042 build, byte-equal to this folder's, re-counted 16 new points over all four
footings and the two committed points bit-equal; all 29 rows, the scope and the merge re-derive; no E214 measurement and no E215 datum was
read). It found three nits and two information notes, none of which changes a number. [`README.md`](README.md),
[`SHA256SUMS`](SHA256SUMS) (sha256 4c39d0d3cf4ad405d5d32d4128f828d0d39272aab8dc0c822a2eacbb49be664a) and every file it lists are committed
byte for byte as the lane `counts-e214` froze them (final 10:00:39 PST): MM1's unread test of E214 (the lane `unread-e214`) cited these
counts by that SHA256SUMS in its declaration before it read any E214 measurement, so the nits are answered in this note and not by editing
those files. **No count, row, check or rule changes, and nothing is scored here.** The interpreter was `/usr/bin/python3` 3.12.3 with
`-I -B`, and git 2.43.0. Labels: **desk check** (this lane's runs on the committed objects and this folder's files) and **REPORTED** (the
verifier's, not re-run here).*

## 1. The s01 path count (nit 1)

When it ran, `scripts/s01_setup_inner.sh` printed "paths naming an E214 data dir or e215: 1". Its `grep -c` reads whole lines of its tree
listing (`<blob sha1> <path>`, from `git ls-tree -r` of GitHub main 8bde0182 over its source paths), and its one hit is inside a blob hash,
not a path: `aedc0aa0f27b5699c74e276204ed2571e2151a72`, the blob of `tools/matmul/mm1/v3/inputs/SOURCES.tsv`. Desk check: the listing
re-made from the lab's objects at 8bde0182 with s01's own path list (2,081 lines, byte-equal to the lane's) holds the pattern on 1 whole
line, 0 path fields and 1 blob field. **The true path count is 0.** The corrected line reads the path field only:

```
cut -d' ' -f2- "$WK/lab-tree.txt" | grep -c 'docs/reports/data/2026-11-18-e214\|e215'    # prints 0
```

The landed script is kept as it ran, so that it shows what printed the 1.

## 2. "129 committed-kind cells unchanged" (nit 2)

README section 4 and `merge-check.json` (its `summary`) say that the merge leaves 129 committed-kind cells unchanged. All 129 are
unchanged, but **107 of them return a count** (E214's random, zeros and ones cells) and **22 return none, both before and after the
merge**: E214's sparse50 cells (`pattern:sparse50f` 7, `pattern:sparse50h` 4, `pattern:sparse50i` 11). `counts31()` knows these names only
through data_v31's `SPARSE_GEN` alias, which holds `sparse50f` and `sparse50i` alone (E212's names). Desk check over the file's 154 cells:
25 NEEDS-COUNT cells with none before and a count after; 107 committed cells with the same count before and after; 22 sparse50 cells with
none before and after. README section 4 already says that an E214 reader needs the alias for all three names, and MM1's unread test of E214
declared it before its read. Read the figure as "129 committed-kind cells unchanged, 107 of them with a count".

## 3. The sparse50h cross-check is REPORTED (nit 3)

`crosscheck-sparse50h.txt` (its first line) and `crosscheck-sparse50h.json` (its `what`) say "not a new count", but they do not carry the
label REPORTED that README section 0 gives the cross-check. Read each of those lines as beginning "REPORTED, not a row:". Their numbers
stand as computed.

## 4. One more wording slip, found by this lane (not the verifier's)

README section 0 and `recount-check.txt` say that "two committed rows" were re-counted before any new count. They name four rows, two
for each part of the re-count rule: fp32 `pattern:fld_mant` at S1 and `pattern:den8` at S2 (count_e210.py), and int8 `pattern:i8_pm1` and
fp16 `pattern:fld16_mant` at the launch points (run_kinds.py). Those are the 14 bench points, and 492 + 492 + 432 + 555 = 1,971 numbers
bit-equal (`recount-check.txt`, desk check of the file). The verdict, MATCH, is unchanged.

## 5. The verifier's two information notes (no change; REPORTED)

- `pattern:sp_ar4`'s A tile holds 8 all-zero rows (rows 4-7 and 12-15) and its B tile none. Its clocked register bits (1,066.3 a
  multiply-add) and valid share (0.500) equal E210's arow50 (1,066 and 0.500), so its gating structure is arow50's. How a reader gates it is
  the reader's to declare (README section 4).
- `energy_v31.py` as landed reads only `tools/matmul/mm1/v3.1/counts/`: `counts31()` does not see this folder by itself, so a reader merges
  the two tables in memory, as `merge-check.json` does.

## 6. Files

This note and [`SHA256SUMS-note1`](SHA256SUMS-note1), which holds the sha256 of this note, of `README.md` and of `SHA256SUMS`. In this
folder, `sha256sum -c SHA256SUMS` and `sha256sum -c SHA256SUMS-note1` both verify.
