#!/bin/bash
# blind-v3-e212s3 (Q223) step 0: the work copies. Desk; no device; no S3 datum exists or is read here.
# - MM1-v3 (tools/matmul/mm1/v3) and MM1-v2 (tools/matmul/mm1/v2) by git archive of b1493082 (MM1-v3's land) into work/lab-b149/;
# - E212's registration (tools/claims-v3/e212) and its seal notes (tools/claims-v3/sealed-e212) by git archive of LAB HEAD
#   (= GitHub main, checked first) into work/lab-head/. LAB itself is only read.
# - every SHA256SUMS checked; the frozen S3 forecast's sha256 against MM1-v3's README table and SHA256SUMS; the registered schedule
#   a2c0-S3.json against MM1-v3's vendored copy inputs/e212/sched__a2c0-S3.json.
set -u
W=<W>
L=$W/out/blind-v3-e212s3
LAB=<LAB>
LAND=b149308280a73396516937304037af57a5563c16
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
ts() { TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'; }
echo "start $(ts)"
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "GitHub main $REMOTE ; LAB HEAD $HEAD"
if [ "$REMOTE" != "$HEAD" ]; then echo "LAB HEAD differs from GitHub main: stop"; exit 3; fi
echo "$HEAD" > "$L/work/lab-head-commit.txt"
git -C "$LAB" merge-base --is-ancestor "$LAND" "$HEAD" && echo "b1493082 is an ancestor of main $HEAD"
git -C "$LAB" log -1 --format='land commit %H author %ai committer %ci' "$LAND"
echo "--- commits after the land touching MM1-v3, MM1-v2 or E212's registration (expect none):"
git -C "$LAB" log --format='%h %ci %s' "$LAND..$HEAD" -- tools/matmul/mm1/v3 tools/matmul/mm1/v2 tools/claims-v3/e212 | cut -c1-160
if [ -d "$L/work/lab-b149/tools" ] || [ -d "$L/work/lab-head/tools" ]; then echo "work copies exist already: stop (no overwrite)"; exit 4; fi
mkdir -p "$L/work/lab-b149" "$L/work/lab-head"
git -C "$LAB" archive --format=tar "$LAND" tools/matmul/mm1/v3 tools/matmul/mm1/v2 | tar -x -C "$L/work/lab-b149"
echo "archive (b1493082) rc ${PIPESTATUS[0]} $(ts)"
git -C "$LAB" archive --format=tar "$HEAD" tools/claims-v3/e212 tools/claims-v3/sealed-e212 | tar -x -C "$L/work/lab-head"
echo "archive (HEAD) rc ${PIPESTATUS[0]} $(ts)"
echo "--- MM1-v3 SHA256SUMS check (work copy)"
( cd "$L/work/lab-b149/tools/matmul/mm1/v3" && sha256sum SHA256SUMS && sha256sum -c SHA256SUMS > "$L/logs/v3-sha256sum-c.txt" 2>&1; echo "rc $?"; echo "not OK: $(grep -vc ': OK$' "$L/logs/v3-sha256sum-c.txt")"; echo "OK: $(grep -c ': OK$' "$L/logs/v3-sha256sum-c.txt")" )
echo "--- MM1-v2 SHA256SUMS check (work copy)"
( cd "$L/work/lab-b149/tools/matmul/mm1/v2" && sha256sum SHA256SUMS && sha256sum -c SHA256SUMS > "$L/logs/v2-sha256sum-c.txt" 2>&1; echo "rc $?"; echo "not OK: $(grep -vc ': OK$' "$L/logs/v2-sha256sum-c.txt")"; echo "OK: $(grep -c ': OK$' "$L/logs/v2-sha256sum-c.txt")" )
echo "--- E212 registration SHA256SUMS check (work copy)"
( cd "$L/work/lab-head/tools/claims-v3/e212" && ls SHA256SUMS* && for f in SHA256SUMS*; do sha256sum "$f"; sha256sum -c "$f" > "$L/logs/e212reg-$f-c.txt" 2>&1; echo "$f rc $?"; echo "not OK: $(grep -vc ': OK$' "$L/logs/e212reg-$f-c.txt")"; echo "OK: $(grep -c ': OK$' "$L/logs/e212reg-$f-c.txt")"; done )
echo "--- the frozen S3 forecast file"
V3=$L/work/lab-b149/tools/matmul/mm1/v3
sha256sum "$V3/out/mm1_v3_e212_s3s4.csv"
grep -F 'out/mm1_v3_e212_s3s4.csv' "$V3/SHA256SUMS"
grep -c . "$V3/out/mm1_v3_e212_s3s4.csv"
echo "--- the registered schedule against MM1-v3's vendored copy"
find "$L/work/lab-head/tools/claims-v3/e212" -name '*a2c0-S3*' -print0 | xargs -0 sha256sum
sha256sum "$V3/inputs/e212/sched__a2c0-S3.json"
echo "end $(ts)"
