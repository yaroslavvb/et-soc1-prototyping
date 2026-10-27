#!/usr/bin/env bash
# E74 (Q129), the register-file cell ladder, one stage per call. Run it from the tree that holds the binaries
# (aifoundry3: ~/aifoundry; aifoundry1: ~/nekko):
#
#   bash tools/claims-v3/rf/run_e74.sh setup          # operand set + --check, binary identity, .text hashes, dry run
#   bash tools/claims-v3/rf/run_e74.sh dry            # the dry run alone (no device call at all)
#   bash tools/claims-v3/rf/run_e74.sh go <first> <n>  # the detached queue of passes (CARD RUN)
#
# `setup` and `dry` never open a card: every device call goes through V3_DRY=1. `go` goes through rf/block.sh,
# which holds the card lock, caps every device process at `timeout 10` and stops on another user. Nothing here
# waits for a person.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=${RF_GEN:-$ROOT/build/rf-gen}
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
EN=${RF_ENERCAT:-build/enercat-df/host/enercat_host}
ITEMS=${RF_ITEMS:-anchor_pi,rf_,rfz_}
stage=${1:?setup|dry|go}

case "$stage" in
setup)
  echo "== card and host =="
  et-boot-check --status 2>&1 | tail -5
  et-who 2>&1 | head -5
  who; uptime
  echo "== operand set =="
  RF_GEN=$GEN "$PY" tools/claims-v3/rf/make_rf.py "$GEN" --check
  echo "== the two kernels this experiment needs =="
  for m in df.un1a.fnot df.un1b.fnot; do
    if grep -a -q "$m" "$EN"; then echo "present: $m"; else echo "MISSING: $m in $EN"; fi
  done
  grep -a -q -- '--operands file:' "$EN" && echo "present: --operands file:" || echo "MISSING: --operands file:"
  echo "== .text hashes (compare these between aifoundry1 and aifoundry3 before comparing numbers) =="
  bash tools/claims-v3/text_hash.sh "$EN" build/sparsity/host/sparsity_host 2>/dev/null
  echo "== dry run =="
  RF_GEN=$GEN V3_DRY=1 bash tools/claims-v3/rf/block.sh 7400 "$ITEMS" 2>&1 | tail -6
  echo "== size of one pass =="
  "$PY" tools/claims-v3/hl/run_hl.py /dev/null --root "$ROOT" --gen "$GEN" --items "$ITEMS" --burnin 2 --ec-s 4 --list
  ;;
dry)
  RF_GEN=$GEN V3_DRY=1 bash tools/claims-v3/rf/block.sh "${2:-7400}" "$ITEMS" 2>&1 | tail -20
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  export RF_GEN=$GEN
  setsid nohup bash tools/claims-v3/rf/queue_rf.sh "$p" "$n" "$ITEMS" \
    > "$ROOT/build/e74-rf.log" 2>&1 < /dev/null &
  echo "rf queue started: passes $p..$((p + n - 1)), log $ROOT/build/e74-rf.log"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
