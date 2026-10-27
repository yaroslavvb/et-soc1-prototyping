#!/usr/bin/env python3
"""Check the structural mapping against a direct simulation of the post-CTS netlist.

The post-CTS netlist OpenROAD writes is FLAT, so its net names ARE the extractor's names: a SAIF
taken on it needs no mapping at all. Comparing it net by net against the activity the structural
rules infer from the pre-route SAIF is the test of those rules.
"""
import gzip, json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

D = os.path.dirname(os.path.abspath(__file__)) + "/"
pat = sys.argv[1] if len(sys.argv) > 1 else "randn"
VDD = 0.517
V2 = VDD * VDD
MA = 512.0
CLK = re.compile(r"(^|/)(clock|clk|CLK)(\[|$|/)|clknet|clkbuf")

cap = {}
for line in open(D + "in/net_cap_keep.txt"):
    if line.startswith("#"):
        continue
    p = line.split()
    if len(p) >= 3:
        cap[p[0]] = (float(p[1]) + float(p[2])) * 1e15

pnr = json.load(gzip.open(D + f"in/red/pnr_{pat}.json.gz"))
psim = {k.replace("\\", ""): v for k, v in pnr["toggles"].items()}
pnames = set(n.replace("\\", "") for n in pnr["names_measured"])

rows = json.load(gzip.open(D + f"res/q129_syn_{pat}-nets.json.gz"))
inferred = {r["net"]: (r["toggles"], r["method"]) for r in rows}

miss_name = {n: c for n, c in cap.items() if n not in pnames}
print(f"extracted nets {len(cap)}   not named by the post-CTS simulation: {len(miss_name)} "
      f"({sum(miss_name.values()):.1f} fF, {sum(miss_name.values())/sum(cap.values())*100:.2f}%)")
if miss_name:
    for n, c in sorted(miss_name.items(), key=lambda kv: -kv[1])[:8]:
        print(f"   {c:8.2f} fF  {n}")

# energy from the direct post-CTS SAIF, over ALL extracted nets
e_s = e_c = t_s = t_c = 0.0
for n, c in cap.items():
    v = psim.get(n, 0)
    e = 0.5 * c * 1e-15 * V2 * v
    if CLK.search(n):
        e_c += e; t_c += v
    else:
        e_s += e; t_s += v
print(f"post-CTS SAIF, all extracted nets: signal {t_s/MA:9.2f} tog/MAC {e_s/MA*1e12:.4f} pJ | "
      f"clock {t_c/MA:7.2f} tog/MAC {e_c/MA*1e12:.4f} pJ | total {(e_s+e_c)/MA*1e12:.4f} pJ")

# net-by-net disagreement, on the nets the structural rules had to infer
agree = dis = 0
dis_tog = 0.0
dis_e = 0.0
worst = []
for n, (t, m) in inferred.items():
    if m in ("direct", "cts_name"):
        continue
    d = psim.get(n, 0)
    t = t or 0
    if d == t:
        agree += 1
    else:
        dis += 1
        dis_tog += (d - t)
        de = 0.5 * cap.get(n, 0) * 1e-15 * V2 * (d - t)
        dis_e += de
        worst.append((abs(de), n, m, t, d, cap.get(n, 0)))
print(f"\ninferred nets checked: {agree+dis}  exact {agree}  differ {dis}  "
      f"net toggle error {dis_tog/MA:+.2f}/MAC  energy error {dis_e/MA*1e12:+.5f} pJ/MAC")
worst.sort(reverse=True)
print("worst by energy error:")
for de, n, m, t, d, c in worst[:10]:
    print(f"   {de/MA*1e12:+.5f} pJ/MAC  {m:9s} inferred {t:7.0f} direct {d:7.0f}  {c:7.2f} fF  {n}")

# the nets the published join DID price: how far apart are the two simulations themselves?
syn = json.load(gzip.open(D + f"in/red/syn_{pat}.json.gz"))
ssim = {k.replace("\\", ""): v for k, v in syn["toggles"].items()}
dt = de2 = 0.0
nd = 0
for n, c in cap.items():
    if n in ssim:
        d = psim.get(n, 0)
        dt += d - ssim[n]
        de2 += 0.5 * c * 1e-15 * V2 * (d - ssim[n])
        nd += 1
print(f"\nnets both simulations name ({nd}): post-CTS minus pre-route "
      f"{dt/MA:+.2f} toggles/MAC, {de2/MA*1e12:+.5f} pJ/MAC "
      "(two Verilator runs of logically identical netlists)")
import json as _j
_j.dump({"pattern": pat,
         "extracted_nets": len(cap),
         "nets_not_named_by_post_cts_sim": len(miss_name),
         "cap_fF_not_named_by_post_cts_sim": sum(miss_name.values()),
         "post_cts_direct": {"signal_toggles_per_muladd": t_s/MA,
                             "clock_toggles_per_muladd": t_c/MA,
                             "signal_pJ_per_muladd": e_s/MA*1e12,
                             "clock_pJ_per_muladd": e_c/MA*1e12,
                             "pJ_per_muladd": (e_s+e_c)/MA*1e12},
         "inferred_vs_direct": {"nets_checked": agree+dis, "exact": agree, "differ": dis,
                                "toggle_error_per_muladd": dis_tog/MA,
                                "energy_error_pJ_per_muladd": dis_e/MA*1e12},
         "two_sims_on_shared_nets": {"nets": nd, "toggle_delta_per_muladd": dt/MA,
                                     "energy_delta_pJ_per_muladd": de2/MA*1e12}},
        open(D + f"res/cmp_{pat}.json", "w"), indent=1)
