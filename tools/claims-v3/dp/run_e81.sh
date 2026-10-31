#!/usr/bin/env bash
# E81 (Q130), the DRAM pattern question, one stage per call. Run it from the tree that holds the binaries
# (aifoundry3: ~/aifoundry). It runs E75's block and queue unchanged (tools/claims-v3/mf/block.sh and queue_mf.sh)
# with MF_GEN=build/dp-gen and MF_EXPN=dp, so the data land in build/claims-v3/aifoundry3/dp/p<pass>/ and each
# pass's code.sha256 hashes lib.sh and this directory.
#
#   bash tools/claims-v3/dp/run_e81.sh setup           # images + --check, operand strings, hashes, dry run. No card.
#   bash tools/claims-v3/dp/run_e81.sh dry             # the dry run alone (no device call at all)
#   bash tools/claims-v3/dp/run_e81.sh smoke 8101      # one short block: anchor_pi, dp_bern, dp_s2 (CARD RUN)
#   bash tools/claims-v3/dp/run_e81.sh go 8110 10      # the detached queue of passes (CARD RUN); log build/e81-dp.log
#   bash tools/claims-v3/dp/run_e81.sh status          # passes, block.json, card minutes
#
# `setup` and `dry` never open a card: every device call goes through V3_DRY=1. `smoke` and `go` go through
# mf/block.sh, which holds the card lock, caps every device process at `timeout 10` and stops on another user.
# Nothing here waits for a person.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=${DP_GEN:-$ROOT/build/dp-gen}
PY=${PY:-python3}
EN=build/enercat-hl/host/enercat_host
ITEMS=${DP_ITEMS:-anchor_pi,dp_}
export MF_GEN=$GEN MF_EXPN=dp
stage=${1:?setup|dry|smoke|go|status}

case "$stage" in
setup)
  echo "== card and host =="
  et-who 2>&1 | head -5
  uptime
  echo "== operand set =="
  "$PY" tools/claims-v3/dp/make_dp.py "$GEN" --check --e75-gen build/mf-gen
  echo "== the pattern and the operands this experiment needs =="
  for s in flw_pat 'bern:' '--operands file:'; do
    if grep -a -q -- "$s" "$EN"; then echo "present: $s"; else echo "MISSING: $s in $EN"; fi
  done
  echo "== .text hashes (E75 ran the same binary) =="
  bash tools/claims-v3/text_hash.sh "$EN" build/sparsity/host/sparsity_host 2>/dev/null
  echo "== harness hashes =="
  sha256sum tools/claims-v3/lib.sh tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh tools/claims-v3/mf/block.sh \
    tools/claims-v3/mf/queue_mf.sh tools/claims-v3/mf/make_mf.py tools/claims-v3/dp/*
  echo "== dry run =="
  V3_DRY=1 bash tools/claims-v3/mf/block.sh 8100 "$ITEMS" 2>&1 | tail -8
  echo "== size of one pass =="
  "$PY" tools/claims-v3/runitems.py /dev/null --root "$ROOT" --gen "$GEN" --items "$ITEMS" --tool "$EN" \
    --burnin 2 --item-s 4 --list
  ;;
dry)
  V3_DRY=1 bash tools/claims-v3/mf/block.sh "${2:-8100}" "$ITEMS" 2>&1 | tail -40
  ;;
smoke)
  p=${2:?pass}
  bash tools/claims-v3/mf/block.sh "$p" anchor_pi,dp_bern,dp_s2 < /dev/null > "$ROOT/build/e81-smoke.log" 2>&1
  rc=$?
  tail -14 "$ROOT/build/e81-smoke.log"
  echo "smoke rc=$rc"
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  setsid nohup bash tools/claims-v3/mf/queue_mf.sh "$p" "$n" "$ITEMS" > "$ROOT/build/e81-dp.log" 2>&1 < /dev/null &
  echo "dp queue started: passes $p..$((p + n - 1)), items $ITEMS, log $ROOT/build/e81-dp.log"
  ;;
status)
  "$PY" - "$ROOT/build/claims-v3/aifoundry3/dp" <<'PYEOF'
import glob, json, os, sys
tot = 0.0
for d in sorted(glob.glob(os.path.join(sys.argv[1], "p81*"))):
    try:
        b = json.load(open(os.path.join(d, "block.json")))
        m = (b["t1_ms"] - b["t0_ms"]) / 60000.0
        tot += m
        print("%s %s %.2f min, die %s -> %s C %s" % (os.path.basename(d), b["status"], m, b["die_c_start"],
                                                    b["die_c_end"], b.get("note", "")[:60]))
    except (OSError, ValueError, KeyError):
        print("%s (running or no block.json)" % os.path.basename(d))
print("card minutes in finished blocks: %.2f" % tot)
PYEOF
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
