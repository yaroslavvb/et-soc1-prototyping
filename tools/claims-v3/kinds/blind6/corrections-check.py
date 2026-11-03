#!/usr/bin/env python3
"""Q139(b) blind pool 6: the checks behind CORRECTIONS.md (Tue 3 Nov 2026, the fix pass after the pool's independent
verification, whose verdict was "holds with fixes").

Desk only. It reads the frozen pool (blind6.json, MANIFEST, SHA256SUMS, the tiles, make_blind6.py, fetch_real6.py,
real/) and make_kinds.py, and changes nothing in the pool. It writes corrections-check.json and corrections-check.txt
in --out-dir (default: this file's directory), and with --network also corrections-network.json.

    python3 -B tools/claims-v3/kinds/blind6/corrections-check.py --ccheck     # numpy, plus cc for Q139(k)'s accum.c
    python3 -B tools/claims-v3/kinds/blind6/corrections-check.py --network    # huggingface.co, about 28 MB; numpy

Sections (CORRECTIONS.md quotes the same numbers):
 0  the frozen c_check reproduces: make_blind6.c_check, unchanged, on all 50 tiles equals blind6.json's, tile by tile,
    so this environment computes what the designer's did;
 1  C1: fp16's C under the card's rule (E36 LAT-S1 "math": every two-term update applied) against the frozen
    PRM-literal one; make_blind6.c_check runs unchanged except that every fp16 update applies;
 2  C2: the launch-end C descriptor as a mean over non-power-of-two op counts (fp16 under the card's rule), against
    the frozen one-op-from-2^19-or-2^20 figure;
 3  C3: the subnormal departure in fp16.real_smol_softmax_v: what keeping that value would move, under each rule;
 4  C4 (--ccheck): the first op's C against Q139(k)'s reference (tools/claims-v3/ccheck/ccheck.py, accum.c), n = 1;
 5  C5: rule texts checked on the bytes (exp_only_narrow2's exponent steps; the a_onebit tiles' words);
 6  C6: the pool's own files: SHA256SUMS against the 80 files it lists, the MANIFEST hash, and the 52 files
    make_blind6.py builds compared alone (what its --check should compare), with every other file listed;
 7  (--network) the real tiles: fetch_real6.py, unchanged, re-run into a temporary directory (every cut and
    provenance.json must equal the frozen ones byte for byte); the down projection input's zero-word share over the
    whole layer; the licence and base model each model card declares at the pinned revision.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile

sys.dont_write_bytecode = True   # never leave __pycache__ in the pool's (or any lab) directory

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST_SHA = "a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0"
NOTE_FILES = {"CORRECTIONS.md", "corrections-check.py", "corrections-check.json", "corrections-check.txt",
              "corrections-network.json"}
CYCLES_PER_OP = {"fp32": 546, "fp16": 546, "int8": 318}                      # surface_hpl.py; E36's LAT-S1
LAUNCH_OPS = {t: int(round(0.5 * 600e6 / c)) for t, c in CYCLES_PER_OP.items()}   # a 0.5 s launch at 600 MHz
END_FACTORS = [0.825 + 0.05 * k for k in range(8)]                           # 8 starting counts, +-17.5% of a launch
END_OPS = 32                                                                  # consecutive ops from each start
RULE_FROZEN = "PRM 9.4's pseudo-code taken literally: the two-term update applies only when a1, a2, b1 and b2 are all nonzero"
RULE_CARD = ("the card's (E36 LAT-S1 'math': fp16 pair result 'math' at 50% and 100%, 3 kept passes on each of aifoundry1 "
             "card 1, aifoundry2 and aifoundry3; blind pool 5's CORRECTIONS.md C1): the plain sum a1*b1 + a2*b2 for "
             "every k pair; A-side half zeros tested directly, B-side ones by the update's symmetry")


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=HERE, help="the blind6 directory (default: this file's directory)")
    ap.add_argument("--kinds-dir", default=None, help="the directory holding make_kinds.py (default: the pool's parent)")
    ap.add_argument("--repo", default=None, help="the lab repo's top directory (default: three levels above --kinds-dir)")
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--ccheck", action="store_true", help="section 4: needs cc and tools/claims-v3/ccheck/ccheck.py")
    ap.add_argument("--ccheck-cache", default=None, help="accum.c's build cache (default: ccheck.py's own)")
    ap.add_argument("--network", action="store_true", help="section 7 only: huggingface.co, writes corrections-network.json")
    a = ap.parse_args()
    a.pool = os.path.abspath(a.pool)
    a.kinds_dir = os.path.abspath(a.kinds_dir or os.path.dirname(a.pool))
    a.repo = os.path.abspath(a.repo or os.path.join(a.kinds_dir, "..", "..", ".."))
    a.out_dir = os.path.abspath(a.out_dir)
    return a


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(pool, kinds_dir):
    sys.path.insert(0, kinds_dir)
    sys.path.insert(0, pool)
    import make_kinds   # noqa: E402
    import make_blind6  # noqa: E402
    make_blind6.mk = make_kinds
    return make_kinds, make_blind6


def make_rules(mb):
    """make_blind6.steps_of as frozen (PRM-literal for fp16) and the card's (every fp16 update applies)."""
    literal = mb.steps_of

    def card(a, b, type_name):
        st, ap = literal(a, b, type_name)
        if type_name == "fp16":
            ap = [np.ones_like(x, dtype=bool) for x in ap]
        return st, ap

    return {"literal": literal, "card": card}


@contextlib.contextmanager
def rule(mb, rules, name):
    mb.steps_of = rules[name]
    try:
        yield
    finally:
        mb.steps_of = rules["literal"]


def operands(mk, raw, type_name):
    A, B = mk.decode(raw, type_name)
    if type_name == "int8":
        return A.astype(np.int64), B.astype(np.int64)
    return A.astype(np.float64), B.astype(np.float64)


def first_op(mk, mb, raw, type_name):
    a, b = operands(mk, raw, type_name)
    steps, applies = mb.steps_of(a, b, type_name)
    zero = np.zeros((16, 16), dtype=np.int64 if type_name == "int8" else np.float32)
    c1, _, _ = mb.run_op(zero, steps, applies, type_name)
    return c1


def as_words(c, type_name):
    if type_name == "int8":
        return (np.asarray(c, dtype=np.int64) & 0xFFFFFFFF).astype(np.uint32).reshape(-1)
    return np.ascontiguousarray(np.asarray(c, dtype=np.float32)).view(np.uint32).reshape(-1)


def half_zero_words(mk, raw):
    A, B = mk.decode(raw, "fp16")
    za, zb = np.asarray(A, float) == 0, np.asarray(B, float) == 0
    return {"a": int((za[:, 0::2] != za[:, 1::2]).sum()), "b": int((zb[0::2, :] != zb[1::2, :]).sum())}


def end_counts(type_name):
    ns = [int(round(LAUNCH_OPS[type_name] * f)) for f in END_FACTORS]
    assert all(n & (n - 1) for n in ns) and len(set(ns)) == len(ns)       # none a power of two
    return ns


def launch_end(mk, mb, raw, type_name):
    """C-register flips an op near a 0.5 s launch's end: the mean over END_OPS consecutive ops from each of the
    starting counts, C at a start = the count x the op's exact increment, rounded (as make_blind6's own estimate)."""
    a, b = operands(mk, raw, type_name)
    steps, applies = mb.steps_of(a, b, type_name)
    if type_name == "int8":
        d = sum(steps).astype(np.int64)
    else:
        d = sum(steps) if applies is None else sum(np.where(ap, s, 0.0) for s, ap in zip(steps, applies))
    upd = 16 * 256
    per, chs, mov, fin = [], [], [], True
    for n in end_counts(type_name):
        if type_name == "int8":
            c = ((d * n + (1 << 31)) % (1 << 32) - (1 << 31)).astype(np.int64)
        else:
            c = (d * float(n)).astype(np.float32)
            fin &= bool(np.isfinite(c).all())
        tf, tc, tm = 0, 0, 0.0
        for _ in range(END_OPS):
            cn, ch, fl = mb.run_op(c, steps, applies, type_name)
            if type_name != "int8":
                fin &= bool(np.isfinite(cn).all())
            tf, tc, tm = tf + fl, tc + ch, tm + float(np.mean(cn != c))
            c = cn
        per.append(tf / END_OPS)
        chs.append(tc / (END_OPS * upd))
        mov.append(tm / END_OPS)
    return {"c_reg_flips_per_op": int(round(float(np.mean(per)))),
            "c_reg_flips_per_op_range": [int(round(min(per))), int(round(max(per)))],
            "update_change_frac": round(float(np.mean(chs)), 6), "moving_frac": round(float(np.mean(mov)), 6),
            "finite": fin}


def section0(mk, mb, doc, pool):
    bad = []
    for t in doc["tiles"]:
        raw = open(os.path.join(pool, t["file"]), "rb").read()
        if mb.c_check(raw, t["type"]) != t["c_check"]:
            bad.append(t["name"])
    return {"tiles": len(doc["tiles"]), "equal_to_blind6_json": len(doc["tiles"]) - len(bad), "differ": bad}


def section1(mk, mb, rules, doc, pool):
    out, changed, count_only = {}, [], []
    for t in doc["tiles"]:
        if t["type"] != "fp16":
            continue
        raw = open(os.path.join(pool, t["file"]), "rb").read()
        lit = t["c_check"]
        with rule(mb, rules, "card"):
            card = mb.c_check(raw, "fp16")
            c1c = first_op(mk, mb, raw, "fp16")
        c1l = first_op(mk, mb, raw, "fp16")
        a, b = operands(mk, raw, "fp16")
        st, ap = rules["literal"](a, b, "fp16")
        nz_drop = int(sum(((~x) & (s != 0)).sum() for s, x in zip(st, ap)))
        mx = float(np.abs(c1c).max())
        fields = [k for k in card if card[k] != lit.get(k)]
        desc = [k for k in fields if k not in ("updates_dropped_per_op",)]
        out[t["name"]] = {
            "priority": t["priority"], "half_zero_words": half_zero_words(mk, raw),
            "updates_dropped_per_op_literal": lit["updates_dropped_per_op"],
            "dropped_with_nonzero_sum_per_op": nz_drop,
            "c_op1_max_change_rel_to_max_c": round(float(np.abs(c1c.astype(np.float64) - c1l.astype(np.float64)).max()) / mx, 6) if mx else 0.0,
            "c_start_flips": {"literal_as_frozen": lit["c_start"]["c_reg_flips_per_op"], "card": card["c_start"]["c_reg_flips_per_op"]},
            "c_op1_sha256": {"literal_as_frozen": lit["c_op1_sha256"], "card": card["c_op1_sha256"]},
            "fields_changed": fields,
            "card_c_check": card}
        if desc:
            changed.append(t["name"])
        elif lit["updates_dropped_per_op"]:
            count_only.append(t["name"])
    return {"rule_frozen": RULE_FROZEN, "rule_card": RULE_CARD, "tiles": out,
            "c_descriptors_changed": changed, "dropped_count_only": count_only,
            "all_pass_under_card_rule": all(v["card_c_check"]["pass"] for v in out.values())}


def section2(mk, mb, rules, doc, pool):
    out = {}
    for t in doc["tiles"]:
        raw = open(os.path.join(pool, t["file"]), "rb").read()
        with rule(mb, rules, "card"):
            e = launch_end(mk, mb, raw, t["type"])
        frozen = t["c_check"]["c_launch_end_est"]["c_reg_flips_per_op"]
        e["frozen_at_pow2"] = frozen
        e["frozen_at_pow2_ops"] = t["c_check"]["c_launch_end_est"]["ops"]
        e["ratio_to_frozen"] = round(e["c_reg_flips_per_op"] / frozen, 3) if frozen else None
        if t["type"] == "fp16":
            with rule(mb, rules, "literal"):
                e["literal_rule_mean"] = launch_end(mk, mb, raw, "fp16")["c_reg_flips_per_op"]
        out[t["name"]] = e
    r = [v["ratio_to_frozen"] for v in out.values() if v["ratio_to_frozen"] is not None]
    off = sorted(n for n, v in out.items() if v["ratio_to_frozen"] is not None and not 0.8 <= v["ratio_to_frozen"] <= 1.25)
    return {"method": f"mean over {END_OPS} consecutive ops from each of 8 starting counts, "
                      f"round(launch ops x f) for f = 0.825..1.175 step 0.05 (launch ops: fp32/fp16 {LAUNCH_OPS['fp32']}, "
                      f"int8 {LAUNCH_OPS['int8']}, a 0.5 s launch at 600 MHz), none a power of two; fp16 under the "
                      f"card's rule; C at a start = the count x the op's exact increment, rounded",
            "start_counts": {t: end_counts(t) for t in ("fp32", "fp16", "int8")},
            "tiles": out,
            "summary": {"tiles_with_nonzero_end": len(r), "ratio_min": min(r), "ratio_median": float(np.median(r)),
                        "ratio_max": max(r), "off_by_more_than_25pct": len(off), "off_tiles": off}}


def section3(mk, mb, rules, pool):
    real = lambda n: np.load(os.path.join(pool, "real", f"{n}.npy")).astype(np.float64)
    A = mb.pos_zero(real("smol_p_h1_t16_k0_16x32")).astype(np.float16).astype(np.float64)
    Bk = real("smol_v_kv0_k0_d0_32x16").astype(np.float16)
    sub = np.argwhere((np.abs(Bk) < np.float16(2.0 ** -14)) & (Bk != 0))
    Bk = mb.pos_zero(Bk.astype(np.float64))
    Bz = Bk.copy()
    Bz[tuple(sub.T)] = 0.0
    tile = open(os.path.join(pool, "tiles", "fp16", "fp16.real_smol_softmax_v.bin"), "rb").read()
    Ad, Bd = operands(mk, tile, "fp16")
    out = {"subnormals_in_b": int(len(sub)), "at_k_j": sub.tolist(), "value": float(Bk[tuple(sub[0])]),
           "frozen_tile_equals_the_cut_with_it_zeroed": bool(np.array_equal(Ad, A) and np.array_equal(Bd, Bz))}
    for name in ("card", "literal"):
        cs = []
        for B in (Bk, Bz):
            st, ap = rules[name](A, B, "fp16")
            c1, _, _ = mb.run_op(np.zeros((16, 16), np.float32), st, ap, "fp16")
            cs.append(c1.astype(np.float64))
        out[f"keeping_it_moves_c_op1_rel_to_max_c_{name}"] = float(np.abs(cs[0] - cs[1]).max() / np.abs(cs[1]).max())
    return out


def section4(mk, mb, rules, doc, pool, repo, cache):
    sys.path.insert(0, os.path.join(repo, "tools", "claims-v3", "ccheck"))
    import ccheck  # noqa: E402
    cache = cache or ccheck.default_cache()
    out, agg = {}, {"fp32": [0, 0], "fp16": [0, 0, 0], "int8": [0, 0]}
    for t in doc["tiles"]:
        typ = t["type"]
        raw = open(os.path.join(pool, t["file"]), "rb").read()
        ref = np.frombuffer(ccheck.ref_many(typ, raw, [1], cache)[1], dtype="<u4")
        row = {}
        for name in (("literal", "card") if typ == "fp16" else ("literal",)):
            with rule(mb, rules, name):
                w = as_words(first_op(mk, mb, raw, typ), typ)
            diff = np.nonzero(w != ref)[0]
            sign0 = bool(len(diff) and np.all(((w[diff] | ref[diff]) & 0x7FFFFFFF) == 0))
            ulp = 0
            if len(diff) and typ != "int8":
                o = lambda x: np.where(x & 0x80000000, -(x & 0x7FFFFFFF).astype(np.int64), (x & 0x7FFFFFFF).astype(np.int64))
                ulp = int(np.abs(o(w[diff]) - o(ref[diff])).max())
            key = "emulation_frozen" if name == "literal" else "emulation_card_rule"
            row[key] = {"words_differing": int(len(diff)), "only_zero_signs": sign0, "max_ulp": ulp}
        row["ccheck_ref_c_n1_sha256"] = sha(ref.tobytes())
        row["frozen_c_op1_sha256_equals_ref"] = bool(typ != "int8" and t["c_check"]["c_op1_sha256"] == sha(ref.tobytes()))
        out[t["name"]] = row
        k = "emulation_card_rule" if typ == "fp16" else "emulation_frozen"
        agg[typ][0] += 1
        agg[typ][1] += int(row[k]["words_differing"] == 0)
        if typ == "fp16":
            agg[typ][2] += int(row["emulation_frozen"]["words_differing"] == 0)
    return {"reference": "tools/claims-v3/ccheck/ccheck.py ref (rtl-sim/fma_toggle_v2/accum.c, sha256 " + ccheck.ENGINE_SHA + "), n = 1",
            "tiles": out,
            "summary": {"fp32_equal": f"{agg['fp32'][1]} of {agg['fp32'][0]}",
                        "fp16_equal_card_rule": f"{agg['fp16'][1]} of {agg['fp16'][0]}",
                        "fp16_equal_frozen_literal": f"{agg['fp16'][2]} of {agg['fp16'][0]}",
                        "int8_equal": f"{agg['int8'][1]} of {agg['int8'][0]}",
                        "note": "int8's frozen c_op1_sha256 hashes int64 values (2,048 bytes), so it never equals the "
                                "card's 1,024-byte C; its values are compared here"}}


def section5(mk, doc, pool):
    def words(n):
        t = next(x for x in doc["tiles"] if x["name"] == n)
        return mk.words_of(open(os.path.join(pool, t["file"]), "rb").read())
    pc = lambda x: bin(int(x)).count("1")
    aw, _ = words("fp32.a_onebit_b5_third")
    aw16, _ = words("fp32.a_onebit_b16_half")
    out = {"fp32.a_onebit_b5_third": {"base_word_has_bit5": bool(0x3EAAAAAB & 0x20), "even_rows": sorted({hex(int(x)) for x in aw[0::2].ravel()}),
                                      "odd_rows": sorted({hex(int(x)) for x in aw[1::2].ravel()})},
           "fp32.a_onebit_b16_half": {"base_word_has_bit16": bool(0x3F000000 & (1 << 16)), "odd_rows": sorted({hex(int(x)) for x in aw16[1::2].ravel()})}}
    for n, sh, m, two in (("fp32.exp_only_narrow2", 23, 0xFF, 128), ("fp16.exp_only_narrow2", 10, 0x1F, 16)):
        a, b = words(n)
        if n.startswith("fp32"):
            f = sorted({int(x) for x in ((np.concatenate([a.ravel(), b.ravel()]) >> np.uint64(sh)) & np.uint64(m))})
        else:
            ww = np.concatenate([a.ravel(), b.ravel()])
            f = sorted({int(x) for e in range(2) for x in ((ww >> np.uint64(16 * e + sh)) & np.uint64(m))})
        across = [pc(x ^ y) for x in f for y in f if x < two <= y]
        out[n] = {"exponent_fields": f, "step_1_to_2_flips": pc((two - 1) ^ two),
                  "steps_across_2_flip": [min(across), max(across)],
                  "exp_share_on_the_bus": next(x for x in doc["tiles"] if x["name"] == n)["bus_by_field"]["exp_share"]}
    return out


def section6(mb, doc, pool, kinds_dir):
    listed = []
    for line in open(os.path.join(pool, "SHA256SUMS")):
        h, p = line.rstrip("\n").split("  ", 1)
        listed.append((h, p))
    ok = [p for h, p in listed if os.path.exists(os.path.join(pool, p)) and sha(open(os.path.join(pool, p), "rb").read()) == h]
    built, _ = mb.build_all(kinds_dir)
    same = [p for p, b in built.items() if os.path.exists(os.path.join(pool, p)) and open(os.path.join(pool, p), "rb").read() == b]
    names = {p for _, p in listed} | {"SHA256SUMS"}
    others, note = [], []
    for top, dirs, fnames in os.walk(pool):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fnames:
            rel = os.path.relpath(os.path.join(top, f), pool).replace(os.sep, "/")
            if rel in names or f.endswith(".pyc"):
                continue
            (note if rel in NOTE_FILES else others).append(rel)
    return {"sha256sums_lists": len(listed), "sha256sums_verify": len(ok),
            "manifest_sha256": sha(open(os.path.join(pool, "MANIFEST"), "rb").read()),
            "manifest_is_the_pools": sha(open(os.path.join(pool, "MANIFEST"), "rb").read()) == MANIFEST_SHA,
            "blind6_json_sha256": sha(open(os.path.join(pool, "blind6.json"), "rb").read()),
            "sha256sums_sha256": sha(open(os.path.join(pool, "SHA256SUMS"), "rb").read()),
            "built_files": len(built), "built_files_equal_on_disk": len(same),
            "this_notes_files": sorted(NOTE_FILES),
            "other_files_beside_the_pool": sorted(others),
            "make_blind6_check": ("make_blind6.py --check sums every file in its directory (v1's fault 2), so any file "
                                  "beside the pool, this note's included, makes it report one problem, MISMATCH "
                                  "SHA256SUMS, while the files it builds still compare equal; the checks above are the "
                                  "pool's check")}


def section7(pool, out_dir):
    sys.path.insert(0, pool)
    import fetch_real6 as fr  # noqa: E402
    cache, orig = {}, fr.layer0

    def keep(key):
        cache[key] = orig(key)
        return cache[key]

    fr.layer0 = keep
    with tempfile.TemporaryDirectory(prefix="refetch-", dir=out_dir) as tmp:
        fr.OUT = tmp
        with contextlib.redirect_stdout(io.StringIO()):
            fr.main()
        cuts = sorted(f for f in os.listdir(os.path.join(pool, "real")) if f.endswith(".npy"))
        same = [f for f in cuts if open(os.path.join(tmp, f), "rb").read() == open(os.path.join(pool, "real", f), "rb").read()]
        prov_same = open(os.path.join(tmp, "provenance.json"), "rb").read() == open(os.path.join(pool, "real", "provenance.json"), "rb").read()
    out = {"fetch_real6_sha256": sha(open(os.path.join(pool, "fetch_real6.py"), "rb").read()),
           "cuts_byte_identical": f"{len(same)} of {len(cuts)}", "provenance_json_byte_identical": prov_same,
           "numpy": np.__version__, "models": {}}
    for key in ("smol", "qwen"):
        M = cache[key]
        m = M["m"]
        xq, _ = fr.q_tok(M["act"])
        w = xq.reshape(xq.shape[0], -1, 4)
        z = (w == 0).all(axis=2)
        meta = json.loads(fr.get(f"https://huggingface.co/api/models/{m['repo']}/revision/{m['rev']}"))
        cd = meta.get("cardData") or {}
        out["models"][key] = {
            "repo": m["repo"], "revision": m["rev"], "api_sha_matches": meta.get("sha") == m["rev"],
            "license": cd.get("license"), "license_tags": sorted(t for t in meta.get("tags", []) if t.startswith("license:")),
            "license_link": cd.get("license_link"), "base_model": cd.get("base_model"),
            "fetched_bytes": int(sum(f["bytes"] for f in M["st"].fetched)), "fetched_requests": len(M["st"].fetched),
            "down_input_int8_zero_word_frac": {
                "what": f"SiLU(gate) * up, quantised per token over all {m['ff']} hidden units; int8 words "
                        f"(4 consecutive units, the gate's unit) that are all zero",
                "all_32_tokens": round(float(z.mean()), 4), "tokens_16_31": round(float(z[16:32].mean()), 4),
                "the_cut_tokens_16_31_units_0_63": round(float(z[16:32, 0:16].mean()), 4),
                "words": int(z.size)}}
    return out


def main():
    a = parse()
    if a.network:
        res = section7(a.pool, a.out_dir)
        with open(os.path.join(a.out_dir, "corrections-network.json"), "w") as f:
            json.dump(res, f, indent=1)
            f.write("\n")
        print(json.dumps({k: v for k, v in res.items() if k != "models"}))
        for k, v in res["models"].items():
            print(k, v["license"], v["base_model"], json.dumps(v["down_input_int8_zero_word_frac"]))
        ok = res["cuts_byte_identical"].split()[0] == res["cuts_byte_identical"].split()[-1] and res["provenance_json_byte_identical"]
        return 0 if ok else 1
    mk, mb = load(a.pool, a.kinds_dir)
    rules = make_rules(mb)
    doc = json.load(open(os.path.join(a.pool, "blind6.json")))
    res = {"what": "Q139(b) blind pool 6: the checks behind CORRECTIONS.md (Tue 3 Nov 2026)",
           "numpy": np.__version__, "python": sys.version.split()[0]}
    with np.errstate(all="ignore"):
        res["s0_frozen_c_check_reproduces"] = section0(mk, mb, doc, a.pool)
        res["c1_fp16_rule"] = section1(mk, mb, rules, doc, a.pool)
        res["c2_launch_end"] = section2(mk, mb, rules, doc, a.pool)
        res["c3_subnormal_departure"] = section3(mk, mb, rules, a.pool)
        if a.ccheck:
            res["c4_first_op_against_ccheck"] = section4(mk, mb, rules, doc, a.pool, a.repo, a.ccheck_cache)
        res["c5_rule_texts"] = section5(mk, doc, a.pool)
        res["c6_files"] = section6(mb, doc, a.pool, a.kinds_dir)
    # the corrected C descriptors in one place, for any C-term arm: fp16 under the card's rule, the end as C2's mean
    cor = {}
    for t in doc["tiles"]:
        n = t["name"]
        cc = res["c1_fp16_rule"]["tiles"][n]["card_c_check"] if t["type"] == "fp16" else t["c_check"]
        cor[n] = {"c_start_flips": cc["c_start"]["c_reg_flips_per_op"],
                  "c_end_flips": res["c2_launch_end"]["tiles"][n]["c_reg_flips_per_op"],
                  "fp16_rule": "card" if t["type"] == "fp16" else None}
    res["corrected_c_descriptors"] = {"what": "C-register flips an op at a launch's start (its second op) and near a 0.5 s "
                                              "launch's end (C2's mean); fp16 under the card's rule. Desk descriptors of the "
                                              "emulation, not measurements", "tiles": cor}
    with open(os.path.join(a.out_dir, "corrections-check.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    s0, s1, s2, s3, s6 = (res[k] for k in ("s0_frozen_c_check_reproduces", "c1_fp16_rule", "c2_launch_end",
                                             "c3_subnormal_departure", "c6_files"))
    lines = [f"numpy {res['numpy']}, python {res['python']}",
             f"0  frozen c_check reproduces: {s0['equal_to_blind6_json']} of {s0['tiles']} tiles {s0['differ'] or ''}",
             f"1  fp16 rule: C descriptors change on {s1['c_descriptors_changed']}; dropped count only on "
             f"{s1['dropped_count_only']}; all pass under the card's rule: {s1['all_pass_under_card_rule']}"]
    for n in s1["c_descriptors_changed"]:
        v = s1["tiles"][n]
        lines.append(f"   {n}: half-zero words {v['half_zero_words']}, {v['dropped_with_nonzero_sum_per_op']} updates an op "
                     f"dropped with a nonzero sum, first-op C moves {100 * v['c_op1_max_change_rel_to_max_c']:.1f}% of max |C|, "
                     f"start flips {v['c_start_flips']['literal_as_frozen']} -> {v['c_start_flips']['card']}")
    lines.append(f"2  launch end: {s2['summary']}")
    for n in s2["summary"]["off_tiles"]:
        v = s2["tiles"][n]
        lines.append(f"   {n}: frozen {v['frozen_at_pow2']} at {v['frozen_at_pow2_ops']} ops, mean {v['c_reg_flips_per_op']} "
                     f"{v['c_reg_flips_per_op_range']} (x{v['ratio_to_frozen']})")
    lines.append(f"3  subnormal departure: {json.dumps(s3)}")
    if "c4_first_op_against_ccheck" in res:
        lines.append(f"4  first op against ccheck: {json.dumps(res['c4_first_op_against_ccheck']['summary'])}")
        for n, v in res["c4_first_op_against_ccheck"]["tiles"].items():
            k = "emulation_card_rule" if n.startswith("fp16") else "emulation_frozen"
            if v[k]["words_differing"]:
                lines.append(f"   {n}: {json.dumps(v[k])}")
    lines.append(f"5  rule texts: {json.dumps(res['c5_rule_texts'])}")
    lines.append(f"6  files: {json.dumps(s6)}")
    txt = "\n".join(lines) + "\n"
    with open(os.path.join(a.out_dir, "corrections-check.txt"), "w") as f:
        f.write(txt)
    print(txt, end="")
    good = (s0["equal_to_blind6_json"] == s0["tiles"] and s1["all_pass_under_card_rule"]
            and s6["sha256sums_verify"] == s6["sha256sums_lists"] == 80 and s6["manifest_is_the_pools"]
            and s6["built_files_equal_on_disk"] == s6["built_files"])
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
