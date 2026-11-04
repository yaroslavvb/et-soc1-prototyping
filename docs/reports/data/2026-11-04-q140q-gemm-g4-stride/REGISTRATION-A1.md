# Q140(q) registration, amendment A1 (dated Wed 4 Nov 2026, about 04:00 PST)

*Written **after** every fit, score and prediction of this lane: the registered result and the freeze, `e39d06da`, committed
02:49:40 PST and pushed 02:50:04, and after its verifier's report. It is written **before** any E168 or E169 claim: the card half
waits for the owner's word, and nothing has run. It changes no fit, score, rule, frozen number or verdict, and no frozen prediction
of E168 or E169. [`REGISTRATION.md`](REGISTRATION.md) and [`registration.json`](registration.json) keep their text as committed in
`49575094` (committed 02:26:25 PST, pushed 02:26:29). The README's
[§ Corrections after verification](README.md#corrections-after-verification) lists every correction of this pass (C1-C13, numbered
as the verifier's faults), and [`corrections.txt`](corrections.txt) prints every new number.*

1. **A4's selection (C1).** As registered, the forward rule keeps or drops each term on the same outer held-out losses that it
   then reports. So `loso-g4.json`'s pooled G4 figures are nested in the constants (each fold's constants chosen on the other four
   sessions), not in the choice of terms. A4 is unchanged and so is every verdict. The post hoc reading with the selection itself
   nested (an inner leave one session out on the four training sessions, inner rule 3 of 4 or 2 of 4) is in `corrections.txt`
   C1: T_Z is kept in every fold, T_D in none, and T_G in 3 or 4 of the 5.
2. **T_S in the scores and the freeze (C2).** A2 makes T_S structural, "reported there, not put to the forward rule", and A4
   says "G4 = G3 + the kept terms + T_S, its constants then chosen on all five sessions". `fit_g4.py` applied T_S nowhere: E136's
   four other-kind runs were scored on E136's levels, and `g4.json`'s constants were chosen on those rows. So the registered
   pooled scores are G4 without T_S, and the README now says so. Post hoc (`corrections.txt` C2), with T_S applied in the choice
   too, the constants chosen on all five sessions are `g4.json`'s own (0.2 W/°C, 65.5 °C, d_G 0.12, P_G 56 W). So `g4.json` is
   the G4 that A4 describes, and E168's frozen predictions stand unchanged.
3. **E159 and T_G (C4).** A2 takes T_G's form (a dip opening each process) and its 618 MHz from E159 C1, that is from E159's own H1.
   So E159 is held out of the constants' fit only; it is not blind for T_G. Post hoc, with the dip clock at 600 or 650 MHz, E159
   held out reads 7.80 / 7.71 MHz, 1.81 / 1.82 W and 0.93 / 0.92 °C, against 7.73 MHz, 1.81 W and 0.93 °C (`corrections.txt` C4).
4. **Check (i)'s k_D (C7).** A5 (i) writes the check as P0 + β·δ + k_D·(T_start − T_ref) and gives no value of k_D once T_D is
   rejected. `checks_g4.py` used 0.47 W/°C, the middle of A2's grid. It was written at 02:35:59 PST, before any output of the
   checks and before the fit printed its verdicts (02:38:19). At 0.44 and 0.50 the check reads 0.54 and 0.78 W rms, against
   0.64 W. The bursts' start dies span 47.3-48.3 °C, 6.0-7.1 °C under T_ref, so the check tests the law's offset there, not its
   slope (`corrections.txt` C7).
5. **E168's design (C8, C10). No change.**
   - E168's three int8 holds all start warm (55 °C). So the int8 cold-minus-warm difference that G4's in-run constant predicts
     (+1.33 W in the window for int8 zeros at S2: `predictions-e168.json` `cells.S2-int8-zeros-warm55.both_nominal_starts`, 37.66
     against 36.33 W) is **not tested by E168 as designed**. A card lane that wants it tested adds an int8 zeros hold from a cold
     start by its own dated amendment, committed before its claim; the nominal cold prediction is already frozen in that table.
   - The int8 W8A8 hold (`values` `gemmL3x3x2:tiles:…/int8.real_smol_w8a8_down.bin`) runs rgm136's generator `tiles`, which
     cycles the file's one tile pair (1 KB of A and 1 KB of B, a 2,048-byte file) over the whole GEMM. So it tests one real
     tile's bits in a GEMM, not a whole weight panel. The sparse50 hold runs the generator `sparse50`: pair 0 is the file's and
     the rest are drawn with half their elements zero, 8,192 distinct tiles per pool (`tools/claims-v3/e136/rgm136/host/main.cpp`,
     the `--values` grammar and `fillPools`).
6. **The scorer's own hashes (C11).** `score_e168.py check` hashes 9 frozen files, but not `score_e168.py` itself, and not three
   modules and four data files its score path also loads: `tools/claims-v3/kspeed/e83/predict_e83.py` (imported by
   `make_predictions_e119.py`), `tools/claims-v3/hpl/surface_hpl.py`, `surface_hpl_t.py`, E105's `results-speed.json`, E107's
   `e107.json` and `scored.json`, and `tools/claims-v3/kinds/predictions-e101.json`. They were found by running the self-test,
   which goes through `score()`, and the `--anchors` import under an import and file-open trace:
   [`trace_scorer_e168.py`](trace_scorer_e168.py) → [`trace-scorer-e168.txt`](trace-scorer-e168.txt), which also checks that the
   sidecar covers all 16 files of that path. [`frozen-sha256-e168-scorer.txt`](frozen-sha256-e168-scorer.txt), new in this
   pass, lists the sha256 of all 18 (the 9, `frozen-sha256-e168.json`, the scorer and the 7), in `shasum` format with paths from
   this directory. Before the
   claim, run `shasum -a 256 -c frozen-sha256-e168-scorer.txt` here beside `score_e168.py check`. No frozen file changed: the 9
   hashes equal `frozen-sha256-e168.json`'s.
7. **D5, a rename after the first outputs (C12).** At 02:47 PST, after their outputs had been read, the repository-path variable
   in `stride_sm.py` and `posthoc_sm_policies.py` was renamed to `REPO`, and both were rerun. Their outputs are byte-identical to the
   first run's (the verifier compared the lane's saved copies with the committed files). D1-D4 did not list it.
8. **Times (C13).** `49575094`: committed 02:26:25, pushed 02:26:29 PST. `e39d06da`: committed 02:49:40, pushed 02:50:04 PST (the
   clone's remote-tracking log). The README's "02:26 PST" stands.
