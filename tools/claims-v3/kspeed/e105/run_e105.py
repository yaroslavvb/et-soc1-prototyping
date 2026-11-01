#!/usr/bin/env python3
"""E105 (Q132): the session runner. It IS E101 session 2's run_e101s.py (E80's run_kspeed.py, E64's run_hpl.py), imported and run unchanged, with one addition: the registered admission rule, which decides before each run whether its cell may be launched.

THE RULE (E105.md, "The power limit"). A cell in protocol.json's `admission` table carries its reference c (mm16's, measured by E101, c_ref_w) and either
  * "fixed_p800_w": an estimate frozen from what E101 measured (cells of the as-run layout, the zero and low-power kinds), or
  * "probe": the label of a lower-power cell of the same layout and format, run earlier in the session. rho = (the probe's measured c) / (the probe's c_ref), and the estimate is B_800 + s_800 x c_ref x rho.
The cell runs if its estimate is <= limit_p800_w (88 W, E101's rule). A probe that did not measure refuses the cell. After any run whose board reading reached peak_lock_w (93 W), no cell with an estimate at or above that run's goes on. A refused cell is written to skipped.jsonl and its run does not happen: nothing else changes.

The measured c: the upper quartile of the board readings at >= 790 MHz between 0.3 s and 3.5 s after the run's first launch began, (P - B_800) / s_800, at least 3 samples. Upper, because a held reading from a lower clock can only pull it down, and a low c would admit too much: on E101's own bursts the median read one mm16 int8 run 10 W low. Every other safety path (97 W on three samples, 85 C, the other-user checks, the lock) is run_hpl.py's, unchanged.

    python3 run_e105.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e101"))
import run_e101s as RS  # noqa: E402

H = RS.H
_base_run_one = H.Session.run_one


def base_label(lab):
    return re.sub(r"-rep\d+$", "", lab)


class Admission:
    def __init__(self, proto, rundir):
        self.table = proto.get("admission", {})
        self.limit = proto.get("limit_p800_w", 88.0)
        self.lock_w = proto.get("peak_lock_w", 93.0)
        self.B800, self.S800 = proto["relation"]["B800"], proto["relation"]["s800"]
        self.state_path = os.path.join(os.path.dirname(os.path.abspath(rundir)), "admission.json")
        self.state = {"rho": {}, "lock_est": None, "seen": {}}
        if os.path.exists(self.state_path):
            self.state = json.load(open(self.state_path))

    def save(self):
        tmp = self.state_path + ".tmp"
        json.dump(self.state, open(tmp, "w"), indent=1)
        os.replace(tmp, self.state_path)

    def estimate(self, label):
        """(estimate W, how), estimate None when the rule cannot say."""
        e = self.table.get(base_label(label))
        if e is None:
            return None, "not in the table"
        if "fixed_p800_w" in e:
            return e["fixed_p800_w"], "fixed"
        pr = e["probe"]
        rho = self.state["rho"].get(pr)
        if rho is None:
            return None, f"probe {pr} has no measure"
        return round(self.B800 + self.S800 * e["c_ref_w"] * rho, 2), f"probe {pr} rho {rho}"

    def why_not(self, label):
        est, how = self.estimate(label)
        if base_label(label) not in self.table:
            return "not in the admission table", est, how
        if est is None:
            return how, est, how
        if est > self.limit:
            return f"estimate {est} W > {self.limit} W", est, how
        lock = self.state.get("lock_est")
        if lock is not None and est >= lock:
            return f"estimate {est} W >= {lock} W, the estimate of a run that read {self.lock_w} W", est, how
        return None, est, how

    def after(self, sess, r, rec, est):
        tel = os.path.join(sess.rundir, rec["tel"])
        rows = []
        try:
            for ln in open(tel, "rb"):
                if ln.startswith(b"{"):
                    t = H.parse_tel(ln)
                    if t is not None:
                        rows.append(t)
        except OSError:
            return
        peak = max((x[3] for x in rows if x[3] is not None), default=None)
        t0 = None
        try:
            for ln in open(os.path.join(sess.rundir, "launches.jsonl")):
                d = json.loads(ln)
                if d.get("run") == r.name and d.get("role") == "work" and d.get("sparsity"):
                    t0 = d["sparsity"][0].get("t_start_ms")
                    break
        except (OSError, ValueError):
            pass
        c = None
        if t0 is not None:
            w = [x[3] for x in rows if t0 + 300 <= x[0] <= t0 + 3500 and x[3] is not None and x[4] is not None and x[4] >= 790]
            if len(w) >= 3:
                w.sort()
                c = (w[int(0.75 * (len(w) - 1))] - self.B800) / self.S800
        lab = base_label(r.label)
        e = self.table.get(lab, {})
        rec2 = {"run": r.name, "peak_w": peak, "c_w": None if c is None else round(c, 3), "est_w": est}
        if c is not None and e.get("c_ref_w") and lab not in self.state["rho"]:
            self.state["rho"][lab] = round(c / e["c_ref_w"], 4)
            rec2["rho"] = self.state["rho"][lab]
        self.state["seen"][r.name] = rec2
        if peak is not None and peak >= self.lock_w and est is not None:
            lock = self.state.get("lock_est")
            self.state["lock_est"] = est if lock is None else min(lock, est)
            sess.mark("e105_peak_lock", json.dumps(rec2))
        self.save()
        sess.say(f"    e105: {json.dumps(rec2)}")


ADM = {}


def _run_one(self, r, k, n):
    adm = ADM["adm"]
    why, est, how = adm.why_not(r.label)
    if why is not None:
        rec = {"run": r.name, "label": r.label, "block": r.block, "t_ms": int(time.time() * 1000), "why": why, "est_w": est, "how": how}
        self.jsonl("skipped.jsonl", rec)
        self.mark("e105_not_admitted", json.dumps(rec))
        self.say(f"[{k}/{n}] {r.name}: NOT ADMITTED: {why}")
        return None
    self.say(f"    e105: admitted, estimate {est} W ({how})")
    rec = _base_run_one(self, r, k, n)
    adm.after(self, r, rec, est)
    return rec


H.Session.run_one = _run_one


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        ADM["adm"] = Admission(proto, rd)
        os.makedirs(rd, exist_ok=True)
        if not os.path.exists(os.path.join(rd, "e105.json")):
            json.dump({"experiment": "E105", "wrapper": os.path.relpath(os.path.abspath(__file__), RS.ROOT), "wrapper_sha256": RS.sha256(__file__), "protocol_sha256": RS.sha256(pr),
                       "run_e101s_sha256": RS.sha256(RS.__file__), "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e105.json"), "w"), indent=1)
    return RS.main()


if __name__ == "__main__":
    sys.exit(main())
