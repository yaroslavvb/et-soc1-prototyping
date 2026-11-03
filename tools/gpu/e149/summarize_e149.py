"""E149's tables for the data README, from the committed JSON files (no fitting, no new numbers).

    python summarize_e149.py <data dir> > summary.md
"""
import json
import os
import sys

FMT_N = {"bf16": 2048, "fp16": 1024, "int8": 1024}


def f(x, d=1):
    return "—" if x is None else f"{x:.{d}f}"


def main(D):
    red = json.load(open(os.path.join(D, "reduce-stage1.json")))
    mz = json.load(open(os.path.join(D, "model-e149.json")))
    K = red["kinds"]
    out = []
    w = out.append

    def y(k):
        v = K.get(k)
        return (v["y"], v["se"], v["n"]) if v and v["y"] is not None else (None, None, 0)

    def cell(k):
        a, s, n = y(k)
        return f"{f(a)} ± {f(s)}" if a is not None else "invalid"
    w("### Stage 1, watts over the same GEMM on zeros (y ± SE over the valid replicates)\n")
    w("| bf16 zeros | 0% | 25% | 50% | 75% | 90% | 100% |\n|---|---:|---:|---:|---:|---:|---:|")
    w("| scattered | " + " | ".join(cell(k) for k in ["bf16.randn", "bf16.zs25", "bf16.zs50", "bf16.zs75", "bf16.zs90",
                                                         "bf16.zeros"]) + " |")
    w("| blocks of 64 along K | " + " | ".join(cell(k) for k in ["bf16.randn", "bf16.zb25", "bf16.zb50", "bf16.zb75",
                                                                    "bf16.zb90", "bf16.zeros"]) + " |")
    w(f"\nOne-sided 50% scattered: A only {cell('bf16.zsA50')}, B only {cell('bf16.zsB50')}. int8 scattered 0/25/50/75/90%: "
      + ", ".join(cell(k) for k in ["int8.rand", "int8.zs25", "int8.zs50", "int8.zs75", "int8.zs90"])
      + f"; blocks 50%: {cell('int8.zb50')}. fp16 50%/75% scattered {cell('fp16.zs50')} / {cell('fp16.zs75')}, 50% blocks "
      f"{cell('fp16.zb50')}.\n")
    w("| Hamming ladder from the base 1.0 (k flips per element) | base | rungs |\n|---|---:|---|")
    w(f"| bf16 mantissa (7 bits), k = 1, 2, 3, 5, 7 | {cell('bf16.base1')} | "
      + ", ".join(cell(f"bf16.mk{k}") for k in (1, 2, 3, 5, 7)) + " |")
    w(f"| bf16 exponent (low 5 bits), k = 1, 2, 3, 5 | {cell('bf16.base1')} | "
      + ", ".join(cell(f"bf16.ek{k}") for k in (1, 2, 3, 5)) + " |")
    w(f"| bf16 sign, p = 0.10, 0.25, 0.50 | {cell('bf16.base1')} | " + ", ".join(cell(f"bf16.sp{p}") for p in (10, 25, 50))
      + " |")
    w(f"| fp16 mantissa (10 bits), k = 1, 3, 5, 7, 10 | {cell('fp16.base1')} | "
      + ", ".join(cell(f"fp16.mk{k}") for k in (1, 3, 5, 7, 10)) + " |")
    w(f"| fp16 exponent (low 3 bits), k = 1, 2, 3 | {cell('fp16.base1')} | " + ", ".join(cell(f"fp16.ek{k}") for k in (1, 2, 3))
      + " |")
    w(f"| fp16 sign, p = 0.25, 0.50; A only 0.50 | {cell('fp16.base1')} | " + ", ".join(cell(k) for k in
                                                                                       ("fp16.sp25", "fp16.sp50", "fp16.sp50A")) + " |")
    w(f"| int8 bits 1–7 from 1, k = 1, 2, 3, 5, 7 | {cell('int8.base1')} | " + ", ".join(cell(f"int8.k{k}") for k in (1, 2, 3, 5, 7))
      + " |")
    w(f"| int8 p = 0.5 in bits 1–3, 4–6, 7; bit 7 on A only | {cell('int8.base1')} | "
      + ", ".join(cell(k) for k in ("int8.low", "int8.high", "int8.sign", "int8.signA")) + " |")
    w(f"\nSingle positions (p = 0.5), bf16 mantissa bits 0, 3, 6: " + ", ".join(cell(f"bf16.mb{b}") for b in (0, 3, 6))
      + "; exponent bits 0, 4: " + ", ".join(cell(f"bf16.eb{b}") for b in (0, 4)) + "; fp16 mantissa bits 0, 5, 9: "
      + ", ".join(cell(f"fp16.mb{b}") for b in (0, 5, 9)) + ". One-sided bf16 mantissa k = 3 A / B: "
      + f"{cell('bf16.mk3A')} / {cell('bf16.mk3B')}; exponent k = 2 A / B: {cell('bf16.ek2A')} / {cell('bf16.ek2B')}; "
      + f"fp16 mantissa k = 5 on A: {cell('fp16.mk5A')}; int8 random on A / B: {cell('int8.randA')} / {cell('int8.randB')}.\n")
    w("| bf16 signs, magnitude 1.5 | fixed + | A −, B + | random both | random A | random B | |randn| fixed + | same, random signs |")
    w("|---|---:|---:|---:|---:|---:|---:|---:|")
    w("| y | " + " | ".join(cell(k) for k in ("bf16.sfix", "bf16.sfixAneg", "bf16.srand", "bf16.srandA", "bf16.srandB",
                                               "bf16.smagfix", "bf16.smagrand")) + " |")
    w("\n| bf16 order | sorted along K | the same values shuffled | magnitudes sorted, random signs | sorted along M/N | sorted along K, rolled |")
    w("|---|---:|---:|---:|---:|---:|")
    w("| y | " + " | ".join(cell(k) for k in ("bf16.dsortK", "bf16.dshufK", "bf16.dabsK", "bf16.dsortM", "bf16.drollK")) + " |")
    w("\n| square wave along K, block b | 1 | 2 | 4 | 8 | 16 | 64 |\n|---|---:|---:|---:|---:|---:|---:|")
    w("| y | " + " | ".join(cell(f"bf16.sq{b}") for b in (1, 2, 4, 8, 16, 64)) + " |")
    w("\n### The models on stage 1 (rms W; nested = leave-one-kind-out)\n")
    w("| model | bf16 in · nested | fp16 in · nested | int8 in · nested |\n|---|---|---|---|")
    for m, fm in mz["models"].items():
        w(f"| {m}{' (lag ' + str(mz.get(m + '_lag')) + ')' if m in ('G1s', 'G4') else ''} | " + " | ".join(
            f"{f(fm[x]['rms_in'], 2)} · {f(fm[x]['rms_loko'], 2)}" for x in ("bf16", "fp16", "int8")) + " |")
    w("\nLag scan (G1's form at K-lag s; pooled nested rms over the three formats, W): " + ", ".join(
        f"s = {s}: {f(v['rms_loko_pooled'], 2)}" for s, v in sorted(mz["lag_scan"].items(), key=lambda t: int(t[0]))) + ".\n")
    tf = {}
    for k, v in K.items():
        if v.get("tflops"):
            tf.setdefault(k.split(".")[0], []).append(v["tflops"])
    w("### Frozen coefficients, G1 and G1s (W per flip per multiply-add; fJ per flip at the measured rate)\n")
    for m in ("G1", "G1s"):
        for fmt in ("bf16", "fp16", "int8"):
            fz = mz["models"][m][fmt]
            rate = sum(tf.get(fmt, [0])) / max(1, len(tf.get(fmt, []))) / 2.0 * 1e12
            parts = []
            for n, c in zip(fz["names"], fz["coef"]):
                fj = c / rate * 1e15 if rate else None
                parts.append(f"{n} {c:.2f}" + (f" ({fj:.0f} fJ)" if n.startswith("flip") and fj is not None else ""))
            w(f"- {m} {fmt} (MAC rate {rate / 1e12:.1f} T/s): " + "; ".join(parts))
    h = mz["heat"]
    hp = h["pooled"]
    w(f"\n### Heat\n\nPooled two-pole fit: τ₁ {hp['tau1']:.2f} s, τ₂ {hp['tau2']:.1f} s, r₁ {hp['r1']:.4f}, r₂ {hp['r2']:.4f} °C/W, "
      f"**die rise per board W {hp['R_ss']:.4f} °C/W**, {100 * hp['F30']:.0f}% of it in 30 s ({hp['rise30_per_W']:.4f} °C/W), "
      f"rms {hp['rms']:.2f} °C over {hp['n']} samples; grid edge {hp['edge']}.")
    for un, v in h["per_unit"].items():
        w(f"- unit {un}: τ₁ {v['tau1']:.2f} s, τ₂ {v['tau2']:.1f} s, R {v['R_ss']:.4f} °C/W, 30 s share {100 * v['F30']:.0f}%, rms "
          f"{v['rms']:.2f} °C; leakage {h['leakage'][un]['lambda_w_per_c']:.2f} W/°C over {h['leakage'][un]['T_range']} °C")
    w(f"- out-of-board 30 s rises (fit on one board, scored on the other): " + "; ".join(
        f"{c['fit_on']}→{c['scored_on']} {f(c['rms_c'], 2)} °C (n {c['n']})" for c in h["cross"]))
    w("\n### Stage 1's rules\n")
    for k, v in mz["rules_stage1"].items():
        w(f"- {k}: **{v['verdict']}**")
    sp = os.path.join(D, "score-e149.json")
    if os.path.exists(sp):
        sc = json.load(open(sp))
        w("\n### Stage 2, blind (measured − predicted, W)\n")
        w("| kind | measured y ± SE | G1 | G1s | G0 | S1 | G2 | G3 | G4 | G1 band | inside |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
        for k, v in sorted(sc["per_kind"].items()):
            w(f"| {k}{'' if v['blind'] else ' (seen)'} | {f(v['meas'])} ± {f(v['se'])} | " + " | ".join(
                f"{f(v['pred'][m])}" for m in ("G1", "G1s", "G0", "S1", "G2", "G3", "G4")) + f" | ±{f(v['band90_w'])} | "
              f"{'yes' if abs(v['err']['G1']) <= v['band90_w'] else 'no'} |")
        w("\n| model | rms | bias | worst | n |\n|---|---:|---:|---:|---:|")
        for m, v in sc["models"].items():
            w(f"| {m} | {f(v['rms_w'], 2)} | {f(v['bias_w'], 2)} | {f(v['max_abs_w'], 2)} | {v['n']} |")
        if sc.get("heat", {}).get("rows"):
            w("\n| hold (30 s after 15 s of zeros) | measured rise °C | blind | with measured power | band |\n|---|---:|---:|---:|---:|")
            for k, v in sorted(sc["heat"]["rows"].items()):
                w(f"| {k} | {f(v['meas_rise_c'], 2)} | {f(v['pred_blind_c'], 2)} | {f(v['pred_measP_c'], 2)} | ±{f(v['band90_c'], 2)} |")
        w("\nRules: " + "; ".join(f"{k} **{v['verdict']}**" for k, v in sc["rules"].items()))
        sec = sc.get("secondary_board_scale", {})
        if sec:
            w("\nA2's board-scaled arm (no verdict): power scale " + json.dumps({k: round(v, 4) for k, v in sec["power"]["scale"].items()})
              + "; " + "; ".join(f"{m} rms {f(v['rms_w'], 2)} bias {f(v['bias_w'], 2)} inside {v['inside']}/{v['of']}"
                                 for m, v in sec["power"].items() if m != "scale")
              + (f"; heat scale {json.dumps({k: round(v, 3) for k, v in sec['heat'].get('scale', {}).items()})}, rms "
                 f"{f(sec['heat'].get('rms_c'), 2)} °C, inside {sec['heat'].get('inside')}/{sec['heat'].get('of')}" if sec.get('heat') else ""))
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
