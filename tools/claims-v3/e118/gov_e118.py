#!/usr/bin/env python3
"""E118: pin aifoundry1 card 0 at its vmin-LUT floor by setting the static TDP level to 0, and put it back.
E72's gov_e72.py, adapted to a two-card host and to the no-PMIC-read profile (README "Departures from E72").

    python3 tools/claims-v3/e118/gov_e118.py gates   --out <dir>      # live gates, no write
    python3 tools/claims-v3/e118/gov_e118.py pin     --out <dir> [--deadline-s 4500]
    python3 tools/claims-v3/e118/gov_e118.py restore --out <dir>
    python3 tools/claims-v3/e118/gov_e118.py ring    --out <dir> --tag <name>
    python3 tools/claims-v3/e118/gov_e118.py readback --out <dir> --tag <name>

Exactly ONE firmware field is written: DM_CMD_SET_MODULE_STATIC_TDP_LEVEL (26), only ever with the literal 0 or 65,
on card 0 (-n 0). The software temperature threshold is never written; a threshold that does not read 65 C is a stop.
- Every stock dev_mngt_service call (the set, the restore, the watchdog's restore, the vmin-LUT read) holds BOTH card
  locks, /run/lock/etsoc-shire0.lock and etsoc-shire1.lock, because that binary opens both cards' management nodes
  whatever -n says (field manual, hosts section 4; E84's identity read). A refusal of either lock is a refusal.
- Reads go through build/ettelem-e118/ettelem (E118-NO-PMIC-READ; card 0 only through ET_DEVICES=0) under card 0's
  lock: `config` = the TDP, threshold, power-state and frequency GETs (RAM and PLL registers; no PMIC), `uptime`,
  `sptrace` (the SP trace ring, read only; never a trace reset).
- Identity by continuity: no firmware-revisions query (it is a PMIC firmware-management command at 836a4ab). The
  module uptime must show no service-processor reset since E84's read (31 Oct 2026 15:42:00 PDT, 5 d 0 h 40 m).
- The vmin-LUT floor is parsed IN CODE from the binary file DM_CMD_GET_VMIN_LUT writes (E72's text parse found
  nothing): 18-byte points, the frequency the first little-endian uint16 of each; the floor must be 600 MHz.
- A deadline watchdog is armed before the set: after `release` appears it exits; at the deadline it retries the
  restore (both locks, flock -w 120) every 30 s until the TDP reads 65, for up to 6 h. It never resets anything,
  never raises the cap and never addresses card 1.
"""
import argparse
import fcntl
import json
import os
import struct
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
ET_LIB = "/opt/et/lib"
DEVMNGT = "/opt/et/bin/dev_mngt_service"
ETT = os.path.join(ROOT, "build/ettelem-e118/ettelem")
LOCK0 = "/run/lock/etsoc-shire0.lock"
LOCK1 = "/run/lock/etsoc-shire1.lock"
NODE = "0"
TDP_PIN_W = 0
ORIG_TDP_W = 65
ORIG_THR_C = 65
PIN_MHZ = 600
# E84's identity read of card 0 (docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/ident/ident-154200.out)
E84_READ_EPOCH = 1793486520.286          # 2026-10-31 15:42:00.286 PDT, the uptime line's t_ms
E84_UPTIME_MIN = 5 * 1440 + 0 * 60 + 40  # 5 d 0 h 40 m


def iso(t=None):
    t = time.time() if t is None else t
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t)) + f".{int((t % 1) * 1000):03d}" + time.strftime("%z", time.localtime(t))


def env():
    return dict(os.environ, LD_LIBRARY_PATH=ET_LIB, ET_DEVICES="0")


def run(argv, timeout=25, cwd=None):
    t0 = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=env(), cwd=cwd or ROOT, stdin=subprocess.DEVNULL)
        return p.returncode, p.stdout.decode(errors="replace"), p.stderr.decode(errors="replace"), t0
    except subprocess.TimeoutExpired:
        return -9, "", "timeout", t0
    except OSError as e:
        return -1, "", str(e), t0


def jsonl(out, rec):
    rec = dict(rec)
    rec.setdefault("t_iso", iso())
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "gov.jsonl"), "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


class Locks:
    """Exclusive locks, taken non-blocking (retried every 2 s up to wait_s). Card 0's alone for ettelem reads;
    both for any stock dev_mngt_service call."""

    def __init__(self, paths, wait_s=0):
        self.paths, self.wait_s, self.fds = paths, wait_s, []

    def __enter__(self):
        deadline = time.time() + self.wait_s
        while True:
            fds = []
            try:
                for p in self.paths:
                    fd = os.open(p, os.O_RDWR)
                    fds.append(fd)
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.fds = fds
                return self
            except OSError:
                for fd in fds:
                    try:
                        fcntl.flock(fd, fcntl.LOCK_UN)
                    except OSError:
                        pass
                    os.close(fd)
                if time.time() >= deadline:
                    raise SystemExit(f"error:lock_refused:{self.paths}")
                time.sleep(2)

    def __exit__(self, *a):
        for fd in self.fds:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)
        self.fds = []
        return False


def last_json(text):
    for line in reversed(text.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def read_config():
    """ettelem-e118 config: the TDP, threshold, power-state and frequency GETs. Caller holds card 0's lock."""
    rc, so, se, t0 = run(["timeout", "20", ETT, "config"])
    cfg = last_json(so) if rc in (0, 1) else None
    ident = {}
    for line in (so + se).splitlines():   # the device layer's banner names the node and the PCI address it opened
        for key, tag in (("PCIe target:", "node"), ("PCIBUS device name:", "bdf")):
            if line.strip().startswith(key):
                ident[tag] = line.split(":", 1)[1].strip()
    return cfg, {"rc": rc, "t_iso": iso(t0), "stderr_tail": se[-200:], **ident}


def read_uptime():
    rc, so, se, t0 = run(["timeout", "20", ETT, "uptime"])
    u = last_json(so)
    return u, {"rc": rc, "t_iso": iso(t0)}


def continuity(u):
    """No service-processor reset since E84's read: the module uptime now must be at least E84's plus the wall time
    since, less 2 minutes (minute resolution on both reads)."""
    if not u or u.get("rc") != 0:
        return False, "uptime unreadable"
    now_min = u["day"] * 1440 + u["hours"] * 60 + u["mins"]
    expect = E84_UPTIME_MIN + (u["t_ms"] / 1000.0 - E84_READ_EPOCH) / 60.0
    ok = now_min >= expect - 2
    return ok, f"module uptime {now_min} min; E84's {E84_UPTIME_MIN} min + {expect - E84_UPTIME_MIN:.1f} min since = {expect:.1f}"


def dm(cmd, *extra, cwd=None):
    """One stock dev_mngt_service call on card 0. Caller holds BOTH locks. Only two commands can ever be sent."""
    if cmd not in ("DM_CMD_GET_VMIN_LUT", "DM_CMD_SET_MODULE_STATIC_TDP_LEVEL"):
        raise SystemExit(f"error:command_not_allowed:{cmd}")
    if cmd == "DM_CMD_SET_MODULE_STATIC_TDP_LEVEL" and list(extra) not in (["-l", "0"], ["-l", "65"]):
        raise SystemExit(f"error:tdp_value_not_allowed:{extra}")
    argv = ["timeout", "20", DEVMNGT, "-m", cmd, "-n", NODE, *extra, "-u", "5000"]
    rc, so, se, t0 = run(argv, cwd=cwd)
    return argv, rc, so, se, t0


def vmin_floor(out):
    """DM_CMD_GET_VMIN_LUT writes the LUT to a binary file; parse it in code. Only the frequency of each point is kept."""
    lutdir = os.path.join(out, "lut")
    os.makedirs(lutdir, exist_ok=True)
    for f in os.listdir(lutdir):
        os.remove(os.path.join(lutdir, f))
    argv, rc, so, se, t0 = dm("DM_CMD_GET_VMIN_LUT", cwd=lutdir)
    files = sorted(f for f in os.listdir(lutdir) if f.endswith(".bin"))
    rec = {"argv": argv, "rc": rc, "t_iso": iso(t0), "files": files, "stdout_tail": so[-300:], "stderr_tail": se[-300:]}
    if rc != 0 or not files:
        return None, rec
    import hashlib
    blob = open(os.path.join(lutdir, files[0]), "rb").read()
    pts = []
    for i in range(len(blob) // 18):
        f = struct.unpack_from("<H", blob, i * 18)[0]
        if any(blob[i * 18:(i + 1) * 18]):
            pts.append(f)
    rec.update({"file": files[0], "file_bytes": len(blob), "file_sha256": hashlib.sha256(blob).hexdigest(),
                "point_size_bytes": 18, "nonzero_points_mhz": pts})
    sane = pts and all(100 <= f <= 1600 for f in pts)
    return (min(pts) if sane else None), rec


def set_tdp(out, w, why):
    """Write one field (both locks held by the caller), read it back through ettelem-e118 config."""
    assert w in (TDP_PIN_W, ORIG_TDP_W)
    argv, rc, so, se, t0 = dm("DM_CMD_SET_MODULE_STATIC_TDP_LEVEL", "-l", str(int(w)))
    sent = {"cmd": argv, "rc": rc, "t_iso": iso(t0), "stdout_tail": so[-500:], "stderr_tail": se[-300:]}
    after, meta = read_config()
    return sent, after, meta


def watchdog(out, deadline_s):
    rel = os.path.join(out, "release")
    log = os.path.join(out, "watchdog.log")
    sh = os.path.join(out, "watchdog.sh")
    with open(sh, "w") as f:
        f.write(f"""#!/usr/bin/env bash
# E118 deadline watchdog: put card 0's TDP back to {ORIG_TDP_W} W unless the session released it first.
set -u
REL={rel!r}; LOG={log!r}
end=$(( $(date +%s) + {int(deadline_s)} ))
while [ "$(date +%s)" -lt "$end" ]; do
  [ -e "$REL" ] && {{ echo "$(date -Is) released by the session, nothing to do" >> "$LOG"; exit 0; }}
  sleep 10
done
echo "$(date -Is) DEADLINE reached, restoring card 0's TDP {ORIG_TDP_W} W" >> "$LOG"
stop=$(( $(date +%s) + 21600 ))
while [ "$(date +%s)" -lt "$stop" ]; do
  [ -e "$REL" ] && {{ echo "$(date -Is) released meanwhile" >> "$LOG"; exit 0; }}
  /usr/bin/flock -w 120 {LOCK0!r} /usr/bin/flock -w 120 {LOCK1!r} env LD_LIBRARY_PATH={ET_LIB} timeout 20 {DEVMNGT} \\
    -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n {NODE} -l {ORIG_TDP_W} -u 5000 >> "$LOG" 2>&1 < /dev/null
  echo "$(date -Is) set rc=$?" >> "$LOG"
  got=$(/usr/bin/flock -w 120 {LOCK0!r} env LD_LIBRARY_PATH={ET_LIB} ET_DEVICES=0 timeout 20 {ETT!r} config 2>/dev/null < /dev/null | grep '^{{' | tail -1)
  echo "$(date -Is) read back: $got" >> "$LOG"
  case "$got" in *'"tdp_w":{ORIG_TDP_W},'*) echo "$(date -Is) restored" >> "$LOG"; touch "$REL"; exit 0 ;; esac
  sleep 30
done
echo "$(date -Is) GAVE UP after 6 h" >> "$LOG"
""")
    p = subprocess.Popen(["setsid", "nohup", "bash", sh], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    jsonl(out, {"event": "watchdog_armed", "pid": p.pid, "deadline_s": int(deadline_s), "script": sh, "release_file": rel})
    return p.pid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["gates", "pin", "restore", "ring", "readback"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-s", type=int, default=4500)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    if not os.access(ETT, os.X_OK) or b"E118-NO-PMIC-READ" not in open(ETT, "rb").read():
        raise SystemExit(f"error:{ETT} is not the E118-NO-PMIC-READ build")

    if a.stage == "gates":
        verdict = []
        with Locks([LOCK0]):
            cfg, m1 = read_config()
            u, m2 = read_uptime()
        jsonl(out, {"event": "original", "config": cfg, "meta": m1})
        ok, why = continuity(u)
        jsonl(out, {"event": "uptime", "uptime": u, "meta": m2, "continuity": ok, "why": why})
        with Locks([LOCK0, LOCK1]):
            floor, lut = vmin_floor(out)
        jsonl(out, {"event": "vmin_floor", "floor_mhz": floor, "lut": lut})
        if cfg is None:
            verdict.append("FAIL: config unreadable")
        else:
            if cfg.get("tdp_w") != ORIG_TDP_W:
                verdict.append(f"FAIL: TDP reads {cfg.get('tdp_w')}, not {ORIG_TDP_W}")
            if cfg.get("temp_threshold_c") != ORIG_THR_C:
                verdict.append(f"FAIL: threshold reads {cfg.get('temp_threshold_c')}, not {ORIG_THR_C}")
        if m1.get("bdf") != "0000:01:00.0" or m1.get("node") != "/dev/et0_mgmt":
            verdict.append(f"FAIL: ettelem-e118 opened {m1.get('node')} at {m1.get('bdf')}, not card 0 (/dev/et0_mgmt, 0000:01:00.0)")
        if not ok:
            verdict.append(f"FAIL: identity continuity: {why}")
        if floor != PIN_MHZ:
            verdict.append(f"FAIL: vmin-LUT floor {floor} (points {lut.get('nonzero_points_mhz')}), not {PIN_MHZ}")
        res = {"config": cfg, "uptime": u, "continuity": why, "vmin_floor_mhz": floor,
               "lut_points_mhz": lut.get("nonzero_points_mhz"), "verdict": verdict or ["PASS"]}
        jsonl(out, {"event": "gates_verdict", **res})
        print(json.dumps(res, indent=1))
        return 0 if not verdict else 3

    if a.stage == "readback":
        with Locks([LOCK0], wait_s=60):
            cfg, m = read_config()
            u, mu = read_uptime()
        ok, why = continuity(u)
        rec = jsonl(out, {"event": "readback", "tag": a.tag, "config": cfg, "meta": m, "uptime": u, "continuity": why})
        print(json.dumps(rec, indent=1))
        return 0 if cfg else 4

    if a.stage == "ring":
        path = os.path.join(out, f"ring-{a.tag}.bin")
        with Locks([LOCK0], wait_s=60):
            rc, so, se, t0 = run(["timeout", "20", ETT, "sptrace", path])
        import hashlib
        h = hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else None
        rec = jsonl(out, {"event": "ring", "tag": a.tag, "rc": rc, "t_start": iso(t0), "file": os.path.basename(path),
                          "sha256": h, "stdout_tail": so[-200:]})
        print(json.dumps(rec))
        return 0 if rc == 0 else 5

    if a.stage == "pin":
        # exit 10 = refused before any write (the session then writes nothing back); any other failure may follow a
        # write and the session restores
        try:
            lk = Locks([LOCK0, LOCK1]).__enter__()
        except SystemExit as e:
            jsonl(out, {"event": "pin_refused", "why": str(e)})
            print(f"pin refused before any write: {e}")
            return 10
        try:
            cfg, m = read_config()
            if cfg is None or cfg.get("tdp_w") != ORIG_TDP_W or cfg.get("temp_threshold_c") != ORIG_THR_C:
                jsonl(out, {"event": "pin_refused", "config": cfg, "meta": m})
                print(f"pin refused before any write: not at the originals: {cfg}")
                return 10
            watchdog(out, a.deadline_s)
            sent, after, m2 = set_tdp(out, TDP_PIN_W, "E118 pin at the vmin-LUT floor")
            rec = jsonl(out, {"event": "set", "why": "pin", "asked": {"tdp_w": TDP_PIN_W}, "before": cfg,
                              "after": after, "sent": [sent], "readback_meta": m2})
        finally:
            lk.__exit__(None, None, None)
        if sent["rc"] != 0:
            raise SystemExit(f"error:governor_set_failed:rc{sent['rc']}")
        if after is None or after.get("tdp_w") != TDP_PIN_W:
            raise SystemExit(f"error:governor_readback_mismatch:asked{TDP_PIN_W}:got{after}")
        if after.get("temp_threshold_c") != ORIG_THR_C:
            raise SystemExit(f"error:threshold_moved:{after.get('temp_threshold_c')}")
        print(json.dumps({"pinned": after, "t_iso": rec["t_iso"]}, indent=1))
        return 0

    if a.stage == "restore":
        tries = []
        ok = False
        end = time.time() + 600
        while time.time() < end and not ok:
            try:
                with Locks([LOCK0, LOCK1], wait_s=120):
                    before, _ = read_config()
                    sent, after, m2 = set_tdp(out, ORIG_TDP_W, "E118 restore")
            except SystemExit as e:
                tries.append({"t_iso": iso(), "error": str(e)})
                jsonl(out, {"event": "restore_attempt_failed", "error": str(e)})
                time.sleep(15)
                continue
            ok = bool(after) and after.get("tdp_w") == ORIG_TDP_W and after.get("temp_threshold_c") == ORIG_THR_C
            tries.append({"before": before, "after": after, "sent": sent, "readback_meta": m2})
            jsonl(out, {"event": "restore", "ok": ok, "before": before, "after": after, "sent": [sent],
                        "original": {"tdp_w": ORIG_TDP_W, "temp_threshold_c": ORIG_THR_C}})
            if not ok:
                time.sleep(15)
        if ok:
            open(os.path.join(out, "release"), "w").write(iso() + "\n")
        print(json.dumps({"restore_ok": ok, "attempts": len(tries), "after": tries[-1].get("after") if tries else None}, indent=1))
        return 0 if ok else 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
