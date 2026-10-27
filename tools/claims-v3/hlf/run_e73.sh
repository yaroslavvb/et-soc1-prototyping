#!/usr/bin/env bash
# E73: stage the frozen code on aifoundry2 and start the card session.
#
# Run it ON aifoundry2, from the repo checkout (~/claude/et-soc1-prototyping), which is where the
# heater build, the operand tiles and the camera are.  It never touches the governor, never sets a
# clock, never resets anything: it opens the card only through run_hlc.py, which takes the card lock
# and holds every launch under `timeout 10`.
#
#   bash tools/claims-v3/hlf/run_e73.sh stage          # build/e73/code from E63's frozen copy + hlf
#   bash tools/claims-v3/hlf/run_e73.sh check          # protocol, host, heater, tiles, free space (--dry-ish)
#   bash tools/claims-v3/hlf/run_e73.sh go <rundir>    # the real session, detached
#   bash tools/claims-v3/hlf/run_e73.sh watch <rundir>
set -u
cmd=${1:?usage: run_e73.sh stage|check|go|watch [rundir]}
ROOT="$HOME/claude/et-soc1-prototyping"
CODE="$ROOT/build/e73/code"
SRC="$ROOT/build/e63/code"

stage() {
  mkdir -p "$CODE"
  # E63's frozen runner, recorder, reducer and lock-in, byte for byte
  for f in run_hlc.py record_cam.py reduce_hm.py p3rec.py fpa_trace.py lockin_hlc.py start_hlc.sh \
           tile_check.sh tile_compare.py; do
    cp -p "$SRC/$f" "$CODE/$f"
  done
  mkdir -p "$CODE/prereg" "$CODE/hlc"
  cp -p "$SRC"/prereg/*.npy "$CODE/prereg/"
  # lockin_hlf.py imports lockin_hlc from ../hlc, so give it that shape
  cp -p "$SRC/lockin_hlc.py" "$CODE/hlc/lockin_hlc.py"
  for f in lockin_hlf.py predict_e73.py fit_hlf.py make_protocol_e73.py protocol-e73.json \
           predictions.json; do
    cp -p "$ROOT/tools/claims-v3/hlf/$f" "$CODE/$f"
  done
  ( cd "$CODE" && sha256sum ./*.py ./*.json ./hlc/*.py ./prereg/*.npy > SHA256SUMS )
  echo "staged $CODE"
  sed -n '1,3p' "$CODE/SHA256SUMS"
}

check() {
  cd "$CODE" || exit 1
  echo "== host =="; hostname; date "+%F %T %Z"
  echo "== free =="; df -h "$HOME" | tail -1
  echo "== heater =="; ls -l "$ROOT/build/sparsity_t2/host/sparsity_host" \
      "$ROOT/build/sparsity_t2/kernel/sparsity.elf"
  echo "== tiles =="; sha256sum "$ROOT"/build/hl-gen2/tiles/lq_h23.bin \
      "$ROOT"/build/hl-gen2/tiles/lq_h0.bin
  echo "== card =="; et-who 2>&1 | head -3
  echo "== protocol =="; python3 run_hlc.py --protocol protocol-e73.json --list 2>&1 | tail -22
}

case "$cmd" in
  stage) stage ;;
  check) check ;;
  go)
    out=${2:?usage: run_e73.sh go <rundir>}
    cd "$CODE" || exit 1
    bash start_hlc.sh "$out" "" protocol-e73.json
    ;;
  watch)
    out=${2:?usage: run_e73.sh watch <rundir>}
    tail -5 "$out/run.out" 2>/dev/null
    tail -3 "$out/cam/record.log" 2>/dev/null
    ;;
  *) echo "unknown: $cmd"; exit 2 ;;
esac
