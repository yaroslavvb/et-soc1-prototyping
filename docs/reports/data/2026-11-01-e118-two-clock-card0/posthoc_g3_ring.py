#!/usr/bin/env python3
"""E118, post hoc, after verification (Sun 1 Nov 2026): G1's and G3's ring halves re-read with the lab's full ring
reader, tools/claims-v3/hpl/sptrace_full.py (E64 amendment A1), which steps over the service processor's binary
power-status records.

score_e118.py (frozen) reads the three dumps with tools/claims-v3/dv2/sptrace_events.py, whose walk from the header to
the write offset stops at the first entry that is not a printable string. On this card the governor writes a 16-byte
power-status record right after each `Power throttle up` line, so that walk saw the first throttle-up after the restore
and nothing after it (sptrace_full.py's docstring names the same defect on the 1.3.1 cards). This script re-reads the
dumps, lists every entry new between consecutive dumps (operating points by frequency only, as D4 keeps the vmin-LUT),
checks the release against the return burst's telemetry, and with --apply writes the re-read ring halves into
verdicts.json, keeping the scorer's own reading under `as_scored`. It writes posthoc_g3_ring.json and .txt.

    python3 docs/reports/data/2026-11-01-e118-two-clock-card0/posthoc_g3_ring.py [--apply]
"""
import gzip
import hashlib
import importlib.util
import json
import os
import struct
import sys

H = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(H, "..", "..", "..", ".."))
S = os.path.join(H, "session")
DUMPS = ["before-pin", "after-pinned", "after-back"]
THROTTLE = {0: "POWER_IDLE", 1: "POWER_UP", 2: "POWER_DOWN", 3: "POWER_SAFE"}   # device_mgmt_api_spec.h (sptrace_full)


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(R, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


full = load("sptrace_full", "tools/claims-v3/hpl/sptrace_full.py")
spe = load("sptrace_events", "tools/claims-v3/dv2/sptrace_events.py")


def public(e, t0=None):
    """An entry as published here: no operating-point voltages, no raw text but the governor's lines."""
    d = {"kind": e["kind"], "sp_ts": e["ts"]}
    if t0 is not None:
        d["t_rel_s"] = round((e["ts"] - t0) / 1e6, 6)          # SP timestamps are microseconds (see the burst check)
    if e["kind"] in spe.GOVERNOR:
        d["text"] = e["text"]
        for k in ("pwr_mw", "tdp_mw", "T", "threshold"):
            if k in e:
                d[k] = e[k]
    elif e["kind"] == "new_op":
        d["mhz"] = e["mhz"]
    elif e["kind"] == "pstat":
        d.update({k: e[k] for k in ("power_w", "throttle_state", "power_state", "temp_c", "mhz")})
        d["throttle_state_name"] = THROTTLE.get(e["throttle_state"], "build-specific")
    return d


def delta(ea, eb):
    newest = max(ea, key=lambda e: (e["ts"], e["off"]))
    covered = any(e["ts"] == newest["ts"] and e["kind"] == newest["kind"] and e.get("text") == newest.get("text")
                  for e in eb)
    new = full.since(ea, eb)
    kinds = {}
    for e in new:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    return covered, new, kinds


def old_walk(buf):
    """Where sptrace_events.ring_entries()'s walk from the header stops, and why."""
    wr = struct.unpack_from("<I", buf, 12)[0]
    size = min(struct.unpack_from("<I", buf, 16)[0] or len(buf), len(buf))
    off, n = spe.HEADER, 0
    while off < min(wr, size):
        e = spe._entry_at(buf, off, size)
        if e is None:
            break
        n += 1
        off += 16 + e[1]
    stop = {"walked_entries": n, "stopped_at_offset": off, "write_offset": wr}
    if off < wr:
        ts, ln = struct.unpack_from("<QI", buf, off)
        stop.update(stopped_on={"sp_ts": ts, "length": ln, "record_type": struct.unpack_from("<H", buf, off + 14)[0],
                                "printable_string": False})
    return stop


def main(argv):
    raw = {d: open(os.path.join(S, f"ring-{d}.bin"), "rb").read() for d in DUMPS}
    ents = {d: full.scan(raw[d]) for d in DUMPS}
    out = {"experiment": "E118", "post_hoc": "after verification, Sun 1 Nov 2026; nothing re-run",
           "reader": "tools/claims-v3/hpl/sptrace_full.py scan() (E64 amendment A1)",
           "registered_reader": "tools/claims-v3/dv2/sptrace_events.py (score_e118.py, frozen)",
           "dumps": {d: {"sha256": hashlib.sha256(raw[d]).hexdigest(), "bytes": len(raw[d]),
                         "write_offset": struct.unpack_from("<I", raw[d], 12)[0], "entries": len(ents[d])}
                     for d in DUMPS}}
    txt = ["E118 post hoc: the SP ring halves of G1 and G3 re-read with " + out["reader"]]
    for d in DUMPS:
        x = out["dumps"][d]
        txt.append(f"  ring-{d}.bin  sha256 {x['sha256'][:16]}...  write offset {x['write_offset']}  {x['entries']} entries")

    # G1: before the pin -> after the pinned passes
    c1, n1, k1 = delta(ents["before-pin"], ents["after-pinned"])
    same = raw["before-pin"] == raw["after-pinned"]
    g1 = {"measured": c1, "covered": c1, "new_entries": len(n1), "kinds": k1,
          "power_up": [e["text"] for e in n1 if e["kind"] == "power_up"],
          "governor_lines": [e["text"] for e in n1 if e["kind"] in spe.GOVERNOR], "identical_bytes": same}
    g1_half = "UNMEASURED" if not c1 else ("PASS" if not g1["power_up"] else "FAIL")
    out["G1_before_pin_to_after_pinned"] = dict(g1, log_half=g1_half)
    txt.append(f"G1 before-pin -> after-pinned: {len(n1)} new entries (covered {c1}; byte-identical files {same}) "
               f"-> log half {g1_half}")

    # G3: after the pinned passes -> after the return burst
    c3, n3, k3 = delta(ents["after-pinned"], ents["after-back"])
    t0 = n3[0]["ts"] if n3 else None
    g3 = {"measured": c3, "covered": c3, "new_entries": len(n3), "kinds": k3,
          "power_up": [e["text"] for e in n3 if e["kind"] == "power_up"],
          "governor_lines": [e["text"] for e in n3 if e["kind"] in spe.GOVERNOR],
          "new_op_mhz": [e["mhz"] for e in n3 if e["kind"] == "new_op"],
          "entries": [public(e, t0) for e in n3]}
    ups = [e for e in n3 if e["kind"] == "power_up"]
    ops = [e for e in n3 if e["kind"] == "new_op"]
    if len(ups) >= 2:
        g3["power_up_spacing_s"] = round((ups[1]["ts"] - ups[0]["ts"]) / 1e6, 6)
    if len(ops) >= 3:
        g3["new_op_700_to_800_s"] = round((ops[1]["ts"] - ops[0]["ts"]) / 1e6, 6)
        g3["new_op_800_to_600_s"] = round((ops[2]["ts"] - ops[1]["ts"]) / 1e6, 6)
        g3["first_power_up_to_600_s"] = round((ops[2]["ts"] - ups[0]["ts"]) / 1e6, 6)
    g3_half = "UNMEASURED" if not c3 else ("PASS" if len(ups) >= 1 else "FAIL")
    g3["event_half"] = g3_half
    g3["registered_reader_walk"] = old_walk(raw["after-back"])
    out["G3_after_pinned_to_after_back"] = g3
    txt.append(f"G3 after-pinned -> after-back: {len(n3)} new entries (covered {c3}): "
               + ", ".join(f"{k} {v}" for k, v in sorted(k3.items())) + f" -> event half {g3_half} (registered: >= 1)")
    for e in g3["entries"]:
        if e["kind"] == "power_up":
            s = f"Power throttle up, current pwr {e['pwr_mw']} mW, tdp level {e['tdp_mw']} mW"
        elif e["kind"] == "new_op":
            s = f"New OP: {e['mhz']} MHz"
        elif e["kind"] == "pstat":
            s = (f"power-status record: {e['power_w']} W, throttle state {e['throttle_state']} "
                 f"({e['throttle_state_name']}), power state {e['power_state']}, {e['temp_c']} C, target {e['mhz']} MHz")
        else:
            s = e.get("text", e["kind"])
        txt.append(f"  +{e['t_rel_s']:7.3f} s  {s}")
    w = g3["registered_reader_walk"]
    txt.append(f"the registered reader on ring-after-back.bin: walks {w['walked_entries']} entries from the header and stops "
               f"at offset {w['stopped_at_offset']} of {w['write_offset']}"
               + (f" (a {w['stopped_on']['length']}-byte record of type {w['stopped_on']['record_type']}, not a string)"
                  if "stopped_on" in w else ""))

    # every raise to 700 or 800 MHz in the ring before the pin, and the ramps 600 -> 700 -> 800
    pre = ents["before-pin"]
    raises, after_up, at_start, ramps = 0, 0, 0, []
    for i, e in enumerate(pre):
        if e["kind"] == "new_op" and e["mhz"] in (700, 800):
            raises += 1
            back = [x["kind"] for x in pre[max(0, i - 2):i]]
            if "power_up" in back:
                after_up += 1
            elif i <= 1:
                at_start += 1          # the ring's oldest entries: what preceded them was overwritten
    cur = None
    for e in pre:
        if e["kind"] == "new_op":
            if e["mhz"] == 600:
                cur = {"ups": 0, "ops": [600]}
                ramps.append(cur)
            elif cur is not None:
                cur["ops"].append(e["mhz"])
        elif e["kind"] == "power_up" and cur is not None:
            cur["ups"] += 1
    full_ramps = [r for r in ramps if r["ops"][:3] == [600, 700, 800]]
    out["before_pin_pattern"] = {"raises_to_700_or_800": raises, "raises_right_after_a_power_up": after_up,
                                 "raises_at_the_ring_start": at_start,
                                 "complete_ramps_600_700_800": len(full_ramps),
                                 "power_ups_per_complete_ramp": [r["ups"] for r in full_ramps]}
    txt.append(f"before the pin: {raises} raises to 700 or 800 MHz, {after_up} of them right after a Power throttle up "
               f"and {at_start} at the ring's oldest end (what preceded it was overwritten); {len(full_ramps)} complete "
               f"600 -> 700 -> 800 ramps, throttle-ups per ramp {[r['ups'] for r in full_ramps]}")

    # the return burst's telemetry against the SP's timestamps
    tel = [json.loads(l) for l in gzip.open(os.path.join(H, "aifoundry1-c0", "e118back-smoke", "p901",
                                                          "telemetry.jsonl.gz"), "rt") if l.startswith("{")]
    marks = [json.loads(l) for l in open(os.path.join(H, "aifoundry1-c0", "e118back-smoke", "p901", "marks.jsonl"))
             if l.startswith("{")]
    ts0 = min(m["t_start_ms"] for m in marks if m.get("kind") == "run")
    mhz = [(s["t_ms"], s["mhz"]["minion"]) for s in tel]
    f700 = next(t for t, m in mhz if m == 700)
    f800 = next(t for t, m in mhz if m == 800)
    last800 = max(t for t, m in mhz if m == 800)
    back600 = next(t for t, m in mhz if t > last800 and m == 600)
    out["burst_telemetry"] = {"source": "aifoundry1-c0/e118back-smoke/p901 (10 Hz)", "first_run_start_ms": ts0,
                              "first_700_s": round((f700 - ts0) / 1e3, 3), "first_800_s": round((f800 - ts0) / 1e3, 3),
                              "back_to_600_s": round((back600 - ts0) / 1e3, 3),
                              "700_to_800_s": round((f800 - f700) / 1e3, 3),
                              "first_800_to_600_s": round((back600 - f800) / 1e3, 3)}
    b = out["burst_telemetry"]
    txt.append(f"the return burst (10 Hz telemetry, from its first run's start): 700 MHz first at {b['first_700_s']} s, "
               f"800 MHz at {b['first_800_s']} s, 600 MHz again at {b['back_to_600_s']} s; "
               f"700 -> 800 in {b['700_to_800_s']} s and 800 -> 600 in {b['first_800_to_600_s']} s, against the SP's "
               f"{g3.get('new_op_700_to_800_s')} s and {g3.get('new_op_800_to_600_s')} s (so SP ticks are microseconds)")

    vp = os.path.join(H, "verdicts.json")
    v = json.load(open(vp))
    old = {"G1": v["rules"]["G1"]["ring_before_pin_to_after_pinned"],
           "G3": v["rules"]["G3"]["ring_after_pinned_to_after_back"]}
    as_scored = {k: (o["as_scored"] if "as_scored" in o else dict(o)) for k, o in old.items()}
    out["as_scored_by_score_e118"] = as_scored
    txt.append(f"as scored by score_e118.py: G1 {as_scored['G1']['new_entries']} new entries; G3 "
               f"{as_scored['G3']['new_entries']} new entry, power_up {as_scored['G3']['kinds'].get('power_up', 0)}")
    json.dump(out, open(os.path.join(H, "posthoc_g3_ring.json"), "w"), indent=1)
    open(os.path.join(H, "posthoc_g3_ring.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))

    if "--apply" in argv:
        note = ("re-read after verification (Sun 1 Nov 2026) with tools/claims-v3/hpl/sptrace_full.py by "
                "posthoc_g3_ring.py --apply; the registered reader stops at the first binary power-status record")
        keep = ("measured", "covered", "new_entries", "kinds", "power_up", "governor_lines")
        v["rules"]["G1"]["ring_before_pin_to_after_pinned"] = dict(
            {k: g1[k] for k in keep}, identical_bytes=same, reader=out["reader"], note=note, as_scored=as_scored["G1"])
        v["rules"]["G3"]["ring_after_pinned_to_after_back"] = dict(
            {k: g3[k] for k in keep}, new_op_mhz=g3["new_op_mhz"], power_up_spacing_s=g3.get("power_up_spacing_s"),
            reader=out["reader"], note=note, as_scored=as_scored["G3"])
        r1, r3 = v["rules"]["G1"], v["rules"]["G3"]
        r1["log_half"] = g1_half
        r1["verdict"] = "PASS" if r1["clock_half"] == "PASS" and g1_half == "PASS" else (
            "PARTIAL" if r1["clock_half"] == "PASS" else "FAIL")
        r3["event_half"] = g3_half
        r3["verdict"] = "PASS" if r3["restore_and_readback"] == "PASS" and r3["step_half"] == "PASS" and \
            g3_half == "PASS" else ("PARTIAL" if r3["restore_and_readback"] == "PASS" and r3["step_half"] == "PASS"
                                    else "FAIL")
        changed = [k for k in ("G1", "G3") if v["summary"][k] != v["rules"][k]["verdict"]]
        for k in ("G1", "G3"):
            v["summary"][k] = v["rules"][k]["verdict"]
        v["corrections"] = [{
            "date": "2026-11-01", "after": "the Q133 verifier's report (holds with fixes)", "by": "posthoc_g3_ring.py --apply",
            "rules": ["G3", "G1"],
            "what": (f"G3's ring half held {as_scored['G3']['new_entries']} new entry and "
                     f"{as_scored['G3']['kinds'].get('power_up', 0)} Power throttle up; the dump holds {len(n3)} new entries, "
                     f"{len(ups)} of them Power throttle up ({', '.join(str(e['pwr_mw']) for e in ups)} mW against a "
                     f"{ups[0]['tdp_mw'] if ups else '?'} mW TDP level, {g3.get('power_up_spacing_s')} s apart), "
                     f"{len(ops)} operating points ({', '.join(str(e['mhz']) for e in ops)} MHz) and "
                     f"{k3.get('pstat', 0)} binary power-status records. G1's ring half is unchanged "
                     f"({len(n1)} new entries; " + ("its two dumps are byte-identical)." if same else
                                                     "its two dumps differ but hold no new entry).")),
            "why": ("score_e118.py reads the dumps with tools/claims-v3/dv2/sptrace_events.py, whose walk from the header "
                    "to the write offset stops at the first entry that is not a printable string: here the 16-byte "
                    "power-status record the governor writes right after the first throttle-up."),
            "verdicts_changed": changed or "none"}]
        json.dump(v, open(vp, "w"), indent=1)
        print(f"verdicts.json: G1 {v['summary']['G1']}, G3 {v['summary']['G3']}; verdicts changed: {changed or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
