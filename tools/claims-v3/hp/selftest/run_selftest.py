#!/usr/bin/env python3
"""The HP pipeline on synthetic data with planted effects: development -> P1 -> P3 -> V0 -> PREREG -> validation ->
verdicts, plus the checks of the 27 Sep code review (its findings F0-F16, where they fit a pipeline test).

    python3 tools/claims-v3/hp/selftest/run_selftest.py [<work dir>]      (default: build/hp-selftest)

It writes nothing outside the work directory (params and PREREG go there through HP_PARAMS_DIR / --out-dir, which
hplib.py honours only under V3_DRY=1, so every step runs with V3_DRY=1), and it touches no device. The planted effects
(synth_blocks.py): kappa PER16 0.85 vs INT16 1.0, EDGE8 0.85 and MEM8 0.93 vs CEN8 1.03, N8b 1.06 vs S8b 0.94,
W8b = E8b; a hotter high for concentrated placements; the I/O sensor warmer next to B4NE. The checks assert the
directions the reducer must recover, the registration (every registered item powered at its type's n_val), card 1's
V0 edges reaching PREREG, the lock (PREREG.md, prereg.json, params-val, binaries; no re-freeze), the n_val cap on
validation blocks and the V3 words.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HP = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(HP, "..", "..", ".."))
sys.path.insert(0, HP)


def run(args, env, check=True):
    r = subprocess.run([sys.executable] + args, cwd=ROOT, env=env, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit("failed: %s" % " ".join(args))
    return r


def sh(args, env):
    return run(args, env).stdout


def main():
    work = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "hp-selftest"))
    shutil.rmtree(work, ignore_errors=True)
    params = os.path.join(work, "params")
    os.makedirs(params)
    relaxed = {"_what": "self-test: the development-allowed tau_c void limits (DESIGN2 §5.5)",
               "void_tauc_lo": 0.33, "void_tauc_hi": 3.0}
    for r in ("r1", "r2", "r3"):
        json.dump(relaxed, open(os.path.join(params, "params-%s-aifoundry3.json" % r), "w"))
    env = dict(os.environ, HP_PARAMS_DIR=params, V3_DRY="1")
    for k in ("HP_VT0", "HP_DRY_SPEED", "HP_PREREG_DIR"):
        env.pop(k, None)
    os.environ.update(V3_DRY="1", HP_PARAMS_DIR=params)          # the in-process checks below
    for k in ("HP_VT0", "HP_DRY_SPEED", "HP_PREREG_DIR"):
        os.environ.pop(k, None)
    import hplib as H
    import reduce as RD
    checks = []

    def want(name, cond):
        checks.append((name, bool(cond)))

    data = os.path.join(work, "data")
    # development data; R1 block 1201 lacks MEM8? no: L8 block 2301 lacks MEM8 (the completeness rule, review F9a)
    print(sh([os.path.join(HERE, "synth_blocks.py"), data, "--seed", "7", "--drop", "2301:MEM8"], env).strip())
    a3 = os.path.join(data, "aifoundry3")
    sh([os.path.join(HP, "reduce.py"), "--data", a3, "--card", "aifoundry3", "--dev", "--out", os.path.join(work, "dev.json")], env)
    devj = json.load(open(os.path.join(work, "dev.json")))["dev"]
    dev = devj["items"]
    show = lambda k: (dev[k]["n_blocks"], dev[k]["ci99"] and round(dev[k]["ci99"]["mean"], 3),
                      dev[k]["ci99"] and [round(dev[k]["ci99"]["lo"], 3), round(dev[k]["ci99"]["hi"], 3)])
    for k in ("PLACE-t", "PLACE-kappa", "PLACE8-t", "PLACE-tS", "MEM", "EDGE", "GRAD-EW", "GRAD-NS", "LIN", "CONC",
              "MAP", "SPREAD", "INTRA-TILE"):
        print("  dev %-13s blocks, mean, 99%% CI: %s" % (k, show(k)))
    m = lambda k: dev[k]["ci99"]["mean"] if dev[k]["ci99"] else None
    want("PLACE-t > 0 (PER16 planted to trip later)", (m("PLACE-t") or 0) > 0)
    want("PLACE8-t > 0", (m("PLACE8-t") or 0) > 0)
    want("EDGE >= MEM > 0 (EDGE8 0.85, MEM8 0.93 vs CEN8 1.03; equal when both are censored at 150 s)",
         (m("EDGE") or 0) >= (m("MEM") or 0) > 0)
    want("GRAD-NS < 0 (N8b 1.06 trips earlier than S8b 0.94)", (m("GRAD-NS") or 0) < 0)
    want("|GRAD-EW| < |GRAD-NS| (W8b = E8b)", abs(m("GRAD-EW") or 0) < abs(m("GRAD-NS") or 1))
    want("CONC > 0 (concentrated placements lift the high)", (m("CONC") or 0) > 0)
    want("MAP > 0 (the I/O sensor warmer beside B4NE)", (m("MAP") or 0) > 0)
    want("PLACE-kappa < 0 where computed (PER16 kappa below INT16)", m("PLACE-kappa") is None or m("PLACE-kappa") < 0)
    want("sign count favours PER16 in PLACE-t", dev["PLACE-t"]["sign_count"]["A_longer"] >= dev["PLACE-t"]["sign_count"]["B_longer"])
    # F9a: block 2301 lost MEM8, so it is dropped from EVERY item (PLACE8-t, EDGE and LIN too), not only from MEM
    inval = lambda k: 2301 in [p for p, _ in dev[k]["values"]]
    want("F9a: L8 block 2301 without MEM8 is incomplete and dropped from EVERY L8 item (PLACE8-t, EDGE, MEM, LIN)",
         devj.get("incomplete_blocks", {}).get("2301") == ["MEM8"] and not any(inval(k) for k in ("PLACE8-t", "EDGE", "MEM", "LIN"))
         and dev["PLACE8-t"]["n_blocks"] >= 3)
    sh([os.path.join(HP, "reduce.py"), "--data", a3, "--card", "aifoundry3", "--p1", "--out", os.path.join(work, "p1.json")], env)
    p1 = json.load(open(os.path.join(work, "p1.json")))["p1"]
    print("  P1 decisions:", json.dumps(p1["decisions"])[:400])
    want("P1 keeps L16", p1["decisions"].get("keep_L16") is True)

    # ---- 27 Sep fault: P1 took each tier's start edge from the CURRENT params file, not from the edge each block ran
    # at (after params-r1 became S_L 61 / S_L8 64, --p1 on the R1b blocks, which ran at 60 / 63, said "S_L 62" and
    # "censored at S_L8 = 64: L8 and G8 dropped"). Synthetic R1b (1601-1603) at S_L 60 / S_L8 63 in its own params
    # directory; P1 before and after params-r1 is edited must decide the same, from the edges the blocks recorded
    psc = os.path.join(work, "params-scout")
    os.makedirs(psc)
    json.dump(relaxed, open(os.path.join(psc, "params-r1-aifoundry3.json"), "w"))
    envs = dict(env, HP_PARAMS_DIR=psc)
    scd = os.path.join(work, "scout")
    sh([os.path.join(HERE, "synth_blocks.py"), scd, "--seed", "3", "--passes", "1601,1602,1603"], envs)
    sc3 = os.path.join(scd, "aifoundry3")
    p1cmd = lambda *d: [os.path.join(HP, "reduce.py")] + [x for dd in d for x in ("--data", dd)] + \
        ["--card", "aifoundry3", "--p1", "--no-kappa", "--out", os.path.join(work, "p1x.json")]
    sh(p1cmd(sc3), envs)
    pa = json.load(open(os.path.join(work, "p1x.json")))["p1"]
    json.dump(dict(relaxed, S_L=61, S_L8=64), open(os.path.join(psc, "params-r1-aifoundry3.json"), "w"))
    sh(p1cmd(sc3), envs)
    pb = json.load(open(os.path.join(work, "p1x.json")))["p1"]
    dd = lambda p: {k: p["decisions"][k] for k in ("D-L16", "D-L8", "D-S", "keep_S", "keep_L16")}
    print("  P1 on synthetic R1b: D-L16 %s; D-L8 %s" % (
        {k: pa["decisions"]["D-L16"][k] for k in ("S_L", "ran_at", "why")},
        {k: pa["decisions"]["D-L8"][k] for k in ("S_L8", "keep_L8_G8", "ran_at", "why")}))
    want("P1 edge fault: D-L16 and D-L8 start from the edges the R1b blocks recorded (S_L 60, S_L8 63), and the "
         "decisions are unchanged after params-r1 is edited to S_L 61 / S_L8 64",
         pa["decisions"]["D-L16"]["ran_at"] == 60 and pa["decisions"]["D-L8"]["ran_at"] == 63
         and pa["decisions"]["D-L16"]["S_L"] is not None and dd(pa) == dd(pb) and pb["notes"])
    # a block without its record is refused, never filled in from the current params file
    nop = os.path.join(work, "scout-noparams")
    shutil.copytree(scd, nop)
    f_ = os.path.join(nop, "aifoundry3", "hp", "p1601", "plan.json")
    d_ = json.load(open(f_)); d_.pop("params"); json.dump(d_, open(f_, "w"))
    rr = run(p1cmd(os.path.join(nop, "aifoundry3")), envs, check=False)
    want("P1 edge fault: a block whose plan.json recorded no params is refused (%s)" % rr.stderr.strip()[:70],
         rr.returncode != 0 and "P1 refused" in rr.stderr and "p1601" in rr.stderr)
    # an R1 L16 block run at S_L 61 beside 1201-1203 at 60: PLACE-t may not pool them (DESIGN2 §2.4: identical parameters)
    mix = os.path.join(work, "mix")
    sh([os.path.join(HERE, "synth_blocks.py"), mix, "--seed", "4", "--passes", "1204"], envs)
    rr = run(p1cmd(a3, os.path.join(mix, "aifoundry3")), envs, check=False)
    want("P1 edge fault: R1 L16 blocks at S_L 60 and 61 are refused for PLACE-t, naming both edges (%s)"
         % rr.stderr.strip()[:90], rr.returncode != 0 and "P1 refused" in rr.stderr and "PLACE-t" in rr.stderr
         and "edge 60" in rr.stderr and "edge 61" in rr.stderr)
    want("P1 edge fault: every P1 item reports the edges its blocks used (PLACE-t: R1 L16 at 60, %s)"
         % p1["items"]["PLACE-t"].get("edges"), list(p1["items"]["PLACE-t"].get("edges") or {}) == ["60"] and
         all("edges" in v for v in p1["items"].values()))

    # ---- V0 on card 1 (DESIGN2 §6.1): T_cal from aifoundry3's R3 CAL chains; a large T_cal L makes card 1's edge
    # fall to 58 (below development's 59-62), so validation must accept S_L = 58 (review F6)
    blocks = RD.load_blocks(a3, "aifoundry3")
    cal = lambda typ: [x["obs"]["t66_c"] for b in blocks if b["round"] == "r3" and b["type"] == typ for x in b["runs"]
                       if x["rec"]["role"] == "cal" and not x["obs"]["void"]]
    T_L8 = H.median(cal("L8"))
    json.dump({"_what": "self-test V0", "S_L": 60, "S_L8": 63, "L8_offset": 3, "T_cal_s": {"L": 400.0, "L8": T_L8}},
              open(os.path.join(params, "params-v0-aifoundry1-c1.json"), "w"))
    c1 = os.path.join(data, "aifoundry1-c1")
    for series in ("5501,5502,5503", "5511,5512,5513"):
        sh([os.path.join(HERE, "synth_blocks.py"), data, "--seed", "5", "--card", "aifoundry1-c1", "--passes", series], env)
    v0p = os.path.join(work, "v0.json")
    r = run([os.path.join(HP, "hplib.py"), "v0final", "--data", c1, "--card", "aifoundry1-c1", "--write", v0p], env, check=False)
    v0 = json.load(open(v0p)) if os.path.exists(v0p) else json.loads(r.stdout.splitlines()[0])
    print("  V0: S_L %s (%s), S_L8 %s (%s, started at %s)" % (v0["S_L"], v0["L"].get("why"), v0["S_L8"], v0["L8"].get("why"),
                                                             v0["L8"].get("start")))
    want("F6: V0 settles card 1's S_L at 58 (below development's range) and writes v0.json", v0.get("S_L") == 58 and os.path.exists(v0p))
    L8blk = [json.loads(l) for l in open(os.path.join(c1, "hp", "p5511", "runs.jsonl"))]
    want("F6: the S_L8 series starts at card 1's settled S_L + the L8 offset (58 + 3 = 61), not aifoundry3's 60 + 3",
         L8blk and L8blk[0]["edge"] == 61)

    # ---- P3 (review F4, F5, F9b)
    rr = run([os.path.join(HP, "reduce.py"), "--data", a3, "--card", "aifoundry3", "--p3", "--out", os.path.join(work, "x.json")], env, check=False)
    want("F5: P3 refuses without card 1's V0 data (no silent ratio 1)", rr.returncode != 0 and "P3 refused" in rr.stderr)
    sh([os.path.join(HP, "reduce.py"), "--data", a3, "--card", "aifoundry3", "--p3", "--cal-card1", c1,
        "--out", os.path.join(work, "reg.json")], env)
    reg = json.load(open(os.path.join(work, "reg.json")))["registration"]
    for k, v in reg["items"].items():
        print("  P3 %-13s %s" % (k, ("REGISTERED %s n=%s h(n_val)=%.3g <= %.3g" % (v["prediction"], v["projected_n"],
                                    v["h_at_n_val"], v["target_h"])) if v.get("registered")
                                  else "reported, not tested: %s" % v.get("reason")))
    print("  P3 beta %.3g, types kept %s, n_val %s, card-1 minutes %s" % (reg["beta"] or float("nan"), reg["types_kept"],
                                                                         reg["n_val"], reg["card1_minutes"]))
    print("  P3 cv %s" % json.dumps(reg["cv"]))
    print("  P3 notes %s" % reg["notes"])
    want("P3 registers PLACE-t as SIGN+", reg["items"]["PLACE-t"].get("prediction") == "SIGN+" and reg["items"]["PLACE-t"].get("registered"))
    ok4 = all(v["h_at_n_val"] <= v["target_h"] + 1e-12 and v["type"] in reg["n_val"]
              for v in reg["items"].values() if v.get("registered"))
    want("F4: every registered item meets h(n_val) <= 0.7 x band/|estimate| at its type's frozen n_val", ok4)
    want("F4: no registered item needs more blocks than its type's n_val",
         all((v.get("projected_n") or 99) <= reg["n_val"][v["type"]] or v["h_at_n_val"] <= v["target_h"]
             for v in reg["items"].values() if v.get("registered")))
    prim_ok = True
    for typ, n in reg["n_val"].items():
        its = {k: v for k, v in reg["items"].items() if v["type"] == typ}
        if typ in RD.PRIMARY_OF_TYPE:
            pv = its[RD.PRIMARY_OF_TYPE[typ]]
            want_n = pv["projected_n"] if pv.get("candidate") and pv.get("projected_n") is not None else 5
        else:
            want_n = min([v["projected_n"] for v in its.values() if v.get("candidate") and v.get("projected_n")] or [5])
        prim_ok = prim_ok and n == want_n
    want("F4: n_val per type: L16 by its primary PLACE-t, S/L8/G8 by the first candidate to reach step 4, else 5 "
         "(§2.4 step 5, README departure 22)", prim_ok)
    # review low (27 Sep): G8 has no primary in DESIGN2; GRAD-NS reaching step 4 at n = 12 must not be capped at 5
    # because GRAD-EW (the old stand-in primary) is no candidate
    g8 = {"GRAD-EW": {"candidate": False}, "GRAD-NS": {"candidate": True, "projected_n": 12}}
    want("P3 (review low): G8 n_val = 12 from GRAD-NS when GRAD-EW is no candidate (was 5)",
         RD.choose_n_val("G8", g8, H.DEFAULTS)[0] == 12 and RD.choose_n_val("L16", {"PLACE-t": {"candidate": False}},
                                                                             H.DEFAULTS)[0] == 5)
    want("P3 (review low): the synthetic registration keeps G8 with GRAD-NS registered at its n_val",
         "G8" in reg["types_kept"] and reg["items"]["GRAD-NS"].get("registered") is True)
    want("H11 (review low): [FAIL, INSUFFICIENT] is FAIL; [PASS, INSUFFICIENT] INSUFFICIENT; [PASS, PASS] PASS",
         RD.h11_word(["FAIL", "INSUFFICIENT"]) == "FAIL" and RD.h11_word(["PASS", "INSUFFICIENT"]) == "INSUFFICIENT"
         and RD.h11_word(["PASS", "PASS"]) == "PASS")
    want("F5: the CV ratio uses aifoundry3's R3 L16 CAL chains at S_L and card 1's V0 chains at the settled edge",
         reg["cv"]["card1"] is not None and reg["cv"]["aifoundry3"] is not None and "S_L=60" in reg["cv"]["aifoundry3_what"]
         and "edge 58" in reg["cv"]["card1_what"] and reg["cv"]["ratio_used"] >= 1.0)
    # F9b: with R1's Tier S INT16/PER16 runs censored, D-S removes PLACE-tS in P3 (in-process, on the same blocks)
    bl = RD.load_blocks(a3, "aifoundry3")
    RD.mark_incomplete(bl)
    for b in bl:
        if b["round"] == "r1" and b["type"] == "S":
            for x in b["runs"]:
                if x["rec"]["name"] in ("INT16@32", "PER16@32"):
                    x["obs"]["censored"] = True
    c1b = {"data": c1, "blocks": RD.load_blocks(c1, "aifoundry1-c1", rounds=["v0"])}
    regx = RD.p3(bl, "aifoundry3", c1b)
    want("F9b: P1's D-S (censored Tier S runs) makes PLACE-tS reported, not tested in P3",
         not regx["items"]["PLACE-tS"].get("registered") and "D-S" in (regx["items"]["PLACE-tS"].get("reason") or ""))
    # ---- the edge fault in P3: aifoundry3's frozen S_L is the edge its R3 L16 blocks RAN at (the old code took
    # params-r3's S_L, found no CAL chain at an edited value and refused), and V0's rule runs on the params the V0
    # blocks recorded (not params-v0 now: a T_cal equal to card 1's first-edge median would settle it at 60, not 58)
    t5501 = [x["obs"]["t66_s"] for b in c1b["blocks"] if b["pass"] == 5501 for x in b["runs"]
             if x["rec"]["role"] == "meas" and not x["obs"]["void"] and not x["obs"]["censored"]]
    pr3, pv0 = os.path.join(params, "params-r3-aifoundry3.json"), os.path.join(params, "params-v0-aifoundry1-c1.json")
    keep3, keepv0 = open(pr3).read(), open(pv0).read()
    try:
        json.dump(dict(relaxed, S_L=61), open(pr3, "w"))
        d_ = json.loads(keepv0); d_["T_cal_s"]["L"] = H.median(t5501) or 60.0; json.dump(d_, open(pv0, "w"))
        rr = run([os.path.join(HP, "reduce.py"), "--data", a3, "--card", "aifoundry3", "--p3", "--cal-card1", c1,
                  "--out", os.path.join(work, "reg-edited.json")], env, check=False)
    finally:
        open(pr3, "w").write(keep3); open(pv0, "w").write(keepv0)
    reg2 = json.load(open(os.path.join(work, "reg-edited.json")))["registration"] if rr.returncode == 0 else {}
    nonotes = lambda r: {k: v for k, v in r.items() if k != "notes"}
    want("P3 edge fault: with params-r3 edited to S_L 61 and params-v0's T_cal_s changed, P3 gives the same registration, "
         "n_val and CV (R3 L16 at S_L 60, card 1 at 58), and notes both edits (%s)" % (rr.stderr.strip()[:60] or "rc 0"),
         rr.returncode == 0 and nonotes(reg2) == nonotes(reg) and reg2["cv"]["aifoundry3_edge"] == 60
         and any("S_L 61" in n for n in reg2["notes"]) and any("T_cal_s" in n for n in reg2["notes"]))
    want("P3 edge fault: every P3 item reports the edges its pooled blocks used (PLACE-t: L16 at 60)",
         all("edges" in v for v in reg["items"].values()) and list(reg["items"]["PLACE-t"]["edges"]) == ["60"])
    bl2 = RD.load_blocks(a3, "aifoundry3")
    RD.mark_incomplete(bl2)
    b_ = next(b for b in bl2 if b["round"] == "r3" and b["type"] == "L8" and RD.usable(b))
    b_["params"] = dict(b_["params"], S_L8=64)
    for x in b_["runs"]:
        x["rec"] = dict(x["rec"], edge=64)
    try:
        RD.p3(bl2, "aifoundry3", c1b)
        msg = ""
    except SystemExit as e:
        msg = str(e)
    want("P3 edge fault: an R3 L8 block run at S_L8 64 beside R3 L8 blocks at 63 is refused for PLACE8-t, naming both "
         "edges (%s)" % msg[:90], "P3 refused" in msg and "PLACE8-t" in msg and "edge 63" in msg and "edge 64" in msg)
    # F9c: D-L8 takes CEN8's median only (CEN8 30, 45 -> median 37.5 < 40: lower; with W8b 60 pooled it was 45: keep)
    def fake(name, t):
        return {"rec": {"role": "meas", "slot": name + str(t), "name": name, "edge": 63},
                "obs": {"name": name, "t66_s": t, "censored": False, "void": [], "tier": "L"}}
    sc = [{"pass": 1602, "round": "r1", "type": "SCOUT", "k": 2, "void": [], "params": H.DEFAULTS,
           "params_recorded": True, "runs": [fake("CEN8", 30.0), fake("CEN8", 45.0), fake("W8b", 60.0)]}]
    d8 = RD.p1(sc, "aifoundry3")["decisions"]["D-L8"]
    want("F9c: D-L8 uses CEN8's median only (37.5 s < 40: lower S_L8)", d8["S_L8"] == 62 and "37.5" in d8["why"])
    # F9e: trigb_card passes candidate= (an ALIVE_CANDIDATE card's first down event needs an idle event after it)
    import sptrace_events as SE
    seen = {}
    orig = SE.trigb_evaluate
    SE.trigb_evaluate = lambda *a, **k: seen.update(k) or {"holds": None}
    with tempfile.TemporaryDirectory() as td:
        for f in ("sp-idle.bin", "sp-1.bin"):
            open(os.path.join(td, f), "wb").write(b"")
        RD.trigb_card(td, "aifoundry1-c1", [{"dir": td, "pass": 9201, "runs": [{"rec": {"idx": 1, "role": "meas"},
                                                                                "obs": {}, "tel": []}]}], candidate=True)
    SE.trigb_evaluate = orig
    want("F9e: TRIG-B on an ALIVE_CANDIDATE card is evaluated with candidate=True", seen.get("candidate") is True)

    # ---- PREREG for validation, into the work directory (dry: --out-dir/--params-dir allowed)
    json.dump({"class": "SILENT"}, open(os.path.join(work, "probe-c1.json"), "w"))
    bins = {r: {"path": "build/x/%s" % r, "sha256": ("%064x" % (i + 1))} for i, r in
            enumerate(("heater", "heater_kernel", "ettelem", "ettelem_hp"))}
    json.dump(bins, open(os.path.join(work, "bin-c1.json"), "w"))
    pr = os.path.join(work, "prereg")
    pre = [os.path.join(HP, "prereg.py"), "--val", "--registration", os.path.join(work, "reg.json"), "--probe-c1",
           os.path.join(work, "probe-c1.json"), "--out-dir", pr, "--params-dir", params, "--bin-c1", os.path.join(work, "bin-c1.json")]
    rr = run(pre, env, check=False)
    want("F6: prereg.py --val refuses without --v0", rr.returncode != 0 and "--v0" in rr.stderr)
    print("  " + sh(pre + ["--v0", v0p], env).strip())
    envv = dict(env, HP_PREREG_DIR=pr)
    lock = lambda e=envv: run([os.path.join(HP, "hplib.py"), "vallock", "--card", "aifoundry1-c1",
                               "--bins", os.path.join(work, "bin-c1.json")], e, check=False)
    r0 = lock()
    print("  vallock: %s" % r0.stdout.strip())
    want("F1: the validation lock holds on the fresh PREREG", r0.returncode == 0)
    mdh0 = H.sha256(os.path.join(pr, "PREREG.md"))
    rw = lock(dict(envv, HP_PREREG_SHA256="0" * 64))
    rr_ = lock(dict(envv, HP_PREREG_SHA256=mdh0))
    want("review low: vallock refuses a PREREG.md whose sha256 is not the recorded HP_PREREG_SHA256, holds on the "
         "recorded one", rw.returncode == 1 and "HP_PREREG_SHA256" in rw.stdout and rr_.returncode == 0)
    keep_ov, keep_dry = H.override_dir, H.dry           # outside V3_DRY (in-process): the recorded sha256 is required
    try:
        H.override_dir = lambda var, default: {"HP_PREREG_DIR": pr, "HP_PARAMS_DIR": params}.get(var, default)
        H.dry = lambda: False
        os.environ.pop("HP_PREREG_SHA256", None)
        okn, whyn, _ = H.vallock("aifoundry1-c1", json.load(open(os.path.join(work, "bin-c1.json"))))
        os.environ["HP_PREREG_SHA256"] = mdh0
        oky, _, recy = H.vallock("aifoundry1-c1", json.load(open(os.path.join(work, "bin-c1.json"))))
    finally:
        H.override_dir, H.dry = keep_ov, keep_dry
        os.environ.pop("HP_PREREG_SHA256", None)
    want("review low: outside V3_DRY vallock refuses without HP_PREREG_SHA256 and holds with it (%s)" % whyn[:60],
         not okn and "HP_PREREG_SHA256" in whyn and oky and recy["prereg_md_sha256_recorded"] == mdh0)
    lst = os.path.join(work, "card1-listing.txt")
    open(lst, "w").write("build/claims-v3/aifoundry1-c1/hp/p9201\n")
    rl = run(pre + ["--v0", v0p, "--replace-unused", "--card1-listing", lst], env, check=False)
    open(lst, "w").write("%s  tools/claims-v3/hp/prereg/PREREG.md\n" % ("a" * 64))
    rl2 = run(pre + ["--v0", v0p, "--card1-listing", lst], env, check=False)
    want("review low: prereg.py --val refuses when card 1's host lists a validation directory, or holds a PREREG "
         "(without --replace-unused)", rl.returncode != 0 and "aifoundry1" in rl.stderr and "p9201" in rl.stderr
         and rl2.returncode != 0 and "already has a PREREG" in rl2.stderr)
    pv = json.load(open(os.path.join(params, "params-val-aifoundry1-c1.json")))
    want("F6: params-val carries card 1's V0 edges (S_L 58)", pv["S_L"] == 58 and pv["S_L8"] == v0["S_L8"])
    info, runs, P = H.plan(9201, "aifoundry1-c1")
    want("F6: a validation L16 block plans at S_L = 58 (validation's own range)", runs and all(r["edge"] == 58 for r in runs))

    def tampered(path, edit, label):
        keep = open(path).read()
        try:
            d = json.loads(keep); edit(d); json.dump(d, open(path, "w"), indent=1)
            r = lock()
        finally:
            open(path, "w").write(keep)
        want("F1: the lock refuses %s (%s)" % (label, r.stdout.strip()[:90]), r.returncode == 1)
    pvp = os.path.join(params, "params-val-aifoundry1-c1.json")
    tampered(pvp, lambda d: d.update(S_L=59, kappa_gate=0.85), "a tampered params-val (S_L 58->59, kappa_gate 0.85)")
    tampered(pvp, lambda d: d.update(trigb="auto"), "an extra params-val key")
    tampered(os.path.join(pr, "prereg.json"), lambda d: d["items"]["PLACE-t"].update(band=0.2), "a changed band in prereg.json")
    bad = dict(bins, heater={"path": "build/x/heater", "sha256": "f" * 64})
    json.dump(bad, open(os.path.join(work, "bin-bad.json"), "w"))
    r = run([os.path.join(HP, "hplib.py"), "vallock", "--card", "aifoundry1-c1", "--bins", os.path.join(work, "bin-bad.json")], envv, check=False)
    want("F1: the lock refuses another heater binary", r.returncode == 1 and "heater" in r.stdout)
    r = run([os.path.join(HP, "hplib.py"), "vallock", "--card", "aifoundry1-c1", "--bins", os.path.join(work, "bin-c1.json")],
            dict(envv, V3_DRY=""), check=False)
    want("F1: HP_PREREG_DIR / HP_PARAMS_DIR are refused without V3_DRY", r.returncode != 0 and "V3_DRY" in (r.stdout + r.stderr))
    rr = run(pre + ["--v0", v0p], env, check=False)
    want("F1: prereg.py --val refuses to re-freeze once PREREG.md exists", rr.returncode != 0 and "re-freeze" in rr.stderr)
    # ---- synthetic card-1 validation blocks from the frozen params; L16 gets 2 blocks beyond n_val (review F10)
    n_val = reg["n_val"]
    code = {"S": 1, "L16": 2, "L8": 3, "G8": 4}
    passes = [9000 + code[t] * 100 + k for t in reg["types_kept"] for k in range(1, n_val[t] + 1 + (2 if t == "L16" else 0))]
    print(sh([os.path.join(HERE, "synth_blocks.py"), data, "--seed", "11", "--card", "aifoundry1-c1",
              "--passes", ",".join(map(str, passes))], env).strip())
    mdh = H.sha256(os.path.join(pr, "PREREG.md"))
    for p in passes:                      # what block.sh writes into a validation block
        d = os.path.join(c1, "hp", "p%d" % p)
        json.dump({"prereg_md_sha256": mdh}, open(os.path.join(d, "prereg-lock.json"), "w"))
        json.dump(bins, open(os.path.join(d, "binaries.json"), "w"))
    rr = run(pre + ["--v0", v0p, "--replace-unused", "--val-data", c1], env, check=False)
    want("F1: prereg.py --val refuses even --replace-unused once validation blocks exist",
         rr.returncode != 0 and "validation data exist" in rr.stderr)
    # review high (27 Sep): blockcheck on a validation block of card 1 with one void run: it runs (it raised Refused,
    # reading every block as r1), reads round val from plan['info'] and asks for exactly that slot's re-run
    vb = os.path.join(c1, "hp", "p%d" % passes[0])
    rl_ = open(os.path.join(vb, "runs.jsonl")).read().splitlines()
    k_ = next(i for i, l in enumerate(rl_) if json.loads(l)["role"] == "meas")
    r_ = json.loads(rl_[k_]); r_["rcs"] = [1] + list(r_.get("rcs", []))[1:]
    rl2_ = list(rl_); rl2_[k_] = json.dumps(r_)
    open(os.path.join(vb, "runs.jsonl"), "w").write("\n".join(rl2_) + "\n")
    bc = run([os.path.join(HP, "hplib.py"), "blockcheck", "--out", vb, "--card", "aifoundry1-c1"], env, check=False)
    open(os.path.join(vb, "runs.jsonl"), "w").write("\n".join(rl_) + "\n")
    os.remove(os.path.join(vb, "blockcheck.json"))
    want("review high: blockcheck on validation block p%d with one void run (slot %s): rc 0, round val, RERUN of that "
         "slot only (%s)" % (passes[0], r_["slot"], bc.stdout.strip().replace("\n", "; ")[:120]),
         bc.returncode == 0 and "round val" in bc.stdout and
         [l.split()[1] for l in bc.stdout.splitlines() if l.startswith("RERUN ")] == [str(r_["slot"])])
    valcmd = [os.path.join(HP, "reduce.py"), "--data", c1, "--card", "aifoundry1-c1", "--val", "--prereg",
              os.path.join(pr, "prereg.json"), "--out", os.path.join(work, "val.json")]
    sh(valcmd, env)
    val = json.load(open(os.path.join(work, "val.json")))["validation"]
    for k, v in val["items"].items():
        c = v.get("ci99")
        print("  val %-38s %-24s %s" % (k, v.get("outcome"), c and "mean %.3g [%.3g, %.3g] n=%d" % (c["mean"], c["lo"], c["hi"], c["n"])))
    print("  val blocks: %s" % json.dumps(val["blocks"]))
    want("validation: PLACE-t PASS on synthetic card 1", val["items"]["PLACE-t"]["outcome"] == "PASS")
    want("validation: every item has a V3 word, 'reported, not tested' or a stated 'not tested'",
         all(v.get("outcome") in ("PASS", "FAIL", "CARD-DIFFERENT", "INSUFFICIENT", "reported, not tested", "not tested",
                                  "not tested (waived in PREREG)", RD.POWER_WAIVED_WORD) for v in val["items"].values()))
    want("F10: validation uses the first n_val L16 blocks only; the 2 extra are listed, not used",
         val["items"]["PLACE-t"]["ci99"]["n"] == n_val["L16"] and len(val["blocks"]["extra_blocks_not_used"].get("L16", [])) == 2)
    regd = [k for k, v in reg["items"].items() if v.get("registered")]
    want("F9d: POWER and WORK are reported for CONC, MAP and LIN when registered",
         all(any(k.startswith(i + "/POWER") for k in val["items"]) and any(k.startswith(i + "/WORK") for k in val["items"])
             for i in ("CONC", "MAP", "LIN") if i in regd))
    want("F9f: card-1 TRIG-A is explicitly waived (PREREG and the verdicts)",
         val["items"]["TRIG-A"]["outcome"] == "not tested (waived in PREREG)" and
         "WAIVED" in open(os.path.join(pr, "PREREG.md")).read())
    # the reducer's own lock (review F1 (3))
    keep = open(os.path.join(pr, "prereg.json")).read()
    d = json.loads(keep); d["items"]["PLACE-t"]["band"] = 0.5
    open(os.path.join(pr, "prereg.json"), "w").write(json.dumps(d))
    rr = run(valcmd, env, check=False)
    open(os.path.join(pr, "prereg.json"), "w").write(keep)
    want("F1: reduce.py --val refuses a prereg.json that is not the locked one", rr.returncode != 0 and "refused" in rr.stderr)
    fake_pr = os.path.join(work, "prereg-fake.json")
    open(fake_pr, "w").write(keep)
    rr = run(valcmd[:-4] + ["--prereg", fake_pr, "--out", os.path.join(work, "x.json")], env, check=False)
    want("F1: reduce.py --val refuses a prereg.json without its PREREG.md", rr.returncode != 0 and "refused" in rr.stderr)
    bj = os.path.join(c1, "hp", "p%d" % passes[0], "binaries.json")
    json.dump(bad, open(bj, "w"))
    rr = run(valcmd, env, check=False)
    json.dump(bins, open(bj, "w"))
    want("F1: reduce.py --val refuses a validation block that ran another binary", rr.returncode != 0 and "binary heater" in rr.stderr)
    pl = os.path.join(c1, "hp", "p%d" % passes[0], "prereg-lock.json")
    json.dump({"prereg_md_sha256": "0" * 64}, open(pl, "w"))
    rr = run(valcmd, env, check=False)
    r1_ = lock(dict(envv))
    rv = run([os.path.join(HP, "hplib.py"), "vallock", "--card", "aifoundry1-c1", "--bins", os.path.join(work, "bin-c1.json"),
              "--data", c1], envv, check=False)
    json.dump({"prereg_md_sha256": mdh}, open(pl, "w"))
    want("F1: a block under another PREREG: reduce.py --val refuses, and vallock refuses the next validation block",
         rr.returncode != 0 and rv.returncode == 1 and "ran under PREREG" in rv.stdout)
    # review medium (27 Sep): a validation block that ran with V3_FORCE is never evidence
    mk = os.path.join(c1, "hp", "p%d" % passes[0], "marks.jsonl")
    open(mk, "w").write(json.dumps({"t_ms": 1, "ev": "block_begin", "overrides": "V3_FORCE"}) + "\n")
    rr = run(valcmd, env, check=False)
    os.remove(mk)
    want("review medium: reduce.py --val refuses a validation block that ran with V3_FORCE",
         rr.returncode != 0 and "V3_FORCE" in rr.stderr)
    # ---- README departure 37: Tier S POWER is waived for every pair with INT16@32 (its sw_W window is empty), reported
    # as "waived: no window in Tier S; see Tier L", never INSUFFICIENT; the other pairs keep POWER EQUIV
    want("dep. 37: power_waived: S pairs with INT16@32 only (not S PER-UNI, S B4, L16 PER-INT, L8's identity)",
         RD.power_waived("S", ("PER16@32", "INT16@32")) and RD.power_waived("S", ("INT16@32", "UNI32@16"))
         and not RD.power_waived("S", ("PER16@32", "UNI32@16")) and not RD.power_waived("S", ("B4NE", "B4SW"))
         and not RD.power_waived("L16", ("PER16@32", "INT16@32"))
         and not RD.power_waived("L8", ("UNI32@16", ("INT16@16", "PER16@16")))
         and "Tier S POWER is WAIVED" in open(os.path.join(pr, "PREREG.md")).read())
    vbl = [b for b in RD.load_blocks(c1, "aifoundry1-c1") if b["round"] == "val"]
    fpr = json.loads(open(os.path.join(pr, "prereg.json")).read())
    for iid in ("PLACE-tS", "CONC"):             # registered by hand (the synthetic P3 leaves both reported only)
        fpr["items"][iid] = dict(fpr["items"][iid], registered=True, prediction="SIGN+")
    wv = RD.validate(vbl, "aifoundry1-c1", fpr)["items"]
    print("  dep. 37: %s" % {k: (v.get("outcome"), v.get("tier_L_ci99") and round(v["tier_L_ci99"]["mean"], 3))
                             for k, v in wv.items() if "/POWER" in k})
    want("dep. 37: validation reports PLACE-tS/POWER and CONC/POWER INT16@32-UNI32@16 as waived (with the L16 value), "
         "CONC/POWER PER16@32-UNI32@16 with a V3 word, and WORK on every pair",
         wv["PLACE-tS/POWER"]["outcome"] == RD.POWER_WAIVED_WORD and wv["PLACE-tS/POWER"].get("tier_L_ci99")
         and wv["CONC/POWER INT16@32-UNI32@16"]["outcome"] == RD.POWER_WAIVED_WORD
         and wv["CONC/POWER PER16@32-UNI32@16"]["outcome"] in ("PASS", "FAIL", "INSUFFICIENT")
         and all(k in wv for k in ("PLACE-tS/WORK", "CONC/WORK INT16@32-UNI32@16", "CONC/WORK PER16@32-UNI32@16")))
    regw = RD.p3(RD.load_blocks(a3, "aifoundry3"), "aifoundry3", c1b)
    want("dep. 37: P3 lists the waived POWER pairs of every registered item (none outside Tier S)",
         all(v.get("power_waived_pairs") == ([] if v["type"] != "S" else [RD.pair_label(pp) for pp in
                                             RD.POWER_WORK_PAIRS[k] if "INT16@32" in RD.pair_label(pp)])
             for k, v in regw["items"].items() if v.get("registered")))

    # ---- README departure 36: L8 and G8 dropped (D-L8). V0 needs no S_L8 series, and PREREG freezes without S_L8
    pd = os.path.join(work, "params-drop")
    os.makedirs(pd)
    for r in ("r1", "r2", "r3"):
        shutil.copy(os.path.join(params, "params-%s-aifoundry3.json" % r), pd)
    dv0 = json.load(open(os.path.join(params, "params-v0-aifoundry1-c1.json")))
    dv0.update(types=["S", "L16"], T_cal_s=dict(dv0["T_cal_s"], L8=None))
    json.dump(dv0, open(os.path.join(pd, "params-v0-aifoundry1-c1.json"), "w"))
    envd = dict(env, HP_PARAMS_DIR=pd)
    v0d = os.path.join(work, "v0-drop.json")
    rv = run([os.path.join(HP, "hplib.py"), "v0final", "--data", c1, "--card", "aifoundry1-c1", "--write", v0d], envd, check=False)
    v0dj = json.load(open(v0d)) if os.path.exists(v0d) else {}
    want("dep. 36: with params-v0 types [S, L16], v0final writes a complete v0.json without S_L8 (S_L %s)" % v0dj.get("S_L"),
         rv.returncode == 0 and v0dj.get("complete") is True and v0dj.get("S_L") == 58 and v0dj.get("S_L8") is None)
    keep_pd = os.environ["HP_PARAMS_DIR"]
    try:
        os.environ["HP_PARAMS_DIR"] = pd
        i5511, r5511, _ = H.plan(5511, "aifoundry1-c1")
    finally:
        os.environ["HP_PARAMS_DIR"] = keep_pd
    want("dep. 36: V0's S_L8 pass 5511 is skipped when L8 and G8 are dropped (%s)" % i5511.get("skip"),
         not r5511 and "dropped" in (i5511.get("skip") or ""))
    regd_ = dict(reg, types_kept=[t for t in reg["types_kept"] if t not in ("L8", "G8")],
                 n_val={t: n for t, n in reg["n_val"].items() if t not in ("L8", "G8")},
                 items={k: (dict(v, registered=False, reason="type dropped (D-L8)") if v["type"] in ("L8", "G8") else v)
                        for k, v in reg["items"].items()})
    json.dump({"registration": regd_}, open(os.path.join(work, "reg-drop.json"), "w"))
    prd = os.path.join(work, "prereg-drop")
    pre_d = lambda regf, out, pdir: [os.path.join(HP, "prereg.py"), "--val", "--registration", regf, "--probe-c1",
                                     os.path.join(work, "probe-c1.json"), "--out-dir", out, "--params-dir", pdir,
                                     "--bin-c1", os.path.join(work, "bin-c1.json"), "--v0", v0d]
    rk = run(pre_d(os.path.join(work, "reg.json"), os.path.join(work, "prereg-keep"), pd), envd, check=False)
    want("dep. 36: prereg.py --val still refuses a v0.json without S_L8 when the registration keeps G8 (%s)"
         % rk.stderr.strip()[-80:], rk.returncode != 0 and "S_L8" in rk.stderr)
    rd = run(pre_d(os.path.join(work, "reg-drop.json"), prd, pd), envd, check=False)
    pvd = json.load(open(os.path.join(pd, "params-val-aifoundry1-c1.json"))) if rd.returncode == 0 else {}
    mdd = open(os.path.join(prd, "PREREG.md")).read() if rd.returncode == 0 else ""
    want("dep. 36: with L8 and G8 dropped, prereg.py --val freezes without card 1's S_L8 (params-val S_L 58, S_L8 = "
         "aifoundry3's frozen %s, types %s; PREREG.md says so) (%s)" % (pvd.get("S_L8"), pvd.get("types"),
                                                                      (rd.stderr.strip() or "rc 0")[-60:]),
         rd.returncode == 0 and pvd.get("S_L") == 58 and pvd.get("S_L8") == H.resolve_params("r3", "aifoundry3")["S_L8"]
         and pvd.get("types") == regd_["types_kept"] and "L8 and G8 were dropped" in mdd)
    envdv = dict(envd, HP_PREREG_DIR=prd)
    rl_ = run([os.path.join(HP, "hplib.py"), "vallock", "--card", "aifoundry1-c1", "--bins", os.path.join(work, "bin-c1.json")],
              envdv, check=False)
    try:
        os.environ["HP_PARAMS_DIR"] = pd
        i93, r93, _ = H.plan(9301, "aifoundry1-c1")
        i92, r92, _ = H.plan(9201, "aifoundry1-c1")
    finally:
        os.environ["HP_PARAMS_DIR"] = keep_pd
    want("dep. 36: the lock holds on that PREREG; a validation L8 block is skipped, an L16 block plans at S_L 58 (%s)"
         % rl_.stdout.strip()[:60], rl_.returncode == 0 and not r93 and "dropped" in (i93.get("skip") or "")
         and r92 and all(r["edge"] == 58 for r in r92))
    print()
    for name, okk in checks:
        print("  %s  %s" % ("ok  " if okk else "FAIL", name))
    nfail = sum(1 for _, okk in checks if not okk)
    print("self-test: %d of %d checks pass" % (len(checks) - nfail, len(checks)))
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
