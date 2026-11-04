#!/usr/bin/env python3
"""Q140(l): post hoc readings, written after fit_m9_a2.py's registered result was read (Wed 4 Nov 2026, about 00:55-01:10 PST).
NOT registered; no verdict, no frozen number and nothing in m9_a2.json depends on them.

    python3 posthoc_q140l.py > posthoc.txt        (numpy; about 20 s)

P1  Does the session's own zeros anchor add anything once the die start is in? T1+T3 and T1+T3+T4 (T2 dropped) leave one
    session out, against the frozen T1+T2+T3+T4: the registered order put T2 before T3, so T2 was never tested given T3.
P2  The anchors run in the session against a frozen offset: the final configuration with each fold's fallback offset (the
    mean of the three training sessions' die-referred anchor offsets) in place of the held-out session's own reads.
P3  The final configuration's held-out errors by format and group, and each session's mean die start.
"""
import sys

sys.dont_write_bytecode = True
import os  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m9_a2 as F  # noqa: E402


def setup():
    allc, _ = F.load_cells()
    for i, c in enumerate(allc):
        c["id"] = i
    anchors = {h: {} for h in F.SESS}
    for c in allc:
        if c["anchor"]:
            anchors[c["session"]][c["type"]] = c["runs"]
    cells = [c for c in allc if not c["anchor"] and c["D"] is not None]
    pm, _, _ = F.predict(F.fixed_W_par(F.REG["reference_lines"]["R8"]["W"]), cells, anchors)
    for c, f in zip(cells, pm):
        c["group"] = "governed" if f < 795.0 else "pinned"
    return cells, anchors


def loso_fallback(cfg, cells, anchors):
    """the final configuration, each held-out session predicted with the fold's fallback offset, not its own anchors"""
    preds = {}
    for h in F.SESS:
        chain = F.reads_chain(F.REG["sessions"][h]["dir"]) if cfg["T4"] else F.base_chain()
        train = [c for c in cells if c["session"] != h]
        par = F.fit(cfg, train, chain, anchors)
        have = [F.session_delta(anchors[q], chain, par["kT"], par["T_ref"], cfg["T3"])[2] for q in F.SESS if q != h]
        fb = {t: float(np.mean([x[t] for x in have if t in x])) for t in F.TYPES}
        test = [c for c in cells if c["session"] == h]
        R = F.Runs(test)
        f, P, _, _ = F.run_pred(par, R, {h: fb})
        for c, a, b in zip(test, R.cellmean(f), R.cellmean(P)):
            preds[c["id"]] = (float(a), float(b))
    return F.evaluate(preds, cells)


def main():
    cells, anchors = setup()
    fin_cfg = {"T1": True, "T2": True, "T3": True, "T4": True}
    fin = F.loso(fin_cfg, cells, anchors)
    print("Q140(l) post hoc readings (not registered; nothing frozen depends on them)")
    print(F.fmt_scores("FROZEN T1+T2+T3+T4 (registered)", fin["scores"]))
    print("")
    print("P1. T2 dropped once the die start is in (T1+T3, T1+T3+T4), leave one session out:")
    for lab, cfg in (("T1+T3", {"T1": True, "T2": False, "T3": True, "T4": False}), ("T1+T3+T4", {"T1": True, "T2": False, "T3": True, "T4": True}),
                     ("T1+T2+T3", {"T1": True, "T2": True, "T3": True, "T4": False})):
        a = F.loso(cfg, cells, anchors)
        print(F.fmt_scores(lab, a["scores"]))
        if lab != "T1+T2+T3":
            c = F.compare(fin, a)
            print("    the frozen model against it (would T2 carry, added last?): " + "; ".join(
                f"{q} lower in {v['n_lower']}/4 pooled {v['pooled_cur']:.3f}->{v['pooled_new']:.3f}" for q, v in c["per_quantity"].items())
                + f" -> {'carries' if c['kept'] else 'does not carry'} on {c['carries_on']}")
    print("")
    print("P2. The final configuration with each fold's fallback offset instead of the held-out session's own anchors:")
    fb = loso_fallback(fin_cfg, cells, anchors)
    print(F.fmt_scores("T1+T2+T3+T4, fallback offset", fb))
    print("    own anchors minus fallback, pooled rms: " + ", ".join(f"{q} {fin['scores']['pooled'][q]['rms'] - fb['pooled'][q]['rms']:+.3f}" for q in F.QN)
          + "; sessions where own anchors are better: " + ", ".join(f"{q} {sum(fin['scores'][h][q]['rms'] < fb[h][q]['rms'] for h in F.SESS)}/4" for q in F.QN))
    print("")
    print("P3. The frozen configuration's held-out errors by format (rms, mean), and the sessions' die starts:")
    for t in F.TYPES:
        cs = [c for c in cells if c["type"] == t]
        em = np.array([c["mhz"] - fin["preds"][c["id"]][0] for c in cs])
        ew = np.array([c["w"] - fin["preds"][c["id"]][1] for c in cs])
        g = np.array([c["group"] == "governed" for c in cs])
        gtxt = f"governed n {g.sum()}: clock {F.rms(em[g]):.2f} ({em[g].mean():+.2f}) MHz, board {F.rms(ew[g]):.2f} ({ew[g].mean():+.2f}) W; " if g.any() else "governed n 0; "
        print(f"  {t}: {gtxt}pinned n {(~g).sum()}: board {F.rms(ew[~g]):.2f} ({ew[~g].mean():+.2f}) W")
    for h in F.SESS:
        T = [r["T"] for c in cells if c["session"] == h for r in c["runs"]]
        print(f"  {h}: die start over its scored bursts mean {np.mean(T):.2f} C, range {min(T):.0f}-{max(T):.0f} C, {len(T)} bursts")
    print("")
    print("P4. Heat: a 6 s burst's die rise through M8's frozen burst heat law, k (P - P_idle), on each arm's held-out board (E143, E160:")
    print("    the cells whose results.json carries rise_c; whole-degree die readings)")
    import json
    bh = F.M8["burst_heat"]
    rise = {}
    for h in ("E143", "E160"):
        Rr = json.load(open(os.path.join(F.DD, F.REG["sessions"][h]["dir"], "results.json")))["cells"]
        for c in cells:
            if c["session"] == h and Rr.get(c["label"], {}).get("rise_c") is not None:
                rise[c["id"]] = float(Rr[c["label"]]["rise_c"])
    refs = {}
    for lab in ("R7", "R8"):
        pm, pw, _ = F.predict(F.fixed_W_par(F.REG["reference_lines"][lab]["W"]), cells, anchors)
        refs[lab] = {c["id"]: float(b) for c, b in zip(cells, pw)}
    refs["final"] = {k: v[1] for k, v in fin["preds"].items()}
    for h in ("E143", "E160"):
        ids = [c["id"] for c in cells if c["session"] == h and c["id"] in rise]
        meas = np.array([rise[i] for i in ids])
        txt = []
        for lab in ("R7", "R8", "final"):
            e = meas - np.array([bh["k_used_c_per_w"] * (refs[lab][i] - bh["P_idle_w"]) for i in ids])
            txt.append(f"{lab} {F.rms(e):.3f} ({e.mean():+.3f}) C")
        print(f"  {h} n {len(ids)}: " + "; ".join(txt))
    print("")
    print("P5. The critic's rank-8 reading: the governed clock of the frozen model (s(f) at n = 2 with the session terms) against s(f) at")
    print("    n = 2 with no session term (A0: M8's s(f); T4 alone: the reads' s(f)), per held-out session, paired bootstrap over cells")
    for lab, cfg in (("A0", {"T1": False, "T2": False, "T3": False, "T4": False}), ("T4 alone", {"T1": False, "T2": False, "T3": False, "T4": True})):
        b = F.loso(cfg, cells, anchors)
        txt = []
        for h in F.SESS:
            cs = [c for c in cells if c["session"] == h]
            d = F.boot_diff(cs, np.array([fin["preds"][c["id"]] for c in cs]), np.array([b["preds"][c["id"]] for c in cs]), F.REG["bootstrap"]["seed"])["G"]
            txt.append(f"{h} {d['point']:+.2f} [{d['ci95'][0]:+.2f}, {d['ci95'][1]:+.2f}]{' resolved' if d['resolved_below_zero'] else ''}")
        print(f"  frozen minus {lab}: " + "; ".join(txt))


if __name__ == "__main__":
    main()
