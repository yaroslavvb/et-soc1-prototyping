#!/usr/bin/env bash
# E79 (Q130) on aifoundry3, one stage per call. Run it from the tree that holds the binaries (the E67/E70 tree):
#
#   bash tools/claims-v3/hlp/run_e79.sh setup          # build/hlp-gen, --check, card and host state, dry runs
#   bash tools/claims-v3/hlp/run_e79.sh ident          # read-only identity: ettelem config + firmware revisions
#   bash tools/claims-v3/hlp/run_e79.sh smoke          # five 2 s runs at the current reading, no preheat
#   bash tools/claims-v3/hlp/run_e79.sh go <first> <n> # the measured passes (detached on the box)
#
# Everything that touches the card goes through hlp/block.sh, which holds the card lock, caps every device process
# at `timeout 10` and stops on another user. Nothing here waits for a person. No knob is written: `ettelem config`
# and DM_CMD_GET_* are reads, and the card's TDP stays at the boot-time 0 that pins it to 600 MHz.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=$ROOT/build/hlp-gen
PY=${PY:-$ROOT/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
ITEMS=anchor_pi,z16,z8,h16q,h16q_e7,b16_,b16p_,b16m2,b16m4,a16q,a16q_e7,a16_,h8q,b8_,b8p_,b8m2,b8m4,a8q,a8_,h32q,b32_
stage=${1:?setup|ident|smoke|go}

case "$stage" in
setup)
  echo "== card and host =="
  et-boot-check --status 2>&1 | tail -5
  et-who 2>&1 | head -5
  who; uptime
  echo "== operand set =="
  "$PY" tools/claims-v3/hlp/make_hlp.py "$GEN" --check | tail -3
  ( cd "$GEN" && sha256sum manifest.json tiles/* ) | sha256sum
  echo "== the binary takes fp16 and int8 with file: operands =="
  for s in fp16 int8 'file:'; do
    if grep -a -q "$s" build/sparsity/host/sparsity_host; then echo "  $s: present"; else echo "  $s: MISSING"; fi
  done
  echo "== dry run, every item =="
  HLP_GEN=$GEN V3_DRY=1 bash tools/claims-v3/hlp/block.sh 7900 "$ITEMS" 2>&1 | tail -4
  echo "== estimate =="
  "$PY" tools/claims-v3/hlp/run_hlp.py /dev/null --root "$ROOT" --gen "$GEN" --items "$ITEMS" --list
  ;;
ident)
  # Read-only. ettelem config is taken by block.sh too (config_start/config_end per pass); this stage adds the
  # firmware revisions, which no E79 pass needs and which the Horace hub's Status item 7 asks for.
  out=$ROOT/build/hlp-ident
  mkdir -p "$out"
  et-lab-manifest > "$out/et-lab-manifest.txt" 2>&1 || true
  flock -w 120 /run/lock/etsoc-shire0.lock timeout 20 build/ettelem/ettelem config 2>/dev/null |
    grep '^{' | tail -1 > "$out/config.json" || true
  for c in DM_CMD_GET_MODULE_FIRMWARE_REVISIONS DM_CMD_GET_MODULE_UPTIME DM_CMD_GET_ASIC_CHIP_REVISION \
           DM_CMD_GET_MODULE_STATIC_TDP_LEVEL DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS; do
    echo "### $c"
    flock -w 120 /run/lock/etsoc-shire0.lock timeout 20 /opt/et/bin/dev_mngt_service \
      -m "$c" -n "${V3_DEVICE:-0}" -u 5000 2>&1 | tail -25
  done > "$out/firmware.txt" 2>&1
  cat "$out/config.json"; echo; grep -v '^$' "$out/firmware.txt" | head -60
  ;;
smoke)
  HLP_GEN=$GEN bash tools/claims-v3/hlp/block.sh "${2:-7901}" "$ITEMS" --smoke 2>&1 | tail -20
  ;;
go)
  p=${2:?first pass}; n=${3:?passes}
  export HLP_GEN=$GEN
  setsid nohup bash tools/claims-v3/hlp/queue_hlp.sh "$p" "$n" "$ITEMS" \
    > "$ROOT/build/e79-queue.log" 2>&1 < /dev/null &
  echo "e79 queue started: passes $p..$((p + n - 1)), log $ROOT/build/e79-queue.log"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
