"""Print E162's tables (markdown) from the committed JSON files of the data directory.

    python summarize_e162.py <data dir> > <data dir>/summary.md
"""
import json
import os
import sys


def J(d, f):
    p = os.path.join(d, f)
    return json.load(open(p)) if os.path.exists(p) else None


def fy(v, nd=1):
    return "—" if v is None else f"{v:.{nd}f}"


def main():
    d = sys.argv[1]
    red1 = J(d, "reduce-a1.json")
    m = J(d, "model-e162-a100.json")
    pred = J(d, "predictions-e162-a100.json")
    sc = J(d, "score-e162-a100.json")
    ch = J(d, "choice-ls.json")
    out = []
    w = out.append
    if ch:
        w("## The L40S smoke (bf16, one 5 s window each)\n")
        w(f"Board `{ch['uuid_sha12']}`, enforced {ch['enforced_w']:.0f} W, NVML maximum {ch['nvml_max_sm']} MHz; held clock: "
          f"{ch['held_clock']} ({ch['held_rule']}); verdict: {ch['verdict']}.\n")
        w("| size | random W | random MHz | random TFLOPS | zeros W | zeros MHz | zeros TFLOPS | reason bits |")
        w("|---|---:|---:|---:|---:|---:|---:|---|")
        for r in ch["table"]:
            a, z = r["randn"], r["zeros"]
            w(f"| {r['n']}³ | {fy(a['p_w'])} | {a['sm_min']}–{a.get('sm_max')} | {fy(a['tflops'])} | {fy(z['p_w'])} | "
              f"{z['sm_min']}–{z.get('sm_max')} | {fy(z['tflops'])} | {hex(a['rsn_or'])} / {hex(z['rsn_or'])} in "
              f"{a['cap_frac']:.0%} / {z['cap_frac']:.0%} of samples |")
        w("")
    if red1:
        K = red1["kinds"]

        def row(k):
            v = K.get(k)
            return "—" if not v or v["y"] is None else f"{v['y']:.1f} ± {v['se']:.1f}" if v.get("se") else f"{v['y']:.1f}"
        w("## A100 stage 1: y (W over zeros, this session's boards), ± SE over 2 boards × 2 passes\n")
        w("| b | 1 | 2 | 4 | 8 | 16 | 32 | 64 |")
        w("|---|---:|---:|---:|---:|---:|---:|---:|")
        w("| K wave, shared phase (`kS`) | " + " | ".join(row(f"bf16.kS{b}") for b in (1, 2, 4, 8, 16, 32, 64)) + " |")
        w("| K wave, phase per row (E149's `sq`) | " + " | ".join(row(f"bf16.sq{b}") if b in (1, 16, 64) else "—"
                                                              for b in (1, 2, 4, 8, 16, 32, 64)) + " |")
        w("| row wave, shared phase (`rS`) | " + " | ".join(row(f"bf16.rS{b}") for b in (1, 2, 4, 8, 16, 32, 64)) + " |")
        w("")
        w("| kind | y |")
        w("|---|---:|")
        for k in ("bf16.rC16", "bf16.rowc", "bf16.colc", "bf16.rowcA_colcB", "bf16.colcA_rowcB", "bf16.rollM",
                  "bf16.drollK", "bf16.dsortK", "bf16.dshufK", "bf16.dsortM", "bf16.kS1A", "bf16.kS1B", "bf16.rS1A",
                  "bf16.rS1B", "bf16.randn", "bf16.mk3", "fp16.kS1", "fp16.kS16", "fp16.rS1", "fp16.rS16", "fp16.rowc",
                  "fp16.colc", "fp16.randn", "fp16.mk5", "int8.kS1", "int8.kS16", "int8.rS1", "int8.rS16", "int8.rowc",
                  "int8.colc", "int8.rand", "int8.k3"):
            w(f"| `{k}` | {row(k)} |")
        w("")
    if m:
        w("## The fit (A100, pooled rows on E149's stage-1 footing)\n")
        w(f"Rows: {m['n_rows']}; session scale c (E162 y over E149 y on the bridge kinds): "
          + ", ".join(f"{f} {v['c']:.4f} (n {v['n']}, rms diff {v['rms_diff_w']:.1f} W)" for f, v in m["scale"].items())
          + f"; E149 rows left out: {m['left_out_e149_rows'] or 'none'}.\n")
        rk = m["rk"]
        w(f"RK chose K-lag s = {rk['s']}, row-lag r = {rk['r']}. Scan (pooled LOKO rms, W), the best 8:\n")
        best = sorted(rk["scan"].items(), key=lambda x: x[1]["rms_loo_pooled"])[:8]
        w("| (s, r) | pooled | bf16 | fp16 | int8 |")
        w("|---|---:|---:|---:|---:|")
        for key, v in best:
            w(f"| ({key}) | {v['rms_loo_pooled']:.2f} | " + " | ".join(f"{v['by_fmt'][f]:.2f}" for f in ("bf16", "fp16", "int8"))
              + " |")
        w("")
        w("| model | bf16 in · nested | fp16 in · nested | int8 in · nested |")
        w("|---|---|---|---|")
        w("| RK (ridge; nested = fully nested) | " + " | ".join(
            f"{rk['fmts'][f]['rms_in']:.2f} · {rk['nested'][f]['rms_nested']:.2f}" for f in ("bf16", "fp16", "int8")) + " |")
        w("| RK form by OLS at (s, r) | " + " | ".join(
            f"{rk['ols_at_choice'][f]['rms_in']:.2f} · {rk['ols_at_choice'][f]['rms_loko']:.2f}" for f in ("bf16", "fp16", "int8"))
          + " |")
        for nm, key in (("G1p (G1's form, OLS)", "g1p"), (f"G4p (G4's form, lag {m['g4p'].get('lag')}, OLS)", "g4p")):
            w(f"| {nm} | " + " | ".join(f"{m[key]['fmts'][f]['rms_in']:.2f} · {m[key]['fmts'][f]['rms_loko']:.2f}"
                                       for f in ("bf16", "fp16", "int8")) + " |")
        w("")
        st = m["stable"]
        w(f"STABLE: **{st['verdict']}** — " + "; ".join(
            f"{f}: nested {v['rms_nested']:.2f} / in {v['rms_in']:.2f} = {v['ratio']:.2f}" for f, v in st["by_fmt"].items())
          + f"; pooled nested {st['pooled']['rk_rms_nested']:.2f} against G1's form {st['pooled']['g1form_rms_loko']:.2f} W.\n")
        g = m["g1_frozen_on_new_rows"]
        w(f"E149's frozen G1 on E162's {len(g['rows'])} new stage-1 kinds (never in its fit): {g['rms_w']:.1f} W rms, "
          f"bias {g['bias_w']:+.1f} W.\n")
        w("RK's coefficients (W per unit of each feature, E149's footing):\n")
        for f, v in rk["fmts"].items():
            w(f"- {f} (λ {v['lam']:g}): " + ", ".join(f"{n} {c:+.1f}" for n, c in zip(v["names"], v["coef"])))
        w("")
        R = m["rules_stage1"]
        w("## Which pairing (stage 1 rules)\n")
        for k in ("W1", "W2", "W3", "W5", "R4b"):
            if k in R:
                v = R[k]
                ds = v.get("diffs") or [v.get("diff")]
                w(f"- **{k}** {v['verdict']}: {v.get('what', '')}: " + "; ".join(
                    f"{x['a']} − {x['b']} = {x['diff']:+.1f} ± {x['se']:.1f} W" for x in ds if x))
        for f, v in R.get("W4", {}).items():
            x = v["diff"]
            w(f"- **W4** {f}: {v['verdict']}" + (f" (rowc − colc = {x['diff']:+.1f} ± {x['se']:.1f} W)" if x else ""))
        for kk, v in R.get("W6", {}).items():
            x = v["diff"]
            w(f"- W6 {kk}: {v['verdict']}" + (f" (A only − B only = {x['diff']:+.1f} ± {x['se']:.1f} W)" if x else ""))
        w("")
    if sc:
        w("## Stage 2, blind: the held-out kinds on new boards\n")
        boards = ", ".join("%s %s (%s)" % (u, v.get("uuid_sha12"), v.get("name")) for u, v in sc["units"].items())
        w(f"Boards: {boards}; refused: {sc.get('refused') or 'none'}.\n")
        w("| kind | measured y ± SE | RK | G1 (E149) | G1p | G4p | E149 G4 | RK band | inside |")
        w("|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for k in sorted(sc["per_kind"]):
            v = sc["per_kind"][k]
            p = v["pred"]
            ins = "yes" if abs(v["err"]["RK"]) <= v["band90_w"] else "no"
            w(f"| `{k}` | {v['meas']:.1f} ± {fy(v['se'])} | {p['RK']:.1f} | {p['G1']:.1f} | {p['G1p']:.1f} | {p['G4p']:.1f} | "
              f"{p['e149_G4']:.1f} | ±{v['band90_w']:.1f} | {ins} |")
        w("")
        w("| model | rms W | bias W | worst W | bf16 rms | fp16 rms | int8 rms | board-scaled rms |")
        w("|---|---:|---:|---:|---:|---:|---:|---:|")
        sec = sc["secondary_board_scale"]
        for mm, v in sorted(sc["models"].items(), key=lambda x: x[1]["rms_w"]):
            bf = v["by_fmt"]
            w(f"| {mm} | {v['rms_w']:.2f} | {v['bias_w']:+.2f} | {v['max_abs_w']:.1f} | "
              + " | ".join(fy(bf.get(f, {}).get("rms"), 2) for f in ("bf16", "fp16", "int8"))
              + f" | {fy(sec.get(mm, {}).get('rms_w'), 2)} |")
        w("")
        for k in ("BEAT", "BEAT_p"):
            v = sc["rules"][k]
            w(f"- **{k}** {v['verdict']}: rms RK {v['rms_rk']:.2f} against {v['rms_g1']:.2f} W (ratio {v['ratio']:.3f}, bar 0.8); "
              f"difference {v['diff']:+.2f} W, paired bootstrap 95% [{v['ci95'][0]:+.2f}, {v['ci95'][1]:+.2f}] over {v['n']} kinds")
        st = sc["rules"]["STABLE"]
        w(f"- **STABLE** {st['verdict']} (stage 1)")
        if "HT1" in sc["rules"]:
            h = sc["rules"]["HT1"]
            w(f"- **HT1** {h['verdict']}: cell die rise over its references, rms RK {h['rms_RK_c']:.3f} °C, G1 "
              f"{h['rms_G1_c']:.3f} °C, measured power {h['rms_measP_c']:.3f} °C")
        ib = sc["rules"]["inside_band_RK"]
        w(f"- RK's band: {ib['inside']} of {ib['of']} inside")
        w(f"- board scales (y(bf16 randn) over the fit's span): {sec['scale']}")
        a = sc.get("seen_kinds_e149_stage2")
        if a:
            w(f"- seen-kinds arm (E149's 17 held-out kinds, E149's stage-2 y; not blind to the designer): "
              + ", ".join(f"{mm} {a[mm]['rms_w']:.2f} W (bias {a[mm]['bias_w']:+.2f})" for mm in ("RK", "G1p", "G4p", "G1")))
        w("")
    print("\n".join(out))


if __name__ == "__main__":
    main()
