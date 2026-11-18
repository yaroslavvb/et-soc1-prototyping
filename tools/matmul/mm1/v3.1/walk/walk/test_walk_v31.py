#!/usr/bin/env python3
"""Desk tests of walk_v31.py (Q217, lane v31-trace). No simulator, no card, no device: the walk against its kernels' sources' own statements
and the lab's committed desk models and records (read only, imported by path with bytecode writing off). /usr/bin/python3 3.12.3, numpy for
map_e211 only.

    python3 -I -B test_walk_v31.py [--quick]        prints one line per test and 'WALK TESTS n of n PASS' (exit 0) or the failures (exit 1)

THE TESTS
  T1  which minions a mask enables: hart 0 of minions 0-31 of each masked shire works, hart 1 enters and returns; per_shire != 32 refused
      (the host's validateArm); the host's own participants() list (rgm136 host/main.cpp) re-written here and compared.
  T2  per-minion counts from the event list equal the closed form (64 MB NB KB FMAs, as many A and B loads, 2 MB NB TensorStores) for
      every kernel at 12 shapes; the same at every minion and every mask (a minion's list does not depend on the mask).
  T3  rgm211.gemmLn equals rgm136.gemmL event for event when MB = 1 or NB = 1 (E211's exact controls); at MB, NB >= 2 the two lists
      differ in order and are the same multiset; rgm211.gemmL equals rgm136.gemmL.
  T4  rgm136.gemmLnc equals rgm136.gemmL in every address and in the order, with coop 0 and no tensor_coop value.
  T5  the counted simulator run mm-timing kept (c-gemmL1x1x1-fp32, aifoundry3, one shire: tools/counter's counts-log.json): per working
      hart 64 TensorFMAs, 64 A loads of 1 KiB, 64 TenB loads of 1 KiB, 2 TensorStores of 1 KiB, 128 tensor_coop writes, 66 TensorWaits;
      the walk's counts at 1x1x1 mask 0x1 and the number of working harts (32) equal them.
  T6  kit-e211's committed simulator records (tools/claims-v3/e211/logs/simcheck/*.out): each case's 'iters' (ops a minion) equals the
      walk's 64 MB NB KB and each case's walk tag equals the kernel's walk (nm for gemmLn on rgm211's ELF, mn otherwise).
  T7  the shire's op stream (shire_step_requests, coop kernels) equals E136's reuse_e136.shire_ops (the lab's committed desk model of one
      shire's 4 A and 8 B tile reads an op) at every shape tried, rgm136's walk; and every minion's own A and B offsets are its shire's
      neighbourhood / position entries of that stream.
  T8  the chip's lock-step L3 under a mask: the walk's strict-LRU shares of A's and B's shire requests found in the L3 (weighted by the
      shires asking each tile) equal E206's committed l3_model_masked (tools/claims-v3/e206/desk/reuse_e206.py) at 32, 28 and 24 MB, at
      every mask and shape tried (rgm136's walk); and at the full mask the walk's stack distances equal E211's map_e211.stack_distances for
      both walks (mn, nm) number for number.
  T9  the footprint (distinct tiles a pass) equals MM1-v1's masked closed form (mm1_core.footprint: A 2 MB KB R/8, B NB KB C/4, C 2 MB NB
      n/32 MiB) for every mask and shape tried.
  T10 the sharing: at the full mask an A tile is asked by 4 shires and a B tile by 8 (map_e211's statement); at 0xf by 4 and 1; at 0x1111
      by 1 and 4; in general by the active shires of its row (column) group; a step's distinct tiles are 4 R + 8 C.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import glob
import importlib.util
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walk_v31 as W  # noqa: E402

# t7-0xf (Q221) scrub: the lab checkout is read from the environment variable ET_LAB, else found from this file's place in it
# (tools/matmul/mm1/v3.1/walk/walk/); mm-timing's counted simulator run (c-gemmL1x1x1-fp32, aifoundry3) is read from its byte copy in
# testdata/ beside this file. Nothing else in this file changed.
LAB = os.environ.get("ET_LAB") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
MMT = os.path.join(HERE, "testdata", "counts-log-c-gemmL1x1x1-fp32.json")
QUICK = "--quick" in sys.argv
RESULTS = []


def imp(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(name, ok, detail):
    RESULTS.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + ": " + detail, flush=True)


SHAPES = ["1x1x1", "1x1x2", "1x2x1", "2x1x1", "2x2x1", "2x2x2", "1x5x5", "3x1x8", "2x3x2", "1x16x4", "1x1x16", "2x4x16"]
MASKS = ["0x1", "0xf", "0x1111", "0xff", "0x11111111", "0xffff", "0x33333333", "0xffffff", "0x77777777", "0xffffffff", "0x3", "0xf0f0f0f0"]


def t1():
    ok, notes = True, []
    for mk in MASKS:
        work, idle = W.enabled(mk)
        m = int(mk, 16)
        exp_w = [s * 64 + mm * 2 for s in range(32) if (m >> s) & 1 for mm in range(32)]   # participants(mask, 32, 1)
        exp_i = [h + 1 for h in exp_w]
        ok &= work == exp_w and idle == exp_i
        notes.append("%s %d" % (mk, len(work)))
    try:
        W.enabled("0xf", per_shire=16)
        ok = False
        notes.append("per_shire 16 not refused")
    except ValueError:
        notes.append("per_shire 16 refused")
    check("T1 minions a mask enables", ok, "; ".join(notes))


def t2():
    ok, n = True, 0
    for kern in W.KERNELS:
        for sh in SHAPES[:9] if QUICK else SHAPES:
            MB, NB, KB = W.parse_shape(sh)
            cc = W.minion_counts(kern, MB, NB, KB)
            ref = None
            for (s, m) in ((0, 0), (5, 13), (31, 31), (12, 9)):
                ev = list(W.minion_events(kern, MB, NB, KB, s, m))
                c = collections.Counter(e[0] for e in ev)
                good = (c["F"] == cc["fma"] and c["LA"] == cc["load_a"] and c["LB"] == cc["load_b"] and c["S"] == cc["store"]
                        and cc["fma"] == 64 * MB * NB * KB)
                ok &= good
                n += 1
                if s == 5 and ref is None:
                    ref = W.events_sha(ev)
            # the list does not depend on the mask: minion_events takes no mask at all; check the shape of the first ops at two shires
    check("T2 per-minion counts", ok, "%d (kernel, shape, minion) lists: FMAs = A loads = B loads = 64 MB NB KB, stores = 2 MB NB" % n)


def t3():
    ok, notes = True, []
    for sh in ["1x1x1", "1x2x1", "2x1x1", "1x5x5", "3x1x8", "1x16x4", "1x1x16"]:
        MB, NB, KB = W.parse_shape(sh)
        for (s, m) in ((0, 0), (17, 22)):
            a = list(W.minion_events("rgm136.gemmL", MB, NB, KB, s, m))
            b = list(W.minion_events("rgm211.gemmLn", MB, NB, KB, s, m))
            ok &= a == b
    notes.append("equal at MB = 1 or NB = 1 (7 shapes, 2 minions)")
    for sh in ["2x2x1", "2x3x2", "2x4x16"] if not QUICK else ["2x2x1", "2x3x2"]:
        MB, NB, KB = W.parse_shape(sh)
        a = list(W.minion_events("rgm136.gemmL", MB, NB, KB, 3, 7))
        b = list(W.minion_events("rgm211.gemmLn", MB, NB, KB, 3, 7))
        # the scratchpad line alternates with the op index in both walks, so the multiset of (op-free) events is equal
        ok &= a != b and collections.Counter(a) == collections.Counter(b)
        c = list(W.minion_events("rgm211.gemmL", MB, NB, KB, 3, 7))
        ok &= c == a
    notes.append("differ in order, equal as multisets at 2x2x1, 2x3x2%s; rgm211.gemmL = rgm136.gemmL" % ("" if QUICK else ", 2x4x16"))
    check("T3 the two walks", ok, "; ".join(notes))


def t4():
    ok = True
    for sh in ["2x2x1", "1x5x5", "2x3x2"]:
        MB, NB, KB = W.parse_shape(sh)
        a = list(W.minion_events("rgm136.gemmL", MB, NB, KB, 9, 30))
        b = list(W.minion_events("rgm136.gemmLnc", MB, NB, KB, 9, 30))
        strip = lambda e: (e[0], e[1], e[2]) if e[0] == "LA" else ((e[0], e[1]) if e[0] == "LB" else e)
        ok &= [strip(e) for e in a] == [strip(e) for e in b]
        ok &= all(e[3] == 0 and e[4] == 0 for e in b if e[0] == "LA") and all(e[2] == 0 and e[3] == 0 for e in b if e[0] == "LB")
        ok &= all(e[3] == 1 and e[4] != 0 for e in a if e[0] == "LA") and all(e[2] == 1 and e[3] != 0 for e in a if e[0] == "LB")
    check("T4 gemmLnc = gemmL without cooperation", ok, "same addresses and order at 3 shapes; coop 0 and tcoop 0 on every gemmLnc load")


def t5():
    if not os.path.exists(MMT):
        check("T5 mm-timing's counted run", False, "missing " + MMT)
        return
    c = json.load(open(MMT))
    work = [h for h, v in c["harts"].items() if v.get("tensor", {}).get("fma_fp32", {}).get("ops", 0) > 0]
    cc = W.minion_counts("rgm136.gemmL", 1, 1, 1)
    ok = len(work) == len(W.enabled("0x1")[0]) == 32
    bad = 0
    for h in work:
        v = c["harts"][h]
        t = v["tensor"]
        csr = v["by_csr"]
        good = (t["fma_fp32"]["ops"] == cc["fma"] and t["load"]["ops"] == cc["load_a"] and t["load"]["bytes"] == 1024 * cc["load_a"]
                and t["load_tenb"]["ops"] == cc["load_b"] and t["load_tenb"]["bytes"] == 1024 * cc["load_b"]
                and t["store"]["ops"] == cc["store"] and t["store"]["bytes"] == cc["bytes_stored"]
                and csr["csrw tensor_coop"] == 2 * cc["fma"] and csr["csrw tensor_wait"] == cc["fma"] + 2 and csr["csrw tensor_fma"] == cc["fma"])
        bad += not good
    ok &= bad == 0
    work_ids = sorted(int(h) for h in work)
    ok &= work_ids == W.enabled("0x1")[0]
    check("T5 mm-timing's counted run", ok, "%d working harts (ids = the walk's), %d with counts other than the walk's 64/64/64/2 (+128 coop, 66 waits)"
          % (len(work), bad))


def t6():
    files = sorted(glob.glob(os.path.join(LAB, "tools/claims-v3/e211/logs/simcheck/*.out")))
    ok, n = bool(files), 0
    for f in files:
        for line in open(f):
            if not line.startswith("SPARSITY "):
                continue
            r = json.loads(line[9:])
            if r.get("test") != "fma":
                continue
            m = re.fullmatch(r"(gemmLnc|gemmLn|gemmL)(\d+)x(\d+)x(\d+)", r["arm"])
            MB, NB, KB = (int(x) for x in m.groups()[1:])
            ok &= r["iters"] == 64 * MB * NB * KB
            if "walk" in r:
                if os.path.basename(f).startswith("BAD"):
                    ok &= r["walk_tagged"] == 0     # gemmLn asked of rgm136's ELF: rgm136 never writes the tag (its walk is mn)
                else:
                    want = "nm" if m.group(1) == "gemmLn" else "mn"
                    ok &= r["walk"] == want and (r["walk_tagged"] == (32 if want == "nm" else 0))
            n += 1
    check("T6 kit-e211's simulator records", ok, "%d cases from %d files: ops a minion = 64 MB NB KB, walk tags as the walk" % (n, len(files)))


def t7():
    R = imp("v31_reuse_e136", os.path.join(LAB, "tools/claims-v3/e136/desk/reuse_e136.py"))
    ok, n = True, 0
    A0, B0 = 1 << 32, (1 << 32) + (1 << 30)
    for sh in (["1x1x2", "2x2x1", "2x3x2", "1x5x5"] if QUICK else ["1x1x2", "2x2x1", "2x3x2", "1x5x5", "3x1x8", "2x4x16"]):
        MB, NB, KB = W.parse_shape(sh)
        for s in (0, 5, 13, 31):
            s0, s1 = s & 3, (s >> 2) & 7
            ref = R.shire_ops(("large", MB, NB, KB), s0, s1, A0, B0)
            mine = [([A0 + a for a, _ in A], [B0 + b for b, _ in B]) for _, A, B in W.shire_step_requests("rgm136.gemmL", MB, NB, KB, s)]
            ok &= ref == mine
            # each minion's own loads are its neighbourhood's A entry and its position's B entry of the shire's stream
            for m in (0, 11, 22, 31):
                ev = [e for e in W.minion_events("rgm136.gemmL", MB, NB, KB, s, m) if e[0] in ("LA", "LB")]
                d, p = (m >> 3) & 3, m & 7
                ok &= [e[1] for e in ev if e[0] == "LA"] == [A[d] - A0 for A, _ in mine]
                ok &= [e[1] for e in ev if e[0] == "LB"] == [B[p] - B0 for _, B in mine]
            n += 1
    check("T7 the shire's stream = E136's shire_ops", ok, "%d (shape, shire) streams equal op for op; each minion's loads are its entries" % n)


def t8():
    R6 = imp("v31_reuse_e206", os.path.join(LAB, "tools/claims-v3/e206/desk/reuse_e206.py"))
    ok, n, notes = True, 0, []
    shapes = ["1x2x2", "2x2x2", "1x16x4", "1x1x16"] if QUICK else ["1x2x2", "2x2x2", "1x16x4", "1x1x16", "2x4x16", "3x1x8"]
    for sh in shapes:
        MB, NB, KB = W.parse_shape(sh)
        for mk in ["0xffffffff", "0xf", "0x1111", "0xff", "0x11111111", "0x33333333", "0x3"]:
            for cap in (32, 28, 24):
                ref = R6.l3_model_masked(("large", MB, NB, KB), cap * 1024, int(mk, 16))
                mine = W.summary("rgm136.gemmL", MB, NB, KB, mk, l3_cap_mb=cap)["l3_strict"]
                good = (round(mine["A_in_L3_share_by_shire_request"], 4) == ref["A_in_L3"]
                        and round(mine["B_in_L3_share_by_shire_request"], 4) == ref["B_in_L3"])
                ok &= good
                if not good:
                    notes.append("%s %s %d: mine %.4f/%.4f E206 %.4f/%.4f" % (sh, mk, cap, mine["A_in_L3_share_by_shire_request"],
                                 mine["B_in_L3_share_by_shire_request"], ref["A_in_L3"], ref["B_in_L3"]))
                n += 1
    # full mask: distances equal map_e211's (both walks)
    M = imp("v31_map_e211", os.path.join(LAB, "tools/claims-v3/e211/desk/map_e211.py"))
    nd = 0
    for sh in (["2x2x2", "1x5x5"] if QUICK else ["2x2x2", "1x5x5", "2x3x2", "3x1x8"]):
        MB, NB, KB = W.parse_shape(sh)
        for walk, kern in (("mn", "rgm136.gemmL"), ("nm", "rgm211.gemmLn")):
            res = M.stack_distances(walk, MB, NB, KB)
            dA, dB = res[0], res[1]
            recA, recB = W.l3_distances(kern, MB, NB, KB, "0xffffffff")
            mineA = [[d for d, _ in st] for st in recA]
            mineB = [[d for d, _ in st] for st in recB]
            refA = [[int(x) for x in row] for row in dA]
            refB = [[int(x) for x in row] for row in dB]
            cv = lambda rows: [[(-1 if d >= M.INF else d) for d in row] for row in rows]
            good = cv(mineA) == cv(refA) and cv(mineB) == cv(refB)
            ok &= good
            nd += 1
            if not good:
                notes.append("map_e211 %s %s differs" % (sh, walk))
    check("T8 the masked L3 = E206's l3_model_masked; full mask = map_e211", ok,
          "%d (shape, mask, cap) shares equal to 4 decimals; %d (shape, walk) distance arrays equal%s" % (n, nd, ("; " + "; ".join(notes[:4])) if notes else ""))


def t9():
    C = imp("v31_mm1_core", os.path.join(LAB, "tools/matmul/mm1/v1/mm1_core.py"))
    ok, n, notes = True, 0, []
    for sh in ["1x1x1", "2x2x2", "1x16x4", "1x1x16", "2x4x16", "3x1x8"]:
        MB, NB, KB = W.parse_shape(sh)
        for mk in MASKS:
            f = W.footprint_tiles("rgm136.gemmL", MB, NB, KB, mk)
            ref = C.footprint(MB, NB, KB, C.mask_info(mk))
            good = abs(f["MB"] - ref) < 1e-9
            ok &= good
            n += 1
            if not good:
                notes.append("%s %s %s vs %s" % (sh, mk, f["MB"], ref))
    check("T9 footprint = MM1-v1's masked closed form", ok, "%d (shape, mask) equal%s" % (n, ("; " + "; ".join(notes[:3])) if notes else ""))


def t10():
    ok, notes = True, []
    for mk, ea, eb in (("0xffffffff", {"4": 32}, {"8": 32}), ("0xf", {"4": 4}, {"1": 32}), ("0x1111", {"1": 16}, {"4": 8}),
                       ("0xff", {"4": 8}, {"2": 32}), ("0x11111111", {"1": 32}, {"8": 8}), ("0x33333333", {"2": 32}, {"8": 16})):
        s = W.summary("rgm136.gemmL", 1, 1, 1, mk)
        cs = s["chip_step"]
        good = cs["A_sharing_hist"] == ea and cs["B_sharing_hist"] == eb and cs["A_distinct"] == 4 * len(s["row_groups"]) \
            and cs["B_distinct"] == 8 * len(s["col_groups"])
        # the same from the walk's chip steps directly
        st = next(x for x in W.chip_steps("rgm136.gemmL", 1, 1, 1, mk) if x[0] == "op")
        ha = collections.Counter(str(len(w)) for _, w in st[2])
        hb = collections.Counter(str(len(w)) for _, w in st[3])
        good &= dict(ha) == ea and dict(hb) == eb
        ok &= good
        notes.append("%s A%s B%s" % (mk, ea, eb))
    check("T10 the sharing", ok, "; ".join(notes))


def t11():
    """per-minion levels (minion_levels): over every active minion of every active shire, the L3 / fresh split of the A and B reads equals
    the summary's strict shares by shire request (the same quantity counted two ways); and the desk L2 model's per-read hits (l2_shire_tiles)
    sum to l2_shire's per-op A and B hits"""
    ok, notes = True, []
    cases = [("1x2x2", "0xf"), ("2x2x2", "0x1111"), ("1x16x4", "0xf"), ("1x2x1", "0xffffffff")]
    if not QUICK:
        cases += [("2x4x16", "0xf"), ("2x4x16", "0x1111")]   # A's and B's strict shares both away from 0 and 1
    for sh, mk in cases:
        MB, NB, KB = W.parse_shape(sh)
        s = W.summary("rgm136.gemmL", MB, NB, KB, mk)["l3_strict"]
        cache = {}
        inA = inB = nA = nB = 0
        for shire in W.mask_shires(mk):
            for m in range(32):
                for x in W.minion_levels("rgm136.gemmL", MB, NB, KB, mk, shire, m, _cache=cache):
                    nA += 1
                    nB += 1
                    inA += x[3] != -1 and x[3] < 32 * 1024
                    inB += x[7] != -1 and x[7] < 32 * 1024
        # per minion: the A read of a neighbourhood is seen by its 8 minions and the B read by 4: the shire-request weighting is the same
        good = abs(inA / nA - s["A_in_L3_share_by_shire_request"]) < 1e-6 and abs(inB / nB - s["B_in_L3_share_by_shire_request"]) < 1e-6
        tiles = W.l2_shire_tiles("rgm136.gemmL", MB, NB, KB, W.mask_shires(mk)[0])
        agg = W.l2_shire("rgm136.gemmL", MB, NB, KB, W.mask_shires(mk)[0])
        good &= [(sum(a), sum(b)) for a, b in tiles] == agg
        ok &= good
        notes.append("%s %s A %.4f/%.4f B %.4f/%.4f" % (sh, mk, inA / nA, s["A_in_L3_share_by_shire_request"], inB / nB,
                                                         s["B_in_L3_share_by_shire_request"]))
    check("T11 per-minion levels = the summary's shares; L2 per read = per op", ok, "; ".join(notes))


def main():
    for t in (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11):
        try:
            t()
        except Exception as e:  # a test that cannot run is a FAIL with its reason
            check(t.__name__.upper() + " (did not run)", False, repr(e)[:300])
    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    print("WALK TESTS %d of %d PASS (python %s)" % (n_ok, len(RESULTS), sys.version.split()[0]))
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
