#!/usr/bin/env bash
# E75 (Q129), the memory-path flip ladder, one stage per call. Run it from the tree that holds the binaries
# (aifoundry3: ~/aifoundry; aifoundry1: ~/nekko):
#
#   bash tools/claims-v3/mf/run_e75.sh setup           # operand set + --check, pattern check, .text hashes, dry run
#   bash tools/claims-v3/mf/run_e75.sh dry             # the dry run alone (no device call at all)
#   bash tools/claims-v3/mf/run_e75.sh go <first> <n>  # the detached queue of passes (CARD RUN)
#   bash tools/claims-v3/mf/run_e75.sh go1 <first> <n> # the same, L1 and DRAM only (the two arms that matter most)
#
# `setup` and `dry` never open a card: every device call goes through V3_DRY=1. `go` goes through mf/block.sh,
# which holds the card lock, caps every device process at `timeout 10` and stops on another user. Nothing here
# waits for a person.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=${MF_GEN:-$ROOT/build/mf-gen}
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
EN=${MF_ENERCAT:-build/enercat-hl/host/enercat_host}
ITEMS=${MF_ITEMS:-anchor_pi,mf_}
stage=${1:?setup|dry|go|go1}

case "$stage" in
setup)
  echo "== card and host =="
  et-boot-check --status 2>&1 | tail -5
  et-who 2>&1 | head -5
  who; uptime
  echo "== operand set =="
  "$PY" tools/claims-v3/mf/make_mf.py "$GEN" --check
  echo "== the patterns and the file operand this experiment needs =="
  for m in ld_l1 flw_pat; do
    if grep -a -q "$m" "$EN"; then echo "present: $m"; else echo "MISSING: $m in $EN"; fi
  done
  grep -a -q -- '--operands file:' "$EN" && echo "present: --operands file:" || echo "MISSING: --operands file:"
  echo "== .text hashes (compare between aifoundry1 and aifoundry3 before comparing numbers) =="
  bash tools/claims-v3/text_hash.sh "$EN" build/sparsity/host/sparsity_host 2>/dev/null
  echo "== dry run =="
  MF_GEN=$GEN V3_DRY=1 bash tools/claims-v3/mf/block.sh 7500 "$ITEMS" 2>&1 | tail -8
  echo "== size of one pass =="
  "$PY" tools/claims-v3/runitems.py /dev/null --root "$ROOT" --gen "$GEN" --items "$ITEMS" --tool "$EN" \
    --burnin 2 --item-s 4 --list
  ;;
dry)
  MF_GEN=$GEN V3_DRY=1 bash tools/claims-v3/mf/block.sh "${2:-7500}" "$ITEMS" 2>&1 | tail -40
  ;;
go|go1)
  p=${2:?first pass}; n=${3:?passes}
  it=$ITEMS
  [ "$stage" = go1 ] && it=anchor_pi,mf_l1_,mf_dram_
  export MF_GEN=$GEN
  setsid nohup bash tools/claims-v3/mf/queue_mf.sh "$p" "$n" "$it" \
    > "$ROOT/build/e75-mf.log" 2>&1 < /dev/null &
  echo "mf queue started: passes $p..$((p + n - 1)), items $it, log $ROOT/build/e75-mf.log"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
