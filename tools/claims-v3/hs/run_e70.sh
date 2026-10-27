#!/usr/bin/env bash
# E70 (Q129) on aifoundry3, one stage per call. Run it from the tree that holds the binaries (~/aifoundry):
#
#   bash tools/claims-v3/hs/run_e70.sh setup           # hl-gen5, byte-identity against hl-gen4 and hl-gen3, dry run
#   bash tools/claims-v3/hs/run_e70.sh load            # start the host-load sampler (departure D-b), detached
#   bash tools/claims-v3/hs/run_e70.sh sat <first> <n>  # the one item list, <n> passes from <first> (detached)
#   bash tools/claims-v3/hs/run_e70.sh stoploads       # stop the load sampler
#
# Everything that touches the card goes through hl/block.sh, which holds the card lock, caps every device process
# at `timeout 10` and stops on another user. Nothing here waits for a person, and nothing here changes a card
# setting: no clock is set, the governor is not touched.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=$ROOT/build/hl-gen5
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
ITEMS=anchor_pi,lq_h0,lq_h1,lq_h2,lq_h3,lq_h4,lq_h6,lq_h8,lq_h12,lq_h16,lq_h23,ls_h2,ls_h3,ls_h4,ls_h6,ls_h8,ls_h12,ls_h16,aq_h0,alq_,nrd_a,nrd_b
LOADLOG=$ROOT/build/e70-load.jsonl
stage=${1:?setup|load|sat|stoploads}

case "$stage" in
setup)
  echo "== card and host =="
  et-boot-check --status 2>&1 | tail -5
  et-who 2>&1 | head -5
  who; uptime; cat /proc/loadavg
  echo "== operand set hl-gen5 =="
  "$PY" tools/claims-v3/hl/make_hl.py "$GEN" --check | tail -2
  for ref in build/hl-gen4 build/hl-gen3; do
    echo "== byte-identity against $ref (every file E60, E65 and E67 ran) =="
    n=0; bad=0
    for f in "$ROOT/$ref"/tiles/*.bin "$ROOT/$ref"/srcs/*.bin; do
      [ -e "$f" ] || continue
      g=$GEN/${f#$ROOT/$ref/}
      if [ -f "$g" ]; then
        a=$(sha256sum < "$f"); b=$(sha256sum < "$g")
        n=$((n + 1)); [ "$a" = "$b" ] || { bad=$((bad + 1)); echo "DIFFERS: $f"; }
      else
        echo "MISSING in hl-gen5: $f"
      fi
    done
    echo "byte-identical: $((n - bad))/$n"
  done
  echo "== alq_h1 must equal E67's abit_0 =="
  sha256sum "$GEN/tiles/alq_h1.bin" "$GEN/tiles/abit_0.bin" | awk '{print $1}' | sort -u | wc -l
  echo "== dry run, the one item list =="
  HL_GEN=$GEN V3_DRY=1 bash tools/claims-v3/hl/block.sh 7900 "$ITEMS" 2>&1 | tail -5
  ;;
load)
  # departure D-b: the host's CPU load beside the telemetry. E67's A16: another user's CPU work moved the op rate
  # mid-session and no registered gate saw it. Read-only, no card, no root.
  cat > "$ROOT/build/e70-load.sh" <<'EOS'
set -u
out=${1:?log}
while true; do
  read -r a b c rest < /proc/loadavg
  printf '{"t":%s,"load1":%s,"load5":%s,"load15":%s,"runq":"%s","procs":%s}\n' \
    "$(date +%s)" "$a" "$b" "$c" "$rest" "$(ps -eo stat= | grep -c '^R')" >> "$out"
  sleep 2
done
EOS
  setsid nohup bash "$ROOT/build/e70-load.sh" "$LOADLOG" > /dev/null 2>&1 < /dev/null &
  echo "load sampler started -> $LOADLOG"
  ;;
stoploads)
  pkill -f "$ROOT/build/e70-load.sh" && echo "load sampler stopped" || echo "no load sampler running"
  ;;
sat)
  p=${2:?first pass}; n=${3:?passes}
  export HL_GEN=$GEN
  setsid nohup bash tools/claims-v3/hl/queue_hl.sh "$p" "$n" "$ITEMS" \
    > "$ROOT/build/e70-sat.log" 2>&1 < /dev/null &
  echo "sat queue started: passes $p..$((p + n - 1)), log $ROOT/build/e70-sat.log"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
