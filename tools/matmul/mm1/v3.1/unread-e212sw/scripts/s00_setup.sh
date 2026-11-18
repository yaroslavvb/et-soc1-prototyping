#!/bin/bash
# unread-e212sw (Q218) step 0: the work copies. Desk; no device; no measurement column read.
# - MM1-v3 (tools/matmul/mm1/v3), MM1-v1 (tools/matmul/mm1/v1) and E212's registration (tools/claims-v3/e212: arms, schedules, tiles)
#   by git archive of GitHub main's commit (LAB HEAD = GitHub main, checked first) into work/lab/ (LAB itself is only read);
# - the frozen switch counts (fix-v31counts' land dir) copied into work/counts/, both checked by sha256sum -c.
set -u
W=<W>
L=$W/out/unread-e212sw
LAB=<LAB>
CNT=$W/out/fix-v31counts/land/tools/matmul/mm1/v3.1/counts
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
ts() { TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'; }
echo "start $(ts)"
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "GitHub main $REMOTE ; LAB HEAD $HEAD"
if [ "$REMOTE" != "$HEAD" ]; then echo "LAB HEAD differs from GitHub main: stop"; exit 3; fi
echo "$HEAD" > "$L/work/lab-commit.txt"
mkdir -p "$L/work/lab"
if [ -d "$L/work/lab/tools" ]; then echo "work/lab/tools exists already: stop (no overwrite)"; exit 4; fi
git -C "$LAB" archive --format=tar "$HEAD" tools/matmul/mm1/v3 tools/matmul/mm1/v1 tools/claims-v3/e212 | tar -x -C "$L/work/lab"
echo "archive rc ${PIPESTATUS[0]} $(ts)"
git -C "$LAB" log -1 --format='%H %ci' "$HEAD" -- tools/matmul/mm1/v3
echo "--- MM1-v3 SHA256SUMS check (work copy)"
( cd "$L/work/lab/tools/matmul/mm1/v3" && sha256sum SHA256SUMS && sha256sum -c SHA256SUMS > "$L/logs/v3-sha256sum-c.txt" 2>&1; echo "rc $?"; grep -vc ': OK$' "$L/logs/v3-sha256sum-c.txt"; grep -c ': OK$' "$L/logs/v3-sha256sum-c.txt" )
echo "--- MM1-v1 SHA256SUMS check (work copy)"
( cd "$L/work/lab/tools/matmul/mm1/v1" && sha256sum -c SHA256SUMS > "$L/logs/v1-sha256sum-c.txt" 2>&1; echo "rc $?"; grep -vc ': OK$' "$L/logs/v1-sha256sum-c.txt"; grep -c ': OK$' "$L/logs/v1-sha256sum-c.txt" )
echo "--- E212 registration SHA256SUMS check (work copy)"
( cd "$L/work/lab/tools/claims-v3/e212" && sha256sum -c SHA256SUMS-e212-registration > "$L/logs/e212reg-sha256sum-c.txt" 2>&1; echo "rc $?"; grep -vc ': OK$' "$L/logs/e212reg-sha256sum-c.txt"; grep -c ': OK$' "$L/logs/e212reg-sha256sum-c.txt" )
echo "--- the counts (fix-v31counts land dir), copied"
mkdir -p "$L/work/counts"
cp -a "$CNT/." "$L/work/counts/"
( cd "$L/work/counts" && sha256sum SHA256SUMS && sha256sum -c SHA256SUMS > "$L/logs/counts-sha256sum-c.txt" 2>&1; echo "rc $?"; grep -vc ': OK$' "$L/logs/counts-sha256sum-c.txt"; grep -c ': OK$' "$L/logs/counts-sha256sum-c.txt" )
echo "end $(ts)"
