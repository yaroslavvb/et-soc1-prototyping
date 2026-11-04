#!/usr/bin/env python3
"""E165 (Q141(g)): the run kit's self-test, run before the kit's commit. No card, no device, no ssh.

    python3 -B tools/claims-v3/e165/selftest_e165.py > tools/claims-v3/e165/selftest.txt

  1. the frozen inputs and Q139(k)'s three run-time files hash as committed, and every pool tile is the manifest's;
  2. a tile with one byte changed, or of the wrong size, is refused;
  3. predictions-e165.json holds Q140(x)'s numbers for every tile and model, unchanged (M9.a2_q140l whole; M8's, M7's and M6's burst fields); the
     frozen file's groups are 18 governed and 43 pinned; the six tiles left out by name are admission-aifoundry2-82w.json's, all governed, so 12
     governed and 43 pinned run, 52 are scored (the three zeros anchors are inputs);
  4. the runner's preflight refuses a protocol without the watcher's stop keys, a board stop above 85 W, another heater, a run of a tile left out by
     name, and binaries that are not the pinned ones; the protocol's stops are 76 C / 85 W on 3 samples, the admission limit and the lock 82 W; every
     label is in the admission table, the highest planned estimate is at most 82 W, no left-out tile is in any run and the admission rule refuses each
     of them, and after a lock it refuses a tile at or above the lock's estimate but not one below;
  5. the preflight override keeps every run_hpl.py refusal except the two that assume a compiled heater beside its kernel;
  6. the protocol is the registered order: run_hpl.py's own load_protocol (through run_e165's chain) yields the 171 BURST runs in predictions-e165.json's
     order, idx for idx and label for label, each pass opening with the three zeros anchors; the dry twin is its first two passes; the stop tests run
     fp32.anchor7_zeros with one stop lowered;
  7. the queue's smoke check of the C log on made-up records (E160's step 8, E165's queue): a sound log passes; a missing C record, a C that is not
     +0, another kernel, the poison off, and a DMA time that would overrun the budget each fail.
"""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e165_common as C  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e165.json")))
fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


# 1
bad = C.check_frozen()
M = C.manifest()
tb = [C.check_tile(C.ROOT, t) for t in M.values()]
ok(not bad and not any(tb) and len(M) == 61, f"frozen inputs, Q139(k)'s three files and 61 tiles as committed ({len(M)} tiles, {sum(1 for x in tb if x)} bad; {bad})")

# 2
with tempfile.TemporaryDirectory() as td:
    t = M["fp16.randn_x8"]
    dst = os.path.join(td, C.POOL_REL, t["file"])
    os.makedirs(os.path.dirname(dst))
    b = bytearray(open(os.path.join(C.ROOT, C.POOL_REL, t["file"]), "rb").read())
    b[1500] ^= 0x01
    open(dst, "wb").write(bytes(b))
    w1 = C.check_tile(td, t)
    open(dst, "wb").write(bytes(b[:2047]))
    w2 = C.check_tile(td, t)
    ok(w1 is not None and "sha256 whole" in w1 and w2 is not None and "2047 bytes" in w2, f"a changed byte and a short file are refused ({w1[:60]}...; {w2})")

# 3
Q = json.load(open(os.path.join(C.ROOT, C.PRED_REL)))
A = json.load(open(os.path.join(C.ROOT, C.ADM_REL)))
same = all(P["tiles"][n]["models"]["M9"]["a2_q140l"] == Q["tiles"][n]["M9"]["a2_q140l"] for n in Q["tiles"])
same = same and all(P["tiles"][n]["models"][m][k] == Q["tiles"][n][m][k] for n in Q["tiles"] for m in ("M8", "M7", "M6") for k in P["tiles"][n]["models"][m])
same = same and all(P["tiles"][n]["models"]["M9"]["D600_a3_footing_w"] == Q["tiles"][n]["M9"]["D600_a3_footing_w"] for n in Q["tiles"])
ng = sum(1 for t in P["tiles"].values() if t["group"] == "governed")
gq = sum(1 for n in Q["tiles"] if Q["tiles"][n]["M9"]["a2_q140l"]["group"] == "governed")
lo = sorted(n for n, t in P["tiles"].items() if t["left_out"])
run = [n for n, t in P["tiles"].items() if not t["left_out"]]
ok(same and len(P["tiles"]) == 61 and ng == gq == 18 and lo == sorted(A["left_out"]) and len(lo) == 6 and all(P["tiles"][n]["group"] == "governed" for n in lo)
   and sum(1 for n in run if P["tiles"][n]["group"] == "governed") == 12 and len(run) == 55 and P["n_scored"] == 52 and P["n_governed"] == 12 and P["n_pinned"] == 40,
   f"predictions-e165.json = Q140(x)'s numbers for 61 tiles x 4 models; {ng} governed, {61 - ng} pinned in the frozen file; left out {lo}; run {len(run)}, "
   f"scored {P['n_scored']} ({P['n_governed']} governed, {P['n_pinned']} pinned)")

# 4
import run_e165 as RN  # noqa: E402
proto = json.load(open(os.path.join(HERE, "protocol.json")))
p2 = copy.deepcopy(proto)
p2["safety"] = {"die_c": 76, "board_w": 85, "board_samples": 3}
w = RN.preflight(p2, "/nonexistent")
ok(w is not None and "lacks abs_stop_c" in w and "lacks board_cap_w" in w, f"preflight refuses other stop keys: {w[:110]}")
p3 = copy.deepcopy(proto)
p3["safety"]["board_cap_w"] = 93
p3["tools"]["heater"] = "build/sparsity_t2/host/sparsity_host"
p3["blocks"][1]["runs"].append({"type": "fp32", "values": "file:tools/claims-v3/kinds/blind7/tiles/fp32/fp32.uniform_pm1.bin", "label": "b7-fp32.uniform_pm1"})
w = RN.preflight(p3, "/nonexistent")
ok(w is not None and "above 85 W" in w and "tools.heater" in w and "fp32.uniform_pm1, left out by name" in w,
   f"preflight refuses a 93 W board stop, E80's own heater and a left-out tile: {w[:220]}")
w = RN.preflight(proto, "/nonexistent")
ok(w is not None and "sha256 None" in w and C.CC_HOST_REL in w, f"preflight refuses missing binaries: {w[:150]}")
ok(proto["safety"] == {"abs_stop_c": 76, "board_cap_w": 85, "cap_consecutive": 3} and proto["limit_p800_w"] == 82.0 and proto["peak_lock_w"] == 82.0,
   f"the protocol's stops {proto['safety']}, admission limit {proto['limit_p800_w']} W and lock {proto['peak_lock_w']} W")
labs = [r["label"] for bl in proto["blocks"] for r in bl["runs"]]
est = max(proto["admission"][l]["fixed_p800_w"] for l in labs)
dl = {C.label_of(n) for n in lo}
ok(all(l in proto["admission"] for l in labs) and est <= 82.0 and not (dl & set(labs)) and not (dl & set(proto["admission"])),
   f"every label in the admission table, highest planned estimate {est} W <= 82 W, no left-out label in a run or in the table")
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e105"))
import run_e105 as RE  # noqa: E402
padm = copy.deepcopy(proto)
for n in lo:   # what the rule would say if a left-out tile were put back in the table with its frozen estimate
    padm["admission"][C.label_of(n)] = {"c_ref_w": 0.0, "fixed_p800_w": P["tiles"][n]["admission_estimate_w"]}
with tempfile.TemporaryDirectory() as td:
    adm = RE.Admission(padm, os.path.join(td, "s1"))
    why = {n: adm.why_not(C.label_of(n))[0] for n in lo}
    why_none = RE.Admission(proto, os.path.join(td, "s2")).why_not(C.label_of(lo[0]))[0]
    why_ok = adm.why_not("b7-fp16.randn_x8")[0]
    adm.state["lock_est"] = 80.5
    why_lock = adm.why_not("b7-fp16.randn_x8")[0], adm.why_not("b7-fp16.sorted_k")[0]
ok(all(v and "> 82.0 W" in v for v in why.values()) and why_none is not None and why_ok is None and why_lock[0] and why_lock[1] is None,
   f"admission refuses the left-out tiles at their frozen estimates ({why}) and, absent from the table, refuses them anyway ({why_none}); admits "
   f"fp16.randn_x8 at 81.65 W; after a lock at 80.5 W refuses it ({why_lock[0]}) but not fp16.sorted_k (76.92 W)")
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
raw, runs, badp = RN.H.load_protocol(os.path.join(HERE, "protocol.json"), only=None)
br = [r for r in runs if r.block == "BURST"]
o = P["order"]
match = len(br) == len(o) == 171 and all(r.idx == x["idx"] and r.label == x["label"] and r.rep == 1 for r, x in zip(br, o))
heads = all([C.name_of(br[k * 57 + j].label) for j in range(3)] and all(C.name_of(br[k * 57 + j].label) in C.ZEROS_ANCHORS for j in range(3)) for k in range(3))
rest_ok = all(C.name_of(br[k * 57 + j].label) not in C.ZEROS_ANCHORS for k in range(3) for j in range(3, 57))
per_pass_sets = [sorted(r.label for r in br[k * 57:(k + 1) * 57]) for k in range(3)]
rawd, runsd, badd = RN.H.load_protocol(os.path.join(HERE, "protocol-dry.json"), only=None)
brd = [r for r in runsd if r.block == "BURST"]
ok(match and heads and rest_ok and per_pass_sets[0] == per_pass_sets[1] == per_pass_sets[2] and not badp and len(brd) == 114
   and all(a.label == b.label for a, b in zip(brd, br[:114])),
   f"run_hpl's load_protocol yields the registered order: {len(br)} BURST runs, idx and label as predictions-e165.json's, rep 1; each pass opens with the "
   f"three zeros anchors and holds the same 57 labels; no check refuses ({badp}); the dry twin is its first {len(brd)} runs")
st_ok = True
for kind, key, val in (("board", "board_cap_w", 30), ("die", "abs_stop_c", 30)):
    q = json.load(open(os.path.join(HERE, f"protocol-stoptest-{kind}.json")))
    st_ok = st_ok and q["safety"][key] == val and q["blocks"][0]["runs"][0]["label"] == "b7-fp32.anchor7_zeros" and len(q["blocks"]) == 1
ok(st_ok, "the stop tests: one 6 s burst of fp32.anchor7_zeros with board_cap_w 30 W, or abs_stop_c 30 C, the rest of the protocol unchanged")

# 7
import queue_e165 as QE  # noqa: E402


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

print("\nALL PASS" if not fails else f"\n{len(fails)} FAILED")
sys.exit(1 if fails else 0)
