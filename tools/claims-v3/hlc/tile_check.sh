#!/usr/bin/env bash
# E63: before the session, one short launch of every operand the protocol runs, with --dump-tiles, on the
# session's own mask and minions: the operand files must come back byte for byte, and ones and pi as tiles
# of every float 1.0 and pi. One launch each (--seconds 0: the heater's calibration launch only), under the
# card lock taken without waiting, every process under timeout 10 with stdin from /dev/null.
# Usage, on aifoundry2 from build/e63/code:  bash tile_check.sh <outdir>
set -u
ROOT=$HOME/claude/et-soc1-prototyping
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "${1:?usage: tile_check.sh <outdir>}"
OUT=$(cd "$1" && pwd)
cd "$ROOT" || exit 2
export LD_LIBRARY_PATH=/opt/et/lib
HEATER=build/sparsity_t2/host/sparsity_host
KERNEL=$ROOT/build/sparsity_t2/kernel/sparsity.elf
et-who > "$OUT/et-who.txt" 2>&1
cat "$OUT/et-who.txt"
exec 9<>/run/lock/etsoc-shire0.lock
if ! flock -n 9; then
  echo "the card lock is held: not ours, not waiting"
  exit 3
fi
rc_all=0
for v in file:build/hl-gen2/tiles/lq_h23.bin file:build/hl-gen2/tiles/lq_h0.bin file:build/hl-gen2/tiles/lq_h8.bin ones pi; do
  name=${v#file:}
  name=${name##*/}
  name=${name%.bin}
  arg=$v
  case "$v" in file:*) arg="file:$ROOT/${v#file:}" ;; esac
  timeout 10 "$HEATER" --test fma --type fp32 --pattern none --values "$arg" --shires 0xffffffff \
    --per-shire 8 --seconds 0 --budget 9.5 --seed 1 --kernel "$KERNEL" --stop-file "$OUT/STOP" \
    --dump-tiles "$OUT/$name.dump" < /dev/null > "$OUT/$name.out" 2> "$OUT/$name.err"
  rc=$?
  echo "$name: rc $rc, $(stat -c %s "$OUT/$name.dump" 2>/dev/null || echo 0) bytes dumped"
  [ "$rc" -eq 0 ] || rc_all=1
done
flock -u 9
exec 9>&-
python3 "$HERE/tile_compare.py" "$ROOT" "$OUT" || rc_all=1
exit $rc_all
