#!/usr/bin/env python3
"""Q143(g): E175's dated amendment A1 (E175.md.dated-note-A1.md), the code. make_e175_pool.py (lab c50ff493) stays as committed and is imported
after its sha256 is checked. A1 continues the registered stream past its cap of 64 for the pinned set only: candidate i for i = 64 .. 95 is drawn
by make_e175_pool.candidate(i) unchanged (the same generator, seed, streams, truncation and refusals), and the selection over candidates 0-63 is
make_e175_pool.select unchanged; then, in stream order from 64, a candidate the frozen predictor places pinned and inside the 82 W admission joins
the pinned set until it holds 8; every other candidate is recorded and never kept (the governed set stays the 16 the registered rule chose). The
stream stops at the candidate that fills the pinned set, or after 95.

    python3 -B make_e175_pool_a1.py draw --stream DIR/stream-e175.json --out DIR      # DIR/stream-e175-a1.json: candidates 0-63 as drawn, then 64-95
    python3 -B make_e175_pool_a1.py manifest --stream DIR/stream-e175-a1.json --upto K --out DIR
    python3 -B make_e175_pool_a1.py select --stream DIR/stream-e175-a1.json --predictions P.json --upto K --out design-e175.json
    python3 -B make_e175_pool_a1.py build --stream DIR/stream-e175-a1.json --design design-e175.json --out POOL
    python3 -B make_e175_pool_a1.py check --out POOL                                  # make_e175_pool.check, unchanged

Run with the Intel's /usr/bin/python3 (3.9.6, numpy 1.26.4), as the registered generator. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
GEN = os.path.join(HERE, "make_e175_pool.py")
GEN_SHA256 = "71598008d5a70a75ddd61bbfa124433d3d2195ada3b53abdec6a8f429162977e"          # make_e175_pool.py as committed in c50ff493 (SHA256SUMS-e175-registration)
A1_FIRST, A1_LAST = 64, 95             # the continued stream: candidates 64-95, at most 32 more
A1_NOTE = "tools/claims-v3/e175/E175.md.dated-note-A1.md"


def sha_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def gen():
    if sha_file(GEN) != GEN_SHA256:
        raise SystemExit(f"STOP: make_e175_pool.py differs from its committed sha256 {GEN_SHA256}")
    spec = importlib.util.spec_from_file_location("make_e175_pool", GEN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def draw(stream_path, out):
    M = gen()
    base = json.load(open(stream_path))
    if base.get("generator_sha256") != GEN_SHA256 or base.get("test_seed") or base.get("seed") != M.SEED or len(base["candidates"]) != M.CAP:
        raise SystemExit("STOP: the registered stream is not make_e175_pool.py's own, on the registered seed, with its 64 candidates")
    mk, B8 = M.mods()
    early = M.earlier_hashes()
    seen = {c["sha256_whole"]: c["index"] for c in base["candidates"] if "refused" not in c}
    cands = list(base["candidates"])
    for i in range(A1_FIRST, A1_LAST + 1):
        fmt, fam, m, params, raw = M.candidate(i, mk, B8)
        h = M.sha(raw)
        rec = {"index": i, "type": fmt, "family": fam, "trunc_bits": m, "params": M.jsonable(params), "sha256_whole": h,
               "streams": [["cand", i], ["fam", i]], "amendment": "A1"}
        why = B8.tile_refusal(raw, fmt, mk)
        if why is None:
            ok, why2 = B8.class_check(raw, fmt, "U", "kind", mk)
            why = None if ok else why2
        if why is None and h in early:
            why = f"byte twin of the committed {early[h]}"
        if why is None and h in seen:
            why = f"byte twin of candidate {seen[h]}"
        if why is not None:
            rec["refused"] = why
        else:
            seen[h] = i
            name = f"{fmt}." + M.LABEL.format(i=i, fam=fam, m=m, sig=h[:6])
            rel = f"tiles/{fmt}/{name}.bin"
            os.makedirs(os.path.join(out, "tiles", fmt), exist_ok=True)
            with open(os.path.join(out, rel), "wb") as f:
                f.write(raw)
            rec.update(name=name, file=rel, sha256={"whole": h, "a": M.sha(raw[:1024]), "b": M.sha(raw[1024:])})
        cands.append(rec)
    doc = dict(base)
    doc.update(_note="Q143(g) make_e175_pool_a1.py draw: E175's stream, candidates 0-63 as the registered generator drew them, then 64-95 by dated "
                     "note A1 (the same generator, seed and streams)",
               candidates=cands, cap=A1_LAST + 1, registered_cap=M.CAP, registered_stream_sha256=sha_file(stream_path),
               a1_generator_sha256=sha_file(os.path.abspath(__file__)), a1_note=A1_NOTE)
    with open(os.path.join(out, "stream-e175-a1.json"), "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    new = cands[M.CAP:]
    print(json.dumps({"candidates": len(cands), "a1_drawn": len(new), "a1_refused": sum(1 for c in new if "refused" in c),
                      "a1_by_format": {t: sum(1 for c in new if c["type"] == t and "refused" not in c) for t in M.FORMATS_DRAWN}}, sort_keys=True))


def load_stream(path):
    s = json.load(open(path))
    if s.get("a1_generator_sha256") != sha_file(os.path.abspath(__file__)):
        raise SystemExit("STOP: the A1 stream was drawn by another version of this file")
    return s


def select_a1(M, stream, pred, upto):
    """make_e175_pool.select over candidates 0-63 unchanged; then A1's continuation for the pinned set only"""
    base = dict(stream, candidates=stream["candidates"][:M.CAP])
    res = M.select(base, pred, min(upto, M.CAP))
    if upto <= M.CAP or res["status"] == "FILLED":
        res["a1"] = {"applied": False, "why": "the registered rule's result stands" if res["status"] == "FILLED" else "no candidate past 63 read"}
        return res
    tiles = pred["tiles"]
    pinned = list(res["pinned"])
    stop = None
    for c in stream["candidates"][M.CAP:upto]:
        r = {"index": c["index"], "name": c.get("name"), "type": c["type"], "family": c["family"], "trunc_bits": c["trunc_bits"], "amendment": "A1"}
        if "refused" in c:
            r["outcome"] = "refused by the generator: " + c["refused"]
            res["records"].append(r)
            continue
        t = tiles.get(c["name"])
        if t is None:
            raise SystemExit(f"STOP: candidate {c['index']} ({c['name']}) has no prediction: predict ran on fewer candidates than --upto")
        a, b = t["M10"]["a2_fallback"], t["M9"]["a2_fallback"]
        peak = max(float(a["peak_board_hi95_w"]), float(b["peak_board_hi95_w"]))
        r.update(M10_mhz=a["burst_mhz"], M10_board_w=a["burst_board_w"], M10_group=a["group"], M9_mhz=b["burst_mhz"], peak_hi95_w=round(peak, 3),
                 M10_D600_w=t["M10"]["D600_a3_footing_w"])
        if peak > M.ADMISSION_W:
            r["outcome"] = "out at 82 W: replaced by the next draw (A1)"
        elif a["group"] == "governed":
            r["outcome"] = "governed: never kept under A1 (the governed set is closed at the registered rule's 16)"
        else:
            pinned.append(c["name"])
            r["outcome"] = "pinned: kept (A1)"
        res["records"].append(r)
        if len(pinned) == M.N_PINNED:
            stop = c["index"]
            break
    res["pinned"], res["n_pinned"] = pinned, len(pinned)
    res["upto"] = upto
    res["status"] = "FILLED (A1)" if stop is not None else ("AT A1'S CAP" if upto > A1_LAST else "NEEDS MORE CANDIDATES (A1)")
    res["stopped_at_index"] = stop
    res["a1"] = {"applied": True, "note": A1_NOTE, "first": A1_FIRST, "last": A1_LAST,
                 "rule": "candidates 64-95 in stream order: pinned and admitted at 82 W joins the pinned set until it holds 8; every other is recorded "
                         "and never kept; the governed set is the registered rule's 16"}
    return res


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw")
    d.add_argument("--stream", required=True)
    d.add_argument("--out", required=True)
    m = sub.add_parser("manifest")
    m.add_argument("--stream", required=True)
    m.add_argument("--upto", type=int, required=True)
    m.add_argument("--out", required=True)
    s = sub.add_parser("select")
    s.add_argument("--stream", required=True)
    s.add_argument("--predictions", required=True)
    s.add_argument("--upto", type=int, required=True)
    s.add_argument("--out", required=True)
    b = sub.add_parser("build")
    b.add_argument("--stream", required=True)
    b.add_argument("--design", required=True)
    b.add_argument("--out", required=True)
    c = sub.add_parser("check")
    c.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "draw":
        draw(a.stream, a.out)
        return 0
    M = gen()
    if a.cmd == "check":
        return M.check(a.out)
    stream = load_stream(a.stream)
    if a.cmd == "manifest":
        M.write_manifest(stream, min(a.upto, A1_LAST + 1), a.out)
        return 0
    if a.cmd == "select":
        pred = json.load(open(a.predictions))
        pred["_sha256"] = sha_file(a.predictions)
        res = select_a1(M, stream, pred, min(a.upto, A1_LAST + 1))
        res["stream_sha256"] = sha_file(a.stream)
        res["_stream_path"] = os.path.relpath(os.path.abspath(a.stream), TOP)
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1, sort_keys=True)
        print(json.dumps({k: res[k] for k in ("status", "upto", "stopped_at_index", "n_governed", "n_pinned")}, sort_keys=True))
        return 0
    design = json.load(open(a.design))
    if not str(design["status"]).startswith(("FILLED", "AT CAP", "AT A1")):
        raise SystemExit(f"STOP: the design reads {design['status']}")
    design["_stream_path"] = os.path.join(TOP, design["_stream_path"]) if not os.path.isabs(design["_stream_path"]) else design["_stream_path"]
    st = design["status"]
    design["status"] = "FILLED"          # make_e175_pool.build's own guard, which reads the registered statuses only
    M.build(stream, design, a.out)
    pj = os.path.join(a.out, "e175.json")
    doc = json.load(open(pj))
    doc["design_status"], doc["a1_note"] = st, A1_NOTE
    with open(pj, "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    lines = []
    for dirpath, _, files in os.walk(a.out):
        for fn in sorted(files):
            if fn == "SHA256SUMS":
                continue
            p = os.path.join(dirpath, fn)
            lines.append(f"{sha_file(p)}  {os.path.relpath(p, a.out)}")
    with open(os.path.join(a.out, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(lines, key=lambda x: x.split()[1])) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
