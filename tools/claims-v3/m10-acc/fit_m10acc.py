#!/usr/bin/env python3
"""Q153(m10acc): M10's per-tile accumulator-toggle term (tools/claims-v3/m10-acc/REGISTRATION.md, committed b5586759 before this
file existed). Desk only; numpy and scipy (the Intel's /usr/bin/python3: 3.9.6, numpy 1.26.4, scipy 1.13.1).

    python3 -B fit_m10acc.py selftest                         # the estimator, the bootstraps and the Booth rows on synthetic data
    python3 -B fit_m10acc.py tiles  --job <dir>               # REGISTRATION.md section 3's rows and checks; writes <dir>/tiles/<sha>.bin
                                                              #   and <dir>/joblist.txt (type sha N1,N2,...) for acctrace_m10acc
    python3 -B fit_m10acc.py features --job <dir> --out <dd>  # merges <dir>/out/<sha>.json into <dd>/features-m10acc.json; checks T1, T2
    python3 -B fit_m10acc.py fit --out <dd>                   # sections 4-7: rows-m10acc.json, fit-m10acc.json, m10acc.json,
                                                              #   forecasts-e182-m10acc.json, fit-output.txt

The rows (section 3): (a) M10's 959 rows with their committed held-out errors; (b) pool 8's 40 kinds on E171 and E172; (c) the five
single-bit lists outside M10's rows (70 steps); (d) E178's 40 kinds. The features (section 2) come from acctrace_m10acc.c, run on
the mini. Nothing is fitted before `fit`, and `fit` refuses to run unless the features file's checks passed.
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
import statistics  # noqa: E402
import struct  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
M10D = os.path.join(DD, "2026-11-04-q142m-m10")
M9D = os.path.join(DD, "2026-11-04-q140m-m9")
B7, B8 = os.path.join(ROOT, "tools/claims-v3/kinds/blind7"), os.path.join(ROOT, "tools/claims-v3/kinds/blind8")
E178T = os.path.join(ROOT, "tools/claims-v3/e178")
E178D = os.path.join(DD, "2026-11-06-e178-one-number-aifoundry3")
TERMS = os.path.join(DD, "2026-11-06-q145b-m10-s", "note2-term-s-reg-99.json")
E147T = os.path.join(ROOT, "tools/claims-v3/e147/e147/tiles/fp32")
POOL8 = {"E171": ("a3", os.path.join(DD, "2026-11-05-e171-blind8-aifoundry3", "scored.json")),
         "E172": ("c1", os.path.join(DD, "2026-11-05-e172-blind8-card1", "scored.json"))}
FOOT7 = {"E163": os.path.join(DD, "2026-11-04-e163-blind7-aifoundry3", "e163.json"),
         "E164": os.path.join(DD, "2026-11-04-e164-blind7-card1", "e164.json")}
LISTS = ("E65", "E67", "E70", "E79", "E134")
UOPS = {"fp32": 512, "fp16": 512, "int8": 256}
N_LAUNCH_E178 = {"fp32": 539295, "fp16": 539149, "int8": 912355}     # forecast_e178.N_LAUNCH, for check T1
SEED_JACK_BOOT, SEED_RULE, SEED_FP9, NB = 1531, 1532, 1533, 2000
fam_of = lambda t: "int8" if t == "int8" else "float"  # noqa: E731
load = lambda p: json.load(open(p))  # noqa: E731
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
rms = lambda x: float(math.sqrt(np.mean(np.square(np.asarray(x, float))))) if len(x) else float("nan")  # noqa: E731


def stop(msg):
    raise SystemExit("M10-ACC STOPPED: " + msg)


def rel(p):
    return os.path.relpath(p, ROOT)


# ------------------------------------------------------------------ section 2.3: the launch sizes
def half_up(x):
    return int(math.floor(x + 0.5))


def launch_sizes(exps):
    out = {}
    for e in sorted(set(exps)):
        dirs = sorted(glob.glob(os.path.join(DD, f"*-{e.lower()}-*")))
        its, files = {}, []
        for d in dirs:
            for f in sorted(glob.glob(os.path.join(d, "**", "runs.jsonl"), recursive=True)):
                if "smoke" in f or "stoptest" in f:
                    continue
                files.append(rel(f))
                for line in open(f):
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    if r.get("launch") is None or r["launch"] < 0 or not r.get("iters") or r.get("ok") is False:
                        continue
                    its.setdefault(r.get("type"), []).append(int(r["iters"]))
        if not its:
            stop(f"no timed launches for {e}")
        out[e] = {"dirs": [rel(d) for d in dirs], "runs_files": len(files),
                  "by_type": {t: {"n": len(v), "median": statistics.median(v), "N": half_up(statistics.median(v)), "min": min(v),
                                  "max": max(v)} for t, v in sorted(its.items())}}
    return out


# ------------------------------------------------------------------ section 3: the rows
def tile_ok(path, sha):
    if not os.path.exists(path):
        stop(f"missing tile {rel(path)}")
    if sha is not None and fsha(path) != sha:
        stop(f"{rel(path)} does not hash as its source says")
    return fsha(path)


def assemble():
    m10 = load(os.path.join(M10D, "m10.json"))
    ss = m10["families"]["float"]["session_scales_training"]
    card_t = {f: m10["families"][f]["card1_scale"] for f in ("float", "int8")}
    rows = []
    # (a) M10's 959 rows
    r10 = load(os.path.join(M10D, "rows-m10.json"))
    r9 = {(x["exp"], x["card"], x["key"]): x for x in load(os.path.join(M9D, "rows-m9.json"))}
    man7 = {m["name"]: m for m in load(os.path.join(B7, "blind7.json"))["tiles"]}
    foot7 = {e: load(p)["items"] for e, p in FOOT7.items()}
    for x in r10:
        t, fam = x["type"], fam_of(x["type"])
        key = (x["exp"], x["card"], x["key"])
        e = x["err_w"]["B+a+b" if fam == "float" else "B"]
        row = {"src": "a", "exp": x["exp"], "card": x["card"], "run": f"{x['exp']}|{x['card']}", "key": x["key"], "kind": x["kind"],
               "type": t, "fam": fam, "e": float(e), "s_class": bool(x.get("S_class")),
               "s": float(ss[f"{x['exp']}|{x['card']}"]) if fam == "float" else 1.0,
               "c": card_t[fam] if x["card"] == "c1" else 1.0, "nexp": x["exp"]}
        if key in r9:
            s9 = r9[key]
            row["rate"] = float(s9["rate"])
            row["tile"] = s9["tile_path"]
            row["sha"] = tile_ok(os.path.join(ROOT, s9["tile_path"]), s9["tile_sha256"])
            if x["exp"] == "E147":
                z = s9["zero"].split(".", 1)[1]
                zp = os.path.join(E147T, z + ".bin")
                row["zero_tile"], row["zero_sha"] = rel(zp), tile_ok(zp, None)
                row["zero_key"] = s9["zero"]
            if abs(float(s9["D"]) - float(x["D"])) > 1e-9:
                stop(f"D differs between rows-m10 and rows-m9 for {key}")
        elif x["exp"] in FOOT7:
            m = man7[x["key"]]
            p = os.path.join(B7, m["file"])
            row["tile"], row["sha"] = rel(p), tile_ok(p, m["sha256"]["whole"])
            row["rate"] = float(foot7[x["exp"]][x["key"]]["rate"]["mean"])
        else:
            stop(f"no source row for {key}")
        rows.append(row)
    if len(rows) != 959:
        stop(f"(a) has {len(rows)} rows, not 959")
    # (b) pool 8 at 600 MHz: sets N1 and other_priorities
    sets = load(os.path.join(B8, "sets-blind8.json"))["sets"]
    names = list(sets["N1"]) + list(sets["other_priorities"])
    n1 = set(sets["N1"])
    man8 = {m["name"]: m for m in load(os.path.join(B8, "blind8.json"))["tiles"]}
    for exp, (card, sp) in POOL8.items():
        sc = load(sp)["primary"]
        sf = float(sc["scale"]["s_float"])
        for nm in names:
            r = sc["rows"][nm]
            t, fam = r["type"], fam_of(r["type"])
            if abs((r["D_w"] - r["M10_primary_w"]) - r["e_primary"]) > 1e-9:
                stop(f"(b) e_primary is not D - M10 for {exp} {nm}")
            m = man8[nm]
            p = os.path.join(B8, m["file"])
            rows.append({"src": "b", "exp": exp, "card": card, "run": f"{exp}|{card}", "key": nm, "kind": f"{t}.blind8:{nm.split('.', 1)[1]}",
                         "type": t, "fam": fam, "e": float(r["e_primary"]), "s": sf if fam == "float" else 1.0,
                         "c": card_t[fam] if card == "c1" else 1.0, "rate": float(r["rate_per_s"]), "tile": rel(p),
                         "sha": tile_ok(p, m["sha256"]["whole"]), "case": r.get("case"), "pool8_n1": nm in n1,
                         "s_class": r.get("case") == "S" and nm in n1, "nexp": exp})
    # (c) the single-bit lists outside M10's rows
    for st in load(TERMS)["steps"]:
        if st["run"] not in LISTS:
            continue
        if abs((st["meas_w"] - st["pred_w"]) - st["r_w"]) > 1e-9:
            stop(f"(c) r_w is not meas - pred for {st['run']} {st['item']}")
        p, zp = os.path.join(ROOT, st["tile"]), os.path.join(ROOT, st["zero_tile"])
        rows.append({"src": "c", "exp": st["run"], "card": st["card"], "run": f"list:{st['run']}", "key": f"{st['fmt']}.{st['item']}",
                     "kind": f"{st['fmt']}.{st['run'].lower()}:{st['item']}", "type": st["fmt"], "fam": "float", "e": float(st["r_w"]),
                     "s": float(st["s"]), "c": float(st["c"]), "rate": float(st["rate"]), "tile": st["tile"],
                     "sha": tile_ok(p, st["tile_sha256"]), "zero_tile": st["zero_tile"], "zero_sha": tile_ok(zp, st["zero_sha256"]),
                     "zero_key": st["zero"], "bit": st.get("bit"), "field": st.get("field"), "a_word": st.get("a_word"),
                     "s_class": False, "nexp": st["run"]})
    # (d) E178's 40 kinds
    kinds = load(os.path.join(E178T, "kinds-e178.json"))["kinds"]
    sc = load(os.path.join(E178D, "scored.json"))["primary"]
    sf = float(sc["scale"]["s_float"])
    rk = sc["reported"]["kinds"]
    for k in kinds:
        r = rk[k["key"]]
        if not (r.get("c_kept") and (r.get("n") or 0) >= 2):
            continue
        if abs((r["D_w"] - r["P_w"]) - r["D_minus_P_w"]) > 1e-9:
            stop(f"(d) D_minus_P is not D - P for {k['key']}")
        t, fam = k["type"], fam_of(k["type"])
        p = os.path.join(E178T, "tiles", t, k["name"] + ".bin")
        rows.append({"src": "d", "exp": "E178", "card": "a3", "run": "E178|a3", "key": k["key"], "kind": k["key"], "type": t, "fam": fam,
                     "e": float(r["D_minus_P_w"]), "s": sf if fam == "float" else 1.0, "c": 1.0, "rate": float(r["rate_per_s"]),
                     "tile": rel(p), "sha": tile_ok(p, k["sha256"]), "a_word": k["a_word"], "b_word": k["b_word"],
                     "e_F": float(r["D_minus_F_w"]), "P_w": float(r["P_w"]), "D_w": float(r["D_w"]), "s_class": False, "nexp": "E178"})
    return rows


def counts(rows):
    c = {}
    for r in rows:
        k = f"{r['src']}|{r['fam']}|{r['card']}"
        c[k] = c.get(k, 0) + 1
    return dict(sorted(c.items()))


# ------------------------------------------------------------------ the tile list for the traces
def grid_e182():
    """REGISTRATION.md section 6: the one-number grid (words, as hex)"""
    i8 = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 31, 63, 85, 127, -1, -2, -85, -128]
    w8 = [f"0x{(v & 0xFF) * 0x01010101:08x}" for v in i8]
    vals = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, -1.0]
    w32 = ["0x%08x" % struct.unpack("<I", struct.pack("<f", v))[0] for v in vals]
    h = lambda v: struct.unpack("<H", struct.pack("<e", v))[0]  # noqa: E731
    w16 = ["0x%08x" % ((h(v) << 16) | h(v)) for v in vals]
    return {"int8": list(zip(i8, w8)), "fp32": list(zip(vals, w32)), "fp16": list(zip(vals, w16))}


def one_number_tile(aw, bw):
    return struct.pack("<512I", *([int(aw, 16)] * 256 + [int(bw, 16)] * 256))


def cmd_tiles(a):
    rows = assemble()
    exps = sorted({r["nexp"] for r in rows})
    ls = launch_sizes(exps)
    job = os.path.abspath(a.job)
    os.makedirs(os.path.join(job, "tiles"), exist_ok=True)
    need = {}

    def add(t, sha, path_bytes, n):
        k = (t, sha)
        if k not in need:
            need[k] = set()
            dst = os.path.join(job, "tiles", f"{sha}.bin")
            if not os.path.exists(dst):
                open(dst, "wb").write(path_bytes)
        need[k].add(int(n))
    for r in rows:
        n = ls[r["nexp"]]["by_type"][r["type"]]["N"]
        add(r["type"], r["sha"], open(os.path.join(ROOT, r["tile"]), "rb").read(), n)
        if r.get("zero_tile"):
            add(r["type"], r["zero_sha"], open(os.path.join(ROOT, r["zero_tile"]), "rb").read(), n)
        if r["exp"] == "E178":
            add(r["type"], r["sha"], b"", N_LAUNCH_E178[r["type"]])           # check T1's N
        if r["exp"] == "E67":
            for q in ("min", "max"):
                add(r["type"], r["sha"], b"", ls["E67"]["by_type"]["fp32"][q])
                add(r["type"], r["zero_sha"], b"", ls["E67"]["by_type"]["fp32"][q])
    e178n = {t: ls["E178"]["by_type"][t]["N"] for t in ("fp32", "fp16", "int8")}
    grid = grid_e182()
    gl = []
    for t, vs in grid.items():
        for va, wa in vs:
            for vb, wb in vs:
                raw = one_number_tile(wa, wb)
                sha = hashlib.sha256(raw).hexdigest()
                add(t, sha, raw, e178n[t])
                gl.append({"type": t, "a": va, "b": vb, "a_word": wa, "b_word": wb, "sha": sha})
    # order: the costliest first (fp16, then fp32, then int8), each tile's N ascending
    lines = []
    for (t, sha), ns in sorted(need.items(), key=lambda kv: ({"fp16": 0, "fp32": 1, "int8": 2}[kv[0][0]], kv[0][1])):
        lines.append(f"{t} {sha} {','.join(str(n) for n in sorted(ns))}")
    open(os.path.join(job, "joblist.txt"), "w").write("\n".join(lines) + "\n")
    meta = {"rows": len(rows), "counts": counts(rows), "launch_sizes": ls, "tiles": len(need), "grid": gl,
            "by_type": {t: sum(1 for k in need if k[0] == t) for t in ("fp32", "fp16", "int8")}}
    json.dump(meta, open(os.path.join(job, "tiles-meta.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps({k: meta[k] for k in ("rows", "counts", "tiles", "by_type")}, indent=1))


# ------------------------------------------------------------------ the Booth rows in Python (check T2)
def nzr(mplr):
    ext = (mplr & 0xFFFFFFFF) << 1
    return sum(1 for i in range(17) if ((ext >> (2 * i)) & 7) not in (0, 7))


def excess_half(a, half):
    h = (a >> 16) if half else (a & 0xFFFF)
    if not (h & 0x7C00):
        return 0
    return nzr(0x80000000 | ((h & 0x3FF) << 21)) - 2 if half else nzr((1 << 11) | ((h & 0x3FF) << 1)) - 2


def excess32(a):
    return 0 if not (a & 0x7F800000) else nzr(0x80000000 | ((a & 0x7FFFFF) << 8)) - 2


def sig32(b):
    return (0x800000 | (b & 0x7FFFFF)) if (b & 0x7F800000) else 0


def sig16(b, half):
    h = (b >> 16) if half else (b & 0xFFFF)
    return (0x400 | (h & 0x3FF)) if (h & 0x7C00) else 0


def bth_python(raw, t):
    if t == "int8":
        return 0.0
    w = struct.unpack("<512I", raw)
    A = [[w[16 * i + k] for k in range(16)] for i in range(16)]
    B = [[w[256 + 16 * k + j] for j in range(16)] for k in range(16)]
    prev, have, x = [0] * 8, [False] * 8, 0
    for op in range(2):
        for k in range(16):
            for i in range(16):
                for h in range(2):
                    aw = A[i][k]
                    for ln in range(8):
                        bw = B[k][8 * h + ln]
                        if not aw or not bw:
                            continue
                        if have[ln] and op == 1:
                            if t == "fp32":
                                x += excess32(aw) * bin(sig32(prev[ln]) ^ sig32(bw)).count("1")
                            else:
                                x += excess_half(aw, 1) * bin(sig16(prev[ln], 1) ^ sig16(bw, 1)).count("1")
                                x += excess_half(aw, 0) * bin(sig16(prev[ln], 0) ^ sig16(bw, 0)).count("1")
                        prev[ln], have[ln] = bw, True
    return float(x)


def cmd_features(a):
    job = os.path.abspath(a.job)
    meta = load(os.path.join(job, "tiles-meta.json"))
    feats, missing = {}, []
    for line in open(os.path.join(job, "joblist.txt")):
        if not line.strip():
            continue
        t, sha, ns = line.split()
        p = os.path.join(job, "out", f"{sha}.json")
        if not os.path.exists(p):
            missing.append(sha)
            continue
        o = json.loads(open(p).read().strip().splitlines()[-1])
        if o["type"] != t:
            stop(f"type differs for {sha}")
        want = [int(n) for n in ns.split(",")]
        if sorted(int(n) for n in o["x_acc"]) != want:
            stop(f"N list differs for {sha}")
        feats[sha] = {"type": t, "x_acc": {str(n): o["x_acc"][str(n)] for n in want}, "x_bth": float(o["x_bth_per_op"]),
                      "unique_elements": o["unique_elements"], "uops_per_op": o["uops_per_op"]}
    if missing:
        stop(f"{len(missing)} tiles have no trace output")
    # T1: E178's 40 kinds against flipmodel_e178's c_store launch mean at N_LAUNCH
    fc = load(os.path.join(E178T, "forecast-e178.json"))["kinds"]
    t1 = {}
    for k in load(os.path.join(E178T, "kinds-e178.json"))["kinds"]:
        f = feats[k["sha256"]]
        mine = f["x_acc"][str(N_LAUNCH_E178[k["type"]])]["total"]
        reg = fc[k["key"]]["flips_i"]["launch_mean"]["c_store"]
        t1[k["key"]] = {"x_acc": mine, "flipmodel_c_store": reg, "diff": mine - reg}
        if abs(mine - reg) > 1e-3:
            stop(f"T1 fails for {k['key']}: {mine} against {reg}")
    # T2: x_bth in Python against the C value, on every float tile of rows (b) and (c) and 20 of (a) by a fixed rule (sha order)
    t2, sel = {}, []
    rows = assemble()
    for r in rows:
        if r["fam"] == "float" and (r["src"] in ("b", "c")):
            sel.append((r["type"], r["sha"], r["tile"]))
    fa = sorted({(r["type"], r["sha"], r["tile"]) for r in rows if r["fam"] == "float" and r["src"] == "a"}, key=lambda x: x[1])
    sel += fa[:20]
    for t, sha, tile in sorted(set(sel)):
        py = bth_python(open(os.path.join(ROOT, tile), "rb").read(), t)
        t2[sha] = {"python": py, "c": feats[sha]["x_bth"]}
        if abs(py - feats[sha]["x_bth"]) > 1e-6:
            stop(f"T2 fails for {tile}: {py} against {feats[sha]['x_bth']}")
    out = {"_what": "M10-ACC's features per tile (acctrace_m10acc.c on the mini), by sha256 of the tile's 2,048 bytes; x_acc per op "
                    "(launch mean over ops 1..N-1) at each N, x_bth per op (floats)", "registration": "tools/claims-v3/m10-acc/REGISTRATION.md (b5586759)",
           "launch_sizes": meta["launch_sizes"], "tiles": feats, "grid_e182": meta["grid"],
           "checks": {"T1_e178_against_flipmodel_c_store": {"pass": True, "n": len(t1), "max_abs_diff": max(abs(v["diff"]) for v in t1.values()),
                                                             "kinds": t1},
                      "T2_x_bth_python_against_c": {"pass": True, "n": len(t2), "tiles": t2}}}
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "features-m10acc.json"), "w"), indent=1, sort_keys=True)
    print(f"features: {len(feats)} tiles; T1 PASS ({len(t1)} kinds, max |diff| {out['checks']['T1_e178_against_flipmodel_c_store']['max_abs_diff']:.2e}); "
          f"T2 PASS ({len(t2)} tiles)")


# ------------------------------------------------------------------ section 4: the fit
def ols0(Z, e):
    """least squares through the origin; Z (n, p)"""
    Z, e = np.asarray(Z, float), np.asarray(e, float)
    tau, *_ = np.linalg.lstsq(Z, e, rcond=None)
    return tau


def design(rows, feats, ls, cols):
    """z per row, W per J a toggle: s x c x rate x (x(item) - x(zero))"""
    Z = np.zeros((len(rows), len(cols)))
    X = np.zeros((len(rows), 2))
    for i, r in enumerate(rows):
        n = str(ls[r["nexp"]]["by_type"][r["type"]]["N"])
        fi = feats[r["sha"]]
        xa, xb = fi["x_acc"][n]["total"], fi["x_bth"]
        if r.get("zero_sha"):
            fz = feats[r["zero_sha"]]
            xa, xb = xa - fz["x_acc"][n]["total"], xb - fz["x_bth"]
        X[i] = (xa, xb)
        k = r["s"] * r["c"] * r["rate"]
        for j, q in enumerate(cols):
            Z[i, j] = k * (xa if q == "acc" else xb)
    return Z, X


def loro(rows, Z, e):
    runs = sorted({r["run"] for r in rows})
    ep = np.array(e, float).copy()
    taus = {}
    for R in runs:
        m = np.array([r["run"] == R for r in rows])
        if m.all():
            continue
        t = ols0(Z[~m], e[~m])
        taus[R] = t
        ep[m] = e[m] - Z[m] @ t
    return ep, taus


def jackknife(taus):
    T = np.array(list(taus.values()))
    n = len(T)
    mean = T.mean(axis=0)
    se = np.sqrt((n - 1) / n * ((T - mean) ** 2).sum(axis=0))
    return se, n


def cluster_boot_tau(rows, Z, e, seed):
    runs = sorted({r["run"] for r in rows})
    idx = {R: np.where(np.array([r["run"] == R for r in rows]))[0] for R in runs}
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(NB):
        pick = rng.integers(0, len(runs), len(runs))
        ii = np.concatenate([idx[runs[p]] for p in pick])
        out.append(ols0(Z[ii], e[ii]))
    out = np.array(out)
    return np.percentile(out, 2.5, axis=0), np.percentile(out, 97.5, axis=0)


def boot_d_runs(rows, e, ep, seed):
    runs = sorted({r["run"] for r in rows})
    idx = {R: np.where(np.array([r["run"] == R for r in rows]))[0] for R in runs}
    rng = np.random.default_rng(seed)
    ds = []
    for _ in range(NB):
        pick = rng.integers(0, len(runs), len(runs))
        ii = np.concatenate([idx[runs[p]] for p in pick])
        ds.append(rms(ep[ii]) - rms(e[ii]))
    return float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))


def boot_d_kinds(e, ep, seed):
    rng = np.random.default_rng(seed)
    n = len(e)
    ds = []
    for _ in range(NB):
        ii = rng.integers(0, n, n)
        ds.append(rms(ep[ii]) - rms(e[ii]))
    return float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))


def summ(e, ep, mask):
    e, ep = np.asarray(e)[mask], np.asarray(ep)[mask]
    if not len(e):
        return None
    return {"n": int(len(e)), "rms_M10": rms(e), "bias_M10": float(np.mean(e)), "rms_ACC": rms(ep), "bias_ACC": float(np.mean(ep)),
            "d": rms(ep) - rms(e)}


def family_fit(rows, feats, ls, fam, cols, label):
    rr = [r for r in rows if r["fam"] == fam]
    Z, X = design(rr, feats, ls, cols)
    e = np.array([r["e"] for r in rr])
    tau = ols0(Z, e)
    ep, taus = loro(rr, Z, e)
    se, nj = jackknife(taus)
    tq = float(stats.t.ppf(0.975, nj - 1))
    lo, hi = cluster_boot_tau(rr, Z, e, SEED_JACK_BOOT)
    res = e - Z @ tau
    dof = max(len(e) - len(cols), 1)
    cov = float(res @ res) / dof * np.linalg.inv(Z.T @ Z)
    out = {"label": label, "family": fam, "cols": cols, "n_rows": len(rr), "n_runs": nj, "tau_J": {q: float(tau[j]) for j, q in enumerate(cols)},
           "tau_fJ": {q: float(tau[j]) * 1e15 for j, q in enumerate(cols)},
           "jackknife": {q: {"se_J": float(se[j]), "t975": tq, "lo95_J": float(tau[j] - tq * se[j]), "hi95_J": float(tau[j] + tq * se[j])}
                         for j, q in enumerate(cols)},
           "cluster_boot_runs": {q: {"lo95_J": float(lo[j]), "hi95_J": float(hi[j]), "draws": NB, "seed": SEED_JACK_BOOT} for j, q in enumerate(cols)},
           "ols_se_J": {q: float(math.sqrt(cov[j, j])) for j, q in enumerate(cols)},
           "loro_tau_range_J": {q: [float(min(t[j] for t in taus.values())), float(max(t[j] for t in taus.values()))] for j, q in enumerate(cols)},
           "loro_tau_sign_changes": {q: bool(min(t[j] for t in taus.values()) < 0 < max(t[j] for t in taus.values())) for j, q in enumerate(cols)}}
    return out, rr, Z, X, e, ep, taus


def readings(rr, e, ep, fam):
    card = np.array([r["card"] for r in rr])
    typ = np.array([r["type"] for r in rr])
    src = np.array([r["src"] for r in rr])
    scl = np.array([bool(r.get("s_class")) for r in rr])
    out = {"all": summ(e, ep, np.ones(len(rr), bool))}
    for c in ("a3", "c1"):
        out[f"card {c}"] = summ(e, ep, card == c)
    for t in sorted(set(typ)):
        out[f"type {t}"] = summ(e, ep, typ == t)
        for c in ("a3", "c1"):
            s = summ(e, ep, (typ == t) & (card == c))
            if s:
                out[f"type {t} card {c}"] = s
    for s_ in ("a", "b", "c", "d"):
        s = summ(e, ep, src == s_)
        if s:
            out[f"source {s_}"] = s
    if fam == "float":
        out["S class"] = summ(e, ep, scl)
    return out


def rule(rr, e, ep, fam):
    lo, hi = boot_d_runs(rr, e, ep, SEED_RULE)
    d = rms(ep) - rms(e)
    card = np.array([r["card"] for r in rr])
    d_a3 = rms(ep[card == "a3"]) - rms(e[card == "a3"])
    d_c1 = rms(ep[card == "c1"]) - rms(e[card == "c1"])
    R1 = d <= -0.005 and hi < 0
    R2 = d_a3 < 0 and d_c1 < 0
    out = {"R1": {"d_w": d, "lo95_w": lo, "hi95_w": hi, "draws": NB, "seed": SEED_RULE, "holds": bool(R1)},
           "R2": {"d_a3_w": d_a3, "d_c1_w": d_c1, "holds": bool(R2)}}
    ok = R1 and R2
    if fam == "float":
        scl = np.array([bool(r.get("s_class")) for r in rr])
        dS = rms(ep[scl]) - rms(e[scl])
        out["R3"] = {"n": int(scl.sum()), "d_S_w": dS, "holds": bool(dS <= 0)}
        ok = ok and dS <= 0
    out["enters"] = bool(ok)
    return out


def cmd_fit(a):
    fpath = os.path.join(a.out, "features-m10acc.json")
    F = load(fpath)
    if not (F["checks"]["T1_e178_against_flipmodel_c_store"]["pass"] and F["checks"]["T2_x_bth_python_against_c"]["pass"]):
        stop("the features' checks did not pass")
    feats, ls = F["tiles"], F["launch_sizes"]
    rows = assemble()
    m10 = load(os.path.join(M10D, "m10.json"))
    L = ["Q153(m10acc): M10-ACC, the accumulator-toggle term (fit_m10acc.py fit; REGISTRATION.md b5586759). Errors are measured - predicted, W.", ""]
    L.append(f"rows {len(rows)}: " + ", ".join(f"{k} {v}" for k, v in counts(rows).items()))
    fit = {"_what": "M10-ACC's fit, held-out errors, rule, arms, forecasts and post hoc readings (fit_m10acc.py)",
           "registration": "tools/claims-v3/m10-acc/REGISTRATION.md (b5586759)", "features_sha256": fsha(fpath), "counts": counts(rows),
           "families": {}, "arms": {}, "forecasts_P9": {}, "posthoc": {}}
    prim = {}
    per_row = {}
    for fam, cols in (("float", ["acc", "bth"]), ("int8", ["acc"])):
        o, rr, Z, X, e, ep, taus = family_fit(rows, feats, ls, fam, cols, "primary")
        o["readings_heldout"] = readings(rr, e, ep, fam)
        o["rule"] = rule(rr, e, ep, fam)
        o["loro_tau_by_run_J"] = {R: [float(v) for v in t] for R, t in sorted(taus.items())}
        o["sigma_ACC_w"] = {k: v["rms_ACC"] for k, v in o["readings_heldout"].items() if v and (k.startswith("type") or k == "all")}
        fit["families"][fam] = o
        prim[fam] = (rr, Z, X, e, ep, taus, o)
        for i, r in enumerate(rr):
            per_row[(r["src"], r["run"], r["key"])] = {"x_acc": float(X[i, 0]), "x_bth": float(X[i, 1]), "z": [float(v) for v in Z[i]],
                                                        "e_prime": float(ep[i])}
    # arm ACC1: floats with x_acc alone
    o, rr, Z, X, e, ep, taus = family_fit(rows, feats, ls, "float", ["acc"], "ACC1")
    o["readings_heldout"] = readings(rr, e, ep, "float")
    o["rule_reading"] = rule(rr, e, ep, "float")
    fit["arms"]["ACC1_float"] = o
    acc1_ep = {(r["src"], r["run"], r["key"]): float(ep[i]) for i, r in enumerate(rr)}
    # arm strict: fitted on (a) and (c) only; (b) and (d) predicted from the fit on all of (a) and (c)
    strict_ep = {}
    for fam, cols in (("float", ["acc", "bth"]), ("int8", ["acc"])):
        tr = [r for r in rows if r["fam"] == fam and r["src"] in ("a", "c")]
        te = [r for r in rows if r["fam"] == fam and r["src"] in ("b", "d")]
        o, rr, Z, X, e, ep, taus = family_fit(tr, feats, ls, fam, cols, "strict")
        o["readings_heldout_a_c"] = readings(rr, e, ep, fam)
        Zt, Xt = design(te, feats, ls, cols)
        et = np.array([r["e"] for r in te])
        tau = np.array([o["tau_J"][q] for q in cols])
        ept = et - Zt @ tau
        o["readings_b_d_from_a_c"] = readings(te, et, ept, fam)
        fit["arms"][f"strict_{fam}"] = o
        for i, r in enumerate(rr):
            strict_ep[(r["src"], r["run"], r["key"])] = float(ep[i])
        for i, r in enumerate(te):
            strict_ep[(r["src"], r["run"], r["key"])] = float(ept[i])
    # forecasts for the next blind pool's rule (F-P9): pool 8's rows (b), held-out errors of the primary
    for fam in ("float", "int8"):
        rr, Z, X, e, ep, taus, o = prim[fam]
        src = np.array([r["src"] for r in rr])
        card = np.array([r["card"] for r in rr])
        scl = np.array([bool(r.get("s_class")) for r in rr])
        f = {}
        for c in ("a3", "c1"):
            m = (src == "b") & (card == c)
            lo, hi = boot_d_kinds(e[m], ep[m], SEED_FP9)
            f[f"pool8 {c}"] = {"n": int(m.sum()), "d_w": rms(ep[m]) - rms(e[m]), "lo95_w": lo, "hi95_w": hi, "rms_M10": rms(e[m]), "rms_ACC": rms(ep[m])}
            if fam == "float":
                m2 = m & scl
                lo, hi = boot_d_kinds(e[m2], ep[m2], SEED_FP9)
                f[f"pool8 class S {c}"] = {"n": int(m2.sum()), "d_w": rms(ep[m2]) - rms(e[m2]), "lo95_w": lo, "hi95_w": hi,
                                           "rms_M10": rms(e[m2]), "bias_M10": float(np.mean(e[m2])), "rms_ACC": rms(ep[m2]),
                                           "bias_ACC": float(np.mean(ep[m2]))}
        fit["forecasts_P9"][fam] = f
    # post hoc readings
    ph = fit["posthoc"]
    rr, Z, X, e, ep, taus, o = prim["float"]
    cls = []
    for i, r in enumerate(rr):
        if r["src"] == "b" and r.get("s_class"):
            k = (r["src"], r["run"], r["key"])
            cls.append({"card": r["card"], "tile": r["key"], "e_M10": r["e"], "e_ACC": float(ep[i]), "e_ACC1": acc1_ep[k], "e_strict": strict_ep[k],
                        "x_acc_per_op": float(X[i, 0]), "x_acc_per_uop": float(X[i, 0]) / UOPS[r["type"]], "x_bth_per_op": float(X[i, 1])})
    ph["pool8_class_S"] = {"tiles": cls}
    for c in ("a3", "c1"):
        sel = [x for x in cls if x["card"] == c]
        ph["pool8_class_S"][c] = {q: {"rms": rms([x[q] for x in sel]), "bias": float(np.mean([x[q] for x in sel]))}
                                  for q in ("e_M10", "e_ACC", "e_ACC1", "e_strict")} | {"n": len(sel)}
    # E178
    for fam in ("int8", "float"):
        rr, Z, X, e, ep, taus, o = prim[fam]
        tau_wo = taus.get("E178|a3")
        ks = []
        for i, r in enumerate(rr):
            if r["src"] != "d":
                continue
            k = (r["src"], r["run"], r["key"])
            ks.append({"kind": r["key"], "type": r["type"], "D_minus_P_w": r["e"], "D_minus_F_w": r["e_F"], "e_ACC": float(ep[i]),
                       "e_strict": strict_ep[k], "x_acc_per_op": float(X[i, 0]), "x_acc_per_uop": float(X[i, 0]) / UOPS[r["type"]],
                       "term_w_loro": float(Z[i] @ tau_wo), "term_w_frozen": float(Z[i] @ np.array([o["tau_J"][q] for q in o["cols"]]))})
        if fam == "int8":
            ph["e178_int8_levels"] = {"kinds": ks}
            for q in ("D_minus_P_w", "D_minus_F_w", "e_ACC", "e_strict"):
                ph["e178_int8_levels"][q] = {"rms": rms([x[q] for x in ks]), "bias": float(np.mean([x[q] for x in ks])), "n": len(ks)}
            # his pair, 5s - 4s
            rule_h = load(os.path.join(E178D, "scored.json"))["primary"]["rules"]["E178-H-int8"]
            k5 = next(x for x in ks if x["kind"] == "int8.e178_v5")
            k4 = next(x for x in ks if x["kind"] == "int8.e178_v4")
            st = fit["arms"]["strict_int8"]["tau_J"]["acc"]
            r5 = next(r for r in rr if r["src"] == "d" and r["key"] == "int8.e178_v5")
            r4 = next(r for r in rr if r["src"] == "d" and r["key"] == "int8.e178_v4")
            dterm_strict = st * (r5["rate"] * k5["x_acc_per_op"] - r4["rate"] * k4["x_acc_per_op"])
            ph["e178_int8_pair_5s_minus_4s"] = {
                "measured_w": rule_h["mean_w"], "lo95_w": rule_h["lo95_w"], "hi95_w": rule_h["hi95_w"], "P_w": rule_h["dP_w"],
                "dterm_w_loro": k5["term_w_loro"] - k4["term_w_loro"], "P_plus_term_w_loro": rule_h["dP_w"] + k5["term_w_loro"] - k4["term_w_loro"],
                "dterm_w_frozen": k5["term_w_frozen"] - k4["term_w_frozen"],
                "P_plus_term_w_frozen": rule_h["dP_w"] + k5["term_w_frozen"] - k4["term_w_frozen"],
                "dterm_w_strict": dterm_strict, "P_plus_term_w_strict": rule_h["dP_w"] + dterm_strict,
                "x_acc_5s_per_op": k5["x_acc_per_op"], "x_acc_4s_per_op": k4["x_acc_per_op"]}
        else:
            ph["e178_float_levels"] = {"kinds": ks}
            for t in ("fp32", "fp16"):
                sel = [x for x in ks if x["type"] == t]
                ph["e178_float_levels"][t] = {q: {"rms": rms([x[q] for x in sel]), "bias": float(np.mean([x[q] for x in sel]))}
                                              for q in ("D_minus_P_w", "D_minus_F_w", "e_ACC", "e_strict")} | {"n": len(sel)}
    # E67's launch-size sensitivity (reported)
    e67 = {}
    lo_n, hi_n = ls["E67"]["by_type"]["fp32"]["min"], ls["E67"]["by_type"]["fp32"]["max"]
    for r in rows:
        if r["exp"] == "E67":
            fi, fz = feats[r["sha"]], feats[r["zero_sha"]]
            e67[r["key"]] = {str(n): fi["x_acc"][str(n)]["total"] - fz["x_acc"][str(n)]["total"]
                             for n in (lo_n, ls["E67"]["by_type"]["fp32"]["N"], hi_n)}
    fit["e67_launch_sensitivity"] = e67
    # the frozen term
    m10acc = {"_model": "M10-ACC (Q153): M10 + s x c x rate x (tau_acc x x_acc + tau_bth x x_bth), tools/claims-v3/m10-acc/REGISTRATION.md",
              "registration": "tools/claims-v3/m10-acc/REGISTRATION.md (b5586759)", "m10": "docs/reports/data/2026-11-04-q142m-m10/m10.json (6829c9ba)",
              "card1_scale": {f: m10["families"][f]["card1_scale"] for f in ("float", "int8")},
              "uops_per_op": UOPS, "N_rule": "the median, rounded half up, of a kit's timed launches' iters by type (REGISTRATION.md 2.3)",
              "N_e178": {t: ls["E178"]["by_type"][t]["N"] for t in ("fp32", "fp16", "int8")}, "families": {}}
    for fam in ("float", "int8"):
        o = fit["families"][fam]
        m10acc["families"][fam] = {"tau_J": o["tau_J"], "jackknife_95_J": {q: [v["lo95_J"], v["hi95_J"]] for q, v in o["jackknife"].items()},
                                   "cluster_boot_95_J": {q: [v["lo95_J"], v["hi95_J"]] for q, v in o["cluster_boot_runs"].items()},
                                   "sigma_ACC_w": o["sigma_ACC_w"], "rule": o["rule"], "enters": o["rule"]["enters"]}
    m10acc["strict_arm_tau_J"] = {f: fit["arms"][f"strict_{f}"]["tau_J"] for f in ("float", "int8")}
    m10acc["ACC1_arm_tau_J"] = fit["arms"]["ACC1_float"]["tau_J"]
    # forecasts for E182's planned kinds: the grid, aifoundry3 and card 1, at E178's N and measured rates, s = 1
    rate178 = {t: statistics.median([r["rate"] for r in rows if r["src"] == "d" and r["type"] == t]) for t in ("fp32", "fp16", "int8")}
    grid = []
    for g in F["grid_e182"]:
        t, fam = g["type"], fam_of(g["type"])
        n = str(m10acc["N_e178"][t])
        xa = feats[g["sha"]]["x_acc"][n]["total"]
        ta = m10acc["families"][fam]["tau_J"]["acc"]
        lo95, hi95 = m10acc["families"][fam]["jackknife_95_J"]["acc"]
        row = {"type": t, "a": g["a"], "b": g["b"], "a_word": g["a_word"], "b_word": g["b_word"], "x_acc_per_op": xa,
               "x_acc_per_uop": xa / UOPS[t], "rate": rate178[t]}
        for c in ("a3", "c1"):
            cc = m10acc["card1_scale"][fam] if c == "c1" else 1.0
            row[f"term_w_{c}"] = cc * rate178[t] * ta * xa
            row[f"term_w_{c}_95"] = sorted([cc * rate178[t] * lo95 * xa, cc * rate178[t] * hi95 * xa])
        grid.append(row)
    fe = {"_what": "M10-ACC's frozen forecasts for E182's planned kinds: the term's watts for a grid of one-number kinds (REGISTRATION.md "
                   "section 6), aifoundry3 and card 1, at E178's launch sizes and median measured rates, s = 1; add to E182's own M10 forecast P",
          "N": m10acc["N_e178"], "rate": rate178, "tau_J": {f: m10acc["families"][f]["tau_J"] for f in ("float", "int8")}, "kinds": grid}
    # write
    os.makedirs(a.out, exist_ok=True)
    rows_out = []
    for r in rows:
        k = (r["src"], r["run"], r["key"])
        q = dict(r)
        q.update(per_row[k])
        q["e_prime_ACC1"] = acc1_ep.get(k)
        q["e_prime_strict"] = strict_ep.get(k)
        q["N"] = ls[r["nexp"]]["by_type"][r["type"]]["N"]
        rows_out.append(q)
    json.dump(rows_out, open(os.path.join(a.out, "rows-m10acc.json"), "w"), indent=1, sort_keys=True)
    json.dump(fit, open(os.path.join(a.out, "fit-m10acc.json"), "w"), indent=1, sort_keys=True)
    json.dump(m10acc, open(os.path.join(a.out, "m10acc.json"), "w"), indent=1, sort_keys=True)
    json.dump(fe, open(os.path.join(a.out, "forecasts-e182-m10acc.json"), "w"), indent=1, sort_keys=True)
    # the text summary
    for fam in ("float", "int8"):
        o = fit["families"][fam]
        L.append("")
        L.append(f"== {fam}: {o['n_rows']} rows in {o['n_runs']} runs; primary form {'+'.join(o['cols'])}")
        for q in o["cols"]:
            j, b = o["jackknife"][q], o["cluster_boot_runs"][q]
            L.append(f"  tau_{q} = {o['tau_fJ'][q]:+.4f} fJ a toggle; jackknife 95% [{j['lo95_J'] * 1e15:+.4f}, {j['hi95_J'] * 1e15:+.4f}] "
                     f"(se {j['se_J'] * 1e15:.4f}, t {j['t975']:.3f}); runs bootstrap [{b['lo95_J'] * 1e15:+.4f}, {b['hi95_J'] * 1e15:+.4f}]; "
                     f"OLS se {o['ols_se_J'][q] * 1e15:.4f}; LORO range [{o['loro_tau_range_J'][q][0] * 1e15:+.4f}, {o['loro_tau_range_J'][q][1] * 1e15:+.4f}]")
        for k, v in o["readings_heldout"].items():
            if v:
                L.append(f"  {k:24s} n {v['n']:4d}  M10 {v['rms_M10']:.4f} ({v['bias_M10']:+.4f})  M10-ACC {v['rms_ACC']:.4f} ({v['bias_ACC']:+.4f})  d {v['d']:+.4f}")
        ru = o["rule"]
        L.append(f"  R1 d {ru['R1']['d_w']:+.4f} [{ru['R1']['lo95_w']:+.4f}, {ru['R1']['hi95_w']:+.4f}] -> {'holds' if ru['R1']['holds'] else 'fails'}; "
                 f"R2 a3 {ru['R2']['d_a3_w']:+.4f} c1 {ru['R2']['d_c1_w']:+.4f} -> {'holds' if ru['R2']['holds'] else 'fails'}"
                 + (f"; R3 d_S {ru['R3']['d_S_w']:+.4f} over {ru['R3']['n']} -> {'holds' if ru['R3']['holds'] else 'fails'}" if "R3" in ru else "")
                 + f"; ENTERS: {'yes' if ru['enters'] else 'no'}")
    L.append("")
    a1 = fit["arms"]["ACC1_float"]
    L.append(f"arm ACC1 (floats, x_acc alone): tau_acc {a1['tau_fJ']['acc']:+.4f} fJ; all d {a1['readings_heldout']['all']['d']:+.4f}; "
             f"S class d {a1['readings_heldout']['S class']['d']:+.4f}")
    for fam in ("float", "int8"):
        s_ = fit["arms"][f"strict_{fam}"]
        L.append(f"arm strict ({fam}, fitted on a and c): tau " + ", ".join(f"{q} {v:+.4f} fJ" for q, v in s_["tau_fJ"].items())
                 + f"; (b, d) from (a, c): " + ", ".join(f"{k} d {v['d']:+.4f}" for k, v in s_["readings_b_d_from_a_c"].items() if v and k in ("all", "source b", "source d")))
    L.append("")
    L.append("F-P9, forecasts for a pool drawn like pool 8 (held-out errors of pool 8's rows; bootstrap over kinds):")
    for fam, f in fit["forecasts_P9"].items():
        for k, v in f.items():
            L.append(f"  {fam} {k:20s} n {v['n']:3d}  d {v['d_w']:+.4f} [{v['lo95_w']:+.4f}, {v['hi95_w']:+.4f}]  M10 {v['rms_M10']:.4f} -> {v['rms_ACC']:.4f}")
    L.append("")
    L.append("POST HOC (pool 8 and E178 were read before the registration):")
    for c in ("a3", "c1"):
        v = ph["pool8_class_S"][c]
        L.append(f"  pool 8 class S {c} (n {v['n']}): M10 {v['e_M10']['rms']:.3f} ({v['e_M10']['bias']:+.3f}); M10-ACC {v['e_ACC']['rms']:.3f} ({v['e_ACC']['bias']:+.3f}); "
                 f"ACC1 {v['e_ACC1']['rms']:.3f} ({v['e_ACC1']['bias']:+.3f}); strict {v['e_strict']['rms']:.3f} ({v['e_strict']['bias']:+.3f})")
    v = ph["e178_int8_levels"]
    L.append(f"  E178 int8 levels (n {v['D_minus_P_w']['n']}): D-P {v['D_minus_P_w']['rms']:.3f} ({v['D_minus_P_w']['bias']:+.3f}); D-F {v['D_minus_F_w']['rms']:.3f} "
             f"({v['D_minus_F_w']['bias']:+.3f}); M10-ACC {v['e_ACC']['rms']:.3f} ({v['e_ACC']['bias']:+.3f}); strict {v['e_strict']['rms']:.3f} ({v['e_strict']['bias']:+.3f})")
    p = ph["e178_int8_pair_5s_minus_4s"]
    L.append(f"  his int8 pair 5s - 4s: measured {p['measured_w']:+.4f} [{p['lo95_w']:+.4f}, {p['hi95_w']:+.4f}]; P {p['P_w']:+.4f}; P + term "
             f"{p['P_plus_term_w_loro']:+.4f} (LORO), {p['P_plus_term_w_frozen']:+.4f} (frozen), {p['P_plus_term_w_strict']:+.4f} (strict)")
    for t in ("fp32", "fp16"):
        v = ph["e178_float_levels"][t]
        L.append(f"  E178 {t} levels (n {v['n']}): D-P {v['D_minus_P_w']['rms']:.3f} ({v['D_minus_P_w']['bias']:+.3f}); D-F {v['D_minus_F_w']['rms']:.3f} "
                 f"({v['D_minus_F_w']['bias']:+.3f}); M10-ACC {v['e_ACC']['rms']:.3f} ({v['e_ACC']['bias']:+.3f}); strict {v['e_strict']['rms']:.3f} ({v['e_strict']['bias']:+.3f})")
    L.append("")
    L.append("E67's launch sensitivity (x_acc step at N min, median, max): " + "; ".join(
        f"{k} " + "/".join(f"{x:.1f}" for x in v.values()) for k, v in e67.items()))
    txt = "\n".join(L) + "\n"
    open(os.path.join(a.out, "fit-output.txt"), "w").write(txt)
    print(txt)


# ------------------------------------------------------------------ self-test (synthetic, before any row is read)
def cmd_selftest(a):
    rng = np.random.default_rng(7)
    rows, Z, e = [], [], []
    true = np.array([3e-15, -1e-15])
    for R in range(12):
        for i in range(30):
            z = rng.uniform(0, 1e13, 2)
            rows.append({"run": f"r{R}", "card": "a3" if R % 2 else "c1", "s_class": i < 3})
            Z.append(z)
            e.append(float(z @ true + rng.normal(0, 0.01)))
    Z, e = np.array(Z), np.array(e)
    tau = ols0(Z, e)
    assert np.allclose(tau, true, rtol=0.05), tau
    ep, taus = loro(rows, Z, e)
    assert len(taus) == 12 and rms(ep) < rms(e)
    se, n = jackknife(taus)
    assert n == 12 and (se > 0).all()
    lo, hi = cluster_boot_tau(rows, Z, e, 1)
    assert (lo <= tau).all() and (tau <= hi).all()
    ru = rule(rows, e, ep, "float")
    assert ru["enters"], ru
    # Booth rows: 1.0 has none in excess; pi and 1/3 have some; the fp16 halves
    assert excess32(0x3F800000) == 0 and excess32(0x3FC00000) == 0 and excess32(0x40490FDB) > 0
    assert excess_half(0x3C003C00, 1) == 0 and excess_half(0x3C003C00, 0) == 0
    raw = one_number_tile("0x40490fdb", "0x3f800000")
    assert bth_python(raw, "fp32") == 0.0           # constant B: no toggles
    w = [0x40490FDB] * 256 + [0x3F800000 if j < 8 else 0x3F800001 for k in range(16) for j in range(16)]
    raw = struct.pack("<512I", *w)
    exp = 512 * 8 * excess32(0x40490FDB) * 1
    assert bth_python(raw, "fp32") == exp, (bth_python(raw, "fp32"), exp)
    print("SELFTEST PASS: estimator, leave-one-run-out, jackknife, run bootstrap, rule; Booth rows (1.0 and 1.5 excess 0; pi "
          f"{excess32(0x40490FDB)}); x_bth of a one-bit B toggle under A = pi = 512 x 8 x {excess32(0x40490FDB)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("selftest", "tiles", "features", "fit"))
    ap.add_argument("--job")
    ap.add_argument("--out", default=os.path.join(DD, "2026-11-07-q153-m10acc"))
    a = ap.parse_args()
    {"selftest": cmd_selftest, "tiles": cmd_tiles, "features": cmd_features, "fit": cmd_fit}[a.cmd](a)


if __name__ == "__main__":
    main()
