#!/usr/bin/env bash
# E99 (Q132), which mechanism carries the DRAM pattern effect, one stage per call. Run it from the tree that holds the
# binaries (aifoundry3: ~/aifoundry). E75's block and queue unchanged (tools/claims-v3/mf/block.sh and queue_mf.sh), with
# MF_GEN=build/dm-gen, MF_EXPN=dm and MF_ENERCAT=build/enercat-e99/host/enercat_host, so the data land in
# build/claims-v3/aifoundry3/dm/p<pass>/ and each pass's code.sha256 hashes lib.sh and this directory.
#
#   bash tools/claims-v3/dm/run_e99.sh build            # build_host.sh. No card, but it loads the host: only with the card idle.
#   bash tools/claims-v3/dm/run_e99.sh setup            # the images' hashes, harness hashes, dry run. No card.
#   bash tools/claims-v3/dm/run_e99.sh dry              # the dry run alone (no device call at all)
#   bash tools/claims-v3/dm/run_e99.sh smoke 9901       # one short block: anchor_pi, dp_bern, dm_L17 (CARD RUN)
#   bash tools/claims-v3/dm/run_e99.sh go 9910 6        # the detached queue of passes (CARD RUN); log build/e99-dm.log
#   bash tools/claims-v3/dm/run_e99.sh status           # passes, block.json, card minutes
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=${DM_GEN:-$ROOT/build/dm-gen}
PY=${PY:-python3}
EN=build/enercat-e99/host/enercat_host
ITEMS=${DM_ITEMS:-anchor_pi,dp_,dm_}
export MF_GEN=$GEN MF_EXPN=dm MF_ENERCAT=$EN
stage=${1:?build|setup|dry|smoke|go|status}

case "$stage" in
build) bash tools/claims-v3/dm/build_host.sh ;;
setup)
  echo "== card and host =="
  et-who 2>&1 | head -5
  uptime
  echo "== the images, by hash against the Intel's =="
  ( cd "$GEN" && sha256sum -c gen.sha256 2>&1 | grep -v ': OK$' ; echo "sha256 check rc=${PIPESTATUS[0]}" )
  echo "== the operands this experiment needs =="
  for s in flw_pat 'bern:' '--operands file:' 'lines: needs a whole number'; do
    if grep -a -q -- "$s" "$EN"; then echo "present: $s"; else echo "MISSING: $s in $EN"; fi
  done
  echo "== .text hashes =="
  bash tools/claims-v3/text_hash.sh "$EN" build/sparsity/host/sparsity_host 2>/dev/null
  echo "== harness hashes =="
  sha256sum tools/claims-v3/lib.sh tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh tools/claims-v3/mf/block.sh \
    tools/claims-v3/mf/queue_mf.sh tools/claims-v3/mf/make_mf.py tools/claims-v3/dm/*
  echo "== dry run =="
  V3_DRY=1 bash tools/claims-v3/mf/block.sh 9900 "$ITEMS" > build/e99-dry.log 2>&1
  tail -6 build/e99-dry.log
  echo "== size of one pass =="
  "$PY" tools/claims-v3/runitems.py /dev/null --root "$ROOT" --gen "$GEN" --items "$ITEMS" --tool "$EN" \
    --burnin 2 --item-s 4 --list
  ;;
dry)
  V3_DRY=1 bash tools/claims-v3/mf/block.sh "${2:-9900}" "$ITEMS" 2>&1 | tail -40
  ;;
smoke)
  p=${2:?pass}
  bash tools/claims-v3/mf/block.sh "$p" anchor_pi,dp_bern,dm_L17 < /dev/null > "$ROOT/build/e99-smoke.log" 2>&1
  rc=$?
  tail -14 "$ROOT/build/e99-smoke.log"
  echo "smoke rc=$rc"
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  setsid nohup bash tools/claims-v3/mf/queue_mf.sh "$p" "$n" "$ITEMS" > "$ROOT/build/e99-dm.log" 2>&1 < /dev/null &
  echo "dm queue started: passes $p..$((p + n - 1)), items $ITEMS, log $ROOT/build/e99-dm.log"
  ;;
status)
  "$PY" - "$ROOT/build/claims-v3/aifoundry3/dm" <<'PYEOF'
import glob, json, os, sys
tot = 0.0
for d in sorted(glob.glob(os.path.join(sys.argv[1], "p99*"))):
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
