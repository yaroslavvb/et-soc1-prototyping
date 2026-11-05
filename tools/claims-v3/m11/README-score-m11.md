# M11's scorer, `score_m11.py` (Q143(k); REGISTRATION.md section 13 step 1, as amended by A1-A4)

*Thu 5 Nov 2026 (week 45), on the Intel, desk only, before any M11 hold: no M11 kit had run, no E176 or E177 data exists. New files only;
every earlier M11 file stays as committed. For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
items 9 and 8.*

- **What it reads.** An aifoundry3 session's measured pass, with score_e166's readers unchanged (`records`, `classify`, `arm_a_error`,
  `read_one`), on § 1's window: R3's [b − 300 s, b), with b the last process's end. Each hold of § 5 (H_E, Z, L1, S, L2) is read by name. A
  hold is scored only if X1 reads it complete. The launch order is read from the launch marks.
- **What it decides, through the committed design code's own functions**, imported unchanged rather than re-written:
  - HM-LG, by `design_power_groups.lg_test`;
  - A1-4's path, by `design_power_heat_v2.decide`, on the sessions HM-LG counts;
  - HM-E144 and HM-HE, by `design_power_heat_a3.he_departs_exact` at the exact t point;
  - HM-CAL, by `design_power_heat_a3.cal_by_name` (the pair by name, run first), pooled as A2 pools it, with A2-3's outcome from
    `design_power_heat_a2.a2_entry`;
  - HM-CAL-I8, by `design_power_heat_a4.cal_i8_by_name`, `hm_cal_i8`, `int8_misses` and `i8_entry`.
- **What it prints:**
  - per session, the two-term fit with its intervals, the room's drift over R0, and each hold's P, R, e and reason;
  - RMS_c with its χ² interval and the floor;
  - the ×1.032 arm on the same holds;
  - what M11 carries;
  - the blind precedence: every registration and amendment commit an ancestor of HEAD and older than the session's first launch record.
- **σ_c** is `design_power_heat.noise()`'s, at the power code's own precision: 0.0884 and 0.2296 °C to four decimals, the registered
  figures. Only so do the committed cells re-make exactly.
- **aifoundry2** has no reader here: `score_e167.read_hold` is tied to E167's holds and predictions, so an `--a2` pass is refused (E177 is
  its own lane).
- **Its self-test** ([`selftest-score-m11.txt`](selftest-score-m11.txt), `.json`): **PASS**, as the E176 kit's README
  ([`../e176/README.md`](../e176/README.md)) quotes it. It covers the lists, M10's nine holds (with E154's `K_S` window difference
  recorded), 11 synthetic sessions over A1-4's and A2-A4's paths, one committed cell each of A2, A3 and A4, and the precedence check.

      /usr/bin/python3 -B tools/claims-v3/m11/score_m11.py --self-test --json <out>
      /usr/bin/python3 -B tools/claims-v3/m11/score_m11.py score --a3 <pass dir> [--a3 <pass dir>] --json <out> --md <out>

[`SHA256SUMS-score-m11`](SHA256SUMS-score-m11) pins the scorer, its self-test output and this README.

SPDX-License-Identifier: Apache-2.0
