#!/usr/bin/env bash
# E67 (Q128) on aifoundry3, one stage per call. Run it from the tree that holds the binaries (~/aifoundry):
#
#   bash tools/claims-v3/ha/run_e67.sh setup           # hl-gen4, byte-identity against E65's set, dry runs
#   bash tools/claims-v3/ha/run_e67.sh as <first> <n>  # blocks 1+2+4: the A scan, busy partner, anchors (detached)
#   bash tools/claims-v3/ha/run_e67.sh ix <first> <n>  # block 3: the interaction grid (detached)
#
# Everything that touches the card goes through hl/block.sh, which holds the card lock, caps every device process
# at `timeout 10` and stops on another user. Nothing here waits for a person.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=$ROOT/build/hl-gen4
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
ITEMS_AS=anchor_pi,anchor_zeros,anchor_ones,anchor_randn,lq_h0,lb_h0,aq_,ap_h0,abit_,abp_,nrd_
ITEMS_IX=anchor_pi,ix_
stage=${1:?setup|as|ix}

case "$stage" in
setup)
  echo "== card and host =="
  et-boot-check --status 2>&1 | tail -5
  et-who 2>&1 | head -5
  who; uptime
  echo "== operand set =="
  "$PY" tools/claims-v3/hl/make_hl.py "$GEN" --check | tail -2
  echo "== byte-identity against E65's build/hl-gen3 (every file E60 and E65 ran) =="
  n=0; bad=0
  for f in build/hl-gen3/tiles/*.bin build/hl-gen3/srcs/*.bin; do
    g=$GEN/${f#build/hl-gen3/}
    if [ -f "$g" ]; then
      a=$(sha256sum < "$f"); b=$(sha256sum < "$g")
      n=$((n + 1)); [ "$a" = "$b" ] || { bad=$((bad + 1)); echo "DIFFERS: $f"; }
    else
      echo "MISSING in hl-gen4: $f"
    fi
  done
  echo "byte-identical: $((n - bad))/$n"
  echo "== dry run, blocks 1+2+4 =="
  HL_GEN=$GEN V3_DRY=1 bash tools/claims-v3/hl/block.sh 7490 "$ITEMS_AS" 2>&1 | tail -4
  echo "== dry run, block 3 =="
  HL_GEN=$GEN V3_DRY=1 bash tools/claims-v3/hl/block.sh 7491 "$ITEMS_IX" 2>&1 | tail -4
  ;;
as)
  p=${2:?first pass}; n=${3:?passes}
  export HL_GEN=$GEN
  setsid nohup bash tools/claims-v3/hl/queue_hl.sh "$p" "$n" "$ITEMS_AS" \
    > "$ROOT/build/e67-as.log" 2>&1 < /dev/null &
  echo "as queue started: passes $p..$((p + n - 1)), log $ROOT/build/e67-as.log"
  ;;
ix)
  p=${2:?first pass}; n=${3:?passes}
  export HL_GEN=$GEN
  setsid nohup bash tools/claims-v3/hl/queue_hl.sh "$p" "$n" "$ITEMS_IX" \
    > "$ROOT/build/e67-ix.log" 2>&1 < /dev/null &
  echo "ix queue started: passes $p..$((p + n - 1)), log $ROOT/build/e67-ix.log"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
