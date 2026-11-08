# M12's and M10's forecasts for E186's merged candidate list, frozen (Q158)

**M12 (post hoc, fitted on E182) and M10 (frozen), frozen Sun 8 Nov 2026 06:56:00 PST, sha256
810423fa5d439dcc3f61fbe9bbbda411cada138f46f9cbe16a13e0c3adae4d1b (`candidates-m12-e186.json`), covering E186's merged candidate list:
39 one-number kinds K01-K39 (int8 17, fp32 20, fp16 2) and 22 trains: Q3-swap, Q3-sign, Q63-swap, Q63-sign, X8, B23-B15, B15-B7, A23-A15,
A15-A7, S15, S23, H16 (= R5), EB, EA, R1, R2, R3, R4, R6, R7, R8, R9.**

- **What is new and what is carried.** M12's 20 kinds and 14 trains are `candidates-m12.json`'s values as frozen (05:07:07 PST, sha256
  e97a2ae4fb27d6d161d1fd209f13a7fad91c10c1455a86b984625862fb734907), recomputed by the same code and equal to the last bit. The other 19
  kinds and 8 trains are computed here with M12 exactly as committed (`m12.json`, no refit). M10's frozen forecast is given for all 39 kinds
  and 22 trains.
- Its inputs at the freeze, by sha256: `kinds-m12-e186.json` 9af274eb1c10db3e8caa1800304b00b3b4078fac4fc567760808e8a63a96d80a,
  `bench/counts-m12-e186.json` 32f6cc61cae98486bbc54fd36baca14ac4741ab9bf400707f6c696242b3cf72b, `m12.json`
  34118a60d338a33c0d4983f51f438156d9b9065a7ec1864f87b6b4da1ca05e56, `candidates-m12.json`
  e97a2ae4fb27d6d161d1fd209f13a7fad91c10c1455a86b984625862fb734907, the script `candidates_m12_e186.py`
  ae6954a495a5ab15b6dd6d8f14977f1ea747fa25b6395fc771ee92b417f0757c; its readable copy `candidates-m12-e186.md`
  c2f3cd3021ca4a6258b652165124cdf93a137b6aa4beea5884a4343d99358873. The clock time is the Intel's `TZ=America/Los_Angeles date` at the
  hash; the commit that adds this file carries git's own time.
- **A forecast for a registration to take, not a registration.** The forecasts are blind for a run only if its registration commits this
  file, unchanged, before that run's first datum; M12 itself stays post hoc (fitted after E182's data). E186's registration, committed after
  this file, takes it.
- **What a registration still owes** (M12's verifier's list, `FREEZE-m12.md.dated-note-1.md`): its own rules and thresholds; the session's
  float scale s applied to P10 (here s = 1) and the measured rates in place of E182's; a registered session anchor (M12-S1's form) before any
  int8 kind's absolute level is scored, the trains scored as frozen; an fp16-scaled arm beside F16-SAME and M10 for H16; power and separation
  at both train noises (both are in this file); its own Builds-on block; a kit, a dmcmd audit, a dry pass and a readiness critic. Nothing
  here touches a card.

SPDX-License-Identifier: Apache-2.0
