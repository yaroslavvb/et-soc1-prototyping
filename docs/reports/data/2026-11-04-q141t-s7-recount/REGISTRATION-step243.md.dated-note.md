# Dated amendment beside REGISTRATION-step243.md (Wed 4 Nov 2026, about 14:55 PST; Q141(t2)'s fix pass)

*REGISTRATION-step243.md (`9496466c`, 13:26:09 PST) stays as committed, and so do the step's outputs (`5e1bb309`, 14:11:08 PST).
Its verifier found four minor faults in quoted text, and three of them are in the registration. This amendment corrects those
three. It is committed before any output it governs. The only output it could govern is an F2 registration, and none exists: no
commit had touched this directory since `5e1bb309` when this was checked by git log at about 14:50 PST.*

*No rule, outcome, reading, threshold, tile, count or verdict changes. B1 still passes. F1 still carries `fp32.cal_third_b21` as
5.543 ± 0.125 W. F2's four conditions stand as written. The fourth fault, G4's card-1 rounding, is in the outputs; see
[`step243/README.md.dated-note.md`](step243/README.md.dated-note.md).*

## 1. Section 2, B1: 155 content-hashed inputs, not 156 files

**What section 2 says:** "156 of 156 files are identical across the two builds: the 153 RTL and bench files and Verilator's own
three".

**What the record holds.** Verilator's record of the files a build read (`obj_vpu/Vtb__verFiles.dat`) is copied into
[`step243/build-record-intel.json`](step243/build-record-intel.json) and [`step243/build-record-mini.json`](step243/build-record-mini.json)
as `verilator_files_read`. It has 156 entries, but only **155 carry a content hash**.
- **The 155 are identical** across the two builds: 150 core-et RTL files, the bench's 3, and Verilator's `verilated_std.sv` and
  `verilated_std_waiver.vlt`.
- **The 156th entry**, Verilator's own binary `verilator_bin`, is written "unhashed" on both builds. The two binaries are different
  builds of Verilator 5.052:
  - on the Intel, conda-forge's x86_64 build, 11,274,048 bytes;
  - on the mini, Homebrew's arm64 build, 11,761,152 bytes.

**What closes the gap: the model Verilator generated.** All 126 `obj_vpu` .cpp and .h files are identical once each build's two
directory prefixes, the core-et tree and the bench directory, are replaced by fixed markers.
- 103 are identical raw. The other 23 differ only in those embedded path strings.
- The source is [`step243/check-b1-generated.json`](step243/check-b1-generated.json), written by
  [`step243/check_b1_generated.py`](step243/check_b1_generated.py). It ran at about 14:56 PST on each build where it stands, the
  mini's under a memory and time cap. No build or count ran.

**So B1 reads:**
- 155 of 155 content-hashed build inputs are identical.
- Verilator's binary is unhashed in its own record: a different build of 5.052 on each machine.
- The generated model is identical: 126 of 126 files once the path prefixes are replaced.

B1 passes on that reading. B2, B3 and D243 stand unchanged. The pushed message of `9496466c` ("B1: 156 of 156 build inputs byte for
byte the Intel's") cannot change, so this note carries the correction.

## 2. Section 4.2 item 1: the binade look holds on two of the four tiles it looked at

**What item 1 says:** "C's binade alone is too coarse. A look at the committed 81 points, with no new count, shows the spread inside
one binade (sd 1.2-1.9 W) about as large as over the whole launch."

**The look, re-run per tile.** It uses the same committed 81 points, the same binade rule (floor(log2(16 n w)), from the op index n
and the base word w) and no new count. The source is [`step243/look-binades.json`](step243/look-binades.json) `at_81_points`,
written by [`step243/look_binades.py`](step243/look_binades.py). The table gives the sd inside the binades holding at least 6 points,
against the sd over the whole launch.

| tile | inside one binade (W) | whole launch (W) | item 1's sentence |
|---|---:|---:|---|
| `fp32.cal_third_b21` | 1.66-1.94 | 1.99 | holds |
| `fp32.cal_pi_b21` | 1.22-1.47 | 1.36 | holds |
| `fp32.cal_third_b20` | 1.35-1.50, but **0.435** at 2^21 (n = 23) | 1.32 | not uniform: one binade is a tight stratum |
| `fp32.cal_pi_b20` | **0.60**-1.16 (0.60 at 2^23, n = 24) | 0.90 | not in the 1.2-1.9 W range |

- **The step's other four tiles**, which the look did not cover:
  - `fp32.cal_w67_b21` 1.21-1.47 W (whole launch 1.26);
  - `fp32.cal_w79_b21` 0.89-1.29 (1.08);
  - `fp32.cal_w67_b20` 0.63-1.05 (1.04);
  - `fp32.cal_w79_b20` 0.50-1.08 (0.97).
- **At the 243 points, for reference only** (`at_243_points_reference_only`): `fp32.cal_third_b21` reads 1.56-1.89 W against 1.94,
  and `fp32.cal_third_b20`'s 2^21 binade 0.401 W (n = 69) against 1.38.

**What it changes.**
- The sentence's conclusion stands for `fp32.cal_third_b21`, the one tile F1 carries. There, C's binade alone is too coarse a
  stratum, and the points sit near 4 W or near 7.8 W, as item 1's second bullet says.
- It does not hold for every calibration tile.
- **An F2 registration uses the per-tile figures**, never the single 1.2-1.9 W range. It takes its strata from `accum.c`'s C
  (condition 1), not from this look's approximate binade.
- F2's four conditions are unchanged. The pushed message of `9496466c` carries the old range.

## 3. The header and section 0 name M9 by its model commit only

- **What it should say.** M9 is `1f244140`, the model (01:12:04 PST), with its registration `8dfafae3` (00:45:51 PST), as Q141(t)'s
  [`REGISTRATION.md`](REGISTRATION.md) names them. `9496466c` and `5e1bb309` descend from both (`git merge-base --is-ancestor`).
- **What the step reads of M9**, all through `recount_rule.py` and all last changed in `1f244140`:
  - `m9.json`: the float prices and the card-1 scale;
  - `nested-m9.json`: pool 6's rows, for G5;
  - `fit_m9.py`: the frozen rate;
  - `bench-check/`: the calibration tiles and their committed counts.
- **For the records:** the step's parents are M9 `1f244140` / `8dfafae3`, the recount rule `b4444dd4` with its pilot `b85ca0f9`, and
  Q141(t)'s arm `67d5e44f` with its amendment A1 in `c31e7ae3`.
