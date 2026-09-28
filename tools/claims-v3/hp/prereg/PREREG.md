# PREREG: heat placement, validation on aifoundry1 card 1 (DESIGN2 §6)

Written 2026-09-27 22:50 PDT by `tools/claims-v3/hp/prereg.py --val` from the development registration (P3, `reduce.py --p3`) and
card 1's V0 calibration. Once the first validation block starts, code, parameters and this item list stay as hashed
(DESIGN2 §6.4). This file's sha256 is in `PREREG.sha256`; the lock at the end holds the sha256 of `prereg.json` (every
item, prediction, band, beta, primary and n_val), of `params-val-aifoundry1-c1.json`, of the code and helpers, and of
card 1's binaries. `block.sh` refuses a validation block and `reduce.py --val` refuses to reduce on any mismatch, and
on aifoundry1 a validation block also refuses a PREREG other than the one earlier validation blocks ran under.

- Probe classes: aifoundry3 SILENT, aifoundry1-c1 SILENT; TRIG-B registered on card 1: False.
- TRIG-A on card 1 is WAIVED: DESIGN2 §3.4 registers it only if card 1's probe is ALIVE and its smoke shows the clock leaving 600 MHz below 65 C; this implementation has no card-1 clock-step protocol (its validation runs void any sample off 600 MHz), so TRIG-A is not tested on card 1 whatever the probe says (card 1's probe: SILENT).
- Family size: 2 registered items at 99% (plus POWER and WORK EQUIV on every pair of a registered item,
  CONC, MAP and LIN included). Under a global null each SIGN item holds falsely with probability 0.005; no Bonferroni
  correction (V3 practice).
- Outcome precedence (README departure 18, fixed before any data): a 99% CI lying wholly inside +-band FAILS a SIGN or
  NONZERO item even when it also excludes 0 (the effect is shown negligible).
- Each type uses its first n_val usable validation blocks in pass order (void or incomplete blocks are replaced by
  later ones, §4.4); later blocks are listed as extra and never used; fewer than n_val usable blocks gives
  INSUFFICIENT. A block is used only if every registered pair in it is complete.
- Tier S POWER is WAIVED for every pair with INT16@32 (PLACE-tS, PLACE-kappa-S, CONC's INT16@32-UNI32@16): sw_W is the median over t0 + 1 s .. t0 + t66 (DESIGN2 §5.5, unchanged) and INT16@32 crosses 66 C in < 1 s from S_S (R1c: 0.86-0.97 s), so its window is empty and POWER cannot be computed (it would be INSUFFICIENT by construction, card 1 heating faster). The verdicts list these pairs as "waived: no window in Tier S; see Tier L". Equal power for the INT/PER/UNI placements rests on the Tier L check: development R1c L16 sw_W INT16@32 13.96, PER16@32 13.87, UNI32@16 13.83 W, every pair within +-0.5 W; on card 1 PLACE-t's POWER EQUIV (PER16@32-INT16@32, L16) is tested when PLACE-t is registered, and the verdicts report the waived pairs' L16 values. WORK is not waived; the other Tier S pairs (CONC's PER16@32-UNI32@16, MAP's B4NE-B4SW) keep POWER EQUIV.
- L8 and G8 were dropped (types kept: L16, S; by D-L8 in development, DESIGN2 §5.3, or by P3): card 1 runs no S_L8 V0 series and no L8 or G8 validation block; the frozen S_L8 (aifoundry3's R3 value) is unused (README departure 36).
- kappa gate 0.9 (as designed; decided 27 Sep 2026 before any validation data): an item whose
  development runs never passed it is listed below as reported, not tested.
- beta = 0.3187383699621604; the primary contrast per time item as listed (L or L_adj, chosen by P3).
- CV ratio for card 1 (§2.4): {"aifoundry3": 0.0467462914299326, "aifoundry3_runs": 3, "aifoundry3_what": "R3 L16 CAL chains at S_L=61", "aifoundry3_edge": 61, "aifoundry3_blocks": [3201, 3202, 3203], "card1": 0.10058659020513096, "card1_runs": 3, "card1_what": "V0 chains at the settled edge 60 (pass 5502)", "card1_edges": {"61": [5501], "60": [5502]}, "ratio_used": 2.1517555110419586}.
- Only signs transfer between cards, never magnitudes.

| Item | Block type | Prediction | Band | Primary | n / reason |
|---|---|---|---|---|---|
| PLACE-t | L16 | SIGN+ | 0.09531 | L | n_val 5; POWER and WORK EQUIV on PER16@32-INT16@32 |
| PLACE-kappa | L16 | reported, not tested | 0.05 | | fewer than 3 development blocks |
| PLACE8-t | L8 | reported, not tested | 0.09531 | | fewer than 3 development blocks |
| PLACE-tS | S | SIGN+ | 0.09531 | L | n_val 5; POWER and WORK EQUIV on PER16@32-INT16@32; POWER waived on PER16@32-INT16@32 (no window in Tier S; see Tier L) |
| PLACE-kappa-S | S | reported, not tested | 0.05 | | fewer than 3 development blocks |
| MEM | L8 | reported, not tested | 0.09531 | | fewer than 3 development blocks |
| EDGE | L8 | reported, not tested | 0.09531 | | fewer than 3 development blocks |
| GRAD-EW | G8 | reported, not tested | 0.09531 | | fewer than 3 development blocks |
| GRAD-NS | G8 | reported, not tested | 0.09531 | | fewer than 3 development blocks |
| LIN | L8 | reported, not tested | 0.05 | | fewer than 3 development blocks |
| CONC | S | reported, not tested | 0.5 | | development does not support the fixed prediction SIGN+ (got None) |
| MAP | S | reported, not tested | 0.5 | | power at n_val = 5: h = 0.809 > 0.7 x |estimate| = 0.467 |

## Frozen parameters (card 1)

S_L is card 1's V0 edge (S_L8: L8 and G8 dropped, unused) ({"S_L": 60, "S_L8": null, "L8_offset": 3}); the rest are
aifoundry3's frozen R3 values.

```json
{
 "S_L": 60,
 "S_L8": 64,
 "S_S": 64,
 "target_S": 68,
 "target_L_over": 2,
 "target_L8_over": 2,
 "chain_cap_s": 150,
 "C_L": 150.0,
 "kappa_gate": 0.9,
 "void_tauc_lo": 0.5,
 "void_tauc_hi": 2.0,
 "void_widle_range_w": 1.0,
 "types": [
  "L16",
  "S"
 ],
 "n_val": {
  "L16": 5,
  "S": 5
 }
}
```

## Development values (aifoundry3, REPORTED)

```json
{
 "PLACE-t": {
  "mean": 0.4794598250708295,
  "lo": 0.40879589617123263,
  "hi": 0.5501237539704263,
  "n": 9,
  "sd": 0.06318682166879004,
  "half": 0.07066392889959687
 },
 "PLACE-kappa": null,
 "PLACE8-t": null,
 "PLACE-tS": {
  "mean": 0.5811432801927948,
  "lo": 0.45427279804050724,
  "hi": 0.7080137623450824,
  "n": 6,
  "sd": 0.07707538310862716,
  "half": 0.1268704821522876
 },
 "PLACE-kappa-S": {
  "mean": -0.23494960999259307,
  "lo": -1.6717061621845501,
  "hi": 1.2018069421993638,
  "n": 2,
  "sd": 0.03191920137515549,
  "half": 1.436756552191957
 },
 "MEM": null,
 "EDGE": null,
 "GRAD-EW": null,
 "GRAD-NS": null,
 "LIN": null,
 "CONC": {
  "mean": 0.11111111111111115,
  "lo": -0.3019244805756104,
  "hi": 0.5241467027978327,
  "n": 6,
  "sd": 0.2509242175696938,
  "half": 0.41303559168672155
 },
 "MAP": {
  "mean": 0.6666666666666679,
  "lo": 0.36613913049069824,
  "hi": 0.9671942028426375,
  "n": 6,
  "sd": 0.18257418583505408,
  "half": 0.3005275361759696
 }
}
```

## Files and binaries (sha256)

| File | sha256 |
|---|---|
| `tools/claims-v3/hp/block.sh` | `d8aa50d1594e345c5fc77c03bfe39f9a3c4c8ddf269a153aaaa782773ba510c5` |
| `tools/claims-v3/hp/ettelem-hp/ettelem.cpp` | `9452b09dee761e68fb1d74e6d1369ae994e7fa6c2d30f0a053c86b8c5679308a` |
| `tools/claims-v3/hp/hplib.py` | `f7ccd59471dbaa9a23d5928a7430da285784f36a22d6c81412f15ddad1ecc008` |
| `tools/claims-v3/hp/hplib.sh` | `c54b3fa57cbb0049c282486c2c8889755581d867692327f9fdee562af2398ac4` |
| `tools/claims-v3/hp/params/params-val-aifoundry1-c1.json` | `76d4a72a405d86c20e52a6ef32aac6fea479d15f05d6b134a8d9318b6a461901` |
| `tools/claims-v3/hp/placements.json` | `3d0380c8860a0eff2a48ae2182abe018556a3503d31f996248aeb974dd632215` |
| `tools/claims-v3/hp/prereg/prereg.json` | `3714c59f6d1ecf38c58f0b0bed25f598099cfd12019dfb987fa0cdfab669eb64` |
| `tools/claims-v3/hp/probe.sh` | `d0a8ed921923101bf0f34f90a7c1dfa64b04a27f89c0ea96791f5e1573a513d1` |
| `tools/claims-v3/hp/reduce.py` | `9751f549c2eb3fd468a7182ba8ae5d5ae62988bb353f09444669ed49fbbbdffd` |
| `tools/claims-v3/hp/run_queue.sh` | `56159e399f1b75f002acb9fe7eaf0c8aa37074d0ab14dfacfaf01484056f4f90` |
| `tools/claims-v3/hp/sptrace_events.py` | `8cbb7df0d6e32494945ad5a8d761b9b02c4b6ad3efa1d087b0c7091a71178834` |
| `tools/claims-v3/lib.sh` | `033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa` |
| `tools/claims-v3/queue.sh` | `4b63600429614c2379ce6e63e0cfc4fe518e8069bfa3a01b594b663facd924e9` |
| `tools/ettelem/ettelem.cpp` | `39bfdc8a9a5304b2122f2a9060129d85e631d48fd9a9834332fbceb8fccdfebd` |
| `tools/ettelem/flip_thermal_model.py` | `dd40f4d09e9f16f17688d5dcd0d4843ce9701a0cb5dc1098b36da71d2db0da4c` |

| Binary (role, card 1) | Path | sha256 |
|---|---|---|
| ettelem | `build/ettelem/ettelem` | `8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325` |
| ettelem_hp | `build/ettelem-hp/ettelem` | `51a9ac46baa58729bdba2a28b636659dd3ea10d0ad2aead4859d088463efb5ff` |
| heater | `build/sparsity/host/sparsity_host` | `1641d27764478465cc054ca24c38b678bbe8616c3cc1bce9f47a93ee389d2bf6` |
| heater_kernel | `build/sparsity/host/../kernel/sparsity.elf` | `990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24` |

## The lock (machine-readable; block.sh and reduce.py --val check every entry)

<!-- lock-begin -->
```json
{
 "binaries": {
  "ettelem": {
   "path": "build/ettelem/ettelem",
   "sha256": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325"
  },
  "ettelem_hp": {
   "path": "build/ettelem-hp/ettelem",
   "sha256": "51a9ac46baa58729bdba2a28b636659dd3ea10d0ad2aead4859d088463efb5ff"
  },
  "heater": {
   "path": "build/sparsity/host/sparsity_host",
   "sha256": "1641d27764478465cc054ca24c38b678bbe8616c3cc1bce9f47a93ee389d2bf6"
  },
  "heater_kernel": {
   "path": "build/sparsity/host/../kernel/sparsity.elf",
   "sha256": "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24"
  }
 },
 "card": "aifoundry1-c1",
 "files": {
  "tools/claims-v3/hp/block.sh": "d8aa50d1594e345c5fc77c03bfe39f9a3c4c8ddf269a153aaaa782773ba510c5",
  "tools/claims-v3/hp/ettelem-hp/ettelem.cpp": "9452b09dee761e68fb1d74e6d1369ae994e7fa6c2d30f0a053c86b8c5679308a",
  "tools/claims-v3/hp/hplib.py": "f7ccd59471dbaa9a23d5928a7430da285784f36a22d6c81412f15ddad1ecc008",
  "tools/claims-v3/hp/hplib.sh": "c54b3fa57cbb0049c282486c2c8889755581d867692327f9fdee562af2398ac4",
  "tools/claims-v3/hp/params/params-val-aifoundry1-c1.json": "76d4a72a405d86c20e52a6ef32aac6fea479d15f05d6b134a8d9318b6a461901",
  "tools/claims-v3/hp/placements.json": "3d0380c8860a0eff2a48ae2182abe018556a3503d31f996248aeb974dd632215",
  "tools/claims-v3/hp/prereg/prereg.json": "3714c59f6d1ecf38c58f0b0bed25f598099cfd12019dfb987fa0cdfab669eb64",
  "tools/claims-v3/hp/probe.sh": "d0a8ed921923101bf0f34f90a7c1dfa64b04a27f89c0ea96791f5e1573a513d1",
  "tools/claims-v3/hp/reduce.py": "9751f549c2eb3fd468a7182ba8ae5d5ae62988bb353f09444669ed49fbbbdffd",
  "tools/claims-v3/hp/run_queue.sh": "56159e399f1b75f002acb9fe7eaf0c8aa37074d0ab14dfacfaf01484056f4f90",
  "tools/claims-v3/hp/sptrace_events.py": "8cbb7df0d6e32494945ad5a8d761b9b02c4b6ad3efa1d087b0c7091a71178834",
  "tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa",
  "tools/claims-v3/queue.sh": "4b63600429614c2379ce6e63e0cfc4fe518e8069bfa3a01b594b663facd924e9",
  "tools/ettelem/ettelem.cpp": "39bfdc8a9a5304b2122f2a9060129d85e631d48fd9a9834332fbceb8fccdfebd",
  "tools/ettelem/flip_thermal_model.py": "dd40f4d09e9f16f17688d5dcd0d4843ce9701a0cb5dc1098b36da71d2db0da4c"
 },
 "params_val": "tools/claims-v3/hp/params/params-val-aifoundry1-c1.json",
 "prereg_json": "tools/claims-v3/hp/prereg/prereg.json"
}
```
<!-- lock-end -->
