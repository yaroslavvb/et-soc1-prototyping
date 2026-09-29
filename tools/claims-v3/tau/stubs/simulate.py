#!/usr/bin/env python3
"""TAU: simulated passes without a clock, for calibrating the decision code (calibrate.py). No device, no block.sh.

    simulate.py --card aifoundry3 --passes 101,102,103 --out DIR [--seed 1] [--noise 1.0] [--fixed-delay 0.263]

Writes DIR/p<pass>/ as block.sh would (tel-NN.jsonl, windows.jsonl, bursts.jsonl, block.json), from the same simulated
card as the dry-run stubs (stub-common.py: the offline filters, one pass late plus extra_d, the in-burst creep and the
noise matched to the offline residuals) and block.sh's timeline: each window's sampler gives its first line 0.30-0.45 s
after its launch, the burst's host process starts 1.5 s later and its kernel 0.70-0.76 s after that (enercat's device
setup), the sampler stops after sampler_seconds, and the next window's sampler starts 0.08-0.25 s later. The SP's pass
phase is random in each window. The schedule and its seeded order are reduce.py's (tau.json).
"""
import argparse, importlib.util, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(HERE))
import reduce as rd  # noqa: E402

_spec = importlib.util.spec_from_file_location("sc", os.path.join(HERE, "stub-common.py"))
sc = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sc)


def configure(card, noise=1.0, extra_d=True, creep=True, noise_w=None):
    sc.CARD_NAME = card
    sc.CARD = dict(sc.CARDS[card])
    if noise_w:                                   # calibrate.py match: these noise_w (W) times noise, as given
        sc.CARD["noise_w"] = dict(sc.CARD["noise_w"], **noise_w)
    sc.RAW_NOISE = bool(noise_w)
    sc.NOISE, sc.EXTRA_D, sc.CREEP = noise, extra_d, creep


def simulate_pass(out, card, pass_, rng, t0_ms, mode="full", fixed_delay=None, salt=0):
    """One pass into out/p<pass>/; returns the virtual time (ms) its last window ended."""
    c = rd.cfg()
    d = os.path.join(out, f"p{pass_}"); os.makedirs(d, exist_ok=True)
    bs = []; L = t0_ms
    W = open(os.path.join(d, "windows.jsonl"), "w"); B = open(os.path.join(d, "bursts.jsonl"), "w")
    sched = rd.schedule(c, mode, pass_)
    for w, (rate, kind, secs, sws) in enumerate(sched, 1):
        F = L + rng.uniform(300, 450)
        P = sc.CARD["pass"][rate]
        phase = rng.uniform(0, P)
        rec = None
        if kind != "idle":
            on = F + c["pre_burst_s"] * 1000 + rng.uniform(0, 40) + rng.uniform(700, 760)
            rec = sc.burst_record(on, secs, kind); bs.append(rec)
        with open(os.path.join(d, f"tel-{w:02d}.jsonl"), "w") as f:
            for i in range(int(sws * 1000 / rate)):
                s = sc.sample_row(F + i * rate, rate, bs, phase=phase, salt=salt, fixed_delay=fixed_delay)
                f.write(json.dumps(s, separators=(",", ":")) + "\n")
        W.write(json.dumps({"win": w, "rate": rate, "kind": kind, "secs": float(secs), "sampler_s": sws, "try_": 1, "fails": 0,
                            "t_launch": int(L), "t_first": int(F), "start_ms": int(F) - int(L), "status": "ok",
                            "check": {"status": "ok", "die_mean": 60.0, "die_last": 60}}) + "\n")
        if rec:
            B.write(json.dumps({"win": w, "kind": kind, "secs": float(secs), "rate_ms": rate, "t_on_ms": int(rec["on"]),
                                "t_off_ms": int(rec["off"]), "launches": rec["n"], "rc": "0", "status": "ok"}) + "\n")
        L = F + sws * 1000 + rng.uniform(80, 250)
    W.close(); B.close()
    json.dump({"exp": "tau", "pass": pass_, "card": card, "mode": mode, "role": "simulated", "t0_ms": int(t0_ms),
               "t1_ms": int(L), "windows": len(sched), "dry": True, "simulated": True, "status": "ok",
               "note": f"simulate.py noise {sc.NOISE} fixed_delay {fixed_delay}"}, open(os.path.join(d, "block.json"), "w"))
    return L


def simulate(out, card, passes, seed=1, noise=1.0, fixed_delay=None, mode="full", extra_d=True, creep=True, noise_w=None):
    configure(card, noise, extra_d, creep, noise_w)
    rng = random.Random(seed)
    t = 1.79e12 + seed * 1e7
    dirs = []
    for p in passes:
        t = simulate_pass(out, card, p, rng, t, mode, fixed_delay, salt=seed * 1000 + p) + 60000 + rng.uniform(0, 60000)
        dirs.append(os.path.join(out, f"p{p}"))
    return dirs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--card", required=True, choices=sorted(sc.CARDS)); ap.add_argument("--passes", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--noise", type=float, default=1.0, help="the residual as a multiple of the card's offline one")
    ap.add_argument("--fixed-delay", type=float)
    ap.add_argument("--mode", default="full", choices=("full", "smoke"))
    a = ap.parse_args()
    for d in simulate(a.out, a.card, [int(p) for p in a.passes.split(",")], a.seed, a.noise, a.fixed_delay, a.mode):
        print(d)


if __name__ == "__main__":
    main()
