# Dated note on `queue_e159.py` (Tue 3 Nov 2026, week 45, E159's corrections after verification)

Written beside the script and not inside it. [`queue_e159.py`](queue_e159.py) is part of E159's registration (`d8badb73`), and the box ran
those bytes (sha256 `eff7f6c9a901…`, checked file by file against `d8badb73` before the claim), so they stay as registered and as run.

- **Its docstring, step 5b (lines 21-23), names the wrong burst for the board stop test.** It says the test runs "one 6 s burst of D8 fp32
  random", E146's wording carried over when E158's queue was copied with its names changed. What E159 registered and ran is **one 6 s burst of
  H1 fp32 zeros**:
  - [`protocol-stoptest-board.json`](protocol-stoptest-board.json): its one run, `H1-fp32-zeros`;
  - [`E159.md`](E159.md) § What runs: "one 6 s burst of H1 fp32 zeros, P0(800) 38.5 W over a 22 W rest";
  - the session's record: `docs/reports/data/2026-11-03-e159-gemm-sustained/aifoundry2/stoptest-board/tel/STOPTEST-00-H1-fp32-zeros-r1.jsonl.gz`.
- **Only the comment is wrong.** Step 5b's code runs whatever `protocol-stoptest-board.json` holds, so the test ran as registered and passed
  its registered check (63 ms from the third live line over 30 W to the trip, the launch ended 281 ms later).
- **The rest of the docstring holds.**

The corrections are in the data README,
[§ Corrections after verification](../../../docs/reports/data/2026-11-03-e159-gemm-sustained/README.md#corrections-after-verification-tue-3-nov-2026)
(C7).
