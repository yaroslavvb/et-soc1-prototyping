#!/bin/bash
# decl-e217 (Q228) step 0: the work copies. Desk; no device; no ssh; no E217 datum anywhere (none exists in any place this reads).
# - MM1-v3.1 (tools/matmul/mm1/v3.1, landed 2c971828, with its counts 3e8991d0 and walk 5a75e212), MM1-v3 (tools/matmul/mm1/v3, b1493082),
#   MM1-v2 (tools/matmul/mm1/v2, 3ca4b717), E215's band code (tools/claims-v3/e215/rules_e215.py, rules-e215.json) and E214's registration
#   (tools/claims-v3/e214: its tiles, for the prior-tile comparison) by git archive of GitHub main's commit (LAB HEAD = GitHub main, checked
#   first) into work/lab/ (LAB itself is only read);
# - the frozen candidate terms, from their lanes' land dirs (not on main yet): the contention term F1 (#1.29.1, OUT/lay-contention/land) into
#   work/lab/tools/matmul/mm1/v3.2-terms/layout/ (its own relative paths resolve the work copy's MM1-v3.1), the gemmLnc term F3 (#1.29,
#   OUT/lnc-energy/land) into work/lab/tools/matmul/mm1/v3.2-terms/gemmlnc/ (recorded; E217 runs no gemmLnc arm); verify-lay's script and
#   its fits record (#1.29.1.1's maker) into work/verify-lay/; every frozen file checked against its posted sha256;
# - the orchestrator's copy of the kit's src (out/orch/e217-src) into work/e217-src/, checked by its SRC-SHA256SUMS.txt (854bd075...);
# - counts-e214's land dir into work/counts-e214/ (checked; E217 reuses none of its tiles: recorded).
set -u
. <W>/out/decl-e217/scripts/env.sh
echo "start $(ts)"
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "GitHub main $REMOTE ; LAB HEAD $HEAD"
if [ "$REMOTE" != "$HEAD" ]; then echo "LAB HEAD differs from GitHub main: stop"; exit 3; fi
echo "$HEAD" > "$L/work/lab-commit.txt"
mkdir -p "$L/work/lab"
if [ -d "$L/work/lab/tools" ]; then echo "work/lab/tools exists already: stop (no overwrite)"; exit 4; fi
git -C "$LAB" archive --format=tar "$HEAD" tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 tools/matmul/mm1/v2 tools/claims-v3/e214 \
  tools/claims-v3/e215/rules_e215.py tools/claims-v3/e215/rules-e215.json tools/claims-v3/kinds | tar -x -C "$L/work/lab"
echo "archive rc ${PIPESTATUS[0]} $(ts)"
for d in tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 tools/matmul/mm1/v2 tools/claims-v3/e215/rules_e215.py; do
  git -C "$LAB" log -1 --format="last change %H %ci $d" "$HEAD" -- "$d"
done
chk() {  # $1 label, $2 dir, $3 sums file, $4 log name
  ( cd "$2" && echo "$1: $(sha256sum "$3")" && sha256sum -c "$3" > "$L/logs/$4" 2>&1; echo "$1: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/$4") ; not OK $(grep -vc ': OK$' "$L/logs/$4")" )
}
chk "MM1-v3.1" "$L/work/lab/tools/matmul/mm1/v3.1" SHA256SUMS v31-sha256sum-c.txt
chk "MM1-v3.1 counts (3e8991d0)" "$L/work/lab/tools/matmul/mm1/v3.1/counts" SHA256SUMS v31counts-sha256sum-c.txt
chk "MM1-v3" "$L/work/lab/tools/matmul/mm1/v3" SHA256SUMS v3-sha256sum-c.txt
chk "MM1-v2" "$L/work/lab/tools/matmul/mm1/v2" SHA256SUMS v2-sha256sum-c.txt
echo "--- the frozen terms (land dirs of Q225's lanes), copied"
LAY=$W/out/lay-contention/land/tools/matmul/mm1/v3.2-terms/layout
LNC=$W/out/lnc-energy/land/tools/matmul/mm1/v3.2-terms/gemmlnc
mkdir -p "$L/work/lab/tools/matmul/mm1/v3.2-terms"
cp -a "$LAY" "$L/work/lab/tools/matmul/mm1/v3.2-terms/layout"
cp -a "$LNC" "$L/work/lab/tools/matmul/mm1/v3.2-terms/gemmlnc"
chk "layout term land (now 25 files)" "$L/work/lab/tools/matmul/mm1/v3.2-terms/layout" SHA256SUMS layout-sha256sum-c.txt
chk "gemmLnc term land" "$L/work/lab/tools/matmul/mm1/v3.2-terms/gemmlnc" SHA256SUMS gemmlnc-sha256sum-c.txt
echo "posted #1.29.1 (FROZEN.txt) against the copies:"
( cd "$L/work/lab/tools/matmul/mm1/v3.2-terms/layout" && sha256sum forecast-e215-v31-layout.csv forecast-e215-v31-layout.json freeze_layout.py eval_layout.py features_layout.py out/features_layout.json out/eval_layout.json DECLARED-layout.md DECLARED-layout-addendum-1.md )
echo "posted #1.29: term-gemmlnc.json forecasts-gemmlnc-e215.csv/json:"
( cd "$L/work/lab/tools/matmul/mm1/v3.2-terms/gemmlnc" && ls && sha256sum term-gemmlnc.json forecasts-gemmlnc-e215.csv forecasts-gemmlnc-e215.json 2>&1 )
echo "--- verify-lay's maker (#1.29.1.1) and its fits record"
mkdir -p "$L/work/verify-lay"
cp -a "$W/out/verify-lay/scripts/v02_fits.py" "$W/out/verify-lay/work/v02_fits.json" "$W/out/verify-lay/work/v02_e215_controls.csv" "$L/work/verify-lay/"
( cd "$L/work/verify-lay" && sha256sum v02_fits.py v02_fits.json v02_e215_controls.csv )
sha256sum "$W/out/orch/q225-controls/v02_e215_controls.csv"
echo "--- the kit's src (the orchestrator's copy)"
mkdir -p "$L/work/e217-src"
cp -a "$W/out/orch/e217-src/." "$L/work/e217-src/"
( cd "$L/work/e217-src" && echo "SRC-SHA256SUMS.txt $(sha256sum SRC-SHA256SUMS.txt)" && sha256sum -c SRC-SHA256SUMS.txt > "$L/logs/e217src-sha256sum-c.txt" 2>&1; echo "e217-src: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/e217src-sha256sum-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/e217src-sha256sum-c.txt")" )
( cd "$L/work/e217-src/src" && sha256sum -c SRC-SHA256SUMS > "$L/logs/e217src-own-sha256sum-c.txt" 2>&1; echo "e217-src src/SRC-SHA256SUMS (the kit's own): rc $? ; OK $(grep -c ': OK$' "$L/logs/e217src-own-sha256sum-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/e217src-own-sha256sum-c.txt")" )
echo "--- counts-e214 (land dir), copied"
CNT=$W/out/counts-e214/land/tools/matmul/mm1/v3.1/counts-e214
mkdir -p "$L/work/counts-e214"
cp -a "$CNT/." "$L/work/counts-e214/"
chk "counts-e214 work copy" "$L/work/counts-e214" SHA256SUMS counts-e214-work-sha256sum-c.txt
echo "end $(ts)"
