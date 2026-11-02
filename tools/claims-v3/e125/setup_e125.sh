#!/usr/bin/env bash
# E125 (Q134): files-only setup on aifoundry1 (run from ~/nekko, the rsynced tree), before the claim:
#   bash tools/claims-v3/e125/setup_e125.sh
# Writes build/hl-gen6-e113 with E113's own make_e113.py --check (make_hl.py's set plus E113's nine tiles), checks that every file
# E113's pass 1131 ran (its gen.sha256, copied here as e113-p1131-gen.sha256) is byte-identical in it, prints card 1's holders and
# the host's load, and runs the registered item list as a V3_DRY=1 dry run on card 1 (every device call printed, none made).
# Opens no device; sets nothing.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
GEN=$ROOT/build/hl-gen6-e113
# aifoundry1 keeps numpy unpacked in pylib/ (lib.sh); use the first interpreter that imports it
[ -d "$ROOT/pylib/numpy" ] && export PYTHONPATH="$ROOT/pylib${PYTHONPATH:+:$PYTHONPATH}"
for c in "${PY:-}" "$ROOT/.venv/bin/python3" python3; do [ -n "$c" ] && "$c" -c "import numpy" 2> /dev/null && { PY=$c; break; }; done
echo "python: ${PY:-none}"
. tools/claims-v3/e125/items_e125.sh
echo "== $(date '+%F %T %Z') host and card (read only) =="
timeout 20 et-who 2>&1 | head -5; echo "logins: $(who | wc -l) (names not recorded)"; uptime; cat /proc/loadavg
ls -la build/enercat-hl/host/enercat_host build/sparsity/host/sparsity_host build/ettelem/ettelem 2>&1 | awk '{print $5, $6, $7, $8, $9}'
sha256sum build/sparsity/host/sparsity_host build/ettelem/ettelem build/enercat-hl/host/enercat_host
echo "== operand set $GEN =="
rm -rf "${GEN:?}"
"$PY" tools/claims-v3/e113/make_e113.py "$GEN" --check | tail -2
echo "== byte-identity against E113's pass 1131 (gen.sha256: manifest.json, tiles/*, srcs/*) =="
( cd "$GEN" && sha256sum manifest.json tiles/* srcs/* ) > build/e125-gen.sha256
n=$(wc -l < tools/claims-v3/e125/e113-p1131-gen.sha256)
same=$(sort -k2 build/e125-gen.sha256 | diff - <(sort -k2 tools/claims-v3/e125/e113-p1131-gen.sha256) > /dev/null && echo yes || echo no)
echo "files in E113's list: $n; in this set: $(wc -l < build/e125-gen.sha256); identical lists: $same"
[ "$same" = yes ] || sort -k2 build/e125-gen.sha256 | diff - <(sort -k2 tools/claims-v3/e125/e113-p1131-gen.sha256) | head -5
echo "== dry run of the registered list on card 1 =="
V3_DEVICE=1 HL_GEN=$GEN HL_EXPN=e125 V3_DRY=1 timeout 120 bash tools/claims-v3/hl/block.sh 12599 "$E125_ITEMS" 2>&1 | tail -4
