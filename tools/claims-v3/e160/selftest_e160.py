#!/usr/bin/env python3
"""E160 (Q139): the self-test, run before the registration's commit. No card.

    python3 tools/claims-v3/e160/selftest_e160.py > tools/claims-v3/e160/selftest.txt

  1. the frozen inputs and Q139(k)'s three run-time files hash as committed, and every pool tile is the manifest's;
  2. a tile with one byte changed, or of the wrong size, is refused;
  3. predictions-e160.json holds Q139(x)'s numbers for every tile and model, unchanged; the groups are 19 governed and 31 pinned, of which the two tiles
     whose M8 95% upper peak exceeds 82 W are dropped (both governed), so 17 and 31 run;
  4. the runner's preflight refuses a protocol without the watcher's stop keys, a board stop above 85 W, another heater, and binaries that are not the
     pinned ones; the protocol's stops are 76 C / 85 W on 3 samples, the admission limit and the lock 82 W; every label is in the admission table, the
     highest planned estimate is at most 82 W, the dropped tiles are in no run and the admission rule would refuse them;
  5. the preflight override keeps every run_hpl.py refusal except the two that assume a compiled heater beside its kernel;
  6. the bootstrap is reproducible and the coverage line is E140's (21 of 25);
  7. the scoring at known answers: measured = M8's predictions gives every rule PASS with rms 0; governed clocks 30 MHz low fail F1 and F3 but not F2;
     boards 5 W high fail W1, W2 and W3; rises 2 C high fail H1 and H3; peaks 3 W over the 95% value fail PK; a replicate 30 MHz off fails R0;
  8. the queue's smoke check of the C log on made-up records: a sound log passes; a missing C record, a C that is not +0, another kernel, the poison
     off, and a DMA time that would overrun the budget each fail;
  9. the reduction's join of the C check, on E143's committed session s1 (E80's host, no C log of its own) with made-up verdicts: every launch PASS
     counts every complete run; one launch FAIL or without a record leaves its run out; the E160-C verdict follows.
"""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e160_common as C  # noqa: E402
import reduce_e160 as RD  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e160.json")))
fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


# 1
bad = C.check_frozen()
M = C.manifest()
tb = [C.check_tile(C.ROOT, t) for t in M.values()]
ok(not bad and not any(tb) and len(M) == 50, f"frozen inputs, Q139(k)'s three files and 50 tiles as committed ({len(M)} tiles, {sum(1 for x in tb if x)} bad; {bad})")

# 2
with tempfile.TemporaryDirectory() as td:
    t = M["fp16.anchor6_randn"]
    dst = os.path.join(td, C.POOL_REL, t["file"])
    os.makedirs(os.path.dirname(dst))
    src = os.path.join(C.ROOT, C.POOL_REL, t["file"])
    b = bytearray(open(src, "rb").read())
    b[1500] ^= 0x01
    open(dst, "wb").write(bytes(b))
    w1 = C.check_tile(td, t)
    open(dst, "wb").write(bytes(b[:2047]))
    w2 = C.check_tile(td, t)
    ok(w1 is not None and "sha256 whole" in w1 and w2 is not None and "2047 bytes" in w2, f"a changed byte and a short file are refused ({w1[:60]}...; {w2})")

# 3
Q = json.load(open(os.path.join(C.ROOT, C.PRED_REL)))
same = all(P["tiles"][n]["models"][m][k] == Q["tiles"][n][m][k] for n in Q["tiles"] for m in C.MODELS for k in P["tiles"][n]["models"][m])
ng = sum(1 for t in P["tiles"].values() if t["group"] == "governed")
drop = sorted(n for n, t in P["tiles"].items() if t["dropped"])
flag = sorted(n for n in Q["tiles"] if Q["tiles"][n]["M8"]["peak_board_hi95_w"] > 82.0)
ok(same and len(P["tiles"]) == 50 and ng == 19 and drop == flag == ["fp32.anchor6_randn", "fp32.real_qwen_softmax_v"] and P["n_governed"] == 17 and P["n_pinned"] == 31,
   f"predictions-e160.json = Q139(x)'s numbers for 50 tiles x 3 models; {ng} governed, {50 - ng} pinned; dropped {drop} (flagged {flag}); run {P['n_governed']} + {P['n_pinned']}")

# 4
import run_e160 as RN  # noqa: E402
proto = json.load(open(os.path.join(HERE, "protocol.json")))
p2 = copy.deepcopy(proto)
p2["safety"] = {"die_c": 76, "board_w": 85, "board_samples": 3}
w = RN.preflight(p2, "/nonexistent")
ok(w is not None and "lacks abs_stop_c" in w and "lacks board_cap_w" in w, f"preflight refuses other stop keys: {w[:110]}")
p3 = copy.deepcopy(proto)
p3["safety"]["board_cap_w"] = 93
p3["tools"]["heater"] = "build/sparsity_t2/host/sparsity_host"
w = RN.preflight(p3, "/nonexistent")
ok(w is not None and "above 85 W" in w and "tools.heater" in w, f"preflight refuses a 93 W board stop and E80's own heater: {w[:150]}")
w = RN.preflight(proto, "/nonexistent")
ok(w is not None and "sha256 None" in w and C.CC_HOST_REL in w, f"preflight refuses missing binaries: {w[:150]}")
ok(proto["safety"] == {"abs_stop_c": 76, "board_cap_w": 85, "cap_consecutive": 3} and proto["limit_p800_w"] == 82.0 and proto["peak_lock_w"] == 82.0,
   f"the protocol's stops {proto['safety']}, admission limit {proto['limit_p800_w']} W and lock {proto['peak_lock_w']} W")
labs = [r["label"] for bl in proto["blocks"] for r in bl["runs"]]
est = max(proto["admission"][l]["fixed_p800_w"] for l in labs)
dl = {C.label_of(n) for n in P["dropped"]} | set(P["replicate_dropped"])
ok(all(l in proto["admission"] for l in labs) and est <= 82.0 and not (dl & set(labs)), f"every label in the admission table, highest planned estimate {est} W <= 82 W, no dropped label in a run")
import run_e105 as RE  # noqa: E402
with tempfile.TemporaryDirectory() as td:
    adm = RE.Admission(proto, os.path.join(td, "s1"))
    why = {n: adm.why_not(C.label_of(n))[0] for n in P["dropped"]}
    why_ok = adm.why_not("b6-fp16.anchor6_randn")[0]
    adm.state["lock_est"] = 80.17
    why_lock = adm.why_not("b6-fp16.anchor6_randn")[0], adm.why_not("b6-fp32.real_qwen_dequant_q")[0]
ok(all(v and "> 82.0 W" in v for v in why.values()) and why_ok is None and why_lock[0] and why_lock[1] is None,
   f"admission refuses the dropped tiles ({why}), admits fp16.anchor6_randn at 81.12 W, and after a lock at 80.17 W refuses it but not 78.06 W")
ok(proto["tools"]["heater"] == C.WRAPPER_REL and proto["tools"]["kernel"] == C.KERNEL_REL and proto["ccheck"]["host_sha256"] == C.CC_HOST_SHA256,
   f"heater {proto['tools']['heater']} (host {proto['ccheck']['host']} {proto['ccheck']['host_sha256'][:12]}...), kernel {proto['tools']['kernel']}")


# 5
class Fake:
    dry = True
    root = "/nonexistent"


saved = RN._prev_preflight


def raiser(msgs):
    def f(self):
        raise RN.H.Refuse("; ".join(msgs))
    return f


try:
    RN._prev_preflight = raiser(["heater and kernel come from different builds", "heater has no --budget", "no card lock /run/lock/etsoc-shire0.lock"])
    try:
        RN._preflight(Fake())
        r5a = None
    except RN.H.Refuse as e:
        r5a = str(e)
    RN._prev_preflight = raiser(["heater and kernel come from different builds", "heater has no --budget"])
    try:
        RN._preflight(Fake())
        r5b = None
    except RN.H.Refuse as e:
        r5b = str(e)
finally:
    RN._prev_preflight = saved
ok(r5a == "no card lock /run/lock/etsoc-shire0.lock" and r5b is None, f"the override keeps other refusals ({r5a}) and drops only the compiled-heater two ({r5b})")

# 6
a1 = C.boot_rms_range(P["reference"]["governed"]["mhz_err"], 17)
a2 = C.boot_rms_range(P["reference"]["governed"]["mhz_err"], 17)
ok(a1 == a2 and C.coverage_line(25) == 21 and C.coverage_line(48) == 42, f"bootstrap reproducible {tuple(round(x, 3) for x in a1)}; coverage lines 25 -> {C.coverage_line(25)}, 48 -> {C.coverage_line(48)}")


# 7
def cells_at(fn_mhz=lambda n, v: v, fn_w=lambda n, v: v, fn_rise=lambda n, v: v, fn_pk=lambda n, v: v, rep_mhz=0.0):
    cells = {}
    for n, t in P["tiles"].items():
        if t["dropped"]:
            continue
        m = t["models"]["M8"]
        pk = fn_pk(n, m["peak_board_w"])
        cells[t["label"]] = {"label": t["label"], "name": n, "n": 3, "passes": [1, 2, 3], "burst_mhz": fn_mhz(n, m["burst_mhz"]),
                             "burst_w": fn_w(n, m["burst_board_w"]), "rise_c": fn_rise(n, m["burst_die_rise_c"]), "D_w": m["burst_D_w"], "kernel_mhz": None,
                             "burst_mhz_runs": [], "burst_w_runs": [], "rise_runs": [], "die_start_runs": [], "D_runs": [], "p800_w_runs": [], "first_down": [],
                             "peak_w_runs": [pk, pk, pk], "peak_w": pk, "c_minus_zeros_w": None}
    for lab, r in P["replicate"].items():
        cells[lab] = {"label": lab, "n": 3, "burst_mhz": r["ref_burst_mhz"] + rep_mhz, "burst_w": r["ref_burst_w"], "rise_c": 5.0, "peak_w": None}
    return cells


sc = RD.score(cells_at(), P, 2)
v = {k: x["verdict"] for k, x in sc["rules"].items()}
ok(all(x.startswith("PASS") for x in v.values()) and sc["rules"]["E160-F1"]["rms"] == 0.0 and sc["tiles_scored"] == 48, f"at M8's numbers ({sc['tiles_scored']} tiles): {v}")
gov = {n for n, t in P["tiles"].items() if t["group"] == "governed"}
sc = RD.score(cells_at(fn_mhz=lambda n, x: x - 30 if n in gov else x), P, 2)
v = {k: x["verdict"] for k, x in sc["rules"].items()}
ok(v["E160-F1"] == "FAIL" and v["E160-F3"] == "FAIL" and v["E160-F2"].startswith("PASS"), f"governed clocks 30 MHz low: F1 {v['E160-F1']}, F2 {v['E160-F2']}, F3 {v['E160-F3']}")
sc = RD.score(cells_at(fn_w=lambda n, x: x + 5), P, 2)
v = {k: x["verdict"] for k, x in sc["rules"].items()}
ok(v["E160-W1"] == "FAIL" and v["E160-W2"] == "FAIL" and v["E160-W3"] == "FAIL", f"boards 5 W high: W1 {v['E160-W1']}, W2 {v['E160-W2']}, W3 {v['E160-W3']}")
sc = RD.score(cells_at(fn_rise=lambda n, x: x + 2), P, 2)
v = {k: x["verdict"] for k, x in sc["rules"].items()}
ok(v["E160-H1"] == "FAIL" and v["E160-H3"] == "FAIL", f"rises 2 C high: H1 {v['E160-H1']}, H3 {v['E160-H3']}")
sc = RD.score(cells_at(fn_pk=lambda n, x: P["tiles"][n]["models"]["M8"]["peak_board_hi95_w"] + 3), P, 2)
ok(sc["rules"]["E160-PK"]["verdict"] == "FAIL" and sc["rules"]["E160-PK"]["inside"] == 0, f"peaks 3 W over the 95% value: PK {sc['rules']['E160-PK']['verdict']} ({sc['rules']['E160-PK']['inside']} inside)")
r0 = RD.replicate(cells_at(rep_mhz=30.0), P)
r1 = RD.replicate(cells_at(), P)
ok(r0["verdict"] == "FAIL" and r1["verdict"] == "PASS", f"a replicate 30 MHz off: R0 {r0['verdict']}; at the reference: {r1['verdict']}")

# 8
import queue_e160 as QE  # noqa: E402


def smoke_case(mutate=None, gap=3):
    with tempfile.TemporaryDirectory() as td:
        launches, recs = [], []
        t = 1_000_000
        for k, ty in enumerate(("fp32", "fp16", "int8")):
            recs.append({"ccheck": 1, "kind": "host", "host": "x", "host_sha256": C.CC_HOST_SHA256, "kernel": "k", "kernel_sha256": C.E80_SHA256[C.KERNEL_REL], "kernel_from": "runner"})
            recs.append({"ccheck": 1, "kind": "tiles", "type": ty, "fnv": "0" * 16, "a": "00" * 1024, "b": "00" * 1024})
            sp = []
            for j in range(-1, 4):
                a0, a1 = t, t + 400
                t = a1 + gap
                sp.append({"launch": j, "t_start_ms": a0, "t_end_ms": a1, "minions": 1024, "ok": True})
                recs.append({"ccheck": 1, "kind": "c", "type": ty, "launch": j, "iters": 5, "t_start_ms": a0, "t_end_ms": a1, "ok": True, "participants": 1024,
                             "poison": True, "use_mask": 0, "row_mask": "0xffff", "b_stream": 0, "fnv": "0" * 16,
                             "groups": [{"count": 1024, "first_minion": 0, "minions": [], "hex": "0" * 2048}]})
            launches.append({"run": f"SMOKE-0{k + 1}", "role": "work", "sparsity": sp})
        if mutate:
            mutate(recs, launches)
        with open(os.path.join(td, "c-log.jsonl"), "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        return QE.check_smoke_clog(td, launches, proto)


good = smoke_case()
miss = smoke_case(lambda recs, L: recs.pop(5))
nz = smoke_case(lambda recs, L: recs[4]["groups"][0].update(hex="3f80" + "0" * 2044))
kern = smoke_case(lambda recs, L: recs[0].update(kernel_sha256="ab" * 32))
pois = smoke_case(lambda recs, L: recs[3].update(poison=False))
slow = smoke_case(gap=40)
ok(good is None and miss and "no C record" in miss and nz and "not +0" in nz and kern and "pinned host" in kern and pois and "poison" in pois and slow and "budget" in slow,
   f"smoke C log: sound {good}; missing record: {miss}; nonzero C: {str(nz)[:60]}; other kernel: {str(kern)[:50]}; poison off: {str(pois)[:60]}; 40 ms gaps: {str(slow)[:90]}")

# 9
S143 = os.path.join(C.ROOT, "docs/reports/data/2026-11-02-e143-blind5-aifoundry2/aifoundry2/s1")
with tempfile.TemporaryDirectory() as td:
    sd = os.path.join(td, "s1")
    shutil.copytree(S143, sd)
    import gzip
    lines = []
    for ln in gzip.open(os.path.join(sd, "launches.jsonl.gz"), "rt"):
        L = json.loads(ln)
        if L.get("role") == "work":
            lines += [(L["run"], s) for s in L.get("sparsity") or []]
    first_run = lines[0][0]
    second_run = next(r for r, _ in lines if r != first_run)
    ver = [{"t_start_ms": s["t_start_ms"], "t_end_ms": s["t_end_ms"], "verdict": "PASS", "type": s["type"]} for _, s in lines]
    vp = os.path.join(td, "cc-all.json")
    json.dump({"launches": ver}, open(vp, "w"))
    runs_all = RD.collect([sd], RD.load_ccheck([vp]))
    i = next(k for k, (r, _) in enumerate(lines) if r == first_run)
    ver2 = copy.deepcopy(ver)
    ver2[i]["verdict"] = "FAIL"
    j = next(k for k, (r, _) in enumerate(lines) if r == second_run)
    del ver2[j]
    vp2 = os.path.join(td, "cc-two.json")
    json.dump({"launches": ver2}, open(vp2, "w"))
    runs_two = RD.collect([sd], RD.load_ccheck([vp2]))
    c_all, c_two = RD.c_rule(runs_all, True), RD.c_rule(runs_two, True)
nb = len(runs_all)
ca = sum(m["counted"] for m in runs_all)
cm = sum(m["complete"] for m in runs_all)
ct = {m["run"]: m["counted"] for m in runs_two}
ok(nb == 117 and ca == cm == 117 and not ct[first_run] and not ct[second_run] and sum(ct.values()) == 115 and c_all["verdict"] == "PASS" and c_two["verdict"] == "FAIL"
   and c_two["by_verdict"].get("NO_RECORD") == 1 and c_two["by_verdict"].get("FAIL") == 1,
   f"the C join on E143's s1: {nb} bursts, all PASS -> {ca} counted of {cm} complete (C {c_all['verdict']}); one FAIL and one missing record -> "
   f"{sum(ct.values())} counted (C {c_two['verdict']}, {c_two['by_verdict']})")

print("\nALL PASS" if not fails else f"\n{len(fails)} FAILED")
sys.exit(1 if fails else 0)
