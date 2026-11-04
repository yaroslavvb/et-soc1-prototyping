# Dated note beside step243/README.md (Wed 4 Nov 2026, about 14:55 PST; Q141(t2)'s fix pass)

*These files stay as committed in `5e1bb309` (14:11:08 PST): `README.md`, `readings-243.json` and `.txt`, `summary243.json` and
`.txt`, and `recount-rule.json` and `.txt`. The step's verifier re-derived every figure from the committed counts with its own code.
Two quoted figures need a correction. Nothing counted, decided or read changes. The registration's own corrections are in
[`../REGISTRATION-step243.md.dated-note.md`](../REGISTRATION-step243.md.dated-note.md).*

## 1. Results 4, G4 on card 1: the 243-point k is −0.1505 W, not −0.150

- **The exact value.** k243 = s × (3pt − 243) = 0.96160 × (−0.15653 W) = **−0.15052 W**, with u243 = 0.05297 W.
  [`readings-243.json`](readings-243.json) holds `G4_arm_b20_pi.aifoundry1c1.k243_w` = −0.1505.
- **Where −0.150 comes from.** `readings_243.py` rounds the value to 4 decimals and then prints 3: double rounding. At 3 decimals
  the exact value is −0.151. The −0.150 is printed in three places:
  - [`readings-243.txt`](readings-243.txt) line 19;
  - Results 4;
  - the pushed message of `5e1bb309`.
- **For the records:** on card 1, k = **−0.1505 ± 0.053 W** at 243 points.
- **The 27-point figure on the same line.** "−0.299 ± 0.190 at 27 (frozen)" is the frozen arm's own text,
  [`../arm-s7.txt`](../arm-s7.txt). [`../arm-s7.json`](../arm-s7.json) holds `k_w` −0.2995, from the unrounded −0.29953, which is
  −0.300 at 3 decimals. The frozen files stay as they are. Quote it as −0.2995 ± 0.190.
- **The gap.** "0.155 W larger in size … 0.78 of its own u" is aifoundry3's figure (0.3115 − 0.1565 W; 0.15496 unrounded). On card
  1 the gap is 0.149 W (0.2995 − 0.1505), the same 0.78 u.
- **The rest of G4 needs no change.** Every other figure rounds once to what is printed:
  - aifoundry3: −0.157 ± 0.055 at 243, −0.172 ± 0.100 at 81, −0.311 ± 0.198 at 27, and D 12.093 → 12.249 W;
  - card 1: −0.166 ± 0.097 at 81, and D 11.628 → 11.779 W.

## 2. Results 5, B1: 155 content-hashed inputs, not 156 files byte for byte

- **What Results 5 says:** "the mini's build read the same 156 files as the Intel's, byte for byte".
- **Why that overstates it.** The count includes Verilator's own binary, `verilator_bin`, which Verilator's record writes as
  "unhashed" on both builds. The two binaries are different builds of Verilator 5.052 (x86_64 against arm64).
- **For the records:** 155 of 155 content-hashed build inputs are identical. Verilator's binary is unhashed in its own record, a
  different build of 5.052 on each machine. The generated model is identical: 126 of 126 files once the path prefixes are replaced
  ([`check-b1-generated.json`](check-b1-generated.json)). The detail is in the registration's note, section 1.

## 3. Nothing else changes

- **The outcome.** 7 of the 8 tiles meet the bound at 243 points, and `fp32.cal_third_b21` does not. 15 of the 16 calibration tiles
  meet it. N\* is not reached by uniform points at the cap. F1 carries `fp32.cal_third_b21` as 5.543 ± 0.125 W.
- **The readings.** G1-G3 and G5 stand as printed.
- **The checks.** B2, B3, D243 and C (0 mismatches over 1,296 points) stand.
- **The pushed message.** `5e1bb309`'s message ("B1 (156 of 156 files the builds read identical)", "-0.150 +- 0.053 card 1") cannot
  change, so this note carries the corrections.
