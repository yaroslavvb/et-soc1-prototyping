#!/usr/bin/env python3
"""E166 (Q141(h)): the smoke gate, E154's smoke_gate_e154.py with E166's four hold tiles. Reads the smoke block (block_e166.sh 16601 --smoke: the smoke plan, then the five stop-path tests on live
samples) and exits 0 only if every check below passes; session_e166.sh runs the measured pass only then. Standard library only (it runs on the
box). It opens no device: it reads the block's files.

  1. block.json: status ok;
  2. the five stop tests (the "stoptest" mark): the launch gate (no launch), the hold's die and board lines (the hold ends, no launch), the
     in-launch board line (the launch in flight ends early, at least one launch) and the session line (exit 6) - every one passed;
  3. each of the four hold tiles (K_S, K_Q, K_L, K_OL) ran in the smoke: a "hold" mark that ended on time with at least one
     launch (K_S: two, its duty pattern), and launch records in runs.jsonl, every record ok with no tensor error on 1,024 minions;
  4. a sound C log (Q139(k)): every host record names the registered C-logging host and kernel by sha256; at least one C record for every launch
     record in runs.jsonl; every C record poisoned, with no mask and no stream, on 1,024 participants;
  5. the 34 raw codes (command 74 group 0, E144's probe): at least 90% of the telemetry lines carry a status-0, fault-free reading of 34 sensors,
     whose 34-sensor mean (E97's conversion of the raw codes) lies in [35, 75] C and within 3 C of the firmware's minshire[0]; the minion clock
     reads 600 MHz in every line that carries it;
  6. the block's two config reads: TDP 0 W, threshold 65 C, 600 MHz (the card as E144 and E153 found it; nothing is set).

    python3 tools/claims-v3/e166/smoke_gate_e166.py <smoke pass dir>    # prints one JSON object; exit 0 = GO, 1 = NO-GO
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import sys

HOST_SHA = "99ed75fbcad323b4a640377710d1f9c5428224401e988400177e9c0749e911a4"     # build/ccheck/b/host/sparsity_host on aifoundry3
KERNEL_SHA = "d521e43248d00b4da455ada7020741f39b8940e52bbbce05380beccedcd17d19"   # build/sparsity/kernel/sparsity.elf (E78's, E144's)
HOLDS = {"K_S": "fp32.real_smol_softmax_v_causal", "K_Q": "int8.real_qwen_w8a8_v",
         "K_L": "int8.b_line_zero_ff", "K_OL": "fp32.a_onebit_b5_third"}
G_TS, H_TS, CAL5 = 57400, 249400, 4096


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def lines(p):
    op = gzip.open if p.endswith(".gz") else open
    out = []
    with op(p, "rt") as f:
        for x in f:
            x = x.strip()
            if x.startswith("{"):
                try:
                    out.append(json.loads(x))
                except ValueError:
                    pass
    return out


def main():
    d = sys.argv[1]
    probs, info = [], {}

    def need(ok, msg):
        if not ok:
            probs.append(msg)

    try:
        bj = json.load(open(os.path.join(d, "block.json")))
    except (OSError, ValueError) as e:
        bj = {}
        probs.append(f"block.json unreadable: {e}")
    need(bj.get("status") == "ok", f"block.json status {bj.get('status')!r}")
    marks = lines(os.path.join(d, "marks.jsonl")) if os.path.exists(os.path.join(d, "marks.jsonl")) else []
    st = [m for m in marks if m.get("kind") == "stoptest"]
    need(len(st) == 1 and st[0].get("all_pass") is True, f"stop tests: {st[-1].get('results') if st else 'no stoptest mark'}")
    if st:
        info["stoptests"] = st[0].get("results")
    runs = lines(os.path.join(d, "runs.jsonl")) if os.path.exists(os.path.join(d, "runs.jsonl")) else []
    info["launch_records"] = len(runs)
    for name, item in HOLDS.items():
        hm = [m for m in marks if m.get("kind") == "hold" and m.get("name") == name]
        need(len(hm) == 1, f"{name}: {len(hm)} hold marks")
        if hm:
            need(hm[0].get("why_end") == "time", f"{name}: ended {hm[0].get('why_end')!r}")
            need((hm[0].get("launches") or 0) >= (2 if name == "K_S" else 1), f"{name}: {hm[0].get('launches')} launches")
        rr = [r for r in runs if r.get("block") == name]
        need(len(rr) >= 1 and all(r.get("item") == item for r in rr), f"{name}: {len(rr)} launch records for {item}")
        bad = [r for r in rr if not (r.get("ok") is True and r.get("tensor_errors") == 0 and r.get("minions") == 1024)]
        need(not bad, f"{name}: {len(bad)} launch records not ok / with tensor errors / not 1,024 minions")
    cl = os.path.join(d, "c-log.jsonl")
    clog = lines(cl) if os.path.exists(cl) else []
    hosts = [x for x in clog if x.get("kind") == "host"]
    crec = [x for x in clog if x.get("kind") == "c"]
    info["c_log"] = {"host_records": len(hosts), "c_records": len(crec), "launch_records": len(runs)}
    need(len(hosts) >= 1, "no host record in the C log")
    need(all(h.get("host_sha256") == HOST_SHA and h.get("kernel_sha256") == KERNEL_SHA for h in hosts),
         "a host record names another host or kernel: " + json.dumps(sorted({(h.get("host_sha256"), h.get("kernel_sha256")) for h in hosts}))[:300])
    need(len(crec) >= len(runs) and len(runs) > 0, f"{len(crec)} C records for {len(runs)} launch records")
    badc = [x for x in crec if not (x.get("poison") is True and x.get("use_mask") == 0 and x.get("b_stream") == 0
                                    and x.get("participants") == 1024)]
    need(not badc, f"{len(badc)} C records not poisoned / masked / streamed / not 1,024 participants")
    tel = lines(os.path.join(d, "telemetry.jsonl.gz")) if os.path.exists(os.path.join(d, "telemetry.jsonl.gz")) else []
    good, near, mhz_bad, means = 0, 0, 0, []
    for r in tel:
        pv = r.get("pvt") or {}
        cs = pv.get("c") or []
        if pv.get("st") == 0 and not pv.get("f") and len(cs) == 34:
            good += 1
            m = sum(code_to_c(x) for x in cs) / 34.0
            means.append(m)
            try:
                fw = float(r["temp_c"]["minshire"][0])
                near += 1 if (35.0 <= m <= 75.0 and abs(m - fw) <= 3.0) else 0
            except (KeyError, IndexError, TypeError, ValueError):
                pass
        mz = (r.get("mhz") or {}).get("minion")
        if mz is not None and mz != 600:
            mhz_bad += 1
    info["telemetry"] = {"lines": len(tel), "pvt_34_ok": good, "mean34_near_firmware": near, "mhz_not_600": mhz_bad,
                         "mean34_range_C": [round(min(means), 3), round(max(means), 3)] if means else None}
    need(len(tel) > 0 and good >= 0.9 * len(tel), f"34 raw codes in {good} of {len(tel)} telemetry lines")
    need(good > 0 and near >= 0.9 * good, f"the 34-sensor mean in [35, 75] C and within 3 C of minshire[0] in {near} of {good}")
    need(mhz_bad == 0, f"{mhz_bad} telemetry lines off 600 MHz")
    for nm in ("config_start.json", "config_end.json"):
        try:
            cfg = json.loads(open(os.path.join(d, nm)).read().strip() or "{}")
        except (OSError, ValueError):
            cfg = {}
        info[nm] = cfg
        need(cfg.get("tdp_w") == 0 and cfg.get("temp_threshold_c") == 65 and cfg.get("minion_mhz") == 600, f"{nm}: {cfg}")
    out = {"gate": "GO" if not probs else "NO-GO", "dir": d, "problems": probs, **info}
    print(json.dumps(out))
    sys.exit(0 if not probs else 1)


if __name__ == "__main__":
    main()
