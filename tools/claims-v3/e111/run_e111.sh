#!/usr/bin/env bash
# E111 (Q133): stage, check, dry-run, smoke and start the afternoon's queue on aifoundry2. Run it ON aifoundry2 from the lab checkout
# (~/claude/et-soc1-prototyping), each step in a script file run by `ssh aifoundry2 'bash -s' < file`. It never touches the governor,
# never sets a clock, never resets anything: the card is opened only by run_e111.py (E98's runner, run_kspeed.py over run_hpl.py),
# by run_hlc.py (E63's camera runner, as E73 ran it) and by the read-only `ettelem config` under the card lock with `timeout 10`.
#
#   bash tools/claims-v3/e111/run_e111.sh stage                 # build/e111/cam from the tree's hlc, hm, hlf + E111's camera protocols
#   bash tools/claims-v3/e111/run_e111.sh check                 # host, logins (a count), free space, binaries, card, camera, the plans
#   bash tools/claims-v3/e111/run_e111.sh dry                   # the whole queue with --dry: toy card, real camera, no device opened
#   bash tools/claims-v3/e111/run_e111.sh config <tag>          # a read-only ettelem config into build/e111/config-<tag>.json
#   bash tools/claims-v3/e111/run_e111.sh smoke                 # E98's smoke by hand (the queue runs it itself as its first step)
#   bash tools/claims-v3/e111/run_e111.sh go <w1-not-before> <w1-latest>   # the queue (SMOKE, W1, W2, END, CAM), detached
#   bash tools/claims-v3/e111/run_e111.sh watch
set -u
cmd=${1:?usage: run_e111.sh stage|check|dry|config|smoke|go|watch}
ROOT="$HOME/claude/et-soc1-prototyping"
T="$ROOT/tools/claims-v3"
B="$ROOT/build/e111"
CAM="$B/cam"
cd "$ROOT" || exit 1
mkdir -p "$B"

stage() {
  mkdir -p "$CAM/prereg" "$CAM/hlc"
  for f in run_hlc.py lockin_hlc.py fpa_trace.py dips_hlc.py; do cp -p "$T/hlc/$f" "$CAM/$f"; done
  cp -p "$T/hlc/lockin_hlc.py" "$CAM/hlc/lockin_hlc.py"
  for f in record_cam.py reduce_hm.py p3rec.py; do cp -p "$T/hm/$f" "$CAM/$f"; done
  cp -p "$T/hlf/lockin_hlf.py" "$CAM/lockin_hlf.py"
  cp -p "$T"/hlc/prereg/*.npy "$CAM/prereg/"
  for f in protocol-cam.json protocol-cam-dry.json predictions-e111.json run_hlc_e111.py idle_logins_e111.py; do cp -p "$T/e111/$f" "$CAM/$f"; done
  ( cd "$CAM" && sha256sum ./*.py ./*.json ./hlc/*.py ./prereg/*.npy > SHA256SUMS )
  echo "staged $CAM from $(git -C "$ROOT" rev-parse --short HEAD)"; cat "$CAM/SHA256SUMS"
}

config() {
  tag=${1:-now}
  LD_LIBRARY_PATH=/opt/et/lib flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem-hpl/ettelem config < /dev/null \
    > "$B/config-$tag.json" 2> "$B/config-$tag.err"
  echo "config rc=$? $(date '+%F %T %Z')"; tail -1 "$B/config-$tag.json"
}

case "$cmd" in
  stage) stage ;;
  check)
    echo "== host =="; hostname; date "+%F %T %Z"; uptime
    echo "== other logins (a count) =="; who | awk '{print $1}' | sort -u | grep -vc "^$(id -un)$"
    echo "== free =="; df -h "$HOME" | tail -1
    echo "== binaries =="; sha256sum build/sparsity_t2/host/sparsity_host build/sparsity_t2/kernel/sparsity.elf build/ettelem-hpl/ettelem
    echo "== card =="; timeout 10 et-who 2>&1 | head -3
    echo "== camera =="; curl -s -m 6 http://p3-phone:8080/health | head -c 300; echo
    echo "== git =="; git log -1 --format='%h %s' | cut -c1-100; git status --porcelain -- tools/claims-v3/hpl tools/claims-v3/kspeed tools/claims-v3/hlc tools/claims-v3/hm tools/claims-v3/hlf | head
    echo "== plans =="
    for p in w1 w2 end smoke; do python3 "$T/e111/run_e111.py" --protocol "$T/e111/protocol-$p.json" --out /dev/null --list 2>&1 | tail -1; done
    ( cd "$CAM" && python3 run_hlc_e111.py --protocol protocol-cam.json --list 2>&1 | sed -n '1,4p' )
    echo "== amendment A1's decision (counts only) =="; python3 "$T/e111/idle_logins_e111.py"
    ;;
  dry)
    D="$B/dry-$(date +%H%M%S)"; mkdir -p "$D"
    now=$(date +%H:%M); late=$(date -d '+50 min' +%H:%M); cut=$(date -d '+60 min' +%H:%M)
    python3 "$T/e111/make_schedule_e111.py" --date "$(date +%F)" --w1-not-before "$now" --w1-latest "$late" --no-start-after "$late" \
      --cutoff "$cut" --out "$D/schedule.json"
    setsid nohup timeout 1800 python3 "$T/e111/queue_e111.py" --schedule "$D/schedule.json" --runs "$D/runs" --dry > "$D/queue.out" 2>&1 < /dev/null &
    echo "dry queue pid $! -> $D"; echo "$D" > "$B/dry-latest.txt"
    ;;
  config) config "${2:-now}" ;;
  smoke)
    D="$B/smoke"; mkdir -p "$D"
    config smoke-before
    timeout 300 python3 "$T/e111/run_e111.py" --protocol "$T/e111/protocol-smoke.json" --out "$D" --max-card-min 4 > "$D/run.out" 2>&1 < /dev/null
    echo "smoke rc=$?"; tail -6 "$D/run.out"; cat "$D/end.json"; echo
    date +%s%3N > "$B/smoke-end-ms.txt"
    ;;
  go)
    nb=${2:?w1 not before HH:MM}; lt=${3:?w1 latest HH:MM}; cmb=${4:-0}
    if [ -e "$B/runs/queue.jsonl" ]; then echo "refusing: $B/runs already has a queue"; exit 2; fi
    rf=0   # the queue runs the smoke itself, first; W1's rest counts from its end
    python3 "$T/e111/make_schedule_e111.py" --date "$(date +%F)" --w1-not-before "$nb" --w1-latest "$lt" --no-start-after 18:00 \
      --cutoff 18:55 --rest-from-ms "$rf" --card-min-before "$cmb" --out "$B/schedule.json"
    mkdir -p "$B/runs"
    setsid nohup python3 "$T/e111/queue_e111.py" --schedule "$B/schedule.json" --runs "$B/runs" > "$B/queue.out" 2>&1 < /dev/null &
    echo "queue pid $!"; sleep 3; tail -3 "$B/queue.out"; cat "$B/runs/status.json"; echo
    ;;
  watch)
    cat "$B/runs/status.json" 2>/dev/null; echo; tail -4 "$B/queue.out" 2>/dev/null | cut -c1-400
    for s in W1 W2 END CAM; do [ -f "$B/runs/$s/run.out" ] && { echo "== $s"; tail -2 "$B/runs/$s/run.out" | cut -c1-300; }; done
    ;;
  *) echo "unknown: $cmd"; exit 2 ;;
esac
