#!/bin/bash
# blind-e217 (Q228) step 0: the work copies and EVERY FROZEN FILE'S sha256, before anything else. Desk; no device; no ssh; no E217
# measurement read (this step reads no E217 data file at all).
# - MM1-v3.1 (tools/matmul/mm1/v3.1, landed 2c971828; counts 3e8991d0), MM1-v3 (tools/matmul/mm1/v3, b1493082), MM1-v2 (tools/matmul/mm1/v2,
#   3ca4b717), the two frozen terms as landed (tools/matmul/mm1/v3.2-terms: layout 595fcb59, gemmlnc aaeaa495), E215's band code and the
#   kinds folder, by git archive of GitHub main's commit (LAB HEAD = GitHub main, checked first) into work/lab/ (LAB itself is only read);
# - verify-lay's maker and fits record (#1.29.1.1; the controls' constants) from OUT/verify-lay into work/verify-lay/;
# - decl-e217's frozen files: FROZEN.txt and COUNTS-FROZEN.txt against the posted sha256 (W/out/orch/q228-frozen-posts.txt), every file they
#   name, decl-e217's land dir (SHA256SUMS 996dd5eb..., 81 files) checked and copied to work/decl/ (the declaration, the nominal forecasts,
#   the counts and the step 1/2/4 inputs), and the declaration's own input table re-checked on the copies.
set -u
. <W>/out/blind-e217/scripts/env.sh
echo "start $(ts)"
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "GitHub main $REMOTE ; LAB HEAD $HEAD"
if [ "$REMOTE" != "$HEAD" ]; then echo "LAB HEAD differs from GitHub main: stop"; exit 3; fi
echo "$HEAD" > "$L/work/lab-commit.txt"
mkdir -p "$L/work/lab"
if [ -d "$L/work/lab/tools" ]; then echo "work/lab/tools exists already: stop (no overwrite)"; exit 4; fi
git -C "$LAB" archive --format=tar "$HEAD" tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 tools/matmul/mm1/v2 tools/matmul/mm1/v3.2-terms \
  tools/claims-v3/e215/rules_e215.py tools/claims-v3/e215/rules-e215.json tools/claims-v3/kinds | tar -x -C "$L/work/lab"
echo "archive rc ${PIPESTATUS[0]} $(ts)"
for d in tools/matmul/mm1/v3.1/mm1_v31.py tools/matmul/mm1/v3.1/out/mm1_v31_params.json tools/matmul/mm1/v3/mm1_v3.py tools/matmul/mm1/v2/mm1_v2.py \
         tools/matmul/mm1/v3.2-terms/layout/eval_layout.py tools/matmul/mm1/v3.2-terms/gemmlnc/term-gemmlnc.json tools/matmul/mm1/v3.1/counts/SHA256SUMS; do
  git -C "$LAB" log -1 --format="last change %h %ci $d" "$HEAD" -- "$d"
done
chk() {  # $1 label, $2 dir, $3 sums file, $4 log name
  ( cd "$2" && echo "$1: $(sha256sum "$3")" && sha256sum -c "$3" > "$L/logs/$4" 2>&1; echo "$1: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/$4") ; not OK $(grep -vc ': OK$' "$L/logs/$4")" )
}
M=$L/work/lab/tools/matmul/mm1
chk "MM1-v3.1" "$M/v3.1" SHA256SUMS v31-sha256sum-c.txt
chk "MM1-v3.1 counts (3e8991d0)" "$M/v3.1/counts" SHA256SUMS v31counts-sha256sum-c.txt
chk "MM1-v3" "$M/v3" SHA256SUMS v3-sha256sum-c.txt
chk "MM1-v2" "$M/v2" SHA256SUMS v2-sha256sum-c.txt
chk "layout term (595fcb59) SHA256SUMS" "$M/v3.2-terms/layout" SHA256SUMS layout-sha256sum-c.txt
chk "layout term dated note SHA256SUMS-note1" "$M/v3.2-terms/layout" SHA256SUMS-note1 layout-note1-sha256sum-c.txt
chk "gemmLnc term (aaeaa495) SHA256SUMS" "$M/v3.2-terms/gemmlnc" SHA256SUMS gemmlnc-sha256sum-c.txt
echo "--- the frozen terms' posted files (#1.29, #1.29.1) and the declaration's pins, on the work copies:"
( cd "$M" && sha256sum v3.2-terms/layout/forecast-e215-v31-layout.csv v3.2-terms/layout/forecast-e215-v31-layout.json v3.2-terms/layout/freeze_layout.py \
    v3.2-terms/layout/eval_layout.py v3.2-terms/layout/features_layout.py v3.2-terms/layout/out/features_layout.json v3.2-terms/gemmlnc/term-gemmlnc.json \
    v3.1/out/mm1_v31_params.json v3/out/mm1_v3_params.json v2/out/mm1_v2_params.json v3.1/SHA256SUMS v3.1/counts/SHA256SUMS v3/SHA256SUMS v2/SHA256SUMS \
    v3.1/counts-e214/SHA256SUMS )
sha256sum "$L/work/lab/tools/claims-v3/e215/rules_e215.py"
echo "--- verify-lay's maker (#1.29.1.1) and its fits record, copied"
mkdir -p "$L/work/verify-lay"
cp -a "$W/out/verify-lay/scripts/v02_fits.py" "$W/out/verify-lay/work/v02_fits.json" "$W/out/verify-lay/work/v02_e215_controls.csv" "$L/work/verify-lay/"
( cd "$L/work/verify-lay" && sha256sum v02_fits.py v02_fits.json v02_e215_controls.csv )
sha256sum "$W/out/orch/q225-controls/v02_e215_controls.csv"
echo "--- decl-e217's freeze: the posted record, FROZEN.txt, COUNTS-FROZEN.txt and the files they name"
cat "$W/out/orch/q228-frozen-posts.txt"
( cd "$D" && sha256sum FROZEN.txt COUNTS-FROZEN.txt DECLARED-blind-e217.md DECLARED-blind-e217.json forecasts-nominal-e217.csv forecasts-nominal-e217.json \
    cnt/counts/counts-fp32-gemm-states.json cnt/counts/counts-fp16-int8-launch.json forecasts-nominal-e217-counts.csv forecasts-nominal-e217-counts.json \
    cnt/counts/counts-e217.csv cnt/counts/counts-e217-tiles.csv scripts/s04c_nominal_counts.py scripts/s02b_nominal.py scripts/s02w_walk.py scripts/s02c_write.py \
    work/step2/fc-nominal.json work/step2/walk-feats-e217.json logs/step1-sha256.txt logs/step2-sha256.txt )
DL=$D/land/tools/matmul/mm1/v3.1/blind-e217
chk "decl-e217 land dir" "$DL" SHA256SUMS decl-land-sha256sum-c.txt
echo "--- decl-e217's land copied to work/decl/ and re-checked there"
mkdir -p "$L/work/decl"
cp -a "$DL/." "$L/work/decl/"
chk "decl-e217 land, work copy" "$L/work/decl" SHA256SUMS decl-copy-sha256sum-c.txt
( cd "$L/work/decl" && sha256sum FROZEN.txt COUNTS-FROZEN.txt DECLARED-blind-e217.md DECLARED-blind-e217.json forecasts-nominal-e217.csv forecasts-nominal-e217.json \
    counts-e217/counts-fp32-gemm-states.json counts-e217/counts-fp16-int8-launch.json counts-e217/counts-e217.csv counts-e217/counts-e217-tiles.csv \
    forecasts-nominal-e217-counts.csv forecasts-nominal-e217-counts.json inputs/step1/runs-listed.json inputs/step1/models-step1.json \
    inputs/step1/twin-keys.json inputs/step1/bands.json inputs/step2/fc-nominal.json inputs/step2/walk-feats-e217.json inputs/step4/fc-counts-v31.json \
    inputs/step4/fc-counts-v3.json scripts/s02b_nominal.py scripts/s04c_nominal_counts.py scripts/s02w_walk.py )
echo "--- the E217 kit copy's list (not used for any forecast input here; recorded)"
sha256sum "$W/out/orch/e217-src/SRC-SHA256SUMS.txt"
echo "end $(ts)"
