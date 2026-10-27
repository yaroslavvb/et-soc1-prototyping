#!/usr/bin/env bash
# E72 (Q129) on aifoundry2 card 0, one stage per call. Run it from the tree that holds the binaries.
#
#   bash tools/claims-v3/lq6/run_e72.sh setup            # G0 gates, byte-identity against E60's operands, dry runs
#   bash tools/claims-v3/lq6/run_e72.sh pin              # set the static TDP level to 0 (arms the deadline watchdog)
#   bash tools/claims-v3/lq6/run_e72.sh smoke            # one short pass at the pinned clock: proves 600 MHz
#   bash tools/claims-v3/lq6/run_e72.sh go <first> <n>   # the ladder passes (detached)
#   bash tools/claims-v3/lq6/run_e72.sh restore          # original TDP back, read back, release the watchdog
#   bash tools/claims-v3/lq6/run_e72.sh back             # the post-restore stepping check (a smoke at the defaults)
#
# Every card touch goes through hl/block.sh, which holds the card lock, caps every device process at
# `timeout 10` and stops on another user. Nothing here waits for a person.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=${HL_GEN:-$ROOT/build/hl-gen}
GOVOUT=${GOVOUT:-$ROOT/build/claims-v3/e72-gov}
ITEMS=${E72_ITEMS:-anchor_pi,anchor_ones,anchor_zeros,anchor_randn,lq_,lb_}
stage=${1:?setup|pin|smoke|go|restore|back}

case "$stage" in
setup)
  echo "== host and card =="
  et-who 2>&1 | head -3; who; uptime
  echo "== G0 gates: identity, the originals, the vmin-LUT floor =="
  python3 -I tools/claims-v3/lq6/gov_e72.py gates --out "$GOVOUT"
  echo "== operand set: make_hl.py --check on the set E60 ran =="
  python3 tools/claims-v3/hl/make_hl.py "$GEN" --check | tail -3
  echo "== byte-identity against E60's published hashes (run_e67.sh setup's check, E60's set) =="
  ref=docs/reports/data/2026-10-20-bitflip-ladder/gen.sha256
  n=0; bad=0; miss=0
  while read -r h f; do
    case "$f" in tiles/*|srcs/*|manifest.json) ;; *) continue ;; esac
    if [ -f "$GEN/$f" ]; then
      g=$(sha256sum < "$GEN/$f" | cut -d' ' -f1)
      n=$((n + 1)); [ "$g" = "$h" ] || { bad=$((bad + 1)); echo "DIFFERS: $f"; }
    else
      miss=$((miss + 1)); echo "MISSING in $GEN: $f"
    fi
  done < "$ref"
  echo "byte-identical to E60: $((n - bad))/$n  (missing $miss)"
  echo "== dry run =="
  HL_GEN=$GEN V3_DRY=1 bash tools/claims-v3/hl/block.sh 7260 "$ITEMS" 2>&1 | tail -4
  ;;
pin)
  python3 -I tools/claims-v3/lq6/gov_e72.py pin --out "$GOVOUT" --deadline-s "${E72_DEADLINE_S:-4500}"
  python3 -I tools/claims-v3/lq6/gov_e72.py status --out "$GOVOUT"
  ;;
smoke)
  HL_GEN=$GEN HL_EXPN=e72 bash tools/claims-v3/hl/block.sh 900 "$ITEMS" --smoke
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  export HL_GEN=$GEN HL_EXPN=e72
  setsid nohup bash tools/claims-v3/hl/queue_hl.sh "$p" "$n" "$ITEMS" \
    > "$ROOT/build/e72-go.log" 2>&1 < /dev/null &
  echo "e72 queue started: passes $p..$((p + n - 1)), log $ROOT/build/e72-go.log"
  ;;
restore)
  python3 -I tools/claims-v3/lq6/gov_e72.py restore --out "$GOVOUT"
  ;;
back)
  HL_GEN=$GEN HL_EXPN=e72back bash tools/claims-v3/hl/block.sh 901 anchor_pi,lq_h8 --smoke
  python3 -I tools/claims-v3/lq6/gov_e72.py back --out "$GOVOUT"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
