#!/usr/bin/env bash
# DV2 Z2 on aifoundry3 (DESIGN §6 Z2, PREREG-DEV §4 row 1; critique B5): a read-only state check, about 1 min.
# Standalone: it sources neither ../lib.sh nor any hp code, and runs from the copied tools/claims-v3/dv2/ only.
#
#   bash tools/claims-v3/dv2/z2.sh                   on aifoundry3, from ~/nekko (the tree root)
#   V3_DRY=1 bash tools/claims-v3/dv2/z2.sh          no device: fake outputs (any host)
#
# Steps, each a device process under timeout 10, with the card lock held (flock -n; refused if held):
#   ettelem-dv2 uptime; ettelem-dv2 residency 2 3 4 5 6 (raw 0.20.0 states: POWER_UP, POWER_DOWN, THERMAL_DOWN,
#   POWER_SAFE, THERMAL_SAFE); ettelem-dv2 config; ettelem-dv2 sptrace. No launch, no sampler, no set.
# Before: et-who (no holder), who (no other user), no device process, no framework queue or block running.
# Prediction (frozen, PREREG-DEV §1.2): residencies POWER_UP, POWER_DOWN, THERMAL_DOWN and SAFE are all 0.
# Output: build/claims-v3/aifoundry3/dv2/z2-<time>/ (z2.json: the reads and the prediction check).
# Refused on aifoundry1 (card 1's Z2 needs the owner's slot after 08:00 and the device-1 guard: not in this build) and
# on any card-0 selection. Exit 0 done, 1 failed, 2 refused, 3 someone else on the card.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
export LD_LIBRARY_PATH=/opt/et/lib
HOST=$(hostname)
dry() { [ -n "${V3_DRY:-}" ]; }
case "$HOST" in
  aifoundry3) ;;
  aifoundry1) echo "z2: aifoundry1 is refused in this build (card 1's Z2 needs the owner's slot and the device-1 guard; card 0 is never addressed)" >&2; exit 2 ;;
  *) dry || { echo "z2: runs on aifoundry3 only (this is $HOST); dry tests: V3_DRY=1" >&2; exit 2; } ;;
esac
[ -n "${ET_DEVICES:-}${V3_DEVICE:-}" ] && { echo "z2: ET_DEVICES/V3_DEVICE set: refused (aifoundry3 has one card)" >&2; exit 2; }
CARD=aifoundry3
ETT=build/ettelem-dv2/ettelem
if dry; then OUTROOT=$ROOT/build/claims-v3-dry/$CARD/dv2; else OUTROOT=$ROOT/build/claims-v3/$CARD/dv2; fi
OUT=$OUTROOT/z2-$(date +%Y%m%dT%H%M%S)
mkdir -p "$OUT"
log() { echo "$(date +%FT%T) [z2 $CARD] $*" | tee -a "$OUT/z2.log"; }
dry || [ -x "$ETT" ] || { log "missing $ETT (build it: cmake -S tools/claims-v3/dv2/ettelem-dv2 -B build/ettelem-dv2 ...)"; exit 1; }

# ---- the gate
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'
{ echo "== et-who"; timeout 20 et-who 2>&1; echo "== who"; who; echo "== uptime"; uptime; } > "$OUT/gate.txt" 2>&1 || true
if dry; then holders=; users=; procs=; frame=
else
  holders=$(timeout 20 et-who 2>/dev/null | awk '$1 ~ /^\/dev\/et|^lock:/ {printf "%s:%s:%s ", $1, $2, $3}')
  users=$(who | awk '{print $1}' | sort -u | grep -vx "$USER" | tr '\n' ' ' || true)
  procs=$(ps -eo uid=,pid=,comm= | awk -v re="$DEV_COMM|^Runner.Worker$" '$3 ~ re {printf "%s:%s:%s ", $1, $2, $3}')
  frame=$(pgrep -u "$(id -u)" -af 'tools/claims-v3/(queue\.sh|hp/|[a-z0-9]+/block\.sh)' 2>/dev/null | grep -v pgrep | cut -c1-100 | tr '\n' ';' || true)
fi
if [ -n "${holders// /}${users// /}${procs// /}${frame// /}" ]; then
  log "not starting: holders=[$holders] users=[$users] procs=[$procs] framework=[$frame]"; exit 3
fi
if ! dry; then
  exec 9<>/run/lock/etsoc-shire0.lock || { log "no card lock file"; exit 1; }
  flock -n 9 || { log "the card lock is held: not starting"; exit 3; }
fi

# ---- the reads (each under timeout 10, stdin closed)
run() {   # run <name> <out> <args...>
  local name=$1 out=$2; shift 2
  local t0 rc; t0=$(date +%s%3N)
  if dry; then
    case "$1" in
      uptime) echo '{"t_ms":0,"rc":0,"day":3,"hours":1,"mins":2,"dry":true}' > "$out"; rc=0 ;;
      residency) for s in 2 3 4 5 6; do echo "{\"t_ms\":0,\"state\":$s,\"rc\":0,\"cumulative_us\":0,\"average_us\":0,\"maximum_us\":0,\"minimum_us\":0,\"dry\":true}"; done > "$out"; rc=0 ;;
      config) echo '{"tdp_w":0,"temp_threshold_c":65,"power_state":0,"power_state_name":"max_power","minion_mhz":600,"minion_mv":525,"dry":true}' > "$out"; rc=0 ;;
      sptrace) : > "$2"; echo "sptrace: rc 0 (dry)" > "$out"; rc=0 ;;
    esac
  else
    timeout 10 "$ETT" "$@" > "$out" 2>> "$OUT/mgmt.log" < /dev/null 9>&-; rc=$?
  fi
  echo "{\"step\":\"$name\",\"t0_ms\":$t0,\"t1_ms\":$(date +%s%3N),\"rc\":$rc}" >> "$OUT/steps.jsonl"
  log "$name: rc $rc"
  return 0
}
run uptime "$OUT/uptime.jsonl" uptime
run residency "$OUT/residency.jsonl" residency 2 3 4 5 6
run config "$OUT/config.json" config
run sptrace "$OUT/sptrace.out" sptrace "$OUT/sp.bin"
dry || exec 9>&-
sha256sum "$ETT" tools/claims-v3/dv2/z2.sh tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp > "$OUT/code.sha256" 2>/dev/null || true

python3 - "$OUT" <<'PY'
import json, os, sys
d = sys.argv[1]
def jl(p):
    out = []
    try:
        for l in open(os.path.join(d, p)):
            l = l.strip()
            if l.startswith("{"):
                out.append(json.loads(l))
    except Exception:
        pass
    return out
res = {str(r.get("state")): r for r in jl("residency.jsonl")}
names = {"2": "POWER_UP", "3": "POWER_DOWN", "4": "THERMAL_DOWN", "5": "POWER_SAFE", "6": "THERMAL_SAFE"}
try:
    cfg = json.load(open(os.path.join(d, "config.json")))
except Exception:
    cfg = {}
up = (jl("uptime.jsonl") or [None])[0]
pred = {k: res.get(k, {}).get("cumulative_us") for k in ("2", "3", "4", "5")}
ok = all(r.get("rc") == 0 for r in res.values()) and len(res) == 5
met = ok and all(v == 0 for v in pred.values())
kinds = {}
try:
    sys.path.insert(0, os.path.join(os.getcwd(), "tools", "claims-v3", "dv2"))
    import sptrace_events as SE
    for e in SE.events(open(os.path.join(d, "sp.bin"), "rb").read()):
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
except Exception as e:
    kinds = {"error": str(e)}
z = {"card": "aifoundry3", "uptime": up, "config": cfg,
     "residency": {names[k]: res.get(k) for k in names},
     "prediction": "POWER_UP = POWER_DOWN = THERMAL_DOWN = POWER_SAFE = 0 (the stuck power loop never exits; PREREG-DEV 1.2)",
     "reads_ok": ok, "prediction_met": met if ok else None, "sp_kinds": kinds}
json.dump(z, open(os.path.join(d, "z2.json"), "w"), indent=1)
print("Z2 aifoundry3: reads %s; prediction %s; cumulative us %s; uptime %s; TDP %s, threshold %s" % (
    "ok" if ok else "FAILED", {True: "MET", False: "NOT MET", None: "untested"}[met if ok else None],
    {names[k]: v for k, v in pred.items()}, up and "%sd %sh %sm" % (up.get("day"), up.get("hours"), up.get("mins")),
    cfg.get("tdp_w"), cfg.get("temp_threshold_c")))
PY
log "done -> $OUT"
exit 0
