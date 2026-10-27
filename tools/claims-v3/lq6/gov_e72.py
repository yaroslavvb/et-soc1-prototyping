#!/usr/bin/env python3
"""E72: pin aifoundry2 card 0 at its vmin-LUT floor by setting the static TDP level to 0, and put it back.

    python3 tools/claims-v3/lq6/gov_e72.py gates  --out <dir>          # G0 identity + originals, no write
    python3 tools/claims-v3/lq6/gov_e72.py pin    --out <dir> [--deadline-s 4500]
    python3 tools/claims-v3/lq6/gov_e72.py status --out <dir>
    python3 tools/claims-v3/lq6/gov_e72.py restore --out <dir>
    python3 tools/claims-v3/lq6/gov_e72.py back   --out <dir>          # the post-restore stepping check

Exactly ONE firmware field is written: `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26). The software
temperature threshold is NOT touched by E72 (E69 moved it; one knob at a time), so a threshold that is
not at its original value at `gates` time is a NO-GO.

Why TDP 0 pins the clock, from the source of the running build (BL2 0.22.0, et-platform
836a4ab600e93c3059bb58c898edbc37744cd8d0, `services/thermal_pwr_mgmt.c`
`check_power_throttle_conditions`, lines 866-928):

    if (active_power_management ON && mm_state != IDLE) {
        if (temp_updated && T > threshold)            -> DOWN, gated on f > f_min
        else if (pwr_updated && avg_pwr > tdp_mW)     -> DOWN, gated on f > f_min
        else if (pwr_updated && avg_pwr < tdp_mW)     -> UP,   gated on f < f_max
    }

with `tdp_mW = POWER_IN_MW(module_tdp_level)` and `avg_pwr` an unsigned mW average. At TDP 0 the
second branch is true for any load and the third is unreachable (no unsigned value is < 0), so the
governor can only ever step DOWN, and the DOWN notify is itself gated on `f > f_min`, where
`f_min = vmin_lut_limits.mnn_frequency_min_limit`. The card therefore sits at the LUT floor and stays
there. That is aifoundry3's boot policy, and it is the whole mechanism of E72's 600 MHz.

The guardband macros UPPER/LOWER_POWER_THRESHOLD_GUARDBAND are DEFINED AND NEVER USED in this build
(they appear only at their own definitions, lines 212-223), so the comparison is a bare `>` / `<` and
there is no 1.05x exit condition to satisfy. This corrects E69's hazard note for E72.

RECOVERY, also from the source, which is why this is reversible without a reset: the throttle task
treats POWER_UP as "always allowed" from any state (line 2269), so the pass after the original TDP is
written back has `avg_pwr < 65000` and `f < f_max` and notifies UP. aifoundry3's governor is latched by
a boot-time POLICY that keeps re-writing 0, not by any firmware state machine. A deadline watchdog puts
the original back even if this session dies.
"""
import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
ET_LIB = "/opt/et/lib"
DEVMNGT = "/opt/et/bin/dev_mngt_service"
ETTELEM = os.path.join(ROOT, "build/ettelem/ettelem")
LOCK_PATH = "/run/lock/etsoc-shire0.lock"
NODE = "0"

TDP_PIN_W = 0                 # the only value E72 writes
ORIG_TDP_W = 65               # what the card must read before, and after
ORIG_THR_C = 65               # not written by E72; a different value here is a NO-GO
PIN_MHZ = 600                 # the clock the pin must produce, in every sample


def iso(t=None):
    t = time.time() if t is None else t
    ms = int((t % 1) * 1000)
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t)) + f".{ms:03d}" + time.strftime("%z", time.localtime(t))


def run(argv, timeout=25):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           env=dict(os.environ, LD_LIBRARY_PATH=ET_LIB), cwd=ROOT)
        return p.returncode, p.stdout.decode(errors="replace"), p.stderr.decode(errors="replace")
    except subprocess.TimeoutExpired:
        return -9, "", "timeout"
    except OSError as e:
        return -1, "", str(e)


def jsonl(out, name, rec):
    rec = dict(rec)
    rec.setdefault("t_iso", iso())
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, name), "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def read_config():
    rc, so, _ = run(["timeout", "20", ETTELEM, "config"])
    if rc != 0:
        return None
    try:
        return json.loads(so.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None


def dm(cmd, *extra):
    return run(["timeout", "20", DEVMNGT, "-m", cmd, "-n", NODE, *extra, "-u", "5000"])


class Lock:
    """Exclusive card lock, the same file the harnesses and the owner's dashboard collector honour."""

    def __init__(self, wait_s=0):
        self.wait_s = wait_s
        self.fd = None

    def __enter__(self):
        self.fd = os.open(LOCK_PATH, os.O_RDWR)
        deadline = time.time() + self.wait_s
        while True:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.time() >= deadline:
                    os.close(self.fd)
                    self.fd = None
                    raise SystemExit(f"card lock {LOCK_PATH} is held by someone else")
                time.sleep(2)

    def __exit__(self, *a):
        if self.fd is not None:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
            finally:
                os.close(self.fd)
                self.fd = None
        return False


def vmin_floor():
    """The minion frequency floor from DM_CMD_GET_VMIN_LUT - a pure RAM read, no SPI.

    `asset_svc_getvminlut` -> `flash_fs_get_vmin_lut` is a memcpy out of the service processor's
    in-RAM copy of the persistent config (`driver/flashfs.c:2073`), so this touches no flash and
    changes no programming mode. Returns (floor_mhz | None, raw text).
    """
    rc, so, se = dm("DM_CMD_GET_VMIN_LUT")
    raw = (so + se)[-6000:]
    if rc != 0:
        return None, raw
    freqs = []
    for m in re.finditer(r"(?im)^\s*(?:minion|mnn)\b[^\n]*?(\d{3,4})\s*(?:mhz)?\b", raw):
        freqs.append(int(m.group(1)))
    if not freqs:
        freqs = [int(x) for x in re.findall(r"\b([3-9]\d{2}|1[0-4]\d{2})\s*MHz", raw, re.I)]
    freqs = [f for f in freqs if 100 <= f <= 1600]
    return (min(freqs) if freqs else None), raw


def identity(out):
    """G0 identity, read fresh: firmware revisions, uptime, the card's own ids."""
    recs = {}
    for key, cmd in (("firmware", "DM_CMD_GET_MODULE_FIRMWARE_REVISIONS"),
                     ("uptime", "DM_CMD_GET_MODULE_UPTIME"),
                     ("asic_rev", "DM_CMD_GET_ASIC_CHIP_REVISION"),
                     ("freqs", "DM_CMD_GET_ASIC_FREQUENCIES"),
                     ("tdp", "DM_CMD_GET_MODULE_STATIC_TDP_LEVEL"),
                     ("thresholds", "DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS")):
        rc, so, se = dm(cmd)
        recs[key] = {"rc": rc, "out": (so + se)[-2500:]}
    jsonl(out, "gov.jsonl", {"event": "identity", "queries": recs})
    return recs


def set_tdp(out, w, why):
    """Write one field, read it back, and refuse to continue on any disagreement."""
    before = read_config()
    if before is None:
        raise SystemExit("error:governor_config_unreadable")
    sent = []
    if before.get("tdp_w") != int(w):
        argv = ["timeout", "20", DEVMNGT, "-m", "DM_CMD_SET_MODULE_STATIC_TDP_LEVEL",
                "-n", NODE, "-l", str(int(w)), "-u", "5000"]
        rc, so, se = run(argv)
        sent.append({"cmd": argv, "rc": rc, "t_iso": iso(), "stdout_tail": so[-600:], "stderr_tail": se[-400:]})
        if rc != 0:
            jsonl(out, "gov.jsonl", {"event": "set_failed", "why": why, "before": before, "sent": sent})
            raise SystemExit(f"error:governor_set_failed:tdp={w}:rc{rc}")
    after = read_config()
    rec = jsonl(out, "gov.jsonl", {"event": "set", "why": why, "asked": {"tdp_w": int(w)},
                                   "before": before, "after": after, "sent": sent})
    if after is None or after.get("tdp_w") != int(w):
        raise SystemExit(f"error:governor_readback_mismatch:asked{w}:got{after}")
    if after.get("temp_threshold_c") != ORIG_THR_C:
        raise SystemExit(f"error:threshold_moved:{after.get('temp_threshold_c')} (E72 never writes it)")
    return rec


def arm_watchdog(out, deadline_s):
    """A detached restorer, so TDP 0 cannot outlive this session even if it is killed.

    It waits for the deadline (or for `release` to appear), then takes the card lock with a 120 s wait
    and writes the original TDP back. It never resets anything and never raises the cap.
    """
    os.makedirs(out, exist_ok=True)
    rel = os.path.join(out, "release")
    log = os.path.join(out, "watchdog.log")
    sh = os.path.join(out, "watchdog.sh")
    with open(sh, "w") as f:
        f.write(f"""#!/usr/bin/env bash
# E72 deadline watchdog: put TDP {ORIG_TDP_W} W back if the session has not released by the deadline.
set -u
REL={rel!r}
end=$(( $(date +%s) + {int(deadline_s)} ))
while [ "$(date +%s)" -lt "$end" ]; do
  [ -e "$REL" ] && {{ echo "$(date -Is) released by the session, nothing to do" >> {log!r}; exit 0; }}
  sleep 10
done
echo "$(date -Is) DEADLINE reached, restoring TDP {ORIG_TDP_W} W" >> {log!r}
/usr/bin/flock -w 120 {LOCK_PATH!r} env LD_LIBRARY_PATH={ET_LIB} timeout 20 {DEVMNGT} \
  -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n {NODE} -l {ORIG_TDP_W} -u 5000 >> {log!r} 2>&1
echo "$(date -Is) set rc=$?" >> {log!r}
env LD_LIBRARY_PATH={ET_LIB} timeout 20 {ETTELEM!r} config >> {log!r} 2>&1
""")
    p = subprocess.Popen(["setsid", "nohup", "bash", sh], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
    jsonl(out, "gov.jsonl", {"event": "watchdog_armed", "pid": p.pid, "deadline_s": int(deadline_s),
                             "script": sh, "release_file": rel})
    return p.pid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["gates", "pin", "status", "restore", "back"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-s", type=int, default=4500)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if a.stage == "gates":
        with Lock():
            cfg = read_config()
            jsonl(a.out, "gov.jsonl", {"event": "original", "config": cfg})
            ident = identity(a.out)
            floor, raw = vmin_floor()
            open(os.path.join(a.out, "vmin_lut.txt"), "w").write(raw)
            jsonl(a.out, "gov.jsonl", {"event": "vmin_floor", "floor_mhz": floor})
        verdict = []
        if cfg is None:
            verdict.append("FAIL: ettelem config unreadable")
        else:
            if cfg.get("tdp_w") != ORIG_TDP_W:
                verdict.append(f"FAIL: TDP reads {cfg.get('tdp_w')} W, not the original {ORIG_TDP_W}")
            if cfg.get("temp_threshold_c") != ORIG_THR_C:
                verdict.append(f"FAIL: threshold reads {cfg.get('temp_threshold_c')} C, not {ORIG_THR_C}")
        if floor is None:
            verdict.append(f"UNKNOWN: vmin LUT floor not parsed (G1's in-run clock gate stands in for it)")
        elif floor != PIN_MHZ:
            verdict.append(f"FAIL: vmin LUT floor is {floor} MHz, not {PIN_MHZ} - the pin would not be a "
                           f"600 MHz replicate")
        print(json.dumps({"config": cfg, "vmin_floor_mhz": floor,
                          "verdict": verdict or ["PASS"], "uptime": ident["uptime"]["out"][-300:]}, indent=1))
        return 0 if not verdict or all(v.startswith("UNKNOWN") for v in verdict) else 3

    if a.stage == "pin":
        with Lock():
            cfg = read_config()
            if cfg is None or cfg.get("tdp_w") != ORIG_TDP_W or cfg.get("temp_threshold_c") != ORIG_THR_C:
                raise SystemExit(f"error:not_at_originals:{cfg}")
            arm_watchdog(a.out, a.deadline_s)
            rec = set_tdp(a.out, TDP_PIN_W, "E72 pin at the vmin-LUT floor")
        print(json.dumps({"pinned": rec["after"]}, indent=1))
        return 0

    if a.stage == "status":
        print(json.dumps({"config": read_config(), "t_iso": iso()}, indent=1))
        return 0

    if a.stage == "restore":
        with Lock(wait_s=180):
            before = read_config()
            argv = ["timeout", "20", DEVMNGT, "-m", "DM_CMD_SET_MODULE_STATIC_TDP_LEVEL",
                    "-n", NODE, "-l", str(ORIG_TDP_W), "-u", "5000"]
            rc, so, se = run(argv)
            after = read_config()
            ok = bool(after) and after.get("tdp_w") == ORIG_TDP_W and after.get("temp_threshold_c") == ORIG_THR_C
            rec = jsonl(a.out, "gov.jsonl", {"event": "restore", "ok": ok, "before": before, "after": after,
                                             "sent": [{"cmd": argv, "rc": rc, "stdout_tail": so[-400:],
                                                       "stderr_tail": se[-300:]}],
                                             "original": {"tdp_w": ORIG_TDP_W, "temp_threshold_c": ORIG_THR_C}})
        if ok:
            open(os.path.join(a.out, "release"), "w").write(iso() + "\n")
        print(json.dumps({"restore_ok": ok, "after": after}, indent=1))
        return 0 if ok else 4

    if a.stage == "back":
        cfg = read_config()
        print(json.dumps({"config_before_burst": cfg}, indent=1))
        jsonl(a.out, "gov.jsonl", {"event": "back_check", "config": cfg})
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
