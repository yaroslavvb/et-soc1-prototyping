#!/bin/bash
# decl-e219 (Q232) step 0c, run right before the declaration: is MM1-v3.2 on GitHub main? (tools/matmul/mm1/v3.2 at LAB HEAD = GitHub
# main, and W/out/q230-anchor-lines-v32.txt, the land's anchor record). If yes: the declared models and the base models must be unchanged
# between the work copy's commit and that commit (git diff of v3.1, v3, v2, v3.2-terms: empty), then tools/matmul/mm1/v3.2 alone is
# archived from that commit into work/lab/ beside the work copy's v3.1 (its predictor imports ../v3.1) and its SHA256SUMS checked.
# Writes work/v32-status.json (included or not, and why). Reads LAB only (git ls-remote, rev-parse, ls-tree, diff, archive under the
# lab-git lock). Never edits LAB.
set -u
. <W>/out/decl-e219/scripts/env.sh
OUTJ=$L/work/v32-status.json
BASE=$(cat "$L/work/lab-commit.txt")
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
ANCH=$W/out/q230-anchor-lines-v32.txt
echo "check $(ts): GitHub main $REMOTE ; LAB HEAD $HEAD ; work copy $BASE"
HAS=$(git -C "$LAB" ls-tree --name-only "$HEAD" tools/matmul/mm1/ | grep -c '^tools/matmul/mm1/v3.2$')
echo "tools/matmul/mm1/v3.2 at LAB HEAD: $HAS ; anchor record: $( [ -e "$ANCH" ] && echo present || echo absent )"
status=NOT_ON_MAIN
why="tools/matmul/mm1/v3.2 is not in GitHub main's tree at $(ts) (LAB HEAD ${HEAD:0:8}); W/out/q230-anchor-lines-v32.txt $( [ -e "$ANCH" ] && echo present || echo absent )"
if [ "$REMOTE" != "$HEAD" ]; then
  why="$why; LAB HEAD differs from GitHub main ($REMOTE): only LAB HEAD can be read"
fi
if [ "$HAS" = 1 ] && [ "$REMOTE" = "$HEAD" ]; then
  D=$(git -C "$LAB" diff --stat "$BASE" "$HEAD" -- tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 tools/matmul/mm1/v2 tools/matmul/mm1/v3.2-terms | tail -1)
  if [ -n "$D" ]; then
    status=REFUSED
    why="v3.2 on main ${HEAD:0:8} but the base models changed since the work copy ${BASE:0:8}: $D"
  elif [ -d "$L/work/lab/tools/matmul/mm1/v3.2" ]; then
    status=ALREADY
    why="work/lab/tools/matmul/mm1/v3.2 exists already (not overwritten)"
  else
    flock -w 600 "$W/locks/lab-git.lock" nice -n 10 ionice -c 3 git -C "$LAB" archive --format=tar "$HEAD" tools/matmul/mm1/v3.2 | tar -x -C "$L/work/lab"
    ( cd "$L/work/lab/tools/matmul/mm1/v3.2" && sha256sum -c SHA256SUMS > "$L/logs/v32-sha256sum-c.txt" 2>&1 ); rc=$?
    nok=$(grep -c ': OK$' "$L/logs/v32-sha256sum-c.txt")
    LC=$(git -C "$LAB" log -1 --format='%h %ci' "$HEAD" -- tools/matmul/mm1/v3.2)
    if [ "$rc" = 0 ]; then status=INCLUDED; else status=SUMS_FAIL; fi
    why="tools/matmul/mm1/v3.2 archived from GitHub main ${HEAD:0:8} (last change $LC), SHA256SUMS rc $rc, $nok OK; base models unchanged since ${BASE:0:8}; anchor record $( [ -e "$ANCH" ] && echo present || echo absent )"
    echo "$HEAD" > "$L/work/lab-commit-v32.txt"
  fi
fi
printf '{"status": "%s", "why": "%s", "checked_pst": "%s", "github_main": "%s", "lab_head": "%s", "work_copy": "%s"}\n' "$status" "$why" "$(ts)" "$REMOTE" "$HEAD" "$BASE" > "$OUTJ"
cat "$OUTJ"
plog "step 00c MM1-v3.2 check: $status ($why)"
