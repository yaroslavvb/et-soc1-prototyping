#!/usr/bin/env bash
# E65 (Q126) on aifoundry3, one stage per call. Run it from the tree that holds the binaries (~/aifoundry):
#
#   bash tools/claims-v3/hb/run_e65.sh setup        # hl-gen3, byte-identity against E60's set, dry runs
#   bash tools/claims-v3/hb/run_e65.sh ab <first> <n>   # blocks A+B: n passes of the bit scan (detached)
#   bash tools/claims-v3/hb/run_e65.sh c            # block C: the two hart-ladder sessions (detached)
#   bash tools/claims-v3/hb/run_e65.sh d <first> <n>   # block D: the 65 C launch, if time allows (detached)
#
# Everything that touches the card goes through hl/block.sh or hm/run_hm.py, which hold the card lock, cap every
# device process at `timeout 10` and stop on another user. Nothing here waits for a person.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=$ROOT/build/hl-gen3
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
ITEMS_AB=anchor_pi,lq_h0,lb_h0,bit_,bpi_
ITEMS_D=anchor_pi,lq_h0,lq_h2,lq_h8,bit_22
stage=${1:?setup|ab|c|d}

case "$stage" in
setup)
  echo "== card and host =="
  et-boot-check --status 2>&1 | tail -5
  et-who 2>&1 | head -5
  who; uptime
  echo "== operand set =="
  "$PY" tools/claims-v3/hl/make_hl.py "$GEN" --check | tail -3
  echo "== byte-identity against E60's build/hl-gen2 (every file E60 ran) =="
  n=0; bad=0
  for f in build/hl-gen2/tiles/*.bin build/hl-gen2/srcs/*.bin; do
    g=$GEN/${f#build/hl-gen2/}
    if [ -f "$g" ]; then
      a=$(sha256sum < "$f"); b=$(sha256sum < "$g")
      n=$((n + 1)); [ "$a" = "$b" ] || { bad=$((bad + 1)); echo "DIFFERS: $f"; }
    else
      echo "MISSING in hl-gen3: $f"
    fi
  done
  echo "byte-identical: $((n - bad))/$n"
  echo "== dry run, blocks A+B =="
  HL_GEN=$GEN V3_DRY=1 bash tools/claims-v3/hl/block.sh 650 "$ITEMS_AB" 2>&1 | tail -6
  echo "== dry run, block C =="
  "$PY" tools/claims-v3/hm/run_hm.py --protocol tools/claims-v3/hb/protocol-randn.json --list 2>&1 | head -4
  ;;
ab)
  p=${2:?first pass}; n=${3:?passes}
  export HL_GEN=$GEN
  setsid nohup bash tools/claims-v3/hl/queue_hl.sh "$p" "$n" "$ITEMS_AB" \
    > "$ROOT/build/e65-ab.log" 2>&1 < /dev/null &
  echo "ab queue started: passes $p..$((p + n - 1)), log $ROOT/build/e65-ab.log"
  ;;
d)
  p=${2:?first pass}; n=${3:?passes}
  export HL_GEN=$GEN HL_TARGET=${HL_TARGET:-200} HL_PREHEAT=${HL_PREHEAT:-0}   # A7: no approach, the plateau
  setsid nohup bash tools/claims-v3/hl/queue_hl.sh "$p" "$n" "$ITEMS_D" \
    > "$ROOT/build/e65-d.log" 2>&1 < /dev/null &
  echo "d queue started: passes $p..$((p + n - 1)) with no approach (A7), log $ROOT/build/e65-d.log"
  ;;
c)
  PY=$PY setsid nohup bash tools/claims-v3/hb/ladder_sessions.sh \
    > "$ROOT/build/e65-c.log" 2>&1 < /dev/null &
  echo "c sessions started, log $ROOT/build/e65-c.log"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
