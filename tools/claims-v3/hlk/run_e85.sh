#!/usr/bin/env bash
# E85: stage the frozen code on aifoundry2, check, run the card session, reduce.
#
# Run it ON aifoundry2, from the lab checkout (~/claude/et-soc1-prototyping) after `git pull --ff-only`,
# which holds the heater build, E60's operand tiles, the kinds tiles and the camera.  It never touches the
# governor, never sets a clock, never resets anything: the card is opened only by run_hlk.py (E63's runner,
# which takes the card lock without waiting and holds every launch under `timeout 10`) and by
# tile_check_hlk.py (the same lock and timeout).
#
#   bash tools/claims-v3/hlk/run_e85.sh stage            # build/e85/code from the committed files, SHA256SUMS
#   bash tools/claims-v3/hlk/run_e85.sh check            # host, free space, heater, tiles, card, the plan
#   bash tools/claims-v3/hlk/run_e85.sh dry <rundir>     # the dry protocol, no card: camera + toy sampler
#   bash tools/claims-v3/hlk/run_e85.sh tiles <outdir>   # the operand check (opens the card: after the claim)
#   bash tools/claims-v3/hlk/run_e85.sh go <rundir>      # the real session, detached
#   bash tools/claims-v3/hlk/run_e85.sh reduce <rundir> [protocol]   # reduce_hm + fpa_trace + lockin_hlk + dips
set -u
cmd=${1:?usage: run_e85.sh stage|check|dry|tiles|go|watch|reduce [dir]}
ROOT="$HOME/claude/et-soc1-prototyping"
CODE="$ROOT/build/e85/code"
T="$ROOT/tools/claims-v3"
SRC="${HLK_SRC:-$T/hlk}"   # where the hlk files come from (the committed tree, or a pre-commit copy for the dry run)

stage() {
  mkdir -p "$CODE/prereg"
  for f in run_hlc.py lockin_hlc.py fpa_trace.py dips_hlc.py; do cp -p "$T/hlc/$f" "$CODE/$f"; done
  for f in record_cam.py reduce_hm.py p3rec.py; do cp -p "$T/hm/$f" "$CODE/$f"; done
  cp -p "$T"/hlc/prereg/*.npy "$CODE/prereg/"
  for f in run_hlk.py lockin_hlk.py tile_check_hlk.py start_hlk.sh protocol-e85.json protocol-e85-dry.json \
           predictions.json; do cp -p "$SRC/$f" "$CODE/$f"; done
  ( cd "$CODE" && sha256sum ./*.py ./*.sh ./*.json ./prereg/*.npy > SHA256SUMS )
  echo "staged $CODE: hlc/hm from $(git -C "$ROOT" rev-parse --short HEAD), hlk from $SRC"
  echo "== the same files in E63's frozen copy (build/e63/code), for the record =="
  for f in run_hlc.py lockin_hlc.py fpa_trace.py record_cam.py reduce_hm.py p3rec.py; do
    a=$(sha256sum "$CODE/$f" | cut -c1-16)
    b=$(sha256sum "$ROOT/build/e63/code/$f" 2>/dev/null | cut -c1-16)
    echo "  $f  staged $a  e63-frozen ${b:-absent}"
  done
}

check() {
  cd "$CODE" || exit 1
  echo "== host =="; hostname; date "+%F %T %Z"; uptime
  echo "== who (count) =="; who | wc -l
  echo "== free =="; df -h "$HOME" | tail -1
  echo "== heater =="; sha256sum "$ROOT/build/sparsity_t2/host/sparsity_host" "$ROOT/build/sparsity_t2/kernel/sparsity.elf"
  echo "== operand tiles =="; sha256sum "$ROOT"/build/hl-gen2/tiles/lq_h23.bin "$ROOT"/build/hl-gen2/tiles/lq_h0.bin \
      "$T"/kinds/tiles/fp32/randn.bin "$T"/kinds/tiles/fp32/zeros.bin "$T"/kinds/tiles/fp16/randn.bin \
      "$T"/kinds/tiles/int8/full.bin "$T"/kinds/tiles/fp32/sparse90.bin
  echo "== card =="; timeout 10 et-who 2>&1 | head -3
  echo "== camera =="; curl -s -m 6 http://p3-phone:8080/health | head -c 400; echo
  echo "== plan =="; python3 run_hlk.py --protocol protocol-e85.json --list 2>&1 | sed -n '1,12p'
}

case "$cmd" in
  stage) stage ;;
  check) check ;;
  dry)
    out=${2:?usage: run_e85.sh dry <rundir>}
    cd "$CODE" || exit 1
    bash start_hlk.sh "$out" --dry protocol-e85-dry.json
    ;;
  tiles)
    out=${2:?usage: run_e85.sh tiles <outdir>}
    cd "$CODE" || exit 1
    python3 tile_check_hlk.py --protocol protocol-e85.json --out "$out"
    ;;
  go)
    out=${2:?usage: run_e85.sh go <rundir>}
    cd "$CODE" || exit 1
    bash start_hlk.sh "$out" "" protocol-e85.json
    ;;
  watch)
    out=${2:?usage: run_e85.sh watch <rundir>}
    tail -4 "$out/run.out" 2>/dev/null
    tail -2 "$out/cam/record.log" 2>/dev/null
    ;;
  reduce)
    out=${2:?usage: run_e85.sh reduce <rundir> [protocol]}
    proto=${3:-protocol-e85.json}
    cd "$CODE" || exit 1
    nice -n 5 python3 reduce_hm.py "$out" --out "$out-RED" &&
    nice -n 5 python3 fpa_trace.py "$out" --out "$out-RED/fpa.npz" &&
    nice -n 5 python3 lockin_hlk.py "$out-RED" --protocol "$proto" --predictions predictions.json \
        --template prereg/e62_bloom_dt.npy --scene-ref prereg/e62_scene.npy --fpa "$out-RED/fpa.npz" \
        --out "$out-ANA" &&
    nice -n 5 python3 dips_hlc.py "$out-RED" --out "$out-ANA/dips.json"
    ;;
  *) echo "unknown: $cmd"; exit 2 ;;
esac
