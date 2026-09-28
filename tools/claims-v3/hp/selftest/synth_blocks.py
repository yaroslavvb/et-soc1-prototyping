#!/usr/bin/env python3
"""Synthetic hp blocks with planted effects, in block.sh's file format, for testing reduce.py and prereg.py.

    python3 tools/claims-v3/hp/selftest/synth_blocks.py <out root> [--seed 1] [--card C] [--passes P1,P2,...]
    python3 tools/claims-v3/hp/selftest/run_selftest.py            generates, reduces, pre-registers, validates, checks

The card is an exact two-stage Foster network, T = T_amb + sum_k R_k LP_k(P_idle + kappa_p * dP) with the placement's
gain kappa_p on its switching power dP (so the reducer's kappa should recover kappa_p), whole-degree readings of T
plus N(0, sigma) noise, a windowed high = mean + 1.5 + a concentration term, the I/O sensor with a corner term, and
the heater's SPARSITY lines. Runs follow block.sh's protocol: ALL24 preheat bursts to the target, the falling S+1 -> S
edge, then a chain of 2 s launches until 2 launches after the mean first reads 66 (cap 150 s), or one 7 s launch and
10 s of idle (Tier S). Nothing here touches a device.
"""
import gzip
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import hplib as H  # noqa: E402

# planted gains: PER16 trips later than INT16 (PLACE SIGN+), EDGE8 and MEM8 later than CEN8, N8b vs S8b a gradient,
# W8b = E8b (no E-W gradient)
KAPPA = {"INT16": 1.0, "PER16": 0.85, "UNI32": 0.95, "MEM8": 0.93, "EDGE8": 0.85, "CEN8": 1.03,
         "W8b": 1.0, "E8b": 1.0, "N8b": 1.06, "S8b": 0.94, "B4NE": 1.0, "B4SW": 1.0, "B4C": 1.0}
CONC = {"INT16": 1.2, "PER16": 1.0, "UNI32": 0.4, "B4NE": 1.5, "B4SW": 1.5}
IO = {"B4NE": 2.5}
# DESIGN2 §5.1 (G0): aifoundry3's all-shire heater (27 W) goes 60 -> 66 C in 20-30 s and still rises at 87-89 C;
# 13 W from 60 C about 50-75 s. Card 1 heats about 1.6x faster.
CARDS = {"aifoundry3": {"P_idle": 25.7, "R": [0.2, 1.1], "tau": [8.0, 200.0], "rest": 59.0},
         "aifoundry1-c1": {"P_idle": 34.0, "R": [0.16, 0.9], "tau": [5.0, 125.0], "rest": 56.0}}   # dfo:18-20


class Card:
    def __init__(self, name, rng, sigma=0.12):
        c = CARDS[name]
        self.c, self.rng, self.sigma = c, rng, sigma
        self.T_amb = c["rest"] - sum(c["R"]) * c["P_idle"]
        self.x = [c["P_idle"], c["P_idle"]]
        self.t = 1790000000000.0
        self.hot = 0.0
        self.io = 0.0
        self.tel = []
        self.win_t0 = self.t
        self.win = None

    def T(self):
        return self.T_amb + self.c["R"][0] * self.x[0] + self.c["R"][1] * self.x[1]

    def step(self, dP=0.0, kappa=1.0, conc=0.0, io=0.0, record=True):
        """Advance 0.1 s with switching power dP (W) at gain kappa; record one sampler line."""
        c = self.c
        Pe = c["P_idle"] + kappa * dP
        for k in (0, 1):
            self.x[k] += (1 - math.exp(-0.1 / c["tau"][k])) * (Pe - self.x[k])
        self.hot += (1 - math.exp(-0.1 / 3.0)) * (conc * dP * 0.12 - self.hot)
        self.io += (1 - math.exp(-0.1 / 3.0)) * (io * dP * 0.25 - self.io)
        self.t += 100
        if record:
            n = self.rng.gauss(0, self.sigma)
            T = self.T()
            m = int(math.floor(T + n))
            hi = int(math.floor(T + 1.5 + self.hot + n))
            iov = int(math.floor(T - 0.3 + self.io + n))
            if self.win is None:
                self.win = [m - 3, hi, iov]
            self.win = [min(self.win[0], m - 3), max(self.win[1], hi), max(self.win[2], iov)]
            sr = int(self.t - self.win_t0)
            self.tel.append({"t_ms": int(self.t), "since_reset_ms": sr, "board_w": round(c["P_idle"] + dP + self.rng.gauss(0, 0.1), 2),
                             "temp_c": {"ioshire": [iov, iov - 2, self.win[2]], "minshire": [m, self.win[0], self.win[1]]},
                             "mhz": {"minion": 600}})
            if sr >= 1000:
                self.win_t0 = self.t
                self.win = None

    def mean(self):
        return self.tel[-1]["temp_c"]["minshire"][0] if self.tel else int(self.T())


def run(card, out, idx, slot, role, name, tier, edge, target, launches, heater, PL):
    r = PL[name]
    g = r["group"]
    dP = 0.0256 * r["minions"]
    kap, conc, io = KAPPA.get(g, 1.0), CONC.get(g, 0.6), IO.get(g, 0.2)
    card.tel = []
    lines = []
    # preheat with ALL24 2 s bursts to the target
    nb = 0
    for _ in range(10):
        card.step()
    while card.mean() < target and nb < 30:
        for _ in range(20):
            card.step(19.66, 1.0, 0.4, 0.2)
        for _ in range(3):
            card.step()
        nb += 1
    # the falling edge
    armed, s1, e = False, None, None
    for _ in range(6000):
        card.step()
        m = card.mean()
        if m >= edge + 2:
            armed, s1 = True, None
        elif m == edge + 1 and s1 is None:
            s1 = card.t
        elif m <= edge and s1 is not None:
            e = card.t
            break
    ch_t0 = card.t
    f66 = None
    after = 0
    nlaunch = 0
    rcs = []
    def one_launch(secs):
        nonlocal f66, after
        ts = card.t
        card.step()
        card.step()
        t_first = card.t
        hl = [{"launch": -1, "t_start_ms": int(card.t), "t_end_ms": int(card.t + 20), "iters": 20000, "wall_s": 0.02, "ghz": 0.6}]
        tt = card.t + 20
        k = 0
        steps = int(secs * 10)
        for i in range(steps):
            card.step(dP, kap, conc, io)
            if f66 is None and card.mean() >= 66:
                f66 = card.t
            if i % 5 == 4:
                hl.append({"launch": k, "t_start_ms": int(tt), "t_end_ms": int(tt + 500), "iters": 549000 * (1 + 0.002 * card.rng.gauss(0, 1)),
                           "wall_s": 0.5, "ghz": 0.6})
                tt += 500
                k += 1
        te = card.t
        card.step()
        launches.append({"run": str(idx), "kind": "chain" if tier == "L" else "single", "t_start_ms": int(ts), "t_end_ms": int(card.t), "rc": 0})
        for h in hl:
            lines.append("SPARSITY " + json.dumps(dict(h, minions=r["minions"], shire_mask=r["mask"], test="fma")))
        if f66 is not None and t_first >= f66:
            after += 1
        rcs.append(0)
    if tier == "L":
        while True:
            if f66 is not None and after >= 2:
                break
            if card.t - ch_t0 + 3000 > 150000:
                break
            one_launch(2.0)
            nlaunch += 1
    else:
        one_launch(7.0)
        nlaunch = 1
        for _ in range(100):
            card.step()
    rec = {"idx": idx, "slot": slot, "attempt": 1, "role": role, "name": name, "mask": r["mask"], "per_shire": r["per_shire"],
           "minions": r["minions"], "tier": tier, "edge": edge, "target": target, "preheat_bursts": nb, "edge_ok": e is not None,
           "s1_ms": s1, "edge_ms": e, "tau_c_s": (e - s1) / 1000.0 if e and s1 and armed else None, "chain_t0_ms": ch_t0,
           "chain_t1_ms": card.t, "launches": nlaunch, "rcs": rcs, "first66_live_ms": f66, "stop": None}
    with gzip.open(os.path.join(out, "tel-%d.jsonl.gz" % idx), "wt") as f:
        for s in card.tel:
            f.write(json.dumps(s) + "\n")
    with gzip.open(os.path.join(out, "heater-%d.out.gz" % idx), "wt") as f:
        f.write("\n".join(lines) + "\n")
    return rec


def block(root, card_name, card, pass_no, rng):
    os.environ["HP_DATA_DIR"] = os.path.join(root, card_name)        # V0's edge rule reads the earlier V0 blocks
    info, runs, P = H.plan(pass_no, card_name, first_of_session=False)
    out = os.path.join(root, card_name, "hp", "p%d" % pass_no)
    os.makedirs(out, exist_ok=True)
    if info.get("skip"):                  # as block.sh: a skipped block ends ok with its plan only
        json.dump({"info": info, "runs": [], "params": P}, open(os.path.join(out, "plan.json"), "w"))
        json.dump({"exp": "hp", "pass": pass_no, "card": card_name, "status": "ok", "t1_ms": int(card.t),
                   "note": "skipped: %s" % info["skip"]}, open(os.path.join(out, "block.json"), "w"))
        return out
    PL = H.placements()["runs"]
    launches, recs = [], []
    for i, r in enumerate(runs):
        recs.append(run(card, out, i + 1, i + 1, r["role"], r["name"], r["tier"], r["edge"], r["target"], launches, None, PL))
    json.dump({"info": info, "runs": runs, "params": P}, open(os.path.join(out, "plan.json"), "w"))
    with open(os.path.join(out, "runs.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(out, "launches.jsonl"), "w") as f:
        for l in launches:
            f.write(json.dumps(l) + "\n")
    json.dump({"exp": "hp", "pass": pass_no, "card": card_name, "status": "ok", "t1_ms": int(card.t)},
              open(os.path.join(out, "block.json"), "w"))
    # rest between blocks
    for _ in range(3000):
        card.step(record=False)
    return out


def main():
    root = sys.argv[1]
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1
    card = sys.argv[sys.argv.index("--card") + 1] if "--card" in sys.argv else "aifoundry3"
    rng = random.Random(seed)
    if "--passes" in sys.argv:            # any card (aifoundry3: e.g. the R1b scouting blocks 1601-1603)
        passes = [int(p) for p in sys.argv[sys.argv.index("--passes") + 1].split(",")]
    elif card == "aifoundry3":
        passes = [1101, 1102, 1103, 1201, 1202, 1203, 2301, 2302, 2303, 2401, 2402, 2403,
                  3101, 3102, 3103, 3201, 3202, 3203, 3301, 3302, 3303, 3401, 3402, 3403]
    else:
        raise SystemExit("--passes is required for %s" % card)
    c = Card(card, rng)
    if "--drop" in sys.argv:              # --drop PASS:NAME[,...]: leave a placement's runs out of a block (tests)
        drops = [x.split(":") for x in sys.argv[sys.argv.index("--drop") + 1].split(",")]
    else:
        drops = []
    for p in passes:
        out = block(root, card, c, p, rng)
        for dp, name in drops:
            if int(dp) == p:
                rp = os.path.join(out, "runs.jsonl")
                keep = [l for l in open(rp) if json.loads(l).get("name") != name]
                open(rp, "w").write("".join(keep))
    print("%s: %d blocks" % (card, len(passes)))


if __name__ == "__main__":
    main()
