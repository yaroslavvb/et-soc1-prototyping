#!/usr/bin/env python3
"""Q129 desk-reduce-a3: every sensitivity number, published slope vs E71's measured 0.3803 W/C."""
import json, sys

# argv[1]: refit.sh's output directory.  argv[2]: the repo's docs/reports/data.  Run from the repo root.
W = sys.argv[1] if len(sys.argv) > 1 else "build/q129-leak-sensitivity"
D = sys.argv[2] if len(sys.argv) > 2 else "docs/reports/data"
K = 0.3803
J = lambda p: json.load(open(p))


def pc(a, b):
    return float("nan") if not a else 100 * (b / a - 1)


def line(name, a, b, u="", f="%.4g"):
    print(("  %-44s " + f + " -> " + f + " %s  %+7.2f%%") % (name, a, b, u, pc(a, b)))


out = {"slope_published_vs_measured": {"measured_W_per_C": K, "source": "E71 slopes.json, aifoundry3 58-62 C"}}

# ───────────────────────────── E60, aifoundry3 rows
print("=" * 104)
print("E60 (2026-10-20-bitflip-ladder) aifoundry3, auto k 0.20265 -> %.4f W/C" % K)
print("=" * 104)
a = J(W + "/e60-a3-k0.2026495726495783.json")["cards"]["aifoundry3"]
b = J(W + "/e60-a3-k" + str(K) + ".json")["cards"]["aifoundry3"]
e60 = {}
for fam in ("lq", "lb"):
    for lv in ("designed", "bus", "nets"):
        x, y = a[fam][lv], b[fam][lv]
        sx, sy = x["se_J"] * 1e15, y["se_J"] * 1e15
        line(f"{fam} per {lv} fJ", x["fJ"], y["fJ"], f"(se {sx:.3f} -> {sy:.3f})")
        e60[f"{fam}_{lv}_fJ"] = {"published": x["fJ"], "at_measured_slope": y["fJ"],
                                 "se_published": sx, "se_at_measured_slope": sy,
                                 "pct": pc(x["fJ"], y["fJ"])}
    line(f"{fam} first flip W", a[fam]["first_flip_W"]["W"], b[fam]["first_flip_W"]["W"],
         f"(se {a[fam]['first_flip_W']['se']:.4f} -> {b[fam]['first_flip_W']['se']:.4f})")
    line(f"{fam} marginal W per h", a[fam]["linear"]["W_per_h"], b[fam]["linear"]["W_per_h"])
    line(f"{fam} intercept W", a[fam]["linear"]["intercept_W"], b[fam]["linear"]["intercept_W"])
    e60[f"{fam}_first_flip_W"] = {"published": a[fam]["first_flip_W"], "at_measured_slope": b[fam]["first_flip_W"]}
    e60[f"{fam}_rungs"] = {rk: {"published": a[fam]["rungs"][rk], "at_measured_slope": b[fam]["rungs"][rk]}
                           for rk in a[fam]["rungs"]}
    e60[f"{fam}_linear"] = {"published": a[fam]["linear"], "at_measured_slope": b[fam]["linear"]}
print("  the 6 B positions E60 priced (fJ per alternating bit):")
e60["bits_fJ"] = {}
for k in sorted(a["bits"], key=int):
    x = a["bits"][k]["J_per_alternating_bit"] * 1e15
    y = b["bits"][k]["J_per_alternating_bit"] * 1e15
    print("    bit %-3s %8.1f -> %8.1f fJ  %+6.2f%%" % (k, x, y, pc(x, y)))
    e60["bits_fJ"][k] = {"published": x, "at_measured_slope": y, "pct": pc(x, y)}
print("  anchors (W):", ", ".join("%s %.2f->%.2f" % (n, a["anchors"][n]["p80"], b["anchors"][n]["p80"])
                                  for n in sorted(a["anchors"])))
e60["anchors_W"] = {n: {"published": a["anchors"][n]["p80"], "at_measured_slope": b["anchors"][n]["p80"]}
                    for n in sorted(a["anchors"])}
e60["kept"] = {"published": J(W + "/e60-a3-k0.2026495726495783.json")["gates"]["aifoundry3"]["kept"],
               "at_measured_slope": J(W + "/e60-a3-k" + str(K) + ".json")["gates"]["aifoundry3"]["kept"]}
e60["passes_set_aside_changed"] = (J(W + "/e60-a3-k0.2026495726495783.json")["gates"]["aifoundry3"]["passes_set_aside"]
                                   != J(W + "/e60-a3-k" + str(K) + ".json")["gates"]["aifoundry3"]["passes_set_aside"])
print("  kept runs %s -> %s; pass set-aside list changed: %s" % (e60["kept"]["published"],
      e60["kept"]["at_measured_slope"], e60["passes_set_aside_changed"]))
out["e60_aifoundry3"] = e60

# ───────────────────────────── E65 blocks A+B: the 32 B positions and the flow-M row
print("=" * 104)
print("E65 blocks A+B, auto k 0.18238 -> %.4f W/C   (the flow-M row is bpi_11)" % K)
print("=" * 104)
ca = J(W + "/e65ab-k0.18237745098038693.json")["cards"]["aifoundry3"]
cb = J(W + "/e65ab-k" + str(K) + ".json")["cards"]["aifoundry3"]
e65 = {"bits_fJ": {}, "bpi_fJ": {}}
for k in sorted(ca["bits"], key=int):
    x = ca["bits"][k]["J_per_alternating_bit"] * 1e15
    y = cb["bits"][k]["J_per_alternating_bit"] * 1e15
    e65["bits_fJ"][k] = {"published": x, "at_measured_slope": y, "pct": pc(x, y)}
bp, bq = ca["bits_pi"], cb["bits_pi"]
for k in sorted(bp, key=int):
    x, y = bp[k]["J_per_alternating_bit"] * 1e15, bq[k]["J_per_alternating_bit"] * 1e15
    print("  bpi bit %-3s %8.1f -> %8.1f fJ  %+6.2f%%   (dW %.3f -> %.3f W)"
          % (k, x, y, pc(x, y), bp[k]["dW"], bq[k]["dW"]))
    e65["bpi_fJ"][k] = {"published": x, "at_measured_slope": y, "pct": pc(x, y),
                        "dW_published": bp[k]["dW"], "dW_at_measured_slope": bq[k]["dW"],
                        "se_published": bp[k]["se"], "se_at_measured_slope": bq[k]["se"]}
lo = [e65["bits_fJ"][str(j)] for j in range(10)]
print("  B list: low-mantissa mean %.1f -> %.1f fJ (%+.2f%%); bit22 %.0f -> %.0f; span %.2fx -> %.2fx"
      % (sum(r["published"] for r in lo) / 10, sum(r["at_measured_slope"] for r in lo) / 10,
         pc(sum(r["published"] for r in lo) / 10, sum(r["at_measured_slope"] for r in lo) / 10),
         e65["bits_fJ"]["22"]["published"], e65["bits_fJ"]["22"]["at_measured_slope"],
         max(r["published"] for r in e65["bits_fJ"].values()) / min(r["published"] for r in e65["bits_fJ"].values()),
         max(r["at_measured_slope"] for r in e65["bits_fJ"].values()) / min(r["at_measured_slope"] for r in e65["bits_fJ"].values())))
out["e65_blocks_ab"] = e65

# ───────────────────────────── E67: the 32 A positions and the interaction grid
print("=" * 104)
print("E67 registered, auto k 0.17545 -> %.4f W/C   (block 3 = the interaction grid)" % K)
print("=" * 104)
ea = J(W + "/e67-k0.17545454545454092.json")["cards"]["aifoundry3"]
eb = J(W + "/e67-k" + str(K) + ".json")["cards"]["aifoundry3"]
e67 = {"a_bits_fJ": {}, "abp_fJ": {}}
A = ea.get("a_bits") or {}
Bb = eb.get("a_bits") or {}
for k in sorted(A, key=int):
    x, y = A[k]["J_per_alternating_bit"] * 1e15, Bb[k]["J_per_alternating_bit"] * 1e15
    e67["a_bits_fJ"][k] = {"published": x, "at_measured_slope": y, "pct": pc(x, y)}
pa, pb_ = ea["a_bits_pi"], eb["a_bits_pi"]
for k in sorted(pa, key=int):
    x, y = pa[k]["J_per_alternating_bit"] * 1e15, pb_[k]["J_per_alternating_bit"] * 1e15
    print("  abp bit %-3s %8.1f -> %8.1f fJ  %+6.2f%%" % (k, x, y, pc(x, y)))
    e67["abp_fJ"][k] = {"published": x, "at_measured_slope": y, "pct": pc(x, y)}
ga, gb = ea.get("ix", {}), eb.get("ix", {})
for f in ("base_W", "excess_mean_W", "excess_mean_se", "excess_abs_max_W", "excess_frac_mean"):
    if ga.get(f) is not None:
        line("grid " + f, ga[f], gb[f])
e67["grid"] = {f: {"published": ga.get(f), "at_measured_slope": gb.get(f)}
               for f in ("base_W", "excess_mean_W", "excess_mean_se", "excess_abs_max_W", "excess_frac_mean")}
w20a = sum(1 for c in ga["cells"].values() if c["excess_frac_of_sum"] is not None and abs(c["excess_frac_of_sum"]) < 0.20)
w20b = sum(1 for c in gb["cells"].values() if c["excess_frac_of_sum"] is not None and abs(c["excess_frac_of_sum"]) < 0.20)
print("  grid cells within 20%%: %d/16 -> %d/16; all |excess| <= 0.5 W: %s -> %s"
      % (w20a, w20b, all(abs(c["excess_W"]) <= 0.5 for c in ga["cells"].values()),
         all(abs(c["excess_W"]) <= 0.5 for c in gb["cells"].values())))
e67["grid"]["cells_within_20pct"] = {"published": w20a, "at_measured_slope": w20b}
e67["grid"]["cells"] = {k: {"published": ga["cells"][k], "at_measured_slope": gb["cells"][k]} for k in ga["cells"]}
sa, sb = J(W + "/e67-scored-pub.json"), J(W + "/e67-scored-k.json")
_P = [f"P{i}" for i in range(1, 9)]
print("  E67 verdicts:", " ".join("%s %s->%s" % (p, sa[p]["verdict"], sb[p]["verdict"]) for p in _P))
e67["verdicts"] = {p: {"published": sa[p]["verdict"], "at_measured_slope": sb[p]["verdict"]} for p in _P}
e67["P6"] = {"published": sa["P6"], "at_measured_slope": sb["P6"]}
e67["P8"] = {"published": sa["P8"], "at_measured_slope": sb["P8"]}
e67["marginal_A_over_B"] = {"published": sa["marginal_A_over_B"], "at_measured_slope": sb["marginal_A_over_B"]}
e67["verdicts_changed"] = [p for p in e67["verdicts"] if e67["verdicts"][p]["published"] != e67["verdicts"][p]["at_measured_slope"]]
wa, wb = sa["whole_operand_additivity"], sb["whole_operand_additivity"]
for f in sorted(wa):
    if isinstance(wa[f], (int, float)) and not isinstance(wa[f], bool):
        line("whole-operand " + f, wa[f], wb[f])
e67["whole_operand_additivity"] = {"published": wa, "at_measured_slope": wb}
out["e67"] = e67

# ───────────────────────────── the closure (E67's own closure.py, both slopes)
print("=" * 104)
print("E67 closure (closure.py over the same operand files)")
print("=" * 104)
cpa, cpb = J(W + "/closure-pub.json"), J(W + "/closure-k.json")
cl = {}
for s in ("nrd_a", "nrd_b"):
    x, y = cpa["items"][s], cpb["items"][s]
    print("  %s predicted %.4f -> %.4f W (%+.2f%%), measured %.4f -> %.4f W (%+.2f%%), ratio %.4f -> %.4f"
          % (s, x["predicted_W"], y["predicted_W"], pc(x["predicted_W"], y["predicted_W"]),
             x["measured_W"], y["measured_W"], pc(x["measured_W"], y["measured_W"]),
             x["ratio_measured_over_predicted"], y["ratio_measured_over_predicted"]))
    cl[s] = {k: {"published": x[k], "at_measured_slope": y[k]} for k in
             ("predicted_W", "measured_W", "ratio_measured_over_predicted")}
line("turn_on_W (minus the grid's mean excess)", cpa["turn_on_W"], cpb["turn_on_W"])
cl["turn_on_W"] = {"published": cpa["turn_on_W"], "at_measured_slope": cpb["turn_on_W"]}
out["e67_closure"] = cl

# ───────────────────────────── E70
print("=" * 104)
print("E70 saturation ladder + A-side ladder, auto k 0.19750 -> %.4f W/C" % K)
print("=" * 104)
ta, tb = J(W + "/e70-scored-pub.json"), J(W + "/e70-scored-k.json")
e70 = {}
for fam in ("lq", "ls", "alq"):
    print("  --- %s rungs (dW W, se, fJ/bit) ---" % fam)
    e70[fam] = {}
    for x, y in zip(ta[fam], tb[fam]):
        rk = x["item"]
        assert y["item"] == rk
        print("    %-10s %7.3f +- %5.3f -> %7.3f +- %5.3f W  %+6.2f%%   fJ/bit %6.1f -> %6.1f"
              % (rk, x["dW"], x.get("se") or 0, y["dW"], y.get("se") or 0, pc(x["dW"], y["dW"]),
                 x.get("fJ_per_bit") or 0, y.get("fJ_per_bit") or 0))
        e70[fam][rk] = {"dW_published": x["dW"], "dW_at_measured_slope": y["dW"],
                        "se_published": x.get("se"), "se_at_measured_slope": y.get("se"),
                        "fJ_per_bit_published": x.get("fJ_per_bit"), "fJ_per_bit_at_measured_slope": y.get("fJ_per_bit"),
                        "pct": pc(x["dW"], y["dW"])}
for key in ("D1", "D2", "D3", "D4", "D5", "P3", "ceilings", "A_ceiling", "carry_over_measured",
            "law_W_frozen_Winf_W", "turn_on_T_W", "turn_on_T_se_W", "verdict_Q128_s5_item2"):
    if key not in ta:
        continue
    x, y = ta[key], tb[key]
    if isinstance(x, list):
        e70[key] = []
        for u, v in zip(x, y):
            row = {}
            for f in sorted(u):
                if isinstance(u[f], (int, float)) and not isinstance(u[f], bool) and isinstance(v.get(f), (int, float)):
                    row[f] = {"published": u[f], "at_measured_slope": v[f]}
            e70[key].append(row)
            lab = u.get("h", u.get("item", "?"))
            main = "dW_ls_minus_lq" if "dW_ls_minus_lq" in u else ("rho_per_bit" if "rho_per_bit" in u else None)
            if main:
                line(f"{key} h={lab} {main}", u[main], v[main])
        continue
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        line(key, x, y)
        e70[key] = {"published": x, "at_measured_slope": y}
    elif isinstance(x, dict):
        e70[key] = {}
        for f in sorted(x):
            if isinstance(x[f], (int, float)) and not isinstance(x[f], bool) and isinstance(y.get(f), (int, float)):
                line(f"{key}.{f}", x[f], y[f])
                e70[key][f] = {"published": x[f], "at_measured_slope": y[f]}
            elif isinstance(x[f], str):
                if x[f] != y.get(f):
                    print(f"  {key}.{f}: {x[f]!r} -> {y.get(f)!r}")
                e70[key][f] = {"published": x[f], "at_measured_slope": y.get(f)}
    else:
        if x != y:
            print(f"  {key}: {x!r} -> {y!r}")
        e70[key] = {"published": x, "at_measured_slope": y}
print("  E70 verdicts:", " ".join("%s %s->%s" % (p, ta["scored"][p]["verdict"], tb["scored"][p]["verdict"])
                                  for p in sorted(ta["scored"])))
e70["verdicts"] = {p: {"published": ta["scored"][p]["verdict"], "at_measured_slope": tb["scored"][p]["verdict"]}
                   for p in sorted(ta["scored"])}
e70["verdicts_changed"] = [p for p in e70["verdicts"] if e70["verdicts"][p]["published"] != e70["verdicts"][p]["at_measured_slope"]]
e70["passes_kept"] = {"published": ta.get("passes_kept"), "at_measured_slope": tb.get("passes_kept")}
out["e70"] = e70

# ───────────────────────────── Q128's own data block
print("=" * 104)
print("Q128 data.json, rebuilt through chain.py + build_data.py at the measured slope")
print("=" * 104)
da, db = J(D + "/2026-10-27-matmul-to-transistor/data.json"), J(W + "/q128-data-at-0.3803.json")
cha, chb = J(D + "/2026-10-27-chain-closure/chain.json"), J(W + "/chain-k/chain.json")
q = {}
for nm, x, y in (("flowM_fJ (E65 bpi_11)", cha["price_list"]["B_pi_fJ"]["11"], chb["price_list"]["B_pi_fJ"]["11"]),
                 ("flowM_A_side_fJ (E67 abp_11)", e67["abp_fJ"]["11"]["published"], e67["abp_fJ"]["11"]["at_measured_slope"]),
                 ("flat_fJ_per_bit", da["perbit"]["flat_fJ_per_bit"], db["perbit"]["flat_fJ_per_bit"]),
                 ("flat_marginal_fJ", da["perbit"]["flat_marginal_fJ"], db["perbit"]["flat_marginal_fJ"]),
                 ("beta", da["perbit"]["beta"], db["perbit"]["beta"]),
                 ("B_span", da["perbit"]["B_span"], db["perbit"]["B_span"]),
                 ("A_span", da["perbit"]["A_span"], db["perbit"]["A_span"]),
                 ("e60_lq_fJ", da["perbit"]["e60_lq_fJ"], e60["lq_designed_fJ"]["at_measured_slope"]),
                 ("e60_lb_fJ", da["perbit"]["e60_lb_fJ"], e60["lb_designed_fJ"]["at_measured_slope"]),
                 ("laws.flat.rms", da["perbit"]["laws"]["flat"]["rms"], db["perbit"]["laws"]["flat"]["rms"]),
                 ("laws.free_power.rms", da["perbit"]["laws"]["free_power"]["rms"], db["perbit"]["laws"]["free_power"]["rms"]),
                 ("laws.price_list_compressed.rms", da["perbit"]["laws"]["price_list_compressed"]["rms"],
                  db["perbit"]["laws"]["price_list_compressed"]["rms"]),
                 ("permac data pJ", da["permac"]["this_work_data_pJ"], db["permac"]["this_work_data_pJ"]),
                 ("permac clocking pJ", da["permac"]["this_work_clocking_pJ"], db["permac"]["this_work_clocking_pJ"]),
                 ("board step_W", da["board"]["step_W"], db["board"]["step_W"]),
                 ):
    line(nm, x, y)
    q[nm] = {"published": x, "at_measured_slope": y, "pct": pc(x, y)}
print("  waterfall identical: %s" % (da["waterfall"] == db["waterfall"]))
print("  transistor/floor/gates/rail/toggles identical: %s" %
      all(da[k] == db[k] for k in ("transistor", "floor", "gates", "rail", "toggles")))
q["waterfall_identical"] = da["waterfall"] == db["waterfall"]
q["bottom_up_blocks_identical"] = all(da[k] == db[k] for k in ("transistor", "floor", "gates", "rail", "toggles"))
out["q128_data"] = q
out["q128_perbit_B_fJ"] = {k: {"published": da["perbit"]["B_fJ"][k], "at_measured_slope": db["perbit"]["B_fJ"][k]}
                           for k in da["perbit"]["B_fJ"]}
out["q128_perbit_A_fJ"] = {k: {"published": da["perbit"]["A_fJ"][k], "at_measured_slope": db["perbit"]["A_fJ"][k]}
                           for k in da["perbit"]["A_fJ"]}
out["q128_perbit_shape"] = {"published": da["perbit"]["shape"], "at_measured_slope": db["perbit"]["shape"]}
out["q128_perbit_ladder_rows"] = {"published": da["perbit"]["ladder_rows"], "at_measured_slope": db["perbit"]["ladder_rows"]}

json.dump(out, open(W + "/sensitivity.json", "w"), indent=1, sort_keys=True)
print("\nwrote sensitivity.json")
