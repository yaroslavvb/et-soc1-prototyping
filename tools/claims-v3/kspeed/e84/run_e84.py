#!/usr/bin/env python3
"""E84 (Q130): the session runner for aifoundry1's card 0. It IS E80's runner, ../run_kspeed.py (E64's
tools/claims-v3/hpl/run_hpl.py plus `file:` tiles checked against kinds.json), imported and run unchanged except for
the five places where run_hpl.py names aifoundry2's single card. Each is replaced here, and nothing else is:

  1. the card. ET_DEVICES=0 is set before anything starts, so every child process (the sampler, every launch, every
     management query) opens card 0 only, which the device layer then calls device 0 (lib.sh:22-25). V3_DEVICE or
     ET_DEVICES set to anything else refuses the session. The card lock stays /run/lock/etsoc-shire0.lock.
  2. preflight: the host must be aifoundry1, the heater aifoundry1's own build/sparsity (lib.sh:35-43; build/sparsity_t2
     exists only on aifoundry2), the ettelem build/ettelem-e84 (tools/claims-v3/dv2/ettelem-dv2 built on this host, so
     it honours ET_DEVICES and has the residency read), both cards' lock files present and et-holders answering.
  3. check_others (before the session and before every launch process), as lib.sh's others_present does on a host
     with several cards (its amendment A3): another user who is only logged in does NOT end the session (one lab user
     has kept idle sessions open there for days), but any of these does, on EITHER card: a device node or card lock
     held by another user (et-holders, the helper et-who runs), another user's device process or a running CI job
     (Runner.Worker), one of our own device processes or holders that is not this session's, or the et_soc1 module's
     use count over the baseline taken with only our sampler open (run_hpl's own test). Other users' login names are
     never recorded: a hit names the node or the program, and "other".
  4. drain (only after a failed sampler start or a sampler that ignored SIGTERM): the stock dev_mngt_service opens
     EVERY card's management node whatever -n says (14-card-behaviour.md), so it runs only while card 1's lock can be
     taken non-blocking too, held for the one call; otherwise the drain is deferred (lib.sh:126-143).
  5. the configuration check after every run: run_hpl ends the session unless the TDP and the threshold read 65; here
     they must equal what card 0 read at the session's start (the start read must carry both). Nothing is set either
     way: the check only ends the session if something outside it changed the card.

Everything else that touches the card is run_hpl.py's own code, unchanged: the non-blocking card lock held for the
whole session, `timeout 10` on every device process with an explicit --kernel and --stop-file, the sampler WITHOUT
--reset-ms (stopped with SIGTERM), the trace ring, residencies and `ettelem config` read after every run with the
sampler stopped, the safety stops (a die reading of 85 C, or a board reading over 97 W on three samples, touches the
stop file and ends the session), RUNDIR/STOP, and the card-minute cap. Nothing is set on the card: no TDP, threshold,
clock, voltage, log level or reset.

Before the session it writes <RUNDIR>/e84.json (this wrapper's sha256, the protocol's and predictions.json's, the
freeze commit from E84_FREEZE), beside run_kspeed.py's kspeed.json and run_hpl.py's session.json.

    python3 run_e84.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import errno
import fcntl
import hashlib
import json
import os
import shutil
import socket
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CARD = "0"
HOST = "aifoundry1"
OTHER_LOCK = "/run/lock/etsoc-shire1.lock"
HOLDERS = ["sudo", "-n", "/usr/local/sbin/et-holders"]
HEATER_TAIL = os.path.join("build", "sparsity", "host", "sparsity_host")

for var in ("V3_DEVICE", "ET_DEVICES"):
    if os.environ.get(var, CARD) != CARD:
        print(f"refused: {var}={os.environ[var]}; E84 runs on card {CARD} only", file=sys.stderr)
        sys.exit(2)
os.environ["ET_DEVICES"] = CARD     # (1) inherited by every child: the sampler, the launches, the queries
os.environ["V3_DEVICE"] = CARD

sys.path.insert(0, os.path.join(HERE, ".."))
import run_kspeed as K  # noqa: E402

H = K.H
H.CARD_HOST = HOST
H.LOCK_PATH = "/run/lock/etsoc-shire0.lock"


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def holders():
    """(rc, [(node_or_lock, user, pid)]) from et-holders; it never opens a card node (fuser only)."""
    rc, out, _ = H.run_out(HOLDERS, timeout=20)
    rows = []
    for ln in out.decode(errors="replace").splitlines():
        f = ln.split()
        if len(f) >= 3 and (f[0].startswith("/dev/et") or f[0].startswith("lock:")):
            try:
                rows.append((f[0], f[1], int(f[2])))
            except ValueError:
                rows.append((f[0], f[1], -1))
    return rc, rows


# ---------------------------------------------------------------------------------------------- (2) preflight
def preflight(self):
    pf = []
    host = socket.gethostname().split(".")[0]
    if not self.dry:
        if host != HOST:
            pf.append(f"hostname {host!r} is not {HOST!r}")
        if os.environ.get("ET_DEVICES") != CARD:
            pf.append("ET_DEVICES is not 0")
        if not shutil.which("timeout"):
            pf.append("no `timeout` on PATH")
        for label, p in (("heater", self.heater), ("kernel", self.kernel), ("ettelem", self.ettelem)):
            if not os.path.isfile(p):
                pf.append(f"missing {label} {p}")
        if not self.heater.endswith(os.sep + HEATER_TAIL):
            pf.append("the heater must be aifoundry1's build/sparsity (lib.sh:35-43)")
        if os.path.dirname(os.path.dirname(self.heater)) != os.path.dirname(os.path.dirname(self.kernel)):
            pf.append("heater and kernel come from different builds")
        if os.path.isfile(self.heater):
            blob = open(self.heater, "rb").read()
            for flag in (b"--stop-file", b"--kernel", b"--budget", b"file:"):
                if flag not in blob:
                    pf.append(f"heater has no {flag.decode()}")
        if os.path.isfile(self.ettelem):
            blob = open(self.ettelem, "rb").read()
            for word in (b"residency", b"sptrace", b"config"):
                if word not in blob:
                    pf.append(f"ettelem {self.ettelem} has no {word.decode()} (build ettelem-dv2 into build/ettelem-e84)")
        for lk in (H.LOCK_PATH, OTHER_LOCK):
            if not os.path.exists(lk):
                pf.append(f"no card lock {lk}")
        rc, _ = holders()
        if rc != 0:
            pf.append(f"et-holders does not answer (rc {rc})")
    if os.path.exists(os.path.join(self.rundir, "session.json")):
        pf.append(f"{self.rundir} already holds a session")
    if pf:
        raise H.Refuse("; ".join(pf))


# ---------------------------------------------------------------------------------------------- (3) others
def check_others(self, where):
    if self.dry:
        return
    hits = []
    me = H.me_user()
    mine = {os.getpid()} | self.heater_pids
    if self.sampler is not None:
        mine.add(self.sampler.pid)
    rc, out, _ = H.run_out(["who"])
    n_other = sum(1 for ln in out.decode(errors="replace").splitlines() if ln.split() and ln.split()[0] != me)
    if where == "start":
        self.mark("logins", f"{n_other} login sessions of other users: not a hit on a two-card host (lib.sh A3)")
    rc, rows = holders()
    if rc != 0:
        hits.append(f"et_holders_rc:{rc}")
    for node, user, pid in rows:
        if user != me:
            hits.append(f"holder:{node}:other")
        elif pid not in mine:
            # the lab's live collector reads each card for ~4 ms a second, as this user, ONLY while nobody holds any
            # card node or lock on the machine (its reader is a copy of ettelem named lab-monitor); such a read seen
            # before our lock is taken is recorded, not a hit. Any other process of ours is a hit.
            try:
                comm = open(f"/proc/{pid}/comm").read().strip()
            except OSError:
                comm = ""
            if comm == "lab-monitor":
                self.mark("collector_read", f"{where}: {node} pid {pid}")
            else:
                hits.append(f"ours_not_this_session:{node}:{pid}:{comm}")
    rc, out, _ = H.run_out(["ps", "-eo", "uid=,pid=,state=,comm="])
    for ln in out.decode(errors="replace").splitlines():
        f = ln.split(None, 3)
        if len(f) != 4:
            continue
        try:
            u, pid = int(f[0]), int(f[1])
        except ValueError:
            continue
        if f[2].strip().upper().startswith("Z") or pid in mine:
            continue
        comm = os.path.basename(f[3].strip())
        if u != os.getuid() and H.OTHER_COMM.search(comm):
            hits.append(f"proc:other:{comm}")
        elif u == os.getuid() and H.DEV_COMM.search(comm):
            hits.append(f"ours:{pid}:{comm}")
    n = self.modcount()
    if n is not None and self.ns_baseline is not None and n > self.ns_baseline:
        hits.append(f"et_soc1_use:{n}>{self.ns_baseline}")
    if hits:
        self.mark("other_user", f"{where}: " + "; ".join(hits))
        raise H.EndSession("other_user:" + ";".join(hits)[:200], H.EXIT_CARD)


# ---------------------------------------------------------------------------------------------- (4) drain
def drain(self):
    if self.dry:
        return
    try:
        fd = os.open(OTHER_LOCK, os.O_RDWR)
    except OSError as e:
        self.mark("drain_deferred", f"cannot open {OTHER_LOCK}: {e.strerror}")
        return
    os.set_inheritable(fd, False)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        os.close(fd)
        if e.errno in (errno.EACCES, errno.EAGAIN):
            self.say("drain deferred: card 1's lock is held")
            self.mark("drain_deferred", "card 1's lock is held")
            return
        raise
    try:
        self.say("draining the management queue (card 1's lock held for the one call)")
        H.run_out(["timeout", "20", H.DEVMNGT, "-m", "DM_CMD_GET_MODULE_POWER", "-n", CARD, "-u", "5000"],
                  timeout=25, env=dict(os.environ, LD_LIBRARY_PATH=H.ET_LIB))
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


# ---------------------------------------------------------------------------------------------- (5) config
_base_queries = H.Session.queries


def queries(self, tag):
    out = _base_queries(self, tag)
    if self.dry:
        return out
    cfg = out.get("config") or {}
    if tag == "start":
        if cfg.get("tdp_w") is None or cfg.get("temp_threshold_c") is None:
            self.mark("config_unread", json.dumps(cfg))
            raise H.EndSession(f"error:config_unread_at_start:{cfg}", H.EXIT_ERR)
        self.cfg0 = {"tdp_w": cfg["tdp_w"], "temp_threshold_c": cfg["temp_threshold_c"]}
        self.mark("config_start", json.dumps(cfg))
    return out


def run_one(self, r, k, n):
    """run_hpl.Session.run_one, line for line, except the configuration test at its end (see (5) above)."""
    tag = r.name
    tel = os.path.join(self.rundir, "tel", f"{tag}.jsonl")
    self.say(f"[{k}/{n}] {tag}: {r.processes} x {r.seconds:g} s, {r.minions} minions, start {r.start}")
    self.check_others(tag)
    if not self.start_sampler(tel, r.plan_s() + 900):
        raise H.EndSession("error:sampler_would_not_start", H.EXIT_ERR)
    self.sampler_t0 = H.now_ms()
    if not self.dry:
        self.ns_baseline = self.modcount()
        self.mark("use_count_baseline", str(self.ns_baseline))
    time.sleep(1.0)
    g = self.gate(r)
    self.say(f"    gate: {g}")
    launches = []
    t_first = H.now_ms()
    for p in range(r.processes):
        self.guard(tag)
        self.check_others(tag)
        cmd, rc, out, err, a, b = self.spawn_kernel(r)
        recs = []
        for ln in (out or "").splitlines():
            if ln.startswith("SPARSITY "):
                try:
                    recs.append(json.loads(ln[9:]))
                except ValueError:
                    pass
        launches.append({"proc": p, "rc": rc, "t_start_ms": a, "t_end_ms": b, "n_launch": len(recs)})
        self.jsonl("launches.jsonl", {"run": tag, "role": "work", "proc": p, "cmd": cmd, "rc": rc,
                                      "t_start_ms": a, "t_end_ms": b, "sparsity": recs,
                                      "stderr_tail": err[-400:] if err else ""})
        if rc != 0:
            self.say(f"    process {p} rc {rc}: {err[-200:] if err else ''}")
            if sum(1 for x in launches if x["rc"] != 0) >= 2:
                raise H.EndSession(f"error:kernel_failed:{tag}", H.EXIT_ERR)
    t_last = H.now_ms()
    tail_end = time.time() + r.tail_s
    while time.time() < tail_end:
        self.guard(tag)
        time.sleep(0.2)
    self.stop_sampler()
    q = self.queries(tag)
    rec = {"run": tag, "block": r.block, "idx": r.idx, "rep": r.rep, "label": r.label, "type": r.type,
           "values": r.values, "mask": f"0x{r.mask:08x}", "per_shire": r.per_shire, "minions": r.minions,
           "seconds": r.seconds, "processes": r.processes, "gate": g, "t_first_ms": t_first,
           "t_last_ms": t_last, "launches": launches, "queries": q, "tel": os.path.relpath(tel, self.rundir)}
    self.jsonl("runs.jsonl", rec)
    cfg = q.get("config") or {}
    want = getattr(self, "cfg0", None)
    if not self.dry and (want is None or cfg.get("tdp_w") != want["tdp_w"]
                         or cfg.get("temp_threshold_c") != want["temp_threshold_c"]):
        self.mark("config_changed", json.dumps({"now": cfg, "start": want}))
        raise H.EndSession(f"error:config_changed:{cfg}", H.EXIT_ERR)
    return rec


H.Session.preflight = preflight
H.Session.check_others = check_others
H.Session.drain = drain
H.Session.queries = queries
H.Session.run_one = run_one


def main():
    pred_path = os.path.join(HERE, "predictions.json")
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            proto = sys.argv[sys.argv.index("--protocol") + 1] if "--protocol" in sys.argv else None
            json.dump({"experiment": "E84", "card": f"{HOST}-c{CARD}", "et_devices": os.environ["ET_DEVICES"],
                       "wrapper": "tools/claims-v3/kspeed/e84/run_e84.py", "wrapper_sha256": sha256(__file__),
                       "protocol_sha256": sha256(proto) if proto and os.path.exists(proto) else None,
                       "predictions_sha256": sha256(pred_path) if os.path.exists(pred_path) else None,
                       "run_kspeed_sha256": sha256(K.__file__), "run_hpl_sha256": sha256(H.__file__),
                       "freeze_commit": os.environ.get("E84_FREEZE"), "argv": sys.argv},
                      open(os.path.join(rd, "e84.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
