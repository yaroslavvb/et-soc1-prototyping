#!/usr/bin/env python3
"""E183's dated note M1: the self-test of arm_m1_read_e183.py, on synthetic sessions in the box's layout made by the kit's own generator
(fake_card_e183_v2.py, unchanged), reduced by reduce_e183_v2.py and scored by score_e183.py (both unchanged). Never a card, never a real
run's data. Python's standard modules only.

    /usr/bin/python3 -B tools/claims-v3/e183/selftest_arm_m1_e183.py <scratch dir outside the repository>
                                                                  # prints SELFTEST-ARM-M1-E183 <k> of <n> PASS

THE WORLDS (each FULL unless said; the noise a quarter of sigma_q, as the kit's own self-test, so every word asserted below is certain):
  W3  the trains exactly v3's centrals: b = v3's T1 / 7 a result bit, c = 0 (v3's six trains are b dR + c dO to 1e-6 W);
  W4  every train set to v4's central (--override, the kit's option);
  WC  W3 with T3 cut to 12 processes (6 units: NOT SCORED), so b comes from T1 alone;
  WS  W3 on the SHORT plan (T3, T1, T4, T2: T5 and T6 not run).
THE CHECKS:
  F*   the reader's measured side equals the scorer's (every train's mean and interval, b, c, E183-MECH): the reader runs with --scored;
  P*   every placement word the reader prints (each train, b, c, x, both j's; each arm) equals this test's own placement of the model's
       figure against the SCORER's interval, recomputed here from scored-e183.json and the committed json, not by the reader's code;
  K*   the certain words: in W3 E183-MECH reads RESULT, v3's word reads "the same word" and v4's "a different word"; v4's T1, T3 and T6
       read below and its T2 and T4 above; v4's b below and c above; v3's T2 and T4 have no sign to compare; in W4 E183-MECH reads BOTH,
       v4 "the same word", v3 "a different word", v3's T1, T3, T6 above and T2, T4 below, v3's c below;
  N*   WC: T3 is not read, and the model's b is its T1 over 7; WS: T5 and T6 not read, x not read;
  R1   a copy of the committed json with one digit changed is refused (exit 2); R2 a scorer's file whose T1 mean moved by 1e-6 W is
       refused (exit 3).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e183_common as E  # noqa: E402

PY = "/usr/bin/python3"
BASE_MS = 1_800_000_000_000
T0 = BASE_MS // 1000 - 600
M1 = json.load(open(os.path.join(HERE, "m1-october-forecast-model-e183.json")))
TRAINS = ("T1", "T2", "T3", "T4", "T5", "T6")
results = []


def check(name, ok, what):
    results.append((name, bool(ok)))
    print(f"{name}: {'PASS' if ok else 'FAIL'} - {what}")


def run(args, cwd=TOP):
    return subprocess.run([PY, "-B"] + args, capture_output=True, text=True, cwd=cwd)


def session(tmp, name, args):
    d = os.path.join(tmp, name)
    shutil.rmtree(d, ignore_errors=True)
    raw = os.path.join(d, "raw")
    r = run([os.path.join(HERE, "fake_card_e183_v2.py"), raw] + args)
    assert r.returncode == 0, (name, r.stderr[-600:])
    red = os.path.join(d, "reduced-e183.json")
    r = run([os.path.join(HERE, "reduce_e183_v2.py"), "--raw", raw, "--t0", str(T0), "--out", red])
    assert r.returncode == 0, (name, r.stderr[-600:])
    r = run([os.path.join(HERE, "score_e183.py"), "--reduced", red, "--out", os.path.join(d, "scored-e183")])
    assert r.returncode == 0, (name, r.stderr[-600:])
    r = run([os.path.join(HERE, "arm_m1_read_e183.py"), "--reduced", red, "--scored", os.path.join(d, "scored-e183.json"),
             "--out", os.path.join(d, "arm-m1-e183")])
    assert r.returncode == 0, (name, r.stdout[-600:], r.stderr[-600:])
    return (json.load(open(os.path.join(d, "scored-e183.json"))), json.load(open(os.path.join(d, "arm-m1-e183.json"))),
            open(os.path.join(d, "arm-m1-e183.txt")).read(), red)


def place(m, iv):
    if iv.get("lo") is None:
        return None
    return "inside" if iv["lo"] <= m <= iv["hi"] else ("above" if m > iv["hi"] else "below")


def own_placements(sc, v):
    """this test's own placements of arm v against the scorer's intervals (not the reader's code)"""
    mt = {t: M1["trains"][t][v]["aifoundry3"]["central_W"] for t in TRAINS}
    got = {t: place(mt[t], sc["trains"][t]) for t in TRAINS}
    hb, hc = sc["rules"]["E183-B"]["from"], sc["rules"]["E183-C"]["from"]
    if hb:
        got["b"] = place(sum(mt[t] for t in hb) / (7 * len(hb)), sc["rules"]["E183-B"]["b"])
    if hc:
        got["c"] = place(sum(mt[t] for t in hc) / (7 * len(hc)), sc["rules"]["E183-C"]["c"])
    xs = sc["rules"]["E183-X"]
    if xs["from"]:
        mx = mt["T6"] - 6 * sum(mt[t] for t in hb) / (7 * len(hb)) + sum(mt[t] for t in hc) / (7 * len(hc))
        got["x"] = place(mx, xs["statistic"])
    got["j_T3_minus_T1"] = place(mt["T3"] - mt["T1"], sc["rules"]["E183-J"]["T3_minus_T1"])
    got["j_T4_minus_T2"] = place(mt["T4"] - mt["T2"], sc["rules"]["E183-J"]["T4_minus_T2"])
    return got


def reader_placements(arm, v):
    A = arm["arms"][v]
    got = {t: A["trains"][t].get("model_reads") for t in TRAINS}
    for q in ("b", "c", "x", "j_T3_minus_T1", "j_T4_minus_T2"):
        got[q] = A["prices"][q].get("model_reads")
    return got


def main():
    tmp = sys.argv[1] if len(sys.argv) > 1 else None
    if not tmp or os.path.abspath(tmp).startswith(TOP):
        print("usage: selftest_arm_m1_e183.py <scratch dir outside the repository>")
        sys.exit(2)
    os.makedirs(tmp, exist_ok=True)
    q4 = f"{E.plan()['sigma_q_w'] / 4:.6f}"
    b3 = M1["trains"]["T1"]["v3"]["aifoundry3"]["central_W"] / 7
    # v3's six trains are b dR + c dO with c = 0, to the json's rounding
    dev = max(abs(M1["trains"][t]["v3"]["aifoundry3"]["central_W"] - (b3 * M1["trains"][t]["dR"])) for t in TRAINS)
    check("W3-form", dev < 2e-6, f"v3's six trains are b dR with b = {b3:.7f} W a result bit, c = 0: largest departure {dev:.1e} W")
    ov4 = []
    for t in TRAINS:
        ov4 += ["--override", f"{t}:{M1['trains'][t]['v4']['aifoundry3']['central_W']}"]
    worlds = {
        "W3": ["--b", f"{b3:.10f}", "--c", "0", "--sigma", q4, "--seed", "41"],
        "W4": ["--b", "0", "--c", "0", "--sigma", q4, "--seed", "42"] + ov4,
        "WC": ["--b", f"{b3:.10f}", "--c", "0", "--sigma", q4, "--seed", "43", "--cut", "T3:12"],
        "WS": ["--b", f"{b3:.10f}", "--c", "0", "--sigma", q4, "--seed", "44", "--plan", "SHORT"],
    }
    out = {}
    for name, args in worlds.items():
        sc, arm, txt, red = session(tmp, name, args)
        out[name] = (sc, arm, txt, red)
        check(f"F-{name}", arm["inputs"]["scored_cross_check"] == "equal" and arm["measured"]["E183-MECH"]["word"] == sc["rules"]["E183-MECH"]["verdict"],
              f"the reader's trains, b, c and MECH equal the scorer's (MECH {sc['rules']['E183-MECH']['verdict']}); "
              f"trains scored {sorted(t for t in TRAINS if sc['trains'][t].get('lo') is not None)}")
        for v in ("v3", "v4"):
            own, rd = own_placements(sc, v), reader_placements(arm, v)
            keys = sorted(set(own) | set(rd))
            agree = all((own.get(k) is None and rd.get(k) is None) or own.get(k) == rd.get(k) for k in keys)
            check(f"P-{name}-{v}", agree, "every placement: " + ", ".join(f"{k} {rd.get(k) or 'not read'}" for k in keys))
    # the certain words
    sc, arm, txt, _ = out["W3"]
    A3, A4 = arm["arms"]["v3"], arm["arms"]["v4"]
    ok = (sc["rules"]["E183-MECH"]["verdict"] == "RESULT" and A3["word"]["reads"] == "the same word" and A4["word"]["reads"] == "a different word"
          and [A4["trains"][t]["model_reads"] for t in ("T1", "T3", "T6")] == ["below"] * 3
          and [A4["trains"][t]["model_reads"] for t in ("T2", "T4")] == ["above"] * 2
          and A4["prices"]["b"]["model_reads"] == "below" and A4["prices"]["c"]["model_reads"] == "above"
          and A3["trains"]["T2"]["sign"] == A3["trains"]["T4"]["sign"] == "no sign to compare")
    check("K-W3", ok, f"MECH {sc['rules']['E183-MECH']['verdict']}; v3 {A3['word']['reads']}, v4 {A4['word']['reads']}; v4 T1/T3/T6 "
          f"{[A4['trains'][t]['model_reads'] for t in ('T1', 'T3', 'T6')]}, T2/T4 {[A4['trains'][t]['model_reads'] for t in ('T2', 'T4')]}, "
          f"b {A4['prices']['b']['model_reads']}, c {A4['prices']['c']['model_reads']}; v3 T2 sign '{A3['trains']['T2']['sign']}'")
    sc, arm, txt, _ = out["W4"]
    A3, A4 = arm["arms"]["v3"], arm["arms"]["v4"]
    ok = (sc["rules"]["E183-MECH"]["verdict"] == "BOTH" and A4["word"]["reads"] == "the same word" and A3["word"]["reads"] == "a different word"
          and [A3["trains"][t]["model_reads"] for t in ("T1", "T3", "T6")] == ["above"] * 3
          and [A3["trains"][t]["model_reads"] for t in ("T2", "T4")] == ["below"] * 2 and A3["prices"]["c"]["model_reads"] == "below")
    check("K-W4", ok, f"MECH {sc['rules']['E183-MECH']['verdict']}; v4 {A4['word']['reads']}, v3 {A3['word']['reads']}; v3 T1/T3/T6 "
          f"{[A3['trains'][t]['model_reads'] for t in ('T1', 'T3', 'T6')]}, T2/T4 {[A3['trains'][t]['model_reads'] for t in ('T2', 'T4')]}, "
          f"c {A3['prices']['c']['model_reads']}")
    sc, arm, txt, _ = out["WC"]
    A3 = arm["arms"]["v3"]
    mb = A3["prices"]["b"].get("model")
    ok = ("read" in A3["trains"]["T3"] and A3["prices"]["b"]["from"] == ["T1"]
          and abs(mb - M1["trains"]["T1"]["v3"]["aifoundry3"]["central_W"] / 7) < 1e-15 and sc["trains"]["T3"].get("lo") is None)
    check("N-WC", ok, f"T3 {A3['trains']['T3'].get('read')}; the model's b from {A3['prices']['b']['from']} = {mb:.7f} (its T1 / 7)")
    sc, arm, txt, _ = out["WS"]
    A3 = arm["arms"]["v3"]
    ok = all("read" in A3["trains"][t] and "model_reads" not in A3["trains"][t] for t in ("T5", "T6")) and "read" in A3["prices"]["x"] \
        and all("model_reads" in A3["trains"][t] for t in ("T1", "T2", "T3", "T4"))
    check("N-WS", ok, f"T5 {A3['trains']['T5'].get('read')}; T6 {A3['trains']['T6'].get('read')}; x {A3['prices']['x'].get('read')}")
    # refusals
    sc, arm, txt, red = out["W3"]
    bad = os.path.join(tmp, "m1-bad.json")
    s = open(os.path.join(HERE, "m1-october-forecast-model-e183.json")).read()
    i = s.index("0.066475")
    open(bad, "w").write(s[:i] + "0.066476" + s[i + 8:])
    r = run([os.path.join(HERE, "arm_m1_read_e183.py"), "--reduced", red, "--m1", bad, "--out", os.path.join(tmp, "r1")])
    check("R1", r.returncode == 2 and "REFUSED" in r.stdout, f"a json with one digit changed: rc {r.returncode}, {' '.join(r.stdout.split())[:170]}")
    sc2 = json.loads(json.dumps(sc))
    sc2["trains"]["T1"]["mean"] += 1e-6
    p2 = os.path.join(tmp, "scored-bad.json")
    json.dump(sc2, open(p2, "w"))
    r = run([os.path.join(HERE, "arm_m1_read_e183.py"), "--reduced", red, "--scored", p2, "--out", os.path.join(tmp, "r2")])
    check("R2", r.returncode == 3 and "disagree" in r.stdout, f"a scorer's file with T1 moved 1e-6 W: rc {r.returncode}, {' '.join(r.stdout.split())[:170]}")
    print("--- the reader's text in W3, for the record:")
    print(out["W3"][2].rstrip())
    k = sum(1 for _, o in results if o)
    print(f"SELFTEST-ARM-M1-E183 {k} of {len(results)} {'PASS' if k == len(results) else 'FAIL'}")
    sys.exit(0 if k == len(results) else 1)


if __name__ == "__main__":
    main()
