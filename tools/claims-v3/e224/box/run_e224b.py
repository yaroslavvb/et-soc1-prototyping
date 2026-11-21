#!/usr/bin/env python3
"""E224 ARM B (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): E224 arm B's ONE SESSION on aifoundry2 card 0 under its
governor. It is E208's registered runner (src/run_mms.py, tools/claims-v3/e208/proposal/src/run_mms.py, its bytes UNCHANGED beside this file
and IMPORTED: every step, gate, read, wait, stop, record and file of E208's session is E208's code) with what E224's registration adds - E216's
run_e216.py (landed in 59f5288b, which ran E216 FULL on this card: 69 of 69 runs, data a8ce142d), line for line, with E224's numbers:

  1. THE STOP LINES registered for E224 arm B (E224.md 6; plan-e224.json > arms > B > live_stops): the board strictly above 70 W on 3 samples
     in a row, the shires' mean (minshire[0]) at or above 70 C, the hottest-sensor latch (minshire[2]) at or above 70 C once it has risen
     above its first reading of the session - E208's own class mms_common.Stops, unchanged, given E224's numbers in place of E208's 85 W /
     80 C for this card (E216's lines). The stop-path test (E208's) runs with them and records them as the real lines. mms_common.CARDS
     itself is never changed (E208's reducer, which the registration pins as arm B's measured side, imports it).
  2. THE LINE: no run starts whose planning peak is at or above 67.0 W (E224.md 6's drop line for arm B; the schedule's "e224b_line_w");
     E208's 80 W line stays the schedule reader's word (mms_common.load_sched, unchanged).
  3. FAMILY G, 'rgm136 gemmLnc' (E224.md 2): a run whose --values arm is gemmLnc<MB>x<NB>x<KB> (L-AF4's g01-g03, family D's d29 and d30, and the G block's smoke s03) runs
     rgm211's host (build/e224brgm211/host/sparsity_host, built today on this box by src/build_e224b.sh from E211's rgm211 sources at
     kernel-e224.json's pins) with rgm136's ELF (build/rgm/kernel/sparsity.elf, the --kernel E208's command line already names): the
     process's every other argument is E208's (mms_common.host_argv); only argv[0] differs. Every other run, the smoke and the ties are
     'rgm136 gemmL' on E208's host.
  4. THE IDENTITY GATE PER PROCESS (src/ident_e224b.py: E211's family gate in E215's form): right before every process of the session starts
     (the smoke's, the ties', every run's), its --kernel passes for its family: the .text pin AND the whole ELF pin (aace138c...). A
     refusal starts NO process: the run records the gate's words, and the session stops at once (THE IDENTITY GATE STOP: the hosts' stop
     file touched, nothing further starts); the gate's words for every process go to gates.jsonl in the session folder.
  5. THE WALK CHECK on every family-G process (E211's, by family: rgm211's host prints each launch's walk; 'rgm136 gemmLnc' reads walk "mn"
     and walk_ok true on every fma launch, the walk tag on no hart; the check record's walk "mn" and walk_launches_bad 0).
  6. THE KERNEL STOPS on family G (E211's for a kernel family new on the card): a G process whose identity gate failed, whose rc is not 0
     (a launch timeout, rc 124, among them), whose check of C is not exact or approx, with a tensor error on any launch, or whose walk check
     failed, STOPS THE SESSION at once (the hosts' stop file touched; nothing further starts). The G block runs last, its smoke s03 first
     (E224.md 6: "s03, the G block's own gate and stop path right before the G block"): a failed s03 ends the session before any G point,
     every run before it standing as measured.
  7. THE G BLOCK LAST: the schedule is refused (no session) unless every family-G run comes after every other run of the session.
  8. THE BOX CHECK, after E208's (unchanged): build/BUILD-e224b.json written today on aifoundry2, verdict BUILT, by src/build_e224b.sh;
     rgm211's host at the sha256 it records; the identity gate's own check (src/ident_e224b.py --check: CHECK PASS); rgm136's ELF passing for
     both families. Else no device is opened.
  9. THE SIZED PLAIN TIMEOUT (E224.md 6, E218's R0 lesson: f04 run 77): each run's host process under `timeout <T>`, T the schedule's
     "timeout_s" for that run (desk/timeouts-e224.json: 10 s for every E224 run; never -k); the smoke's processes and every
     other device call keep E208's `timeout 10`.
 10. --dry: rgm211's host's double is src/fake_card_e224b.py (E208's doubles, unchanged, imported, with the walk fields and the G knobs);
     every other double is E208's.
Nothing is ever killed: every child of this runner is E208's (its bounded waits end with SIGTERM and a grace; what outlives them is a
LEFTOVER, recorded and left). Every device command is a READ (E208's guard and host; rgm211's host opens the ops node only).

    python3 -B src/run_e224b.py session --card a2c0 --sched src/sched/a2c0-E224.json --t0 T0 --out sessions/<sid> [--deadline-epoch E]
    python3 -B src/run_e224b.py session --dry --scale 0.02 --card a2c0 --sched ... --t0 T0 --out <dir> [E208's --dry flags]
        [--g-walk-fail ID] [--g-check-wrong ID] [--g-tensor-error ID] [--g-slow ID] [--g-extra-w W]       E224's G knobs (--dry only)
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mms_common as C  # noqa: E402  (E208's, unchanged)
import run_mms as R  # noqa: E402  (E208's runner, unchanged)
import ident_e224b as I  # noqa: E402

ROOT = R.ROOT
E224B_STOPS = {"board_cap_w": 70.0, "cap_consecutive": 3, "abs_stop_c": 70.0}
E224B_LINE_W = 67.0
G_HOST = "build/e224brgm211/host/sparsity_host"
G_BUILD_REC = "build/BUILD-e224b.json"
FAM_L, FAM_G = "rgm136 gemmL", "rgm136 gemmLnc"
G_FLAGS = ("g_walk_fail", "g_check_wrong", "g_tensor_error", "g_slow")


def family_of_values(values):
    """'rgm136 gemmLnc' for a gemmLnc arm, 'rgm136 gemmL' for a gemmL arm, None for anything else (no E224 family)."""
    arm = (values or "").split(":", 1)[0]
    if arm.startswith("gemmLnc"):
        return FAM_G
    if arm.startswith("gemmLn"):
        return None
    if arm.startswith("gemmL"):
        return FAM_L
    return None


def check_sched(s):
    """'' when the schedule is E224 arm B's form, else why: E224's session word, its line, every run under 67.0 W, the G block last, every
    process run with a family, every run's timeout_s a plain one of at least 10 s."""
    bad = []
    if s.get("session") != "E224" or s.get("card") != "a2c0":
        bad.append("not E224's schedule for a2c0")
    if float(s.get("e224b_line_w") or 0) != E224B_LINE_W:
        bad.append(f"its e224b_line_w is {s.get('e224b_line_w')}, not {E224B_LINE_W}")
    over = [r["arm"] for r in s["runs"] + s["smoke"] if float(r.get("est_peak_w") or 0) >= E224B_LINE_W]
    if over:
        bad.append(f"runs at or over the {E224B_LINE_W} W line: {over}")
    tos = [r["arm"] for r in s["runs"] if r["form"] != "null" and not (isinstance(r.get("timeout_s"), int) and 10 <= r["timeout_s"] <= 20)]
    if tos:
        bad.append(f"runs with no plain timeout_s of 10-20 s: {tos[:5]}")
    fams = [None if r["form"] == "null" else family_of_values(r.get("values")) for r in s["runs"]]
    nofam = [r["arm"] for r, f in zip(s["runs"], fams) if r["form"] != "null" and f is None]
    nofam += [r["arm"] for r in s["smoke"] if family_of_values(r.get("values")) != FAM_L]
    if nofam:
        bad.append(f"processes with no E224 family (or a smoke not 'rgm136 gemmL'): {nofam}")
    gi = [k for k, f in enumerate(fams) if f == FAM_G]
    if gi and (gi != list(range(gi[0], len(fams))) or any(f == FAM_G for f in fams[:gi[0]])):
        bad.append("the G block is not last: a family-G run comes before a run of another family")
    for r in s["runs"]:
        fam_decl = r.get("family")
        if r["form"] != "null" and fam_decl not in (None, family_of_values(r.get("values"))):
            bad.append(f"{r['arm']}: its family {fam_decl!r} is not its arm's")
    return "; ".join(bad)


def walk_read(text):
    """THE WALK CHECK on one family-G process's stdout: (ok, words, record)."""
    sp = C.parse_sparsity(text)
    fma = [x for x in sp if x.get("test") == "fma"]
    chk = [x for x in sp if x.get("test") == "check"]
    rec = {"launches": len(fma), "walk": sorted({str(x.get("walk")) for x in fma}),
           "walk_ok_false": sum(1 for x in fma if x.get("walk_ok") is not True),
           "tagged": sum(int(x.get("walk_tagged") or 0) for x in fma),
           "check_walk": chk[-1].get("walk") if chk else None,
           "check_walk_launches_bad": chk[-1].get("walk_launches_bad") if chk else None}
    why = []
    if not fma:
        why.append("no launch record")
    if rec["walk"] and rec["walk"] != ["mn"]:
        why.append(f"walk {rec['walk']} (want mn)")
    if rec["walk_ok_false"]:
        why.append(f"{rec['walk_ok_false']} launch(es) with walk_ok not true")
    if rec["tagged"]:
        why.append(f"the walk tag on {rec['tagged']} hart(s) (want none)")
    if not chk:
        why.append("no check record")
    elif rec["check_walk"] != "mn" or rec["check_walk_launches_bad"] != 0:
        why.append(f"the check record's walk {rec['check_walk']!r}, walk_launches_bad {rec['check_walk_launches_bad']!r}")
    return (not why), ("; ".join(why) or "walk mn on every launch, no tag, walk_launches_bad 0"), rec


class Session(R.Session):
    def __init__(self, a):
        super().__init__(a)
        why = check_sched(self.sched)
        if why:
            raise ValueError(f"the schedule is not E224's: {why}")
        # E224's lines for this card, in this session only (E208's CARDS dict untouched)
        self.K = dict(self.K, stops=dict(E224B_STOPS), line_w=E224B_LINE_W)
        self.stops = C.Stops(**E224B_STOPS, trip_file=self.stop_file)
        self.kernel_stopped = None
        self.gate_f = open(os.path.join(self.out, "gates.jsonl"), "a")
        if self.dry:
            for k in G_FLAGS:
                v = getattr(a, k, "")
                if v:
                    self.env["E224B_FAKE_" + k[2:].upper()] = v
            if getattr(a, "g_extra_w", 0.0):        # E208's own trip knob, aimed at the G block alone (the double names G arms 'nc...')
                self.env.update(MMS_FAKE_TRIP=str(a.g_extra_w), MMS_FAKE_TRIP_ARM="nc")
        self.say(f"E224's lines: board above {E224B_STOPS['board_cap_w']:g} W on {E224B_STOPS['cap_consecutive']} samples, die or a risen "
                 f"latch at or above {E224B_STOPS['abs_stop_c']:g} C; line {E224B_LINE_W:g} W; family G on rgm211's host {G_HOST}")

    # ------------------------------------------------------------------ THE SIZED PLAIN TIMEOUT (the run's timeout_s; the smoke's: 10)
    def one_run(self, r):
        self.cur_timeout = int(r.get("timeout_s") or C.HOST_TIMEOUT_S)
        try:
            return super().one_run(r)
        finally:
            self.cur_timeout = C.HOST_TIMEOUT_S

    def host_cmd(self, argv):
        to = int(getattr(self, "cur_timeout", C.HOST_TIMEOUT_S) or C.HOST_TIMEOUT_S)
        return self.device_call(["timeout", str(to)] + argv)

    # ------------------------------------------------------------------ the doubles (--dry): rgm211's host's is E224's
    def device_call(self, real):
        if self.dry and real and real[0] == "timeout" and len(real) > 2 and real[2] == G_HOST:
            self.calls.write(" ".join(real) + "\n")
            self.calls.flush()
            print("DRY DEVICE CALL: " + " ".join(real), flush=True)
            return ["timeout", real[1], sys.executable, "-B", os.path.join(HERE, "fake_card_e224b.py"), "host"] + real[3:]
        return super().device_call(real)

    # ------------------------------------------------------------------ the gate, the walk and the kernel stops
    def gate_note(self, d, name, fam, ok, words):
        rec = {"t_ms": R.now_ms(), "proc": os.path.relpath(os.path.join(d, name), self.out), "family": fam, "ok": ok, "words": words}
        self.gate_f.write(json.dumps(rec) + "\n")
        self.gate_f.flush()
        return rec

    def kernel_stop(self, why, what="THE KERNEL STOP (family G)"):
        """the session stops at once (the hosts' stop file touched; nothing further starts): THE KERNEL STOP of a family-G process, or
        THE IDENTITY GATE STOP of any process whose gate refused it (what=...)"""
        if not self.kernel_stopped:
            self.kernel_stopped = f"{what}: {why}"
            self.stops.stop = self.stops.stop or f"{what}: {why}"
            self.mark("kernel_stop" if what.startswith("THE KERNEL") else "identity_gate_stop", why)
            try:
                with open(self.stop_file, "a"):
                    os.utime(self.stop_file, None)
            except OSError:
                pass
            self.say(f"{what}: {why}: nothing further starts")

    def run_proc(self, argv, d, name):
        vals = argv[argv.index("--values") + 1] if "--values" in argv else ""
        fam = family_of_values(vals)
        if fam == FAM_G:
            argv = [G_HOST] + list(argv[1:])
        elf = argv[argv.index("--kernel") + 1] if "--kernel" in argv else ""
        os.makedirs(d, exist_ok=True)
        if fam is None:
            ok, words = False, f"no E224 family for the arm {vals.split(':', 1)[0]!r}"
        else:
            ok, words = I.gate(fam, os.path.join(ROOT, elf))
        g = self.gate_note(d, name, fam, ok, words)
        if not ok:
            # NO PROCESS STARTS: the record E208's one_run and smoke read, with nothing launched
            t = R.now_ms()
            with open(os.path.join(d, name + ".gate"), "w") as f:
                f.write("GATE FAILED: " + words + "\n")
            self.kernel_stop(f"the identity gate refused {os.path.relpath(os.path.join(d, name), self.out)} ({fam}): {words}",
                             what="THE IDENTITY GATE STOP")
            return {"name": name, "argv": argv, "rc": None, "t0_ms": t, "t1_ms": t, "n_launch": 0, "launches_ok": False,
                    "check": None, "check_ok": False, "check_cycles_per_op": None, "stopped_by_file": False, "launch_window_ms": None,
                    "ident": {"stderr_targets": [], "stderr_ids": [], "nodes_held": [], "wrong": [], "right": False, "polls": 0,
                              "tripped": None},
                    "family": fam, "gate": g, "not_started": "the identity gate refused it: no process started"}
        p = super().run_proc(argv, d, name)
        p["family"], p["gate"] = fam, g
        if fam == FAM_G:
            text = open(os.path.join(d, name + ".out"), errors="replace").read()
            wok, wwords, wrec = walk_read(text)
            p["walk"] = dict(wrec, ok=wok, words=wwords)
            fma = [x for x in C.parse_sparsity(text) if x.get("test") == "fma"]
            why = []
            if p["rc"] != 0:
                why.append(f"rc {p['rc']}" + (f" (the launch timeout: its plain timeout {getattr(self, 'cur_timeout', 10)} ended it)" if p["rc"] == 124 else ""))
            if p["check"] not in ("exact", "approx") or not p["check_ok"]:
                why.append(f"its check of C {p['check']} (ok {p['check_ok']})")
            te = sum(int(x.get("tensor_errors") or 0) for x in fma)
            if te:
                why.append(f"{te} tensor error(s)")
            if not wok:
                why.append("the walk check: " + wwords)
            if why:
                self.kernel_stop(f"{os.path.relpath(os.path.join(d, name), self.out)}: " + "; ".join(why))
        return p

    # ------------------------------------------------------------------ the box check: E208's, then E224's
    def box_check(self):
        why = super().box_check()
        if why:
            return why
        bad = []
        try:
            rec = C.load(os.path.join(ROOT, G_BUILD_REC))
        except (OSError, ValueError):
            return f"no build record {G_BUILD_REC}: run src/build_e224b.sh first"
        host = socket.gethostname().split(".")[0]
        if rec.get("day") != R.pacific_day() or rec.get("verdict") != "BUILT" or rec.get("box") != self.K["box"] or host != rec.get("box"):
            bad.append(f"{G_BUILD_REC} is not today's BUILT on {self.K['box']} ({rec.get('day')}, {rec.get('verdict')}, {rec.get('box')})")
        p = os.path.join(ROOT, G_HOST)
        got = C.sha256(p) if os.path.isfile(p) else None
        if got is None or got != rec.get("host_sha256"):
            bad.append(f"{G_HOST}: sha256 {got}, want {rec.get('host_sha256')}")
        rc, out, err, left = self.bounded([sys.executable, "-B", os.path.join(HERE, "ident_e224b.py"), "--check"], 60, C.ETWHO_GRACE_S)
        with open(os.path.join(self.out, "ident-check.txt"), "w") as f:
            f.write((out or "") + (err or ""))
        if rc != 0 or left or "CHECK PASS" not in (out or ""):
            bad.append("the identity gate's check did not read CHECK PASS (ident-check.txt)")
        for fam in (FAM_L, FAM_G):
            ok, words = I.gate(fam, os.path.join(ROOT, C.ELF))
            if not ok:
                bad.append(f"{C.ELF} for {fam}: {words}")
        return "; ".join(bad)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("what", choices=["session"])
    parser.add_argument("--card", choices=["a2c0"], required=True)
    parser.add_argument("--sched", required=True)
    parser.add_argument("--t0", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--deadline-epoch", type=int, default=0)
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--only", type=int, default=0)
    parser.add_argument("--trip-arm", default="")
    parser.add_argument("--trip-w", type=float, default=0.0)
    parser.add_argument("--config-fail", action="store_true")
    parser.add_argument("--wrong-card", action="store_true")
    parser.add_argument("--stop-after", type=int, default=0)
    parser.add_argument("--host-hang", default="")
    parser.add_argument("--sampler-stall", type=int, default=0)
    parser.add_argument("--wrong-config", action="store_true")
    parser.add_argument("--host-fail-after", type=int, default=0)
    parser.add_argument("--config-hang", choices=["", "start", "end"], default="")
    parser.add_argument("--holder-after", type=int, default=0)
    parser.add_argument("--closing-holder", action="store_true")
    parser.add_argument("--g-walk-fail", default="")
    parser.add_argument("--g-check-wrong", default="")
    parser.add_argument("--g-tensor-error", default="")
    parser.add_argument("--g-slow", default="")
    parser.add_argument("--g-extra-w", type=float, default=0.0)
    a = parser.parse_args(argv)
    desk = (a.scale != 1.0 or a.only or a.trip_arm or a.config_fail or a.wrong_card or a.stop_after or a.host_hang or a.sampler_stall
            or a.wrong_config or a.host_fail_after or a.config_hang or a.holder_after or a.closing_holder or a.g_walk_fail
            or a.g_check_wrong or a.g_tensor_error or a.g_slow or a.g_extra_w)
    if not a.dry and desk:
        print("refused: --scale, --only, E208's desk flags and E224's --g-* flags are read with --dry only")
        return 2
    os.chdir(ROOT)
    return Session(a).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
