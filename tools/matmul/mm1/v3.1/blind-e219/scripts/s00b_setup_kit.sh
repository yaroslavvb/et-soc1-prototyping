#!/bin/bash
# decl-e219 (Q232) step 0b: the orchestrator's copy of the kit's src (out/orch/e219-src, made by one read-only rsync FROM aifoundry1 in a
# gap between E217's sessions; COPIED.txt) into work/e219-src/, checked by its SRC-SHA256SUMS.txt (and the kit's own src/SRC-SHA256SUMS
# when present, from the kit root). Reads only; no ssh; no E219 datum (the kit's src holds no session data: checked by listing).
set -u
. <W>/out/decl-e219/scripts/env.sh
echo "start $(ts)"
O=$W/out/orch/e219-src
[ -e "$O/COPIED.txt" ] || { echo "no COPIED.txt: stop"; exit 3; }
cat "$O/COPIED.txt"
if [ -d "$L/work/e219-src" ]; then echo "work/e219-src exists already: stop (no overwrite)"; exit 4; fi
mkdir -p "$L/work/e219-src"
cp -a "$O/." "$L/work/e219-src/"
cd "$L/work/e219-src" || exit 2
echo "SRC-SHA256SUMS.txt $(sha256sum SRC-SHA256SUMS.txt)"
sha256sum -c SRC-SHA256SUMS.txt > "$L/logs/e219src-sha256sum-c.txt" 2>&1
echo "e219-src: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/e219src-sha256sum-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/e219src-sha256sum-c.txt")"
echo "files in the copy: $(find src -type f | wc -l); listed: $(wc -l < SRC-SHA256SUMS.txt)"
if [ -f src/SRC-SHA256SUMS ]; then
  sha256sum -c src/SRC-SHA256SUMS > "$L/logs/e219src-own-sha256sum-c.txt" 2>&1
  echo "the kit's own src/SRC-SHA256SUMS from the kit root: rc $? ; OK $(grep -c ': OK$' "$L/logs/e219src-own-sha256sum-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/e219src-own-sha256sum-c.txt")"
  ( cd src && sha256sum -c SRC-SHA256SUMS > "$L/logs/e219src-own-in-src-sha256sum-c.txt" 2>&1; echo "the kit's own src/SRC-SHA256SUMS from inside src: rc $? ; OK $(grep -c ': OK$' "$L/logs/e219src-own-in-src-sha256sum-c.txt")" )
fi
echo "--- any session/data-like path in the copy (should be none):"
find src -iname '*session*' -o -iname '*.jsonl*' -o -iname 'manifest*' -o -iname '*result*' | head -20
echo "--- tree"
find src -maxdepth 2 | sort | head -80
echo "end $(ts)"
