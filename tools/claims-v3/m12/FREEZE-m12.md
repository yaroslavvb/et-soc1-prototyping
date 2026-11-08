# M12's candidate forecasts, frozen (Q157)

**M12 (post hoc, fitted on E182), frozen Sun 8 Nov 2026 05:07:07 PST, sha256
e97a2ae4fb27d6d161d1fd209f13a7fad91c10c1455a86b984625862fb734907 (`candidates-m12.json`), covering 20 one-number kinds (int8 8 new;
fp32 2 committed and 8 new; fp16 2 new) and 14 trains: Q3-swap, Q3-sign, Q63-swap, Q63-sign, X8, B23-B15, B15-B7, A23-A15, A15-A7, S15,
S23, H16, EB, EA.**

- Its inputs at the freeze, by sha256: `m12.json` 34118a60d338a33c0d4983f51f438156d9b9065a7ec1864f87b6b4da1ca05e56, `kinds-m12.json`
  ef72e1e53724c2d40da7c17b22ad1b0587427e9e76d31430dd02989ce875d09e, `bench/counts-m12.json`
  b29bef08d9f87a1c1f501cf84f4f33e0a5497186370d76cd1d4173e5cb08f57d; its readable copy `candidates-m12.md`
  27b2c0c6a1a1773f38b6460a84167bf2963e05a10689e36da163fb595b8578f0. The clock time is the Intel's `TZ=America/Los_Angeles date` at the
  hash; the commit that adds this file carries git's own time.
- **A candidate for the next one-number registration, not a registration.** The forecasts are blind for a run only if a registration
  commits this file, unchanged, before that run's first datum; the model itself stays post hoc (fitted after E182's data).
- **What a registration would still owe:** its own rules and thresholds, the session's float scale s applied to P10 (here s = 1), the
  measured rates in place of E182's, a kit, a dmcmd audit, a dry pass and a readiness critic. Nothing here touches a card.

SPDX-License-Identifier: Apache-2.0
