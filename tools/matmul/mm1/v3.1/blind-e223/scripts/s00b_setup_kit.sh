#!/bin/bash
# decl-e223 (Q239) step 0b: the orchestrator's copy of the kit's src (out/orch/e223-src, made by one read-only local rsync FROM aifoundry2's
# own ~/claude/work/ee-1121-mmsweep7/src/ at 01:57:27 PST Sat 21 Nov; COPIED.txt) into work/e223-src/, checked by its SRC-SHA256SUMS.txt (and
# the kit's own src/SRC-SHA256SUMS from the kit root). Reads only; no ssh; no E223 datum (the kit's src holds no session data: checked).
set -u
. <W>/out/decl-e223/scripts/env.sh
echo "start $(ts)"
O=$W/out/orch/e223-src
[ -e "$O/COPIED.txt" ] || { echo "no COPIED.txt: stop"; exit 3; }
cat "$O/COPIED.txt"
if [ -d "$L/work/e223-src" ]; then echo "work/e223-src exists already: stop (no overwrite)"; exit 4; fi
mkdir -p "$L/work/e223-src"
cp -a "$O/." "$L/work/e223-src/"
cd "$L/work/e223-src" || exit 2
echo "SRC-SHA256SUMS.txt $(sha256sum SRC-SHA256SUMS.txt)"
sha256sum -c SRC-SHA256SUMS.txt > "$L/logs/e223src-sha256sum-c.txt" 2>&1
echo "e223-src: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/e223src-sha256sum-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/e223src-sha256sum-c.txt")"
echo "files in the copy: $(find src -type f | wc -l); listed: $(wc -l < SRC-SHA256SUMS.txt)"
if [ -f src/SRC-SHA256SUMS ]; then
  sha256sum -c src/SRC-SHA256SUMS > "$L/logs/e223src-own-sha256sum-c.txt" 2>&1
  echo "the kit's own src/SRC-SHA256SUMS from the kit root: rc $? ; OK $(grep -c ': OK$' "$L/logs/e223src-own-sha256sum-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/e223src-own-sha256sum-c.txt")"
fi
echo "--- any session/data-like path in the copy (should be none):"
find src -iname '*session*' -o -iname '*.jsonl*' -o -iname 'manifest*' -o -iname '*result*' | head -20
echo "--- the tile files against the lab's kinds (byte for byte)"
for f in src/tiles/*/*.bin; do
  t=$(basename "$(dirname "$f")"); n=$(basename "$f")
  k="$L/work/lab/tools/claims-v3/kinds/tiles/$t/$n"
  if [ -f "$k" ] && cmp -s "$f" "$k"; then echo "$f = kinds/tiles/$t/$n"; else echo "$f DIFFERS or no kind file"; fi
done
echo "end $(ts)"
