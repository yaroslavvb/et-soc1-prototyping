#!/usr/bin/env bash
# E133 (Q136): check, dry-run and start the morning's queue on aifoundry2. Run it ON aifoundry2 from the lab checkout
# (~/claude/et-soc1-prototyping), each step in a script file run by `ssh aifoundry2 'bash -s' < file`. It never touches the governor,
# never sets a clock, never resets anything: the card is opened only by run_e133.py (E111's runner: run_kspeed.py over run_hpl.py, with
# the residency read not sent) and by the read-only `ettelem config` under the card lock with `timeout 10`.
#
#   bash tools/claims-v3/e133/run_e133.sh check                  # host, logins (a count), free space, binaries, hashes, card, the plans
#   bash tools/claims-v3/e133/run_e133.sh dry                    # the whole queue with --dry (the toy card; no device opened), W3 included
#   bash tools/claims-v3/e133/run_e133.sh config <tag>           # a read-only ettelem config into build/e133/config-<tag>.txt
#   bash tools/claims-v3/e133/run_e133.sh go <smoke-not-before>  # the queue (SMOKE, W2, END, W1B, END2, W3), detached
#   bash tools/claims-v3/e133/run_e133.sh go-w3 | skip-w3        # the afternoon probe: allow it (after the post) or drop it
#   bash tools/claims-v3/e133/run_e133.sh watch
set -u
cmd=${1:?usage: run_e133.sh check|dry|config|go|go-w3|skip-w3|watch}
ROOT="$HOME/claude/et-soc1-prototyping"
T="$ROOT/tools/claims-v3"
B="$ROOT/build/e133"
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
    echo "== code =="; sha256sum "$T/hpl/run_hpl.py" "$T/kspeed/run_kspeed.py" "$T/e111/idle_logins_e111.py" "$T/kinds/kinds.json" "$T"/e133/*.py "$T"/e133/protocol-*.json
    echo "== card =="; timeout 10 et-who 2>&1 | head -3
    echo "== git =="; git log -1 --format='%h %s' | cut -c1-100; git status --porcelain -- tools/claims-v3/hpl tools/claims-v3/kspeed tools/claims-v3/kinds | head
    echo "== plans =="
    for p in smoke w2 end w1b end2 w3; do python3 "$T/e133/run_e133.py" --protocol "$T/e133/protocol-$p.json" --out /dev/null --list 2>&1 | tail -1; done
    ;;
  dry)
    D="$B/dry-$(date +%H%M%S)"; mkdir -p "$D/runs"
    now=$(date +%H:%M); late=$(date -d '+50 min' +%H:%M); cut=$(date -d '+60 min' +%H:%M)
    python3 "$T/e133/make_schedule_e133.py" --date "$(date +%F)" --smoke-not-before "$now" --smoke-latest "$late" --w3-not-before "$now" \
      --w3-latest "$late" --no-start-after "$late" --cutoff "$cut" --out "$D/schedule.json"
    touch "$D/runs/GO-W3"
    timeout 1500 python3 "$T/e133/queue_e133.py" --schedule "$D/schedule.json" --runs "$D/runs" --dry > "$D/queue.out" 2>&1 < /dev/null
    echo "dry rc=$? -> $D"; echo "$D" > "$B/dry-latest.txt"
    grep -h '"kind": "\(start\|end\|skip\|queue_end\)"' "$D/queue.out" | cut -c1-240
    ;;
  config) config "${2:-now}" ;;
  go)
    nb=${2:?smoke not before HH:MM}
    if [ -e "$B/runs/queue.jsonl" ]; then echo "refusing: $B/runs already has a queue"; exit 2; fi
    python3 "$T/e133/make_schedule_e133.py" --date "$(date +%F)" --smoke-not-before "$nb" --smoke-latest 11:00 --w3-not-before 14:15 \
      --w3-latest 14:45 --no-start-after 15:00 --cutoff 16:00 --out "$B/schedule.json"
    mkdir -p "$B/runs"
    setsid nohup python3 "$T/e133/queue_e133.py" --schedule "$B/schedule.json" --runs "$B/runs" > "$B/queue.out" 2>&1 < /dev/null &
    echo "queue pid $!"; sleep 3; tail -3 "$B/queue.out" | cut -c1-300; cat "$B/runs/status.json"; echo
    ;;
  go-w3) touch "$B/runs/GO-W3"; echo "GO-W3 $(date '+%T %Z')"; cat "$B/runs/status.json"; echo ;;
  skip-w3) touch "$B/runs/SKIP-W3"; echo "SKIP-W3 $(date '+%T %Z')"; cat "$B/runs/status.json"; echo ;;
  watch)
    cat "$B/runs/status.json" 2>/dev/null; echo; tail -3 "$B/queue.out" 2>/dev/null | cut -c1-400
    for s in SMOKE W2 END W1B END2 W3; do [ -f "$B/runs/$s/run.out" ] && { echo "== $s"; tail -2 "$B/runs/$s/run.out" | cut -c1-300; }; done
    ;;
  *) echo "unknown: $cmd"; exit 2 ;;
esac
