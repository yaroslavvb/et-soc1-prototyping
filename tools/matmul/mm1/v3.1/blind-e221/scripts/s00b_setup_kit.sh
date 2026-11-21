#!/bin/bash
# decl-e221 (Q235) step 0b: the orchestrator's copy of the kit's src (out/orch/e221-src, made by one read-only rsync FROM aifoundry1 at
# 05:54:33 PST Fri 20 Nov; COPIED.txt) into work/e221-src/, checked by its SRC-SHA256SUMS.txt (and the kit's own src/SRC-SHA256SUMS from
# the kit root). Reads only; no ssh; no E221 datum (the kit's src holds no session data: checked by listing).
set -u
. <W>/out/decl-e221/scripts/env.sh
echo "start $(ts)"
O=$W/out/orch/e221-src
[ -e "$O/COPIED.txt" ] || { echo "no COPIED.txt: stop"; exit 3; }
cat "$O/COPIED.txt"
if [ -d "$L/work/e221-src" ]; then echo "work/e221-src exists already: stop (no overwrite)"; exit 4; fi
mkdir -p "$L/work/e221-src"
cp -a "$O/." "$L/work/e221-src/"
cd "$L/work/e221-src" || exit 2
echo "SRC-SHA256SUMS.txt $(sha256sum SRC-SHA256SUMS.txt)"
sha256sum -c SRC-SHA256SUMS.txt > "$L/logs/e221src-sha256sum-c.txt" 2>&1
echo "e221-src: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/e221src-sha256sum-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/e221src-sha256sum-c.txt")"
echo "files in the copy: $(find src -type f | wc -l); listed: $(wc -l < SRC-SHA256SUMS.txt)"
if [ -f src/SRC-SHA256SUMS ]; then
  sha256sum -c src/SRC-SHA256SUMS > "$L/logs/e221src-own-sha256sum-c.txt" 2>&1
  echo "the kit's own src/SRC-SHA256SUMS from the kit root: rc $? ; OK $(grep -c ': OK$' "$L/logs/e221src-own-sha256sum-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/e221src-own-sha256sum-c.txt")"
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
