#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q145(b): term S, a per-position single-high-B-bit term for M10, fitted leave one run out on the committed single-bit price
lists, exactly as tools/claims-v3/m10-s/REGISTRATION.md (committed dfc005bf before this file existed) registers it.

    python3 -B term_s.py selftest                       # the checks of the registration's Builds on block; no residual is computed
    python3 -B term_s.py fit --out <dir> [--footing reg|law] [--base <m10-law.json>]
                                                        # the 95 steps, the four forms, E1-E3, the frozen term, the post hoc readings

--footing reg (default): Q139(u)'s frozen slopes, M10 as frozen. --footing law: each list at FL3's k_s = k_c(T_mid), the base M10 on
the law from --base (law_m10.py's output), or, without --base, M10's first-order one-footing companion (FL7's form). Standard library
and numpy 1.26. Nothing here writes outside --out.
SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse  # noqa: E402
import glob  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DD = os.path.join(TOP, "docs", "reports", "data")
CV = os.path.join(TOP, "tools", "claims-v3")
M10D = os.path.join(DD, "2026-11-04-q142m-m10")
B8 = os.path.join(CV, "kinds", "blind8")
FLD = os.path.join(CV, "footing-law")
for _p in (M10D, FLD):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import fit_m10 as FM  # noqa: E402  (its feature chain, assembly and recount only; nothing of it is refitted here)
import footing_law as FLAW  # noqa: E402  (k_session only)

RR, M7, M9, F = FM.RR, FM.M7, FM.M9, FM.F
load = lambda p: json.load(open(p))  # noqa: E731
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
REL = lambda p: os.path.relpath(p, TOP)  # noqa: E731
ONE = {"fp32": 0x3F800000, "fp16": 0x3C003C00}
K_FROZEN = {"a3": 0.20563713796102187, "c1": 0.3134106532552718}     # Q139(u), footing.json (m10.json > footing)
SEED_STEPS, SEED_RUNS, SEED_E3, NB = 145, 146, 1452, 2000
FIELDS = {"fp32": (("mant", 0, 22), ("exp", 23, 30), ("sign", 31, 31)), "fp16": (("mant", 0, 9), ("exp", 10, 14), ("sign", 15, 15))}
LAW_CARD = {"a3": "aifoundry3", "c1": "aifoundry1c1"}


def stop(msg):
    raise SystemExit("TERM S STOPPED: " + msg)


def rms(v):
    v = [x for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else float("nan")


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else float("nan")


# ------------------------------------------------------------------ the structure (registration section 2)
def one_bit(d, fmt):
    if fmt == "fp32":
        return d.bit_length() - 1 if d and d & (d - 1) == 0 else None
    h, lo = d >> 16, d & 0xFFFF
    return lo.bit_length() - 1 if lo and h == lo and lo & (lo - 1) == 0 else None


def t_s(raw, fmt):
    """T_S: one A word; lane j's B column j one word u_j in all 16 lines and column j + 8 one word u_j ^ m; m the same for every lane,
    one bit (fp32) or the same one bit in both halves (fp16). Returns {'zero': True} for m = 0, {'bit': p, ...} for a single bit."""
    if fmt not in ONE or len(raw) != 2048:
        return None
    w = np.frombuffer(raw, dtype="<u4")
    A, B = w[:256].reshape(16, 16), w[256:].reshape(16, 16)
    a = {int(x) for x in A.ravel()}
    if len(a) != 1:
        return None
    cols = [{int(x) for x in B[:, j]} for j in range(16)]
    if any(len(c) != 1 for c in cols):
        return None
    u = [next(iter(c)) for c in cols]
    ms = {u[j] ^ u[j + 8] for j in range(8)}
    if len(ms) != 1:
        return None
    m = ms.pop()
    out = {"a_word": a.pop(), "bases": u[:8], "one_base": len(set(u[:8])) == 1}
    if m == 0:
        out["zero"] = True
        return out
    p = one_bit(m, fmt)
    if p is None:
        return None
    out.update(zero=False, bit=p)
    return out


def field_of(fmt, p):
    for name, lo, hi in FIELDS[fmt]:
        if lo <= p <= hi:
            return name
    raise ValueError((fmt, p))


# ------------------------------------------------------------------ the lists (registration, Builds on 2 and section 3)
def _rate(v):
    if isinstance(v, dict):
        return v.get("mean")
    return v


def _se_from_ci(ci, n):
    if ci is None or not n or n < 2:
        return None
    t = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306, 10: 2.262}.get(n, 2.0)
    return ci / t


def list_steps():
    """every training step: the list's registered step over its own zero, its leak, rate, tiles and counts rows"""
    out = []
    # E65 and E70: the hl reducer; tiles from the first kept pass, every kept pass's copy checked equal
    hl = os.path.join(DD, "2026-11-01-q132-rtl-bench", "counts-hl.json")
    hlp = os.path.join(DD, "2026-11-01-q132-rtl-bench", "counts-hlp.json")
    e65d = os.path.join(DD, "2026-10-26-e65-bit-prices-hart-ladder")
    j = load(os.path.join(e65d, "hl.json"))
    c = j["cards"]["aifoundry3"]
    k65 = j["gates"]["aifoundry3"]["leak_W_per_C"]
    for fam, key in (("bits", "bit_{}"), ("bits_pi", "bpi_{}")):
        for k, v in c[fam].items():
            item = key.format(k)
            out.append({"run": "E65", "card": "a3", "fmt": "fp32", "item": item, "zero": v["zero"], "dW": v["dW"], "dW_se": v["se"],
                        "k_list": k65, "rate": c["items"][item]["rate"], "passes": c["passes"], "tiles": ("hl", e65d, "p{}"),
                        "counts": [hl], "src": f"{REL(os.path.join(e65d, 'hl.json'))} cards.aifoundry3.{fam}.{k}.dW"})
    e70d = os.path.join(DD, "2026-10-27-e70-saturation-ladder")
    j = load(os.path.join(e70d, "hl.json"))
    c = j["cards"]["aifoundry3"]
    it = c["items"]["lq_h1"]
    out.append({"run": "E70", "card": "a3", "fmt": "fp32", "item": "lq_h1", "zero": "lq_h0", "dW": it["d_p80"], "dW_se": it["d_p80_se"],
                "k_list": j["gates"]["aifoundry3"]["leak_W_per_C"], "rate": it.get("rate") or c["items"]["lq_h0"].get("rate"),
                "passes": c["passes"], "tiles": ("hl", e70d, "p{}"), "counts": [hl],
                "src": f"{REL(os.path.join(e70d, 'hl.json'))} cards.aifoundry3.items.lq_h1.d_p80"})
    # E79: the hlp reducer
    e79d = os.path.join(DD, "2026-10-31-e79-fp16-int8-bit-prices")
    j = load(os.path.join(e79d, "hlp.json"))
    c = j["cards"]["aifoundry3"]
    for k, v in c["prices"]["fp16_b"].items():
        out.append({"run": "E79", "card": "a3", "fmt": "fp16", "item": v["item"], "zero": v["zero"], "dW": v["dW"], "dW_se": v["dW_se"],
                    "k_list": c["leak_W_per_C"], "rate": v["rate_ops_s"], "passes": c["passes"], "tiles": ("hlp", e79d, "p{}"),
                    "counts": [hlp], "src": f"{REL(os.path.join(e79d, 'hlp.json'))} cards.aifoundry3.prices.fp16_b.{k}.dW"})
    v = c["order_probe"]["fp32"]["jg"]
    it = c["items"][v["item"]]
    out.append({"run": "E79", "card": "a3", "fmt": "fp32", "item": v["item"], "zero": it["zero"], "dW": v["dW"],
                "dW_se": _se_from_ci(v.get("dW_ci95"), v.get("n_passes")), "k_list": c["leak_W_per_C"], "rate": it["rate"],
                "passes": c["passes"], "tiles": ("hlp", e79d, "p{}"), "counts": [hlp],
                "src": f"{REL(os.path.join(e79d, 'hlp.json'))} cards.aifoundry3.order_probe.fp32.jg.dW"})
    # E102: card 1, the kinds reducer; steps from scored.json's primary prices, the block the item is listed in
    e102d = os.path.join(DD, "2026-11-01-e102-balanced-bit-prices")
    sc = load(os.path.join(e102d, "scored.json"))["primary"]
    red = load(os.path.join(e102d, "e102.json"))["items"]
    spec = load(os.path.join(CV, "kinds", "e102", "e102.json"))["tiles"]
    for key, v in sc["prices"].items():
        name, blk = key.split("@")
        sp = spec.get(name)
        if sp is None or sp.get("layout") != "bj" or sp.get("side") != "b":
            continue
        out.append({"run": "E102", "card": "c1", "fmt": sp["type"], "item": name.split(".", 1)[1], "zero": sp["zero"].split(".", 1)[1],
                    "dW": v["board"]["W"]["mean"], "dW_se": v["board"]["W"]["se"], "k_list": sc["leak"]["k_w_per_c"],
                    "rate": _rate(red.get(name, {}).get("rate")), "block": blk,
                    "tiles": ("file", os.path.join(CV, "kinds", "e102"), spec), "counts": [os.path.join(e102d, "bench", "counts-e102.json")],
                    "src": f"{REL(os.path.join(e102d, 'scored.json'))} primary.prices.{key}.board.W"})
    # E134 and E147: the kinds reducer, steps over each item's own zero
    for run, ddir, arm, redf in (("E134", "2026-11-02-e134-bit-prices-more", None, "e134.json"),
                                 ("E147", "2026-11-02-e147-bit-prices-rest", "dips_4w", "e147-dips4.json")):
        d = os.path.join(DD, ddir)
        s = load(os.path.join(d, "scored.json"))
        pr = (s["arms"][arm] if arm else s["primary"])["prices"]
        r = load(os.path.join(d, redf))
        preg = load(os.path.join(CV, run.lower(), f"predictions-{run.lower()}.json"))["items"]
        tspec = load(os.path.join(CV, run.lower(), run.lower(), f"{run.lower()}-tiles.json"))["tiles"]
        cnt = [os.path.join(d, "bench", f"counts-{run.lower()}.json")]
        if run == "E147":
            cnt.append(os.path.join(DD, "2026-11-02-e134-bit-prices-more", "bench", "counts-e134.json"))
        for item, v in pr.items():
            if not item.startswith("bj_"):
                continue
            name = "fp32." + item
            out.append({"run": run, "card": "a3", "fmt": "fp32", "item": item, "zero": preg[name]["zero"].split(".", 1)[1],
                        "dW": v["W"]["mean"], "dW_se": v["W"]["se"], "k_list": r["leak"]["k_w_per_c"],
                        "rate": _rate(r["items"].get(name, {}).get("rate")),
                        "tiles": ("file", os.path.join(CV, run.lower(), run.lower()), tspec), "counts": cnt,
                        "src": f"{REL(os.path.join(d, 'scored.json'))} {'arms.' + arm if arm else 'primary'}.prices.{item}.W"})
    return out


def tile_path(st, name, fmt):
    kind, d, spec = st["tiles"]
    if kind in ("hl", "hlp"):
        sub = "hl" if kind == "hl" else "hlp"
        paths = [os.path.join(d, "aifoundry3", sub, spec.format(p), "tiles", f"{name}.b{p}.bin") for p in st["passes"]]
        paths = [p for p in paths if os.path.exists(p)]
        if not paths:
            stop(f"{st['run']} {name}: no committed tile")
        h = {fsha(p) for p in paths}
        if len(h) != 1:
            stop(f"{st['run']} {name}: the kept passes' copies differ")
        return paths[0], len(paths)
    full = f"{fmt}.{name}"
    if isinstance(spec, dict) and full in spec:
        p = os.path.join(d, spec[full]["file"])
    elif isinstance(spec, dict) and name in spec:
        p = os.path.join(d, spec[name]["file"])
    else:
        cands = glob.glob(os.path.join(d, "tiles", fmt, f"{name}.bin")) + glob.glob(os.path.join(d, "tiles", f"{name}.bin"))
        if not cands:
            stop(f"{st['run']} {name}: no tile file")
        p = cands[0]
    return p, 1


def counts_row(files, name, fmt):
    for f in files:
        rows = load(f)["rows"]
        for k in (f"{fmt}.{name}", name):
            if k in rows:
                return rows[k], f"{REL(f)} rows.{k}"
    return None, None


_CACHE = {}


def feats(path, fmt, crow):
    key = (path, fmt, json.dumps(crow["mean"], sort_keys=True)[:200])
    if key not in _CACHE:
        zeros, zr = _zeros()
        _CACHE[key] = FM.chain_feats(crow, path, fmt, zeros, zr)
    return _CACHE[key]


_Z = {}


def _zeros():
    if not _Z:
        _Z["z"], _Z["zr"] = M7.zeros_counts(), M9.zeros_rows()
    return _Z["z"], _Z["zr"]


def e3_of(crow, fmt):
    pr = RR.prices()
    ws = [RR.point_w(p, fmt, pr) for p in crow["points"]]
    return RR.err(ws)["e_w"] if len(ws) >= 3 else None


def assemble():
    """the training steps with their structure, tiles, features, step features and count errors (no model value yet)"""
    steps, notes = [], []
    for st in list_steps():
        ip, n_i = tile_path(st, st["item"], st["fmt"])
        zp, n_z = tile_path(st, st["zero"], st["fmt"])
        si, sz = t_s(open(ip, "rb").read(), st["fmt"]), t_s(open(zp, "rb").read(), st["fmt"])
        if not si or si.get("zero") or not sz or not sz.get("zero"):
            notes.append(f"{st['run']}:{st['item']} fails T_S (item {bool(si)}, zero {bool(sz and sz.get('zero'))}): not a training step")
            continue
        if si["a_word"] != sz["a_word"]:
            notes.append(f"{st['run']}:{st['item']}: its zero holds another A word: not a training step")
            continue
        ci, csi = counts_row(st["counts"], st["item"], st["fmt"])
        cz, csz = counts_row(st["counts"], st["zero"], st["fmt"])
        if ci is None or cz is None:
            notes.append(f"{st['run']}:{st['item']}: no counts row for item or zero: not a training step")
            continue
        for q in ci["points"] + cz["points"]:
            if q.get("check_mismatch"):
                stop(f"{st['run']}:{st['item']}: check_mismatch in its counts")
        fi, fz = feats(ip, st["fmt"], ci), feats(zp, st["fmt"], cz)
        terms = FM_TERMS()
        f_step = {q: float(fi[q]) - float(fz[q]) for q in terms}
        st2 = dict(st)
        st2.pop("tiles")
        st2.update({"bit": si["bit"], "field": field_of(st["fmt"], si["bit"]), "a_word": f"{si['a_word']:08x}", "one_base": si["one_base"],
                    "tile": REL(ip), "zero_tile": REL(zp), "tile_sha256": fsha(ip), "zero_sha256": fsha(zp), "copies_checked": [n_i, n_z],
                    "counts_item": csi, "counts_zero": csz, "f_step": f_step,
                    "e3_w": math.sqrt((e3_of(ci, st["fmt"]) or 0.0) ** 2 + (e3_of(cz, st["fmt"]) or 0.0) ** 2),
                    "rate": float(st["rate"]) if st.get("rate") else F.RATE[st["fmt"]], "rate_src": "the list's measured" if st.get("rate") else "nominal"})
        steps.append(st2)
    return steps, notes


def FM_TERMS():
    return load(os.path.join(M10D, "m10.json"))["families"]["float"]["terms"]


# ------------------------------------------------------------------ the base model and the footings (sections 3.2, 3.3)
def base_from_m10(path=None):
    m = load(path or os.path.join(M10D, "m10.json"))
    fl = m["families"]["float"]
    return {"name": "M10 as frozen" if path is None else REL(path), "terms": fl["terms"], "coef_J": fl["coef_J"],
            "card1_scale": fl["card1_scale"], "sess": dict(fl.get("session_scales_training") or {}),
            "c1": {"a3": m["heat_4p5s"]["coef"]["S|aifoundry3"], "c1": m["heat_4p5s"]["coef"]["S|aifoundry1-c1"]}}


def k_law(st):
    """FL3: k_s = k_c(T_mid), T_mid from the list's committed runs.csv"""
    d = {"E65": "2026-10-26-e65-bit-prices-hart-ladder", "E70": "2026-10-27-e70-saturation-ladder",
         "E79": "2026-10-31-e79-fp16-int8-bit-prices", "E102": "2026-11-01-e102-balanced-bit-prices",
         "E134": "2026-11-02-e134-bit-prices-more", "E147": "2026-11-02-e147-bit-prices-rest"}[st["run"]]
    csvp = os.path.join(DD, d, "runs-dips4.csv" if st["run"] == "E147" else "runs.csv")
    return FLAW.k_session(os.path.join(FLD, "footing-law.json"), LAW_CARD[st["card"]], csvp), REL(csvp)


def model_step(st, base, s=None):
    c = base["card1_scale"] if st["card"] == "c1" else 1.0
    if s is None:
        s = base["sess"].get(f"{st['run']}|{st['card']}", 1.0)
    dot = sum(st["f_step"][q] * cj for q, cj in zip(base["terms"], base["coef_J"]))
    return s * c * st["rate"] * dot, s, c


def residuals(steps, base, footing, companion=False):
    rows = []
    kcache = {}
    for st in steps:
        c1 = base["c1"][st["card"]]
        if footing == "reg":
            k = K_FROZEN[st["card"]]
            ksrc = "Q139(u)'s frozen slope"
        else:
            if st["run"] not in kcache:
                kcache[st["run"]] = k_law(st)
            kk, ksrc = kcache[st["run"]]
            k = kk["k_w_per_c"]
        fac = 1.0 - (k - st["k_list"]) * c1
        meas = st["dW"] * fac
        pred, s, cc = model_step(st, base)
        if companion and footing == "law":
            pred *= 1.0 - c1 * (k - K_FROZEN[st["card"]])
        r = meas - pred
        rows.append(dict(st, k=k, k_src=ksrc, factor=fac, meas_w=meas, meas_se=(st["dW_se"] or 0.0) * fac if st.get("dW_se") is not None else None,
                         pred_w=pred, s=s, c=cc, r_w=r, rho_J=r / (s * cc * st["rate"]),
                         T_mid=(kcache.get(st["run"], ({}, None))[0].get("T_mid") if footing == "law" else None)))
    return rows


# ------------------------------------------------------------------ the forms and the nested fit (section 4)
FORMS = ("S0", "S1", "S2", "S3")


def fit_values(train, form):
    """the cell means of rho (J per op) on the training steps"""
    v = {"S1": {}, "S2": {}, "S3": {}}
    for r in train:
        v["S1"].setdefault(r["fmt"], []).append(r["rho_J"])
        v["S2"].setdefault((r["fmt"], r["field"]), []).append(r["rho_J"])
        v["S3"].setdefault((r["fmt"], r["bit"]), []).append(r["rho_J"])
    return {k: {c: sum(x) / len(x) for c, x in d.items()} for k, d in v.items()}


def tau(vals, form, fmt, bit):
    if form == "S0":
        return 0.0, "none"
    if form == "S3" and (fmt, bit) in vals["S3"]:
        return vals["S3"][(fmt, bit)], "position"
    if form in ("S2", "S3") and (fmt, field_of(fmt, bit)) in vals["S2"]:
        return vals["S2"][(fmt, field_of(fmt, bit))], "field"
    if fmt in vals["S1"]:
        return vals["S1"][fmt], "format"
    return 0.0, "none (no step of the format in the fold)"


def loro(rows):
    runs = sorted({r["run"] for r in rows})
    held = {f: {} for f in FORMS}
    used = {f: {} for f in FORMS}
    for R in runs:
        train = [r for r in rows if r["run"] != R]
        vals = fit_values(train, None)
        for r in rows:
            if r["run"] != R:
                continue
            key = f"{r['run']}:{r['fmt']}.{r['item']}"
            for f in FORMS:
                t, how = tau(vals, f, r["fmt"], r["bit"])
                held[f][key] = r["r_w"] - r["s"] * r["c"] * r["rate"] * t
                used[f][key] = how
    return held, used


def paired_boot(ea, eb, keys, draws=NB, seed=SEED_STEPS):
    d0 = rms([ea[k] for k in keys]) - rms([eb[k] for k in keys])
    rng = random.Random(seed)
    ds = []
    for _ in range(draws):
        s = [keys[rng.randrange(len(keys))] for _ in keys]
        ds.append(rms([ea[k] for k in s]) - rms([eb[k] for k in s]))
    ds.sort()
    return {"d_rms_w": d0, "lo95": ds[int(0.025 * draws)], "hi95": ds[int(0.975 * draws) - 1], "n": len(keys), "draws": draws, "seed": seed}


def summarize(err, keys):
    return {"n": len(keys), "rms_w": rms([err[k] for k in keys]), "bias_w": mean([err[k] for k in keys])}


# ------------------------------------------------------------------ pool 6/7's S rows (E3) and pool 8 (post hoc)
def pool67_s_rows():
    """the 26 case-S rows of rows-m10.json with M10's held-out errors, each tile's T_S reading and its row's rate and session"""
    rows, _ = FM.assemble()
    by = {(r["exp"], r["key"]): r for r in rows}
    out = []
    m10 = load(os.path.join(M10D, "m10.json"))["families"]["float"]
    for r in load(os.path.join(M10D, "rows-m10.json")):
        if not r.get("S_class"):
            continue
        a = by[(r["exp"], r["key"])]
        raw = open(os.path.join(TOP, a["tile_path"]), "rb").read()
        s = t_s(raw, a["type"])
        out.append({"exp": r["exp"], "card": r["card"], "key": r["key"], "type": a["type"], "rate": a["rate"],
                    "e_m10_heldout_w": r["err_w"]["B+a+b"], "t_s_bit": (s or {}).get("bit") if s and not s.get("zero") else None,
                    "s": m10["session_scales_training"].get(f"{r['exp']}|{r['card']}", 1.0),
                    "c": m10["card1_scale"] if r["card"] == "c1" else 1.0, "tile": a["tile_path"]})
    return out


def b8_files():
    """pool 8's tile files by name, from its committed manifest (blind8.json), each checked against its sha256"""
    if "b8" not in _Z:
        m = {}
        for t in load(os.path.join(B8, "blind8.json"))["tiles"]:
            p = os.path.join(B8, t["file"])
            if fsha(p) != t["sha256"]["whole"]:
                stop(f"pool 8's {t['name']} does not hash as blind8.json says")
            m[t["name"]] = p
        _Z["b8"] = m
    return _Z["b8"]


def pool8_600(run, vals, form, base_c1):
    """post hoc: a 600 MHz pool-8 session's scored rows, D - M10 primary with and without the term (registered footing)"""
    d = {"E171": "2026-11-05-e171-blind8-aifoundry3", "E172": "2026-11-05-e172-blind8-card1"}[run]
    sc = load(os.path.join(DD, d, "scored.json"))["primary"]
    pred = load(os.path.join(B8, "predictions-pool8-" + ("aifoundry3" if run == "E171" else "aifoundry1c1") + ".json"))
    sets = pred["sets"]
    s_float = float(sc["scale"]["s_float"])
    c = base_c1 if run == "E172" else 1.0
    out = {"s_float": s_float, "c": c, "tiles": {}}
    for t, r in sc["rows"].items():
        if "e_primary" not in r or r["type"] not in ONE:
            continue
        p = b8_files().get(t)
        s = t_s(open(p, "rb").read(), r["type"]) if p else None
        bit = s["bit"] if s and not s.get("zero") else None
        tv, how = (tau(vals, form, r["type"], bit) if bit is not None else (0.0, "not T_S"))
        add = s_float * c * r["rate_per_s"] * tv
        out["tiles"][t] = {"type": r["type"], "case": r.get("case"), "priority": r.get("priority"), "t_s_bit": bit,
                           "one_base": (s or {}).get("one_base"), "e_m10_w": r["e_primary"], "term_w": add,
                           "e_m10s_w": r["e_primary"] - add, "how": how}
    def grp(name, keys):
        keys = [k for k in keys if k in out["tiles"]]
        return {"n": len(keys), "M10": summarize({k: out["tiles"][k]["e_m10_w"] for k in keys}, keys),
                "M10+S": summarize({k: out["tiles"][k]["e_m10s_w"] for k in keys}, keys)}
    n1 = set(sets["N1"])
    s_n1 = sorted(k for k, v in out["tiles"].items() if v["case"] == "S" and k in n1)
    out["class_S_N1"] = grp("class S N1", s_n1)
    out["case_S_all"] = grp("case S", sorted(k for k, v in out["tiles"].items() if v["case"] == "S"))
    out["F1_B1"] = grp("F1", sorted(set(sets["F1"]) & set(out["tiles"])))
    out["F1_without_S"] = grp("F1 less class S", sorted((set(sets["F1"]) & set(out["tiles"])) - set(s_n1)))
    out["T_S_tiles_in_N1"] = sorted(k for k, v in out["tiles"].items() if v["t_s_bit"] is not None and k in n1)
    return out


def pool8_800(run, vals, form):
    """post hoc: E173 (aifoundry2) and E174 (card 0), the board at the 800 MHz cap, M10 carried with and without the term; the carry
    is the frozen file's own linear ratio per tile (burst D over the 600 MHz D, times kappa0 on card 0)"""
    d = {"E173": "2026-11-05-e173-blind8-aifoundry2", "E174": "2026-11-05-e174-blind8-card0"}[run]
    res = load(os.path.join(DD, d, "results.json"))
    pf = load(os.path.join(B8, "predictions-pool8-" + ("aifoundry2" if run == "E173" else "aifoundry1c0") + ".json"))
    tiles = res["score"]["reported"]["tiles"]
    scored = res["score"].get("tiles_scored") or []
    scored = scored if isinstance(scored, list) else list(scored)
    kappa = res.get("kappa0") if run == "E174" else None
    out = {"tiles": {}, "kappa0": kappa}
    for t, r in tiles.items():
        if r.get("case") != "S" or t not in pf["tiles"]:
            continue
        man = pf["tiles"][t]
        typ = t.split(".")[0]
        p = b8_files().get(t)
        s = t_s(open(p, "rb").read(), typ) if p else None
        bit = s["bit"] if s and not s.get("zero") else None
        m = man["M10"]
        d600 = m["D600_a3_footing_w"]
        a2 = m.get("a2_fallback") or {}
        ratio = (a2.get("burst_D_w") / d600) if a2.get("burst_D_w") and d600 else None
        if run == "E174" and ratio is not None:
            ratio *= float(kappa)
        tv, how = (tau(vals, form, typ, bit) if bit is not None else (0.0, "not T_S"))
        add600 = m.get("rate_nominal_per_s", F.RATE[typ]) * tv
        add = add600 * ratio if ratio is not None else None
        e = r["burst_w"] - r["M10"]["burst_board_w"]
        out["tiles"][t] = {"type": typ, "t_s_bit": bit, "scored": t in scored, "e_m10_board_w": e, "carry_ratio": ratio,
                           "term_600_w": add600, "term_800_w": add, "e_m10s_board_w": (e - add) if add is not None else None, "how": how}
    keys = sorted(k for k, v in out["tiles"].items() if v["scored"] or not scored)
    out["class_S_scored"] = {"n": len(keys), "M10": summarize({k: out["tiles"][k]["e_m10_board_w"] for k in keys}, keys),
                             "M10+S": summarize({k: out["tiles"][k]["e_m10s_board_w"] for k in keys}, keys), "tiles": keys}
    return out


# ------------------------------------------------------------------ the whole fit (sections 4, 5, 7)
def run_fit(out_dir, footing="reg", base_path=None):
    os.makedirs(out_dir, exist_ok=True)
    base = base_from_m10(base_path)
    companion = footing == "law" and base_path is None
    steps, notes = assemble()
    rows = residuals(steps, base, footing, companion)
    keys = [f"{r['run']}:{r['fmt']}.{r['item']}" for r in rows]
    held, used = loro(rows)
    res = {"registration": "tools/claims-v3/m10-s/REGISTRATION.md (dfc005bf)", "footing": footing,
           "base": base["name"] + (" x FL7's first-order companion" if companion else ""), "n_steps": len(rows), "notes": notes,
           "label": "held out (leave one run out) on the price lists; pool 6/7's S kinds held out for the term; pool 8 post hoc"}
    res["by_form"] = {}
    groups = {"all": keys, "fp32": [k for k, r in zip(keys, rows) if r["fmt"] == "fp32"],
              "fp16": [k for k, r in zip(keys, rows) if r["fmt"] == "fp16"],
              "aifoundry3": [k for k, r in zip(keys, rows) if r["card"] == "a3"], "card1": [k for k, r in zip(keys, rows) if r["card"] == "c1"]}
    for run in sorted({r["run"] for r in rows}):
        groups["run " + run] = [k for k, r in zip(keys, rows) if r["run"] == run]
    for fmt, flds in FIELDS.items():
        for name, lo, hi in flds:
            groups[f"{fmt} {name}"] = [k for k, r in zip(keys, rows) if r["fmt"] == fmt and r["field"] == name]
    for f in FORMS:
        res["by_form"][f] = {g: summarize(held[f], ks) for g, ks in groups.items() if ks}
    best = min(("S1", "S2", "S3"), key=lambda f: rms([held[f][k] for k in keys]))
    e1 = paired_boot(held[best], held["S0"], keys)
    e2 = {g: rms([held[best][k] for k in groups[g]]) - rms([held["S0"][k] for k in groups[g]]) for g in ("aifoundry3", "card1") if groups[g]}
    all_vals = fit_values(rows, None)
    # E3: pool 6/7's 26 case-S rows, the term frozen on all 95 steps
    p67 = pool67_s_rows()
    e_old = {f"{r['exp']}:{r['key']}": r["e_m10_heldout_w"] for r in p67}
    e_new = {}
    for r in p67:
        t = tau(all_vals, best, r["type"], r["t_s_bit"])[0] if r["t_s_bit"] is not None else 0.0
        e_new[f"{r['exp']}:{r['key']}"] = r["e_m10_heldout_w"] - r["s"] * r["c"] * r["rate"] * t
    # the bootstrap of E3 over the 13 kinds (a kind = one tile on both cards)
    kinds = sorted({r["key"] for r in p67})
    rng = random.Random(SEED_E3)
    ds = []
    for _ in range(NB):
        pick = [kinds[rng.randrange(len(kinds))] for _ in kinds]
        ks = [f"{r['exp']}:{r['key']}" for k in pick for r in p67 if r["key"] == k]
        ds.append(rms([e_new[k] for k in ks]) - rms([e_old[k] for k in ks]))
    ds.sort()
    e3 = {"d_rms_w": rms(list(e_new.values())) - rms(list(e_old.values())), "lo95": ds[int(0.025 * NB)], "hi95": ds[int(0.975 * NB) - 1],
          "rms_M10_heldout_w": rms(list(e_old.values())), "rms_M10S_w": rms(list(e_new.values())), "bias_M10_w": mean(list(e_old.values())),
          "bias_M10S_w": mean(list(e_new.values())), "n_rows": len(p67), "n_kinds": len(kinds),
          "rows_with_T_S": sum(1 for r in p67 if r["t_s_bit"] is not None),
          "rows": {k: {"e_m10": e_old[k], "e_m10s": e_new[k]} for k in e_old}}
    ok1 = e1["d_rms_w"] <= -0.010 and e1["hi95"] < 0
    ok2 = all(v < 0 for v in e2.values())
    ok3 = e3["d_rms_w"] <= 0
    res["entry"] = {"best_form": best, "E1": dict(e1, holds=ok1), "E2": {"d_rms_w_by_card": e2, "holds": ok2},
                    "E3": dict({k: v for k, v in e3.items() if k != "rows"}, holds=ok3), "enters": bool(ok1 and ok2 and ok3)}
    res["E3_rows"] = e3["rows"]
    # the frozen values and their uncertainty
    def boot_cells(by, seed):
        rng = random.Random(seed)
        out = {}
        cells = fit_values(rows, None)
        for form in ("S1", "S2", "S3"):
            for cell in cells[form]:
                sel = [r for r in rows if (r["fmt"] if form == "S1" else (r["fmt"], r["field"]) if form == "S2" else (r["fmt"], r["bit"])) == cell]
                if by == "steps":
                    xs = [r["rho_J"] for r in sel]
                    bs = sorted(sum(xs[rng.randrange(len(xs))] for _ in xs) / len(xs) for _ in range(NB))
                else:
                    rr = sorted({r["run"] for r in sel})
                    bs = []
                    for _ in range(NB):
                        pick = [rr[rng.randrange(len(rr))] for _ in rr]
                        xs = [r["rho_J"] for k in pick for r in sel if r["run"] == k]
                        bs.append(sum(xs) / len(xs))
                    bs.sort()
                out[f"{form}|{cell}"] = [bs[int(0.025 * NB)], bs[int(0.975 * NB) - 1]]
        return out
    ci_steps, ci_runs = boot_cells("steps", SEED_STEPS), boot_cells("runs", SEED_RUNS)
    nominal = F.RATE
    table = {}
    for form in ("S1", "S2", "S3"):
        for cell, v in all_vals[form].items():
            fmt = cell if form == "S1" else cell[0]
            n = sum(1 for r in rows if (r["fmt"] if form == "S1" else (r["fmt"], r["field"]) if form == "S2" else (r["fmt"], r["bit"])) == cell)
            table[f"{form}|{cell}"] = {"tau_J_per_op": v, "W_at_nominal_rate_a3": v * nominal[fmt], "n_steps": n,
                                       "ci95_J_steps": ci_steps[f"{form}|{cell}"], "ci95_J_runs": ci_runs[f"{form}|{cell}"]}
    res["frozen_values"] = table
    res["sigma_S_w"] = {fmt: rms([held[best][k] for k in groups[fmt]]) for fmt in ("fp32", "fp16") if groups[fmt]}
    # delta, the count bias of three points (Q141(t)'s recount)
    sr = load(os.path.join(M10D, "heldout-m10.json"))["S_recount"]
    delta = {}
    for fmt in ("fp32", "fp16"):
        xs = [v["three_point_minus_N_w"] for k, v in sr.items() if k.startswith(fmt + ".") and v.get("three_point_minus_N_w") is not None]
        m, sd = statistics.mean(xs), statistics.stdev(xs)
        t = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306, 10: 2.262, 11: 2.228, 12: 2.201}.get(len(xs), 2.2)
        hw = t * sd / math.sqrt(len(xs))
        delta[fmt] = {"n_tiles": len(xs), "mean_w": m, "ci95_w": [m - hw, m + hw], "applies": not (m - hw <= 0 <= m + hw)}
    res["delta_count_bias"] = delta
    res["steps"] = []
    for r, k in zip(rows, keys):
        res["steps"].append({kk: r[kk] for kk in ("run", "card", "fmt", "item", "zero", "bit", "field", "a_word", "dW", "dW_se", "k_list", "k",
                                                  "factor", "meas_w", "pred_w", "r_w", "rho_J", "s", "c", "rate", "rate_src", "e3_w", "src",
                                                  "tile", "zero_tile", "tile_sha256", "zero_sha256", "counts_item", "counts_zero", "T_mid")
                             if kk in r} | {"heldout_w": {f: held[f][k] for f in FORMS}, "loro_cell": {f: used[f][k] for f in FORMS}})
    # the agreement table: the same position on aifoundry3 with A = 1.0 in two lists
    agree = {}
    for r in rows:
        if r["card"] == "a3" and r["a_word"] in ("3f800000", "3c003c00"):
            agree.setdefault(f"{r['fmt']} bit {r['bit']}", []).append({"run": r["run"], "meas_w": r["meas_w"], "pred_w": r["pred_w"]})
    res["agreement"] = {k: v for k, v in agree.items() if len({x["run"] for x in v}) > 1}
    # post hoc, pool 8, with the best form frozen on all steps (footing reg only; F-law's post hoc is law_m10.py's)
    if footing == "reg":
        res["posthoc_pool8"] = {"label": "post hoc: pool 8 was measured and its class-S errors read before the registration",
                                "form": best, "E171": pool8_600("E171", all_vals, best, base["card1_scale"]),
                                "E172": pool8_600("E172", all_vals, best, base["card1_scale"]),
                                "E173": pool8_800("E173", all_vals, best), "E174": pool8_800("E174", all_vals, best)}
        res["posthoc_pool8_all_forms"] = {f: {run: (pool8_600(run, all_vals, f, base["card1_scale"])["class_S_N1"] if run in ("E171", "E172")
                                                    else pool8_800(run, all_vals, f)["class_S_scored"]) for run in ("E171", "E172", "E173", "E174")}
                                          for f in ("S1", "S2", "S3")}
    name = f"term-s-{footing}" + ("-companion" if companion else "") + ".json"
    json.dump(res, open(os.path.join(out_dir, name), "w"), indent=1, default=str)
    return res, name


# ------------------------------------------------------------------ the self-tests (Builds on, the checks)
def selftest():
    out = {}
    # (1) M10's predictor self-test
    sys.path.insert(0, M10D)
    import predict_m10 as PM  # noqa: E402
    out["predict_m10_selftest_rc"] = PM.selftest()
    # (2) this lane's step features for E147's rows equal M9's committed ones (the features M10 prices)
    steps, notes = assemble()
    m9 = {r["key"]: r for r in load(os.path.join(DD, "2026-11-04-q140m-m9", "rows-m9.json")) if r["exp"] == "E147"}
    worst, n = 0.0, 0
    for st in steps:
        if st["run"] != "E147":
            continue
        r = m9.get("fp32." + st["item"])
        if r is None:
            continue
        for q, v in st["f_step"].items():
            ref = float(r["f"][q])
            worst = max(worst, abs(v - ref) / max(1.0, abs(ref)))
        n += 1
    out["e147_step_features"] = {"rows_compared": n, "max_rel_diff": worst, "pass": n == 15 and worst <= 1e-9}
    # (3) T_S on pool 8's tiles agrees with make_blind8's single_bit_b (the bit), and the counts of section 2
    man = load(os.path.join(B8, "blind8.json"))["tiles"]
    agree, nS = True, 0
    for m in man:
        if m["type"] not in ONE:
            continue
        p = os.path.join(B8, m["file"])
        s = t_s(open(p, "rb").read(), m["type"])
        if m.get("case") == "S":
            nS += 1
            sb = m["name"].split("_b")[1].split("_")[0] if "s8_onebit_b" in m["name"] or "b_onebit_b" in m["name"] else None
            if m["name"].startswith(m["type"] + ".a_onebit"):
                agree &= (s is None)
            elif sb is not None:
                agree &= bool(s) and not s.get("zero") and s["bit"] == int(sb) and s["one_base"]
    out["t_s_on_pool8"] = {"case_S_tiles": nS, "agree": agree}
    by_run = {}
    for st in steps:
        by_run.setdefault(st["run"], {"fp32": 0, "fp16": 0})[st["fmt"]] += 1
    out["steps"] = {"n": len(steps), "by_run": by_run, "notes": notes,
                    "pass": len(steps) == 95 and sum(v["fp32"] for v in by_run.values()) == 75}
    ok = out["predict_m10_selftest_rc"] == 0 and out["e147_step_features"]["pass"] and agree and out["steps"]["pass"]
    out["selftest"] = "PASS" if ok else "FAIL"
    print(json.dumps(out, indent=1, default=str))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "fit"])
    ap.add_argument("--out")
    ap.add_argument("--footing", default="reg", choices=["reg", "law"])
    ap.add_argument("--base")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    res, name = run_fit(a.out, a.footing, a.base)
    e = res["entry"]
    print(json.dumps({"file": name, "n_steps": res["n_steps"], "best": e["best_form"], "enters": e["enters"],
                      "E1": {k: e["E1"][k] for k in ("d_rms_w", "lo95", "hi95", "holds")}, "E2": e["E2"], "E3": {k: e["E3"][k] for k in ("d_rms_w", "lo95", "hi95", "holds")},
                      "forms_all": {f: res["by_form"][f]["all"] for f in FORMS}}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
