#!/usr/bin/env python3
"""1116-mmsweep: the desk tests of the kit (no device; Python's own modules only). Each case prints PASS or FAIL; the last line
is SELFTEST-MMS <n> of <m> PASS.

    python3 -I -B src/selftest_mms.py <scratch dir>          (dry sessions are written under it; nothing in the kit's folder)

  M1  mms_common's self-check (stop lines, latch rule, counted launch, configs, gates, argv, every schedule's lines and roles)
  M2  mms_ident's self-check (config identity of the three cards, holder reads, host identity, the board's rise, freshness)
  M3  the schedules are make_schedule.py's (MAKE CHECK PASS); M4 the harness file is current (CHECK PASS)
  M5  the device-command audit on the session's files: GO, every send site a READ, no wrapper line
  D1  a short dry session (card 1): smoke, an anchor, a null, a sus3 run and bursts; every device call printed; manifest; the
      reducer against the doubles' law: T an op, the board's lift, the rails undone (the minion rail's share of the lift), a null
      reading near zero under the line rule, J an op = dP x T / minions
  D2  a board stop line tripped by the doubles (governed card): STOP, nothing further starts, it closes (config end, manifest)
  D3  the first config read fails (a collector's collision): one re-run passes and the session runs
  D4  the host names another card: the smoke gate fails, no run starts, rc 16
  D5  the operator's STOP after the second run: nothing further starts, the session closes, rc 0
  D6  card 0 of aifoundry1: the identity gate and read pass for card 0 (ET_DEVICES 0, minion_mv at or above 510)
  D7  the collector on D1's session: COPY-BACK EXACT, the privacy read, the reduction
  D8  the start config read names the other card: the gate, rc 16, and NO closing config read (one config call in all)
  D9  a stale sampler that ignores SIGTERM: no second sampler is started, the session ends, no closing read, the leftover is
      recorded and resolved when the double ends (the card's lock held till then)
  D10 a host that outlives `timeout 10` and ignores SIGTERM: the session ends at once (nothing further starts), no closing read,
      the leftover recorded in queue.json and status.json and resolved when the double ends
  D11 two failed processes in a row (rc not 0, the check of C not ok): the session stops
  D12 the governed card's capped rule: runs the doubles' governor dithers under its cap are flagged capped, the others not;
      `time` runs carry no energy figure; the window view sits after the clock step
  D13 the start config read outlives its bound, deaf to SIGTERM: no SIGKILL (the double ends by itself), no re-run, no launch,
      no closing read, rc 16; the leftover recorded and resolved, the card's lock held till then
  D14 the closing config read outlives its bound, deaf to SIGTERM: the leftover recorded in queue.json and status.json and
      resolved; the double ends by itself
  D15 a holder of another login appears before the closing read: et-who read once more after the sampler stops, NO closing read
  D16 aifoundry2: a holder of another login appears before a run that is not an anchor: the session stops before that run (et-who
      before every run on every card), no closing read
  D17 the box lock handed over: a child given the held descriptor holds it (one open file), a fresh opener is refused, a
      descriptor of another file is refused, and the lock is free once the holder lets go
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import mms_common as C  # noqa: E402
import mms_ident as N  # noqa: E402

PY = [sys.executable, "-B"]


def dry(scratch, name, card, sess, *extra, scale="0.02", timeout=900):
    out = os.path.join(scratch, name)
    os.makedirs(out, exist_ok=True)
    r = subprocess.run(PY + [os.path.join(HERE, "run_mms.py"), "session", "--dry", "--scale", scale, "--card", card, "--sched",
                             os.path.join(HERE, "sched", f"{card}-{sess}.json"), "--t0", str(int(time.time())), "--out", out]
                       + list(extra), cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    q = json.load(open(os.path.join(out, "queue.json"))) if os.path.exists(os.path.join(out, "queue.json")) else {}
    calls = open(os.path.join(out, "device-calls.txt")).read().splitlines() if os.path.exists(os.path.join(out, "device-calls.txt")) else []
    return r.returncode, out, log, q, calls


def reduce(scratch, out, name):
    j = os.path.join(scratch, name + "-data.json")
    r = subprocess.run(PY + [os.path.join(HERE, "reduce_mms.py"), out, "--out", j], capture_output=True, text=True)
    return r.returncode, (json.load(open(j)) if os.path.exists(j) else {}), r.stderr[-500:]


def law(values, t):
    mb, nb, kb = (int(v) for v in values.split(":")[0][5:].split("x"))
    reg = "l2" if (mb, nb, kb) == (1, 1, 1) else ("l3" if 2 * mb * kb + nb * kb + 2 * mb * nb <= 32 else "dram")
    return {"l2": 500.0 if t != "int8" else 250.0, "l3": 1000.0, "dram": 1500.0}[reg]


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    scratch = os.path.abspath(argv[0])
    os.makedirs(scratch, exist_ok=True)
    res = []

    def case(name, ok, detail=""):
        res.append(bool(ok))
        print(f"{name} {'PASS' if ok else 'FAIL'} {detail}", flush=True)

    b = C.selfcheck()
    case("M1", not b, "; ".join(b))
    b = N.selfcheck()
    case("M2", not b, "; ".join(b))
    r = subprocess.run(PY + [os.path.join(HERE, "make_schedule.py"), "--check"], capture_output=True, text=True)
    case("M3", r.returncode == 0 and "MAKE CHECK PASS" in r.stdout, r.stdout.strip())
    r = subprocess.run(PY + [os.path.join(HERE, "check_mms.py"), "--check"], capture_output=True, text=True)
    case("M4", r.returncode == 0 and "CHECK PASS" in r.stdout, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr)
    r = subprocess.run(["bash", os.path.join(HERE, "preflight_mms.sh"), "a1c1", "--audit-only"], cwd=ROOT, capture_output=True,
                       text=True)
    allout = r.stdout + r.stderr
    first = next((ln for ln in allout.splitlines() if ln.startswith("dmcmd_audit:")), "")
    case("M5", r.returncode == 0 and first.startswith("dmcmd_audit: GO") and "WRAPPER" not in allout
         and "[WRITE" not in allout and "NO-GO" not in allout, first)

    # D1: card 1's S3 to its tenth run: anchor, null, bursts and a null; then card 1's S1 sus3 run is in D1b below
    sched = C.load(os.path.join(HERE, "sched", "a1c1-S3.json"))
    rc, out, log, q, calls = dry(scratch, "D1", "a1c1", "S3", "--only", "10")
    n_proc = sum(C.FORM_KEYS[r["form"]] for r in sched["runs"][:10])
    ok = rc == 0 and len([x for x in q.get("queue", []) if x.get("ran")]) == 10 and os.path.exists(os.path.join(out, "MANIFEST.sha256")) \
        and sum(1 for c in calls if "sparsity_host" in c) == 3 + n_proc and sum(1 for c in calls if c.endswith(" config")) == 2 \
        and sum(1 for c in calls if " sample " in c) == 1 and all(not c.split()[0].startswith("/") for c in calls)
    det = f"rc {rc}, calls {len(calls)} (host {sum(1 for c in calls if 'sparsity_host' in c)}, want {3 + n_proc})"
    if ok:
        rrc, d, err = reduce(scratch, out, "D1")
        arm = next(x for x in d["runs"] if x["role"] == "arm" and x["form"] == "burst" and "rnd" in x["arm"])
        v = arm["views"]["band600"]
        want_T = law(arm["values"], arm["type"]) / 600e6 * 1e6
        minion = v["rails"]["minion"]["dW"]
        nul = [x for x in d["runs"] if x["form"] == "null"]
        nl = [x["views"]["band600"]["dP_line"] for x in nul if x.get("views", {}).get("band600")]
        ok = rrc == 0 and abs(v["T_op_us"] / want_T - 1) < 0.01 and 19.0 < v["dP_w"] < 23.0 \
            and abs(v["J_op"] - v["dP_w"] * v["T_op_us"] * 1e-6 / 1024) < 1e-15 and 0.40 < minion / v["dP_w"] < 0.50 \
            and nl and all(abs(x) < 0.5 for x in nl) and v["baseline_rule"] == "line"
        det += (f"; T_op {v['T_op_us']:.4f} us (law {want_T:.4f}); dP {v['dP_w']:.2f} W (the doubles' lift 20 W + leakage); minion rail "
                f"{minion:.2f} W = {minion / v['dP_w']:.3f} of dP (the doubles: 0.45 of the lift); nulls' line reading {[round(x, 3) for x in nl]}")
    case("D1", ok, det)

    s2 = C.load(os.path.join(HERE, "sched", "a2c0-S1.json"))
    first_arm = next(r["arm"] for r in s2["runs"] if r["form"] == "burst" and r["role"] != "anchor")
    rc, out, log, q, calls = dry(scratch, "D2", "a2c0", "S1", "--only", "6", "--trip-arm", first_arm, "--trip-w", "60")
    ran = [x["arm"] for x in q.get("queue", []) if x.get("ran")]
    ok = rc == 0 and "board" in str(q.get("stop")) and "STOP:" in log and "config end" in log \
        and os.path.exists(os.path.join(out, "MANIFEST.sha256")) and ran and ran[-1] == first_arm \
        and all(not x.get("ran") for x in q["queue"][len(ran):])
    case("D2", ok, f"rc {rc}; stop {q.get('stop')}; ran {ran}")

    rc, out, log, q, calls = dry(scratch, "D3", "a1c1", "S1", "--only", "1", "--config-fail")
    ok = rc == 0 and "one re-run in 5 s" in log and len([x for x in q.get("queue", []) if x.get("ran")]) == 1
    case("D3", ok, f"rc {rc}")

    rc, out, log, q, calls = dry(scratch, "D4", "a1c1", "S1", "--only", "2", "--wrong-card")
    ok = rc == 16 and "smoke gate failed" in log and not any(x.get("ran") for x in q.get("queue", [])) and "ANOTHER" in log
    case("D4", ok, f"rc {rc}")

    rc, out, log, q, calls = dry(scratch, "D5", "a1c1", "S1", "--only", "6", "--stop-after", "2")
    ok = rc == 0 and "operator" in str(q.get("stop")) and len([x for x in q["queue"] if x.get("ran")]) == 2 \
        and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
    case("D5", ok, f"rc {rc}; stop {q.get('stop')}")

    rc, out, log, q, calls = dry(scratch, "D6", "a1c0", "S1", "--only", "1")
    ok = rc == 0 and "/dev/et0_mgmt, physical device ID 0, minion_mv 519" in log and "card 0 only" in log
    case("D6", ok, f"rc {rc}")

    r = subprocess.run(PY + [os.path.join(HERE, "collect_mms.py"), os.path.join(scratch, "D1"), "--out", os.path.join(scratch, "D7")],
                       capture_output=True, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr
    ok = "COPY-BACK EXACT" in r.stdout and "PRIVACY READ: 0 hit" in r.stdout and "COLLECT OK" in last
    case("D7", ok, last)

    rc, out, log, q, calls = dry(scratch, "D8", "a1c1", "S1", "--only", "2", "--wrong-config")
    n_cfg = sum(1 for c in calls if c.endswith(" config"))
    ok = rc == 16 and "the card's identity" in log and n_cfg == 1 and "no closing config read" in log \
        and not any(x.get("ran") for x in q.get("queue", []))
    case("D8", ok, f"rc {rc}; config calls {n_cfg}")

    rc, out, log, q, calls = dry(scratch, "D9", "a1c1", "S1", "--only", "40", "--sampler-stall", "2500", timeout=300)
    n_s = sum(1 for c in calls if " sample " in c)
    n_cfg = sum(1 for c in calls if c.endswith(" config"))
    lo = q.get("leftover") or {}
    ok = n_s == 1 and n_cfg == 1 and "LEFTOVER" in log and "no closing config read" in log and lo.get("resolved") is True \
        and any(x["what"] == "sampler" for x in lo.get("records", []))
    case("D9", ok, f"rc {rc}; sampler calls {n_s}; config calls {n_cfg}; leftover {lo.get('resolved')}; stop {q.get('stop')}")

    hang_arm = next(r["arm"] for r in sched["runs"] if r["form"] == "burst" and r["role"] == "arm")
    rc, out, log, q, calls = dry(scratch, "D10", "a1c1", "S3", "--only", "10", "--host-hang", hang_arm, timeout=600)
    lo = q.get("leftover") or {}
    st = json.load(open(os.path.join(out, "status.json"))) if os.path.exists(os.path.join(out, "status.json")) else {}
    ran = [x["arm"] for x in q.get("queue", []) if x.get("ran")]
    ok = "outlived" in str(q.get("stop")) and ran and ran[-1] == hang_arm and lo.get("resolved") is True \
        and any(x["what"] == "host" for x in lo.get("records", [])) and "no closing config read" in log \
        and (st.get("leftover") or {}).get("resolved") is True and sum(1 for c in calls if c.endswith(" config")) == 1
    case("D10", ok, f"rc {rc}; stop {q.get('stop')}; ran {len(ran)}, the last {ran[-1] if ran else None}; leftover {lo.get('resolved')} "
                    f"after {lo.get('waited_s')} s")

    rc, out, log, q, calls = dry(scratch, "D11", "a1c1", "S3", "--only", "12", "--host-fail-after", "4")
    ok = rc == 0 and "failed processes in a row" in str(q.get("stop")) and "config end" in log
    case("D11", ok, f"rc {rc}; stop {q.get('stop')}")

    rc, out, log, q, calls = dry(scratch, "D12", "a2c0", "S1", "--only", "16")
    ok = rc == 0
    det = f"rc {rc}"
    if ok:
        rrc, d, err = reduce(scratch, out, "D12")
        bad = []
        for x in d["runs"]:
            if not x.get("ran") or x["form"] == "null":
                continue
            reg = "l2" if x["arm"].startswith("1x1x1-") else None
            t, kind = x["arm"].split("-")[1], x["arm"].split("-")[2]
            mb, nb, kb = (int(v) for v in x["arm"].split("-")[0].split("x"))
            reg = "l2" if (mb, nb, kb) == (1, 1, 1) else ("l3" if 2 * mb * kb + nb * kb + 2 * mb * nb <= 32 else "dram")
            lift = {"rnd": {"fp32": 20, "fp16": 20, "int8": 10}, "ones": {"fp32": 10, "fp16": 10, "int8": 5},
                    "zeros": {"fp32": 5, "fp16": 5, "int8": 5}}[kind][t] * (1.9 if reg == "l2" else 1.0) + 8.0
            want = 20.0 + lift > 45.0
            if bool(x.get("capped")) != want:
                bad.append(f"{x['arm']} capped {x.get('capped')} (doubles {want})")
            if x["role"] == "time" and (x["views"].get("win") or {}).get("dP_w") is not None:
                bad.append(f"{x['arm']}: a time run with an energy figure")
            w = x["views"].get("win")
            if w and w.get("kclock_mhz") and not 790 <= w["kclock_mhz"] <= 810:
                bad.append(f"{x['arm']}: the window's clock {w['kclock_mhz']:.0f} MHz")
        n_capped = sum(1 for x in d["runs"] if x.get("capped"))
        ok = rrc == 0 and not bad and n_capped > 0
        det += f"; capped runs {n_capped}; " + ("; ".join(bad[:4]) if bad else "every flag as the doubles' cap says")
    case("D12", ok, det)

    def leftover_case(name, which, only, want_rc, want_cfg):
        rc, out, log, q, calls = dry(scratch, name, "a1c1", "S3", "--only", str(only), "--config-hang", which, timeout=400)
        lo = q.get("leftover") or {}
        st = json.load(open(os.path.join(out, "status.json"))) if os.path.exists(os.path.join(out, "status.json")) else {}
        n_cfg = sum(1 for c in calls if c.endswith(" config"))
        ended = os.path.exists(os.path.join(out, "fakedev", f"config-hang-{which}.ended"))
        ok = rc == want_rc and n_cfg == want_cfg and lo.get("resolved") is True and ended \
            and any(x["what"] == "config-read" for x in lo.get("records", [])) and (st.get("leftover") or {}).get("resolved") is True \
            and "LEFTOVER resolved" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
        return ok, rc, log, q, n_cfg, lo, ended

    ok, rc, log, q, n_cfg, lo, ended = leftover_case("D13", "start", 2, 16, 1)
    ok = ok and "no re-run" in log and "no closing config read" in log and not any(x.get("ran") for x in q.get("queue", []))
    case("D13", ok, f"rc {rc}; config calls {n_cfg}; leftover resolved {lo.get('resolved')} after {lo.get('waited_s')} s; the double "
                    f"ended by itself {ended}")

    ok, rc, log, q, n_cfg, lo, ended = leftover_case("D14", "end", 1, 0, 2)
    ok = ok and len([x for x in q.get("queue", []) if x.get("ran")]) == 1 and "config end: config read (end) left" in log
    case("D14", ok, f"rc {rc}; config calls {n_cfg}; leftover resolved {lo.get('resolved')} after {lo.get('waited_s')} s; the double "
                    f"ended by itself {ended}")

    rc, out, log, q, calls = dry(scratch, "D15", "a1c1", "S3", "--only", "2", "--closing-holder")
    n_cfg = sum(1 for c in calls if c.endswith(" config"))
    close_txt = open(os.path.join(out, "etwho-close.txt")).read() if os.path.exists(os.path.join(out, "etwho-close.txt")) else ""
    ok = rc == 0 and n_cfg == 1 and "no closing config read: a holder or a device process right before it" in log \
        and "holder line(s) of another login on the card" in close_txt and len([x for x in q.get("queue", []) if x.get("ran")]) == 2
    case("D15", ok, f"rc {rc}; config calls {n_cfg}; {close_txt.strip()}")

    # et-who calls under --dry: 1 before the first card command, 2 the identity read, then one before every run: run k (from 0)
    # is call 3 + k, so --holder-after 2 + k shows the holder first at run k
    k = next(i for i, r in enumerate(s2["runs"]) if i >= 1 and r["role"] != "anchor")
    rc, out, log, q, calls = dry(scratch, "D16", "a2c0", "S1", "--only", str(k + 2), "--holder-after", str(2 + k))
    qq = q.get("queue", [])
    ran = [x for x in qq if x.get("ran")]
    ok = rc == 0 and len(ran) == k and len(qq) > k and qq[k].get("role") != "anchor" and not qq[k].get("ran") \
        and "holder line(s) of another login" in str(q.get("stop")) and "no closing config read" in log
    case("D16", ok, f"rc {rc}; ran {len(ran)} (want {k}); run {k} ({qq[k].get('role') if len(qq) > k else None}): "
                    f"{qq[k].get('why') if len(qq) > k else None}")

    lock = os.path.join(scratch, "D17-box.lock")
    other = os.path.join(scratch, "D17-other.lock")
    probe = os.path.join(scratch, "D17-probe.py")
    with open(probe, "w") as f:
        f.write("import os, sys\nsys.path.insert(0, sys.argv[1])\nimport run_mms as M\n"
                "fd, how = M.take_box_lock(sys.argv[2], os.environ.get('MMS_BOX_LOCK_FD'))\n"
                "print(('HELD ' if fd is not None else 'REFUSED ') + how)\n")
    open(other, "a").close()
    env_n = {k_: v for k_, v in os.environ.items() if k_ != "MMS_BOX_LOCK_FD"}
    fd = os.open(lock, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fd2 = os.open(other, os.O_RDONLY)

    def probe_run(env, fds=()):
        r = subprocess.run(PY + [probe, HERE, lock], env=env, pass_fds=fds, capture_output=True, text=True, timeout=60)
        return (r.stdout.strip() or r.stderr.strip()[-200:])

    r1 = probe_run(dict(env_n, MMS_BOX_LOCK_FD=str(fd)), (fd,))
    r2 = probe_run(env_n)
    r3 = probe_run(dict(env_n, MMS_BOX_LOCK_FD=str(fd2)), (fd2,))
    os.close(fd)
    os.close(fd2)
    r4 = probe_run(env_n)
    ok = r1.startswith("HELD held since") and r2.startswith("REFUSED the box lock is held") \
        and r3.startswith("REFUSED the descriptor handed over") and r4.startswith("HELD taken")
    case("D17", ok, f"handed: {r1[:40]}; fresh beside it: {r2[:40]}; another file: {r3[:45]}; after: {r4[:20]}")

    n = sum(res)
    print(f"SELFTEST-MMS {n} of {len(res)} PASS")
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
