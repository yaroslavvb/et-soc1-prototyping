#!/bin/bash
# decl-e221 (Q235) step 0a: the lab's work copy (decl-e219's s00a in form). Desk; no device; no ssh; no E221 datum anywhere (none is read).
# - every frozen MM1 (tools/matmul/mm1/v0, v1, v2, v3 b1493082, v3.1 2c971828 with its counts 3e8991d0 and counts-e214, v3.2 4e386f75),
#   the frozen candidate terms (tools/matmul/mm1/v3.2-terms: gemmlnc, layout, scores), E215's band code, the kinds, E136's rgm136 sources
#   and E219's and E217's registrations (THE FORM), by git archive of GitHub main's commit (LAB HEAD = GitHub main, checked first; the
#   archive is a read of LAB under the lab-git lock) into work/lab/ (LAB itself is only read);
# - verify-lay's maker (#1.29.1.1: v02_fits.py and its fits record) from its lane folder into work/verify-lay/;
# - the three MM1-v3.3 candidates' frozen makers (Q234: OUT/layout2 posimb, OUT/lnc-form AF4, OUT/l3-edge L3S) by copy into work/cands/
#   (read only; their FROZEN.txt lines checked against W/out/orch/q234-frozen-posts.txt where posted).
set -u
. <W>/out/decl-e221/scripts/env.sh
echo "start $(ts)"
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "GitHub main $REMOTE ; LAB HEAD $HEAD"
if [ "$REMOTE" != "$HEAD" ]; then echo "LAB HEAD differs from GitHub main: stop"; exit 3; fi
echo "$HEAD" > "$L/work/lab-commit.txt"
mkdir -p "$L/work/lab"
if [ -d "$L/work/lab/tools" ]; then echo "work/lab/tools exists already: stop (no overwrite)"; exit 4; fi
flock -w 600 "$W/locks/lab-git.lock" nice -n 10 ionice -c 3 git -C "$LAB" archive --format=tar "$HEAD" \
  tools/matmul/mm1/v0 tools/matmul/mm1/v1 tools/matmul/mm1/v2 tools/matmul/mm1/v3 tools/matmul/mm1/v3.1 tools/matmul/mm1/v3.2 \
  tools/matmul/mm1/v3.2-terms tools/claims-v3/e215/rules_e215.py tools/claims-v3/e215/rules-e215.json tools/claims-v3/kinds \
  tools/claims-v3/e136 tools/claims-v3/e217 tools/claims-v3/e219 \
  | tar -x -C "$L/work/lab"
echo "archive rc ${PIPESTATUS[0]} $(ts)"
for d in tools/matmul/mm1/v0 tools/matmul/mm1/v1 tools/matmul/mm1/v2 tools/matmul/mm1/v3 tools/matmul/mm1/v3.1 tools/matmul/mm1/v3.2 \
         tools/matmul/mm1/v3.2-terms/gemmlnc tools/matmul/mm1/v3.2-terms/layout tools/claims-v3/e215/rules_e215.py tools/claims-v3/e136 \
         tools/claims-v3/e217 tools/claims-v3/e219; do
  git -C "$LAB" log -1 --format="last change %h %ci $d" "$HEAD" -- "$d"
done
chk() {  # $1 label, $2 dir, $3 sums file, $4 log name
  ( cd "$2" && echo "$1: $(sha256sum "$3")" && sha256sum -c "$3" > "$L/logs/$4" 2>&1; echo "$1: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/$4") ; not OK $(grep -vc ': OK$' "$L/logs/$4")" )
}
T=$L/work/lab/tools/matmul/mm1
[ -f "$T/v0/SHA256SUMS" ] && chk "MM1-v0" "$T/v0" SHA256SUMS v0-sha256sum-c.txt
[ -f "$T/v1/SHA256SUMS" ] && chk "MM1-v1" "$T/v1" SHA256SUMS v1-sha256sum-c.txt
chk "MM1-v2" "$T/v2" SHA256SUMS v2-sha256sum-c.txt
chk "MM1-v3" "$T/v3" SHA256SUMS v3-sha256sum-c.txt
chk "MM1-v3.1" "$T/v3.1" SHA256SUMS v31-sha256sum-c.txt
chk "MM1-v3.1 counts (3e8991d0)" "$T/v3.1/counts" SHA256SUMS v31counts-sha256sum-c.txt
chk "MM1-v3.1 counts-e214" "$T/v3.1/counts-e214" SHA256SUMS counts-e214-sha256sum-c.txt
chk "MM1-v3.2 (4e386f75)" "$T/v3.2" SHA256SUMS v32-sha256sum-c.txt
chk "layout term" "$T/v3.2-terms/layout" SHA256SUMS layout-sha256sum-c.txt
[ -f "$T/v3.2-terms/layout/SHA256SUMS-note1" ] && chk "layout term note 1" "$T/v3.2-terms/layout" SHA256SUMS-note1 layout-note1-sha256sum-c.txt
chk "gemmLnc term" "$T/v3.2-terms/gemmlnc" SHA256SUMS gemmlnc-sha256sum-c.txt
[ -f "$T/v3.2-terms/gemmlnc/SHA256SUMS-note1" ] && chk "gemmLnc term note 1" "$T/v3.2-terms/gemmlnc" SHA256SUMS-note1 gemmlnc-note1-sha256sum-c.txt
echo "posted #1.29.1 (layout F1) files:"
( cd "$T/v3.2-terms/layout" && sha256sum forecast-e215-v31-layout.csv forecast-e215-v31-layout.json freeze_layout.py eval_layout.py features_layout.py out/features_layout.json out/eval_layout.json 2>&1 )
echo "posted #1.29 (gemmLnc F3) files:"
( cd "$T/v3.2-terms/gemmlnc" && sha256sum term-gemmlnc.json forecasts-gemmlnc-e215.csv forecasts-gemmlnc-e215.json 2>&1 )
echo "--- verify-lay's maker (#1.29.1.1) and its fits record"
mkdir -p "$L/work/verify-lay"
cp -a "$W/out/verify-lay/scripts/v02_fits.py" "$W/out/verify-lay/work/v02_fits.json" "$W/out/verify-lay/work/v02_e215_controls.csv" "$L/work/verify-lay/"
( cd "$L/work/verify-lay" && sha256sum v02_fits.py v02_fits.json v02_e215_controls.csv )
echo "(decl-e219 recorded v02_fits.py 4fb92de3..., v02_fits.json 1bfec7fc..., v02_e215_controls.csv c5bc2394...)"
echo "--- the MM1-v3.3 candidates' frozen makers (Q234), copied read-only"
mkdir -p "$L/work/cands"
for c in layout2 lnc-form l3-edge; do
  if [ -e "$W/out/$c/FROZEN.txt" ]; then
    mkdir -p "$L/work/cands/$c"
    cp -a "$W/out/$c/FROZEN.txt" "$W/out/$c/scripts" "$W/out/$c/land" "$L/work/cands/$c/"
    echo "$c: FROZEN.txt $(sha256sum "$W/out/$c/FROZEN.txt" | cut -c1-64) ; files copied $(find "$L/work/cands/$c" -type f | wc -l)"
  else
    echo "$c: no FROZEN.txt at $(ts)"
  fi
done
cat "$W/out/orch/q234-frozen-posts.txt"
echo "end $(ts)"
