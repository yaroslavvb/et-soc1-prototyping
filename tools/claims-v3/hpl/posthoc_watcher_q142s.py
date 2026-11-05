#!/usr/bin/env python3
"""Q142(s), post hoc and desk only: the figures run_hpl.py.dated-note-2.md quotes, read from the committed data. Written Wed 4 Nov 2026,
after the watcher fix's verifier; it changes nothing, and nothing in it is registered.

    python3 -B tools/claims-v3/hpl/posthoc_watcher_q142s.py > tools/claims-v3/hpl/posthoc-watcher-q142s.txt

The sessions are every committed docs/reports/data/**/session.json whose runner hash is the committed run_hpl.py's (68493295...) and
that is not a dry run: the selection the dated amendment's count used.
  1. follow() calls and run boundaries. Session.start_sampler calls Watcher.follow() once per run it starts (run_hpl.py:534), retries
     included, so a session's follow() calls are the runs it started: its runs.jsonl records, or its telemetry files when it ended
     inside a run (one per run, tel/<run>.jsonl). A run boundary is a follow() with an earlier file to race against: every follow()
     but each session's first.
  2. The incidence: the telemetry_stale ends among those sessions, per boundary, with an exact (Garwood) 95% Poisson interval, and per
     session of 150, 160 and 170 boundaries.
  3. The gates. For each run whose start gate recorded a reading (runs.jsonl "gate" > "reading", run_hpl's reading(): die mean, die high,
     board W, minion MHz, with no time of its own), after a run of the same session: is that reading one of its own run's telemetry
     lines up to its first work launch, or the previous run's last line (the W5b race: a gate passing on the previous run's reading),
     both (the two cannot be told apart), or neither?
  4. E165 s1's end, timed from BURST-158's first telemetry line and from its sampler_start mark, beside W5a's 8.4 s in
     selftest-watcher-q142s.txt (counted from the second run's first line, selftest_watcher_q142s.py's first_t).
It reads lines with run_hpl.parse_tel, the watcher's own parse (imported, unchanged; nothing runs). Standard library otherwise; it reads,
and never writes, the data; paths print relative to the lab clone. SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import run_hpl as H  # noqa: E402  (the committed file, for parse_tel only)

RUN_HPL_SHA256 = "68493295504fba5d4e9056b4f7e7387179d555e4157bbae32075b4197f3df227"


def rel(p):
    return os.path.relpath(p, ROOT)


def opn(p):
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p)


def jsonl(d, name):
    for p in (os.path.join(d, name), os.path.join(d, name) + ".gz"):
        if os.path.exists(p):
            with opn(p) as f:
                return [json.loads(ln) for ln in f if ln.strip()]
    return None


def tel(d, relpath):
    for p in (os.path.join(d, relpath), os.path.join(d, relpath) + ".gz"):
        if os.path.exists(p):
            out = []
            with opn(p) as f:
                for ln in f:
                    if ln.startswith("{"):
                        t = H.parse_tel(ln)
                        if t is not None:
                            out.append(t)
            return out
    return None


def garwood(k, conf=0.95):
    """Exact Poisson interval for k events (k >= 1), by bisection on the Poisson tails."""
    a = (1 - conf) / 2

    def cdf(x, mu):   # P(X <= x | mu)
        return sum(math.exp(-mu) * mu ** i / math.factorial(i) for i in range(x + 1))

    def solve(f, lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(mid) > 0:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = solve(lambda mu: a - (1 - cdf(k - 1, mu)), 1e-12, 50.0)    # P(X >= k | mu) = a
    upper = solve(lambda mu: cdf(k, mu) - a, 1e-12, 50.0)              # P(X <= k | mu) = a
    return lower, upper


def main():
    assert hashlib.sha256(open(os.path.join(HERE, "run_hpl.py"), "rb").read()).hexdigest() == RUN_HPL_SHA256, "run_hpl.py differs"
    print("# Q142(s) post hoc desk read for run_hpl.py.dated-note-2.md (committed data only; nothing registered)")
    print(f"# run_hpl.py sha256 {RUN_HPL_SHA256[:12]} (the committed file)")
    sessions, follows, bounds, stale = [], 0, 0, []
    pairs = {"own": 0, "prev_only": [], "both": [], "neither": []}
    modes = {}
    dirs = set()
    for sj in sorted(glob.glob(os.path.join(ROOT, "docs", "reports", "data", "**", "session.json"), recursive=True)):
        try:
            s = json.load(open(sj))
        except (OSError, ValueError):
            continue
        if not isinstance(s, dict) or (s.get("sha256") or {}).get("runner") != RUN_HPL_SHA256 or s.get("dry"):
            continue
        d = os.path.dirname(sj)
        recs = jsonl(d, "runs.jsonl") or []
        td = os.path.join(d, "tel")
        stems = {f[:-3] if f.endswith(".gz") else f for f in os.listdir(td)} if os.path.isdir(td) else set()
        nf = max(len(recs), len(stems))
        sessions.append(rel(d))
        dirs.add(rel(d).split(os.sep)[3])
        follows += nf
        bounds += max(nf - 1, 0)
        try:
            end = json.load(open(os.path.join(d, "end.json")))
        except (OSError, ValueError):
            end = {}
        if "telemetry_stale" in str(end.get("reason", "")):
            stale.append((rel(d), end.get("reason"), end.get("t_end_ms")))
        for prev, cur in zip(recs, recs[1:]):
            g = (cur.get("gate") or {}).get("reading")
            if not g:
                continue
            mode = (cur.get("gate") or {}).get("mode")
            last = tel(d, prev["tel"])
            mine = tel(d, cur["tel"])
            if not last or mine is None:
                pairs["neither"].append((rel(d), cur["run"], "a telemetry file is missing"))
                continue
            starts = [x.get("t_start_ms") for x in cur.get("launches") or [] if x.get("t_start_ms")]
            t_launch = min(starts) if starts else cur.get("t_first_ms")
            G = tuple(g)
            old = tuple(last[-1][1:5])
            own = {tuple(t[1:5]) for t in mine if t_launch is None or t[0] <= t_launch}
            modes[mode] = modes.get(mode, 0) + 1
            if G == old and G not in own:
                pairs["prev_only"].append((rel(d), cur["run"], mode, G))
            elif G == old:
                pairs["both"].append((rel(d), cur["run"], mode, (cur.get("gate") or {}).get("held_s")))
            elif G in own:
                pairs["own"] += 1
            else:
                pairs["neither"].append((rel(d), cur["run"], mode, G))
    n_pairs = pairs["own"] + len(pairs["prev_only"]) + len(pairs["both"]) + len(pairs["neither"])

    print("\n== 1. sessions, follow() calls, run boundaries")
    print(f"measured run_hpl sessions: {len(sessions)}, in {len(dirs)} data directories")
    print(f"follow() calls (runs started): {follows}")
    print(f"run boundaries (follow() calls less each session's first): {bounds}")
    print(f"telemetry_stale ends: {len(stale)}")
    for x in stale:
        print(f"   {x[0]}: {x[1]}")

    print("\n== 2. the incidence (one event: an estimate, with its exact interval)")
    k = len(stale)
    lo, hi = garwood(k) if k else (0.0, -math.log(0.025))
    print(f"Poisson 95% interval for {k} event(s): {lo:.4f} to {hi:.4f}")
    print(f"per run boundary: {k / bounds * 100:.3f}% (95%: {lo / bounds * 100:.4f}% to {hi / bounds * 100:.2f}%)")
    for n in (150, 160, 170):
        p = 1 - math.exp(-n * k / bounds)
        pl, ph = 1 - math.exp(-n * lo / bounds), 1 - math.exp(-n * hi / bounds)
        print(f"a session of {n} boundaries ends early: {p * 100:.1f}% (95%: {pl * 100:.1f}% to {ph * 100:.1f}%)")

    print("\n== 3. the gates: whose telemetry each recorded reading is")
    print(f"runs after a run of their session with a gate reading and both telemetry files: {n_pairs}"
          f" (by gate mode: {json.dumps(modes, sort_keys=True)})")
    print(f"own run's line before its first work launch, not the previous run's last line: {pairs['own']}")
    print(f"the previous run's last line only (a gate passed on the previous run's reading): {len(pairs['prev_only'])}")
    for x in pairs["prev_only"]:
        print(f"   {x}")
    print(f"both (identical readings, cannot be told apart): {len(pairs['both'])}; their held_s: "
          f"{sorted({x[3] for x in pairs['both']})}")
    for x in pairs["both"]:
        print(f"   {x[0]} {x[1]} ({x[2]} gate, held {x[3]} s)")
    print(f"neither: {len(pairs['neither'])}")
    for x in pairs["neither"]:
        print(f"   {x}")

    print("\n== 4. E165 s1's end, from two starting points")
    d = os.path.join(ROOT, "docs", "reports", "data", "2026-11-04-e165-blind7-aifoundry2", "aifoundry2", "s1")
    end = json.load(open(os.path.join(d, "end.json")))
    lines = tel(d, os.path.join("tel", "BURST-158-b7-fp16.randn_x8-r1.jsonl"))
    prev = tel(d, os.path.join("tel", "BURST-157-b7-int8.sparse_rows_a-r1.jsonl"))
    marks = jsonl(d, "marks.jsonl") or []
    start = [m for m in marks if m.get("kind") == "sampler_start" and prev[-1][0] <= m.get("t_ms", 0) <= end["t_end_ms"]]
    t0, tm, te = lines[0][0], start[-1]["t_ms"], end["t_end_ms"]
    print(f"end.json: {end['reason']}")
    print(f"BURST-158's first telemetry line t_ms {t0}; its sampler_start mark {tm}; the end {te}")
    print(f"from the first telemetry line: {(te - t0) / 1000:.3f} s (W5a, counted the same way: 8.4 s)")
    print(f"from the sampler_start mark: {(te - tm) / 1000:.3f} s (the 8.1 s of E165's README and the first dated amendment)")
    print(f"the previous run's last line: die {prev[-1][1]} C (the cool gate's limit 55 C); BURST-158's die first reads 55 C or less at "
          f"{next(t[0] for t in lines if t[1] is not None and t[1] <= 55) - t0} ms after its first line")


if __name__ == "__main__":
    main()
