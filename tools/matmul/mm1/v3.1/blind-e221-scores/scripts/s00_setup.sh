#!/bin/bash
# blind-e221 (Q235) step 0a: the work copies, before anything else. Desk; no device; no ssh; no E221 measurement read (this step opens no
# E221 data file). blind-e219's s00_setup.sh in form.
# - the frozen models and terms as landed (MM1-v3.2, v3.1, v3, v2, v0, v1, v3.2-terms) and what they read (tools/claims-v3/e214, e215's band
#   code, kinds, e136, e217, e219, e213's points), the same paths decl-e221 archived at 0f046200 (s00a_setup_lab.sh, s00d_more_lab.sh), plus
#   the MM1-v3.3 candidates as landed (tools/matmul/mm1/v3.3-cands) and E221's registration (tools/claims-v3/e221), by git archive of GitHub
#   main's commit (LAB HEAD = GitHub main, checked first; the archive under the lab-git lock) into work/lab/ (LAB itself is only read);
# - decl-e221's land dir copied to work/decl/ (the declaration, FROZEN.txt, the nominal forecasts, the step 1/2 inputs);
# - decl-e221's own copies of verify-lay's maker and fits record (work/verify-lay) and of the three candidates' frozen makers (work/cands),
#   copied to work/verify-lay/ and work/cands/ (the files decl-e221's s02b_nominal.py ran on).
# Every sha256 is then checked by s00b_check.py.
set -u
. <WF>/out/blind-e221/scripts/env.sh
echo "start $(ts)"
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "GitHub main $REMOTE ; LAB HEAD $HEAD"
if [ "$REMOTE" != "$HEAD" ]; then echo "LAB HEAD differs from GitHub main: stop"; exit 3; fi
echo "LAB status lines: $(git -C "$LAB" status --porcelain | wc -l)"
echo "$HEAD" > "$L/work/lab-commit.txt"
mkdir -p "$L/work/lab"
if [ -d "$L/work/lab/tools" ]; then echo "work/lab/tools exists already: stop (no overwrite)"; exit 4; fi
flock -w 600 "$W/locks/lab-git.lock" nice -n 10 ionice -c 3 git -C "$LAB" archive --format=tar "$HEAD" \
  tools/matmul/mm1/v0 tools/matmul/mm1/v1 tools/matmul/mm1/v2 tools/matmul/mm1/v3 tools/matmul/mm1/v3.1 tools/matmul/mm1/v3.2 \
  tools/matmul/mm1/v3.2-terms tools/matmul/mm1/v3.3-cands tools/claims-v3/e215/rules_e215.py tools/claims-v3/e215/rules-e215.json \
  tools/claims-v3/kinds tools/claims-v3/e136 tools/claims-v3/e217 tools/claims-v3/e219 tools/claims-v3/e214 \
  tools/claims-v3/e213/points-e213.csv tools/claims-v3/e221 workloads/nocbench/analyze.py \
  | tar -x -C "$L/work/lab"
echo "archive rc ${PIPESTATUS[0]} $(ts): $(find "$L/work/lab" -type f | wc -l) files"
BASE=$(cat "$D/work/lab-commit.txt")
echo "decl-e221's archive commit $BASE"
echo "--- what changed on main since decl-e221's commit in the paths it archived (name-status):"
git -C "$LAB" diff --name-status "$BASE" "$HEAD" -- tools/matmul/mm1/v0 tools/matmul/mm1/v1 tools/matmul/mm1/v2 tools/matmul/mm1/v3 \
  tools/matmul/mm1/v3.1 tools/matmul/mm1/v3.2 tools/matmul/mm1/v3.2-terms tools/claims-v3/e215/rules_e215.py tools/claims-v3/e215/rules-e215.json \
  tools/claims-v3/kinds tools/claims-v3/e136 tools/claims-v3/e217 tools/claims-v3/e219 tools/claims-v3/e214 tools/claims-v3/e213/points-e213.csv \
  | sed -n '1,40p'
echo "(end of the list)"
echo "--- decl-e221's land copied to work/decl/"
DL=$D/land/tools/matmul/mm1/v3.1/blind-e221
mkdir -p "$L/work/decl"
cp -a "$DL/." "$L/work/decl/"
echo "work/decl files: $(find "$L/work/decl" -type f | wc -l)"
echo "--- decl-e221's verify-lay and candidates' copies (the files its s02b_nominal.py ran on) copied to work/"
mkdir -p "$L/work/verify-lay" "$L/work/cands"
cp -a "$D/work/verify-lay/." "$L/work/verify-lay/"
cp -a "$D/work/cands/." "$L/work/cands/"
echo "work/verify-lay files: $(find "$L/work/verify-lay" -type f | wc -l); work/cands files: $(find "$L/work/cands" -type f | wc -l)"
echo "--- layout2's stand-in lane folder (its own lane clone, out/layout2/work/lab, was removed by the 16:07 cleanup): the LANDED f02_private.py"
echo "    (tools/matmul/mm1/v3.3-cands/posimb/scripts, the as-run file but for its LANE line, SCRUB.json) and this lane's archive as work/lab"
mkdir -p "$L/work/layout2-lane/scripts" "$L/work/layout2-lane/work"
cp -a "$L/work/lab/tools/matmul/mm1/v3.3-cands/posimb/scripts/f02_private.py" "$L/work/layout2-lane/scripts/"
ln -s ../../lab "$L/work/layout2-lane/work/lab"
ls -la "$L/work/layout2-lane/work/"
sha256sum "$L/work/layout2-lane/scripts/f02_private.py"
echo "end $(ts)"
