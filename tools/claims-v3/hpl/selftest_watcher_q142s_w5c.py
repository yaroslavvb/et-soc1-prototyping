#!/usr/bin/env python3
"""Q142(s), W5c: W5b's blind window, measured. Written Wed 4 Nov 2026, after the watcher fix's verifier, for run_hpl.py.dated-note-2.md;
post hoc and desk only (no device, no lock, no ssh). run_hpl.py, watcher_q142s.py and the committed self-test are imported unchanged.

W5b (selftest_watcher_q142s.py) showed that with run_hpl.py's committed watcher a run's start gate can pass on the previous run's last
reading. The first dated amendment then put the stops' blind spot at "at most one 10 s launch process". That holds only for launches
of 8 s or more. The guard ends the session once the reading is over 5 s old and the sampler over 8 s old (run_hpl.py:683), and it is
checked before each launch process, so every process that starts before then runs with the watcher off its own run's file. W5c is
W5b's dry two-run Session (the same gate, above the first run's last die; the same forced follow()), with the second run at 3 launch
processes of 3 s. At each work launch of the second run it records what the stops were watching: the watcher's last reading (its t_ms
against the run's first telemetry line) and its position against the size of the file it follows.

    python3 -B tools/claims-v3/hpl/selftest_watcher_q142s_w5c.py <a new, empty scratch dir> > tools/claims-v3/hpl/selftest-watcher-q142s-w5c.txt

Expected: OLD (the committed Watcher) ends error:telemetry_stale in the second run, after two of its three processes ran blind (the last
reading the first run's, the position past the file's end); NEW (watcher_q142s's) runs all three to done, each on its own run's reading.
Exit 0 only if every expectation holds. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_watcher_q142s as S  # noqa: E402  (the committed self-test; its main() does not run on import)

H, WQ = S.H, S.WQ
results = []


def check(ok, what):
    results.append(bool(ok))
    print(f"{'ok  ' if ok else 'FAIL'} {what}", flush=True)


def one(cls, d):
    seen = []
    orig = H.Session.spawn_kernel

    def spy(self, r, *a, **kw):           # before each launch process: what the watcher, and so the stops, are on
        if r.name.startswith("NEXT"):
            w = self.watcher
            last, _ = w.snapshot()
            with w.lock:
                path, pos = w.path, w.pos
            seen.append({"t_ms": H.now_ms(), "last_t": last[0] if last else None, "pos": pos,
                         "size": os.path.getsize(path) if path and os.path.exists(path) else None})
        return orig(self, r, *a, **kw)

    H.Session.spawn_kernel = spy
    try:
        res = S.session(cls, d, 79)
    finally:
        H.Session.spawn_kernel = orig
    run = os.path.join(d, "run")
    first = res["next_first_t"]
    work = [json.loads(ln) for ln in open(os.path.join(run, "launches.jsonl"))]
    work = [x for x in work if x.get("run", "").startswith("NEXT") and x.get("role") == "work"]
    rows = []
    for x, s in zip(work, seen):
        blind = s["last_t"] is None or s["last_t"] < first or (s["size"] is not None and s["pos"] > s["size"])
        rows.append({"proc": x["proc"], "start_s": round((x["t_start_ms"] - first) / 1000, 1),
                     "end_s": round((x["t_end_ms"] - first) / 1000, 1),
                     "last_reading_s": None if s["last_t"] is None else round((s["last_t"] - first) / 1000, 1),
                     "pos": s["pos"], "size": s["size"], "blind": blind})
    return res, rows


def main():
    T = sys.argv[1] if len(sys.argv) > 1 else None
    if not T:
        sys.exit("usage: selftest_watcher_q142s_w5c.py <a new, empty scratch dir>")
    if os.path.isdir(T) and os.listdir(T):
        sys.exit(f"refused: {T} is not empty")
    os.makedirs(T, exist_ok=True)
    print("# Q142(s) W5c: W5b's session with the second run at 3 launch processes of 3 s (post hoc, desk only: no device, no ssh)")
    print(f"# run_hpl.py sha256 {WQ.sha256_of(H.__file__)[:12]} (committed {WQ.RUN_HPL_SHA256 == WQ.sha256_of(H.__file__)}); "
          f"watcher_q142s.py sha256 {WQ.sha256_of(WQ.__file__)[:12]}; selftest_watcher_q142s.py sha256 {WQ.sha256_of(S.__file__)[:12]}")
    S.PROTO["blocks"][1]["runs"][0]["launch"] = {"seconds": 3, "budget": 4.5, "processes": 3}
    t0 = time.time()
    got = {}
    for label, cls in (("OLD", S.OLD), ("NEW", S.NEW)):
        res, rows = one(cls, os.path.join(T, f"w5c-{label}"))
        got[label] = (res, rows)
        print(f"\n== {label}: {cls.__module__}.{cls.__qualname__}")
        print(f"   end {res['reason']!r}; the forced follow() fired: {res['fired']}; the gate's reading t - the run's first line: "
              f"{None if res['gate_t'] is None else round((res['gate_t'] - res['next_first_t']) / 1000, 2)} s")
        for r in rows:
            print(f"   process {r['proc']}: {r['start_s']}-{r['end_s']} s after the run's first telemetry line; at its start the "
                  f"watcher's last reading was {r['last_reading_s']} s, its position {r['pos']} B in a {r['size']} B file: "
                  f"{'BLIND' if r['blind'] else 'on its own run'}")
    o, ores = got["OLD"][1], got["OLD"][0]
    n, nres = got["NEW"][1], got["NEW"][0]
    print("\n== the expectations")
    check(ores["fired"] and nres["fired"], "the forced follow() fired in both sessions (the test does not pass vacuously)")
    check(ores["gate_t"] is not None and ores["gate_t"] < ores["next_first_t"],
          "OLD: the second run's gate passed on the first run's reading (W5b)")
    check(ores["reason"].startswith("error:telemetry_stale:NEXT") and len(o) >= 2 and all(r["blind"] for r in o),
          f"OLD: {len(o)} launch processes, not one, ran blind before the guard's 8 s rule ended the session ({ores['reason']!r})")
    check(nres["reason"] == "done" and len(n) == 3 and not any(r["blind"] for r in n),
          "NEW: all 3 processes ran, each with the watcher on its own run's telemetry, to 'done'")
    print(f"\n{sum(results)} of {len(results)} expectations hold, in {time.time() - t0:.0f} s")
    if all(results):
        print("W5C OK: with launches under 8 s, the committed watcher's blind window is every process that starts before the "
              f"guard's 8 s rule: {len(o)} of 3 s here; the new watcher has none")
        return 0
    print("W5C FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
