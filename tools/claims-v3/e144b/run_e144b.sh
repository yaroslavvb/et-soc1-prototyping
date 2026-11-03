#!/usr/bin/env bash
# E144b (Q138): check, dry-run and start the evening's queue on aifoundry2. Run it ON aifoundry2 from the lab checkout
# (~/claude/et-soc1-prototyping), each step in a script file run by `ssh aifoundry2 'bash -s' < file`. It never touches the governor,
# never sets a clock, never resets anything: the card is opened only by run_e144b.py (E133's runner: run_kspeed.py over run_hpl.py, with
# the residency read not sent) and by the read-only `ettelem config` under the card lock with `timeout 10`.
#
#   bash tools/claims-v3/e144b/run_e144b.sh check                         # host, logins (a count), free space, binaries, hashes, card, plans
#   bash tools/claims-v3/e144b/run_e144b.sh dry                           # the whole queue with --dry (the toy card; no device opened)
#   bash tools/claims-v3/e144b/run_e144b.sh config <tag>                  # a read-only ettelem config into build/e144b/config-<tag>.txt
#   bash tools/claims-v3/e144b/run_e144b.sh go <smoke-not-before> <smoke-latest>   # the queue, detached (cutoff 23:50, no start after 23:40)
#   bash tools/claims-v3/e144b/run_e144b.sh watch
set -u
cmd=${1:?usage: run_e144b.sh check|dry|config|go|watch}
ROOT="$HOME/claude/et-soc1-prototyping"
T="$ROOT/tools/claims-v3"
B="$ROOT/build/e144b"
cd "$ROOT" || exit 1
mkdir -p "$B"

config() {
  tag=${1:-now}
  LD_LIBRARY_PATH=/opt/et/lib flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem-hpl/ettelem config < /dev/null \
    > "$B/config-$tag.txt" 2>&1
  echo "config rc=$? $(date '+%F %T %Z')"; tail -1 "$B/config-$tag.txt"
}

case "$cmd" in
  check)
    echo "== host =="; hostname; date "+%F %T %Z"; uptime
    echo "== other logins (a count) =="; who | awk '{print $1}' | sort -u | grep -vc "^$(id -un)$"
    echo "== the idle-login rule's decision (counts only) =="; python3 "$T/e111/idle_logins_e111.py"
    echo "== free =="; df -h "$HOME" | tail -1
    echo "== binaries =="; sha256sum build/sparsity_t2/host/sparsity_host build/sparsity_t2/kernel/sparsity.elf build/ettelem-hpl/ettelem
    echo "== code =="; sha256sum "$T/hpl/run_hpl.py" "$T/kspeed/run_kspeed.py" "$T/e111/idle_logins_e111.py" "$T/kinds/kinds.json" "$T"/e144b/*.py "$T"/e144b/protocol-*.json
    echo "== card =="; timeout 10 et-who 2>&1 | head -3
    echo "== plans =="
    for p in smoke stoptest-die stoptest-board g1 end g2 end2; do python3 "$T/e144b/run_e144b.py" --protocol "$T/e144b/protocol-$p.json" --out /dev/null --list 2>&1 | tail -1; done
    ;;
  dry)
    D="$B/dry-$(date +%H%M%S)"; mkdir -p "$D/runs"
    now=$(date +%H:%M); late=$(date -d '+50 min' +%H:%M); nsa=$(date -d '+55 min' +%H:%M); cut=$(date -d '+60 min' +%H:%M)
    python3 "$T/e144b/make_schedule_e144b.py" --date "$(date +%F)" --smoke-not-before "$now" --smoke-latest "$late" \
      --no-start-after "$nsa" --cutoff "$cut" --out "$D/schedule.json"
    timeout 1500 python3 "$T/e144b/queue_e144b.py" --schedule "$D/schedule.json" --runs "$D/runs" --dry > "$D/queue.out" 2>&1 < /dev/null
    echo "dry rc=$? -> $D"; echo "$D" > "$B/dry-latest.txt"
    grep -h '"kind": "\(start\|end\|skip\|queue_end\|smoke_check\|stoptest_check\|stoptest_detail\)"' "$D/queue.out" | cut -c1-260
    ;;
  config) config "${2:-now}" ;;
  go)
    nb=${2:?smoke not before HH:MM}; sl=${3:?smoke latest HH:MM}
    if [ -e "$B/runs/queue.jsonl" ]; then echo "refusing: $B/runs already has a queue"; exit 2; fi
    python3 "$T/e144b/make_schedule_e144b.py" --date "$(date +%F)" --smoke-not-before "$nb" --smoke-latest "$sl" \
      --no-start-after 23:40 --cutoff 23:50 --out "$B/schedule.json" || exit 2
    mkdir -p "$B/runs"
    setsid nohup python3 "$T/e144b/queue_e144b.py" --schedule "$B/schedule.json" --runs "$B/runs" > "$B/queue.out" 2>&1 < /dev/null &
    echo "queue pid $!"; sleep 3; tail -3 "$B/queue.out" | cut -c1-300; cat "$B/runs/status.json"; echo
    ;;
  watch)
    cat "$B/runs/status.json" 2>/dev/null; echo; tail -4 "$B/queue.out" 2>/dev/null | cut -c1-400
    for s in SMOKE STOPTEST-DIE STOPTEST-BOARD G1 END G2 END2; do [ -f "$B/runs/$s/run.out" ] && { echo "== $s"; tail -2 "$B/runs/$s/run.out" | cut -c1-300; }; done
    ;;
  *) echo "unknown: $cmd"; exit 2 ;;
esac
