# REFIT.md, dated note 1: CEQ's high-mantissa word is 0x3ff80000, not 0x3ff00000 (Sun 8 Nov 2026, PST; Q157)

*Written after REFIT.md's commit (`d5eb87b5`, 04:56:09 PST) and before any forecast of a candidate kind: found when `candidates_m12.py
stage` printed the staged kinds' popcounts.*

REFIT.md section 5's row **CEQ** reads "fp32 B 0x3f80000f (four low mantissa bits) and 0x3ff00000 (four high), popcount 11 each". The
words and the hex disagree: 0x3ff00000 is 1.875, three high mantissa bits (bits 22-20) on 1.0's exponent, popcount 10. **The rule's words
govern:** four high mantissa bits, popcount 11 like 0x3f80000f, is **0x3ff80000** (1.9375, bits 22-19). So CEQ's kinds are (1.0,
0x3f80000f), (1.0, 0x3ff80000), (0x3f80000f, 1.0) and (0x3ff80000, 1.0), and its trains EB and EA read 0x3ff80000 against 0x3f80000f.
The two tiles staged with 0x3ff00000 were removed before the bench ran; nothing else in REFIT.md changes.

SPDX-License-Identifier: Apache-2.0
