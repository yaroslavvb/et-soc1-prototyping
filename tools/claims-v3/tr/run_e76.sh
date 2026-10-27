#!/usr/bin/env bash
# E76 (Q129), the thirteen instructions that trap in U-mode, one stage per call. Run it from the tree that holds
# the binaries (aifoundry3: ~/aifoundry; aifoundry1: ~/nekko):
#
#   bash tools/claims-v3/tr/run_e76.sh build          # build build/enercat-tr (-DENERCAT_TR=ON). NO CARD.
#   bash tools/claims-v3/tr/run_e76.sh static         # count the trap path and the soft-float routines. NO CARD.
#   bash tools/claims-v3/tr/run_e76.sh setup          # item list, mode list, .text hashes, dry run. NO CARD.
#   bash tools/claims-v3/tr/run_e76.sh probe <first> <n>   # the probe passes: which of the thirteen trap (CARD)
#   bash tools/claims-v3/tr/run_e76.sh price <first> <n> <items>   # price the ones that do NOT trap (CARD)
#
# `build`, `static` and `setup` never open a card. `probe` and `price` go through tr/block.sh, which holds the
# card lock, caps every device process at `timeout 10` and stops on another user. Nothing waits for a person.
#
# A probe launch of a trapping mode ENDS THE KERNEL on every hart that reaches the instruction: the host prints
# "ok":false with no ops and exits 1. That is the result, not a failure of the harness. No card is reset, no
# driver is reloaded, nothing is retried beyond runitems.py's own single retry.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=${TR_GEN:-$ROOT/build/tr-gen}
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
EN=${TR_ENERCAT:-build/enercat-tr/host/enercat_host}
stage=${1:?build|static|setup|probe|price}

case "$stage" in
build)
  nice -n 19 cmake -S workloads/enercat -B build/enercat-tr -DCMAKE_PREFIX_PATH=/opt/et -DENERCAT_TR=ON -Wno-dev \
    > build/enercat-tr.cmake.log 2>&1 || { echo "CMAKE FAILED"; tail -25 build/enercat-tr.cmake.log; exit 1; }
  nice -n 19 cmake --build build/enercat-tr -j4 > build/enercat-tr.build.log 2>&1 ||
    { echo "BUILD FAILED"; grep -nE "[Ee]rror" build/enercat-tr.build.log | head -30; exit 1; }
  echo "built $EN"
  bash tools/claims-v3/text_hash.sh "$EN"
  ;;
static)
  "$PY" tools/claims-v3/tr/static_cost.py --out "${2:-$ROOT/build/tr-static}"
  ;;
setup)
  echo "== card and host =="
  et-boot-check --status 2>&1 | tail -5
  et-who 2>&1 | head -5
  who; uptime
  echo "== the modes in this build =="
  LD_LIBRARY_PATH=/opt/et/lib timeout 20 "$EN" --list 2>/dev/null | grep '^tr\.' || echo "NO tr. modes: built without -DENERCAT_TR=ON"
  echo "== the thirteen mnemonics in the device kernel =="
  OD=/opt/et/riscv64-unknown-elf/bin/objdump
  if [ -x "$OD" ]; then
    "$OD" -d build/enercat-tr/kernel/enercat.elf > build/enercat-tr.dis.txt 2>/dev/null
    for m in fdiv.s fsqrt.s fdiv.ps fsqrt.ps frsq.ps fsin.ps fdiv.pi fdivu.pi frem.pi fremu.pi fcvt.l.s fcvt.s.l rdcycle; do
      printf '%-10s %s\n' "$m" "$(grep -cw -- "$m" build/enercat-tr.dis.txt || true)"
    done
  else
    echo "no cross objdump at $OD"
  fi
  echo "== item list =="
  "$PY" tools/claims-v3/tr/make_tr.py "$GEN" --check | tail -25
  echo "== .text hashes =="
  bash tools/claims-v3/text_hash.sh "$EN" build/sparsity/host/sparsity_host 2>/dev/null
  echo "== dry run (probe items) =="
  TR_GEN=$GEN V3_DRY=1 bash tools/claims-v3/tr/block.sh 7600 anchor_pi,trp_,trx_ 2>&1 | tail -8
  echo "== size of one probe pass =="
  "$PY" tools/claims-v3/runitems.py /dev/null --root "$ROOT" --gen "$GEN" --items anchor_pi,trp_,trx_ \
    --tool "$EN" --burnin 1 --item-s 1 --list
  ;;
probe)
  p=${2:?first pass}; n=${3:?passes}
  export TR_GEN=$GEN TR_BURNIN=${TR_BURNIN:-1} TR_ITEM_S=${TR_ITEM_S:-1}
  setsid nohup bash tools/claims-v3/tr/queue_tr.sh "$p" "$n" anchor_pi,trp_,trx_ \
    > "$ROOT/build/e76-tr-probe.log" 2>&1 < /dev/null &
  echo "tr probe started: passes $p..$((p + n - 1)), log $ROOT/build/e76-tr-probe.log"
  ;;
price)
  p=${2:?first pass}; n=${3:?passes}; items=${4:?items, e.g. anchor_pi,trl_tr_ctl_frcp_ps}
  export TR_GEN=$GEN
  setsid nohup bash tools/claims-v3/tr/queue_tr.sh "$p" "$n" "$items" \
    > "$ROOT/build/e76-tr-price.log" 2>&1 < /dev/null &
  echo "tr price started: passes $p..$((p + n - 1)), items $items, log $ROOT/build/e76-tr-price.log"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
