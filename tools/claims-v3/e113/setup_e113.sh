#!/usr/bin/env bash
# E113 (Q133): files-only setup on aifoundry3, before the claim (run from ~/aifoundry, the tree that holds the binaries).
#   bash tools/claims-v3/e113/setup_e113.sh
# Writes build/hl-gen6-e113 (make_e113.py --check), checks that every file of build/hl-gen5 (E70's operand set) is
# byte-identical in it, prints the card's holders and the host's load, and runs the registered item list as a V3_DRY=1 dry
# run (every device call printed, none made). Opens no device; sets nothing.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=$ROOT/build/hl-gen6-e113
PY=${PY:-$ROOT/.venv/bin/python3}; [ -x "$PY" ] || PY=python3
. tools/claims-v3/e113/items_e113.sh
echo "== $(date '+%F %T %Z') host and card (read only) =="
et-who 2>&1 | head -5; echo "logins: $(who | wc -l) (names not recorded)"; uptime; cat /proc/loadavg
ls -la build/enercat-hl/host/enercat_host build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1 | awk '{print $5, $6, $7, $8, $9}'
echo "== operand set $GEN =="
rm -rf "${GEN:?}"
"$PY" tools/claims-v3/e113/make_e113.py "$GEN" --check | tail -3
echo "== byte-identity against build/hl-gen5 (E70's set: every file E60, E65, E67 and E70 ran) =="
n=0; bad=0
for f in "$ROOT"/build/hl-gen5/tiles/*.bin "$ROOT"/build/hl-gen5/srcs/*.bin; do
  g=$GEN/${f#$ROOT/build/hl-gen5/}
  n=$((n + 1))
  if [ ! -f "$g" ] || [ "$(sha256sum < "$f")" != "$(sha256sum < "$g")" ]; then bad=$((bad + 1)); echo "DIFFERS: $f"; fi
done
echo "byte-identical: $((n - bad))/$n"
( cd "$GEN" && sha256sum tiles/als_h*.bin tiles/alq_h3.bin tiles/alq_h6.bin )
echo "== dry run of the registered list =="
HL_GEN=$GEN HL_EXPN=e113 V3_DRY=1 bash tools/claims-v3/hl/block.sh 1199 "$E113_ITEMS" 2>&1 | tail -4
