#!/usr/bin/env bash
# E110 (Q133), the memory path's width ladder: the stages that touch no card, plus the detached session. Run on aifoundry3 from ~/aifoundry,
# with tools/claims-v3/e110/ and build/e110-gen/ rsynced in from the Intel's lab clone.
#
#   bash tools/claims-v3/e110/run_e110.sh setup     # image hashes, harness and binary hashes, the dry run. No card.
#   bash tools/claims-v3/e110/run_e110.sh go        # the detached card session (session_e110.sh): config, smoke, gate, passes, config
#   bash tools/claims-v3/e110/run_e110.sh status    # passes, block.json, card minutes
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
EN=build/enercat-e99/host/enercat_host
ITEMS=anchor_pi,dp_zeros,dp_bern,dp_c1,dm_,wl_,vl_,l2_
export MF_GEN=$ROOT/build/e110-gen MF_EXPN=e110 MF_ENERCAT=$EN
case "${1:?setup|go|status}" in
setup)
  echo "== card and host =="; et-who 2>&1 | head -5; uptime
  echo "== the images, by hash against the Intel's =="
  ( cd build/e110-gen && sha256sum -c gen.sha256 2>&1 | grep -v ': OK$'; echo "sha256 check rc=${PIPESTATUS[0]}" )
  echo "== the host binary (E99's) =="; sha256sum "$EN"; bash tools/claims-v3/text_hash.sh "$EN" build/sparsity/host/sparsity_host 2>/dev/null
  for s in flw_pat '--operands file:' 'lines: needs a whole number'; do grep -a -q -- "$s" "$EN" && echo "present: $s" || echo "MISSING: $s"; done
  echo "== harness hashes =="
  sha256sum tools/claims-v3/lib.sh tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh tools/claims-v3/mf/block.sh \
    tools/claims-v3/mf/queue_mf.sh tools/claims-v3/mf/make_mf.py tools/claims-v3/e110/*
  echo "== stop files =="; ls -la build/e110-STOP build/mf-STOP build/claims-v3/STOP 2>&1 | head -3
  echo "== dry run =="
  V3_DRY=1 bash tools/claims-v3/mf/block.sh 11000 "$ITEMS" > build/e110-dry.log 2>&1; echo "dry rc=$?"; tail -4 build/e110-dry.log
  grep -c 'enercat_host' build/e110-dry.log
  python3 tools/claims-v3/runitems.py /dev/null --root "$ROOT" --gen "$MF_GEN" --items "$ITEMS" --tool "$EN" --burnin 2 --item-s 4 --list
  ;;
go)
  mkdir -p build/e110
  setsid nohup bash tools/claims-v3/e110/session_e110.sh > build/e110/session.out 2>&1 < /dev/null &
  echo "e110 session started (pid $!), log build/e110/session.log"
  ;;
status)
  tail -4 build/e110/session.log 2>/dev/null; tail -3 build/e110/queue.out 2>/dev/null
  python3 - "$ROOT/build/claims-v3/$(hostname)/e110" <<'PYEOF'
import glob, json, os, sys
tot = 0.0
for d in sorted(glob.glob(os.path.join(sys.argv[1], "p11*"))):
    try:
        b = json.load(open(os.path.join(d, "block.json")))
        m = (b["t1_ms"] - b["t0_ms"]) / 60000.0
        tot += m
        print("%s %s %.2f min, die %s -> %s C" % (os.path.basename(d), b["status"], m, b["die_c_start"], b["die_c_end"]))
    except (OSError, ValueError, KeyError):
        print("%s (running or no block.json)" % os.path.basename(d))
print("card minutes in finished blocks: %.2f" % tot)
PYEOF
  ;;
*) echo "unknown stage" >&2; exit 2 ;;
esac
