#!/bin/bash
# unread-e214 (Q225, track A) step 0: the work copies. Desk; no device; no E214 measurement read; no E215 datum anywhere.
# - MM1-v3.1 (tools/matmul/mm1/v3.1, landed 2c971828, with its counts 3e8991d0), MM1-v3 (tools/matmul/mm1/v3, b1493082), MM1-v2
#   (tools/matmul/mm1/v2, 3ca4b717), E214's registration (tools/claims-v3/e214: arms, schedules, tiles) and E215's band code
#   (tools/claims-v3/e215: rules_e215.py and rules-e215.json only are used) by git archive of GitHub main's commit (LAB HEAD = GitHub main,
#   checked first) into work/lab/ (LAB itself is only read);
# - counts-e214's land dir (verified by verify-counts-e214: HOLDS) copied into work/counts-e214/; every copy checked by sha256sum -c.
set -u
. <W>/out/unread-e214/scripts/env.sh
CNT=$W/out/counts-e214/land/tools/matmul/mm1/v3.1/counts-e214
echo "start $(ts)"
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "GitHub main $REMOTE ; LAB HEAD $HEAD"
if [ "$REMOTE" != "$HEAD" ]; then echo "LAB HEAD differs from GitHub main: stop"; exit 3; fi
echo "$HEAD" > "$L/work/lab-commit.txt"
mkdir -p "$L/work/lab"
if [ -d "$L/work/lab/tools" ]; then echo "work/lab/tools exists already: stop (no overwrite)"; exit 4; fi
git -C "$LAB" archive --format=tar "$HEAD" tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 tools/matmul/mm1/v2 tools/claims-v3/e214 \
  tools/claims-v3/e215/rules_e215.py tools/claims-v3/e215/rules-e215.json | tar -x -C "$L/work/lab"
echo "archive rc ${PIPESTATUS[0]} $(ts)"
for d in tools/matmul/mm1/v3.1 tools/matmul/mm1/v3 tools/matmul/mm1/v2 tools/claims-v3/e214 tools/claims-v3/e215/rules_e215.py; do
  git -C "$LAB" log -1 --format="last change %H %ci $d" "$HEAD" -- "$d"
done
chk() {  # $1 label, $2 dir, $3 sums file, $4 log name
  ( cd "$2" && echo "$1: $(sha256sum "$3")" && sha256sum -c "$3" > "$L/logs/$4" 2>&1; echo "$1: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/$4") ; not OK $(grep -vc ': OK$' "$L/logs/$4")" )
}
chk "MM1-v3.1" "$L/work/lab/tools/matmul/mm1/v3.1" SHA256SUMS v31-sha256sum-c.txt
chk "MM1-v3.1 counts (3e8991d0)" "$L/work/lab/tools/matmul/mm1/v3.1/counts" SHA256SUMS v31counts-sha256sum-c.txt
chk "MM1-v3" "$L/work/lab/tools/matmul/mm1/v3" SHA256SUMS v3-sha256sum-c.txt
chk "MM1-v2" "$L/work/lab/tools/matmul/mm1/v2" SHA256SUMS v2-sha256sum-c.txt
chk "E214 registration" "$L/work/lab" tools/claims-v3/e214/SHA256SUMS-e214-registration e214reg-sha256sum-c.txt
echo "--- counts-e214 (land dir), copied"
mkdir -p "$L/work/counts-e214"
cp -a "$CNT/." "$L/work/counts-e214/"
chk "counts-e214 land dir" "$CNT" SHA256SUMS counts-e214-land-sha256sum-c.txt
chk "counts-e214 work copy" "$L/work/counts-e214" SHA256SUMS counts-e214-work-sha256sum-c.txt
echo "end $(ts)"
