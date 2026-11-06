#!/usr/bin/env python3
"""E178 (Q146, the kit; E171's selftest_watcher_e171.py, ported): the kinds watcher against the race watcher_q142s.py fixes in run_hpl.py (E171.md, "The watcher"). Desk only: a
temporary file stands in for the pass's live sampler file; nothing opens a device. run_e178.py's start_watcher and _check_line (E163's and E171's,
unchanged) and run_e78.last_sample (E78's, unchanged) are imported and driven directly.

The run_hpl race needs a watcher that keeps a file position and a follow() that swaps the file under it. The kinds watcher keeps
neither: every read opens the path and takes the newest complete line from its last 8,000 bytes. The cases force the same moments:
  K1  the file replaced between two reads (the run_hpl W1/W2 moment): the next read is the new file's newest line, never the old one's,
      and never a line found at an old offset;
  K2  the same with the old file's newest line at the die stop: once the file is replaced, the stop line is not read as current (the
      new file's reading decides), and before the replacement it fires the stop (W3's two halves);
  K3  a partial newest line (the sampler mid-write): the previous complete line is read, never a broken one;
  K4  a quiet append (the control): the newest line, and the watcher thread fires the board stop within 0.5 s of the line that crosses it;
  K5  the watcher thread across a replacement: started on one file, the file replaced with one whose newest line is at the board stop,
      STOP is written within 0.5 s, naming the new file's sample.

    /usr/bin/python3 -B tools/claims-v3/e178/selftest_watcher_e178.py [--out <file>]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_e178 as R  # noqa: E402  (imports e178_common, which puts tools/claims-v3/kinds on the path)
import run_e78  # noqa: E402


def line(t_ms, board, die):
    return json.dumps({"t_ms": t_ms, "board_w": board, "temp_c": {"minshire": [die, die, 90.0]}}) + "\n"


def write(path, lines, tail=""):
    tmp = path + ".new"
    with open(tmp, "w") as f:
        f.writelines(lines)
        f.write(tail)
    os.replace(tmp, path)          # an atomic swap of the file at the path: the moment a follow() would move a run_hpl watcher


def main():
    out = {}
    d = tempfile.mkdtemp(prefix="e178-watcher-")
    try:
        p = os.path.join(d, "telemetry.jsonl.raw")
        now = int(time.time() * 1000)
        old = [line(now - 3000 + 100 * i, 30.0 + 0.01 * i, 55.0) for i in range(400)]      # a long old file (about 40 KB)
        new = [line(now + 100 * i, 31.0, 56.0) for i in range(3)]                          # a short new one
        write(p, old)
        a = run_e78.last_sample(p)
        write(p, new)
        b = run_e78.last_sample(p)
        out["K1"] = {"before": a["t_ms"], "after": b["t_ms"], "new_newest": json.loads(new[-1])["t_ms"],
                     "pass": a["t_ms"] == json.loads(old[-1])["t_ms"] and b["t_ms"] == json.loads(new[-1])["t_ms"]}
        hot = old[:-1] + [line(now - 50, 30.0, 75.0)]
        write(p, hot)
        m1 = R._check_line(run_e78.last_sample(p), 65.0, 70.0, "E178", p)
        write(p, new)
        m2 = R._check_line(run_e78.last_sample(p), 65.0, 70.0, "E178", p)
        out["K2"] = {"stop_before_replacement": m1, "stop_after_replacement": m2, "pass": bool(m1 and "die stop" in m1) and m2 is None}
        write(p, new, tail='{"t_ms": %d, "board_w": 99.0, "temp_c": {"minsh' % (now + 400))
        c = run_e78.last_sample(p)
        out["K3"] = {"read": c["t_ms"], "pass": c["t_ms"] == json.loads(new[-1])["t_ms"] and c["board_w"] == 31.0}
        R.TRIPPED.clear()
        od = os.path.join(d, "out-k4")
        os.makedirs(od)
        write(p, new)
        t, ev = R.start_watcher(run_e78.last_sample, p, 65.0, 70.0, od, tag="E178 watcher")
        ev.wait(2.0)
        quiet = not R.TRIPPED
        with open(p, "a") as f:
            f.write(line(now + 500, 66.5, 56.0))
        t0 = time.time()
        while not R.TRIPPED and time.time() - t0 < 2.0:
            time.sleep(0.02)
        dt = time.time() - t0
        k4 = {"quiet_before": quiet, "fired": bool(R.TRIPPED), "seconds": round(dt, 3),
              "stop_file": os.path.exists(os.path.join(od, "STOP")), "message": (R.TRIPPED or [""])[0][:160]}
        k4["pass"] = quiet and bool(R.TRIPPED) and dt < 0.5 and k4["stop_file"] and "board-power stop" in k4["message"]
        out["K4"] = k4
        write(p, new)                 # K4's watcher thread keeps reading p: give it a quiet file before the next case
        time.sleep(0.3)
        R.TRIPPED.clear()
        p5 = os.path.join(d, "telemetry5.jsonl.raw")
        od5 = os.path.join(d, "out-k5")
        os.makedirs(od5)
        write(p5, old)
        t5, ev5 = R.start_watcher(run_e78.last_sample, p5, 65.0, 70.0, od5, tag="E178 watcher")
        ev5.wait(2.0)
        quiet5 = not R.TRIPPED
        write(p5, new[:2] + [line(now + 900, 67.0, 56.0)])
        t0 = time.time()
        while not R.TRIPPED and time.time() - t0 < 2.0:
            time.sleep(0.02)
        dt5 = time.time() - t0
        msg5 = (R.TRIPPED or [""])[0]
        out["K5"] = {"quiet_before": quiet5, "fired": bool(R.TRIPPED), "seconds": round(dt5, 3), "names_new_sample": f"t_ms {now + 900}" in msg5,
                     "pass": quiet5 and bool(R.TRIPPED) and dt5 < 0.5 and f"t_ms {now + 900}" in msg5}
    finally:
        shutil.rmtree(d, ignore_errors=True)
    out["PASS"] = all(v["pass"] for k, v in out.items() if k.startswith("K"))
    out["watcher"] = "run_e178.start_watcher over run_e78.last_sample: no file position, no follow(); watcher_q142s.py pinned, not imported"
    txt = json.dumps(out, indent=1, sort_keys=True)
    if "--out" in sys.argv:
        open(sys.argv[sys.argv.index("--out") + 1], "w").write(txt + "\n")
    print(json.dumps({k: (v["pass"] if isinstance(v, dict) else v) for k, v in out.items() if k != "watcher"}, sort_keys=True))
    return 0 if out["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
