# nocr: hub rungs 31 and 32, NoC places and routing order (development on aifoundry1's card 1, validation on aifoundry3)

Pre-registration: `tools/claims-v3/nocr/PREREG.md` (frozen 29 Sep about 00:10 PDT, sha256 `2472ab3e…`, after the
development result was recorded in it). Code: `workloads/nocroute/`, `tools/claims-v3/nocr/`.

- Development: `raw/aifoundry1-c1/` (p9 smoke, p1-p3; 28 Sep 23:57 - 29 Sep 00:01 PDT).
- Validation: `raw/aifoundry3/` (p9 smoke, p11-p13; 29 Sep 00:28-00:32 PDT). `summary.json` in each from `reduce.py`.

**Result.** R32, both cards: read replies travel **y first** and write requests x first (replies retrace requests);
P9 T-YX survives and P8 T-XY, the chip diagram's assumption for every route, is refuted; links saturate near 92 GB/s
(P10 refuted; P11 adaptive routing refuted). R31: an ESR call costs 1,557 + 35.9 cycles per hop over 992 caller-target
pairs on aifoundry3 (r² 0.995, rms 4.7 cycles; the "via a hub" model rms 62); by the frozen rule (rms <= 4 cycles)
T-DIRECT is **refuted** on aifoundry3, so the places that rest on it (P5, P6, P7) are not decided there. In
development on card 1 T-DIRECT survived and the master shire placed at (0,3), the firmware map's top grey cell.
