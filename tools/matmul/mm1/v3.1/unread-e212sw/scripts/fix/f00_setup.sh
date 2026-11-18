#!/bin/bash
# fix-unread-e212sw (Q218) step 01: work copies by `git archive` of GitHub main (read from the lab clone LAB, whose HEAD equals GitHub main by
# ls-remote over the HTTPS rewrite), and the checks the fixes rest on. Reads only: no fetch, no checkout, no edit in LAB. No E213 path is read.
# Run: bash f00_setup.sh
set -u
W=<W>
ME=$W/out/fix-unread-e212sw
LAB=<LAB>
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
LOG=$ME/logs/f00_setup.out
: > "$LOG"
say() { echo "$*" | tee -a "$LOG"; }

# the load rule: wait in bounded chunks (at most about 8 minutes here) while the 1-minute load is above 6
for i in $(seq 1 32); do
  l1=$(cut -d' ' -f1 /proc/loadavg)
  awk -v l="$l1" 'BEGIN{exit !(l > 6.0)}' || break
  say "load $l1 > 6: waiting 15 s ($i)"
  sleep 15
done
say "start $(TZ=America/Los_Angeles date '+%a %d %b %Y %H:%M:%S %Z'); load $(cut -d' ' -f1-3 /proc/loadavg)"

MAIN=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
say "GitHub main $MAIN; LAB HEAD $HEAD"
[ "$MAIN" = "$HEAD" ] || { say "STOP: LAB HEAD differs from GitHub main"; exit 3; }
echo "$MAIN" > "$ME/work/main-commit.txt"

WL=$ME/work/lab
mkdir -p "$WL"
for p in tools/matmul/mm1/v3 tools/matmul/mm1/v1 tools/matmul/mm1/v3.1/counts tools/matmul/mm1/residuals \
         tools/claims-v3/e209 tools/claims-v3/kinds/real2/tiles; do
  git -C "$LAB" archive --format=tar "$MAIN" "$p" | tar -x -C "$WL" || { say "archive failed: $p"; exit 4; }
done
say "archived at $MAIN: v3, v1, v3.1/counts, residuals, claims-v3/e209, kinds/real2/tiles"

for d in tools/matmul/mm1/v3 tools/matmul/mm1/v1 tools/matmul/mm1/v3.1/counts; do
  out=$(cd "$WL/$d" && sha256sum -c SHA256SUMS 2>&1)
  rc=$?
  ok=$(printf '%s\n' "$out" | grep -c ': OK$')
  bad=$(printf '%s\n' "$out" | grep -vc ': OK$')
  say "sha256sum -c in $d: rc $rc, OK $ok, not OK $bad; SHA256SUMS sha256 $(sha256sum "$WL/$d/SHA256SUMS" | cut -c1-64)"
done

# the counts on main against the land dir the unread lane used (fix-v31counts) and against its work copy
CL=$W/out/fix-v31counts/land/tools/matmul/mm1/v3.1/counts
if diff -r -q "$WL/tools/matmul/mm1/v3.1/counts" "$CL" > "$ME/work/counts-diff-main-vs-land.txt" 2>&1; then
  say "counts on main = fix-v31counts' land dir: identical (diff -r, 0 differences)"
else
  say "counts on main differ from fix-v31counts' land dir: see work/counts-diff-main-vs-land.txt"
fi
n_main=$(cd "$WL/tools/matmul/mm1/v3.1/counts" && find . -type f | wc -l)
say "counts files on main (incl. SHA256SUMS): $n_main"
cmp -s "$WL/tools/matmul/mm1/v3.1/counts/SHA256SUMS" "$W/out/unread-e212sw/work/counts/SHA256SUMS" && say "counts SHA256SUMS on main = the unread lane's work copy's"
c=$(cd "$W/out/unread-e212sw/work/counts" && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$')
say "the unread lane's work copy: sha256sum -c OK $c"

# when the counts reached main (the commit that added the folder), read from the log
git -C "$LAB" log --format='%H %cd' --date=format:'%a %d %b %Y %H:%M:%S %z' --diff-filter=A -1 "$MAIN" -- tools/matmul/mm1/v3.1/counts/SHA256SUMS | tee -a "$LOG"

# nothing changed since the unread lane's commit 8e91dda6 in the paths it and this lane read
git -C "$LAB" diff --stat 8e91dda6 "$MAIN" -- tools/matmul/mm1/v3 tools/matmul/mm1/v1 tools/claims-v3/e212 tools/claims-v3/e209 \
   tools/claims-v3/kinds docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2 > "$ME/work/diff-8e91dda6-main.txt"
say "diff --stat 8e91dda6..main over v3, v1, e212, e209 reg + data, kinds: $(wc -l < "$ME/work/diff-8e91dda6-main.txt") lines (0 = unchanged)"

# the land path must be absent on main (names only)
n=$(git -C "$LAB" ls-tree -r --name-only "$MAIN" -- tools/matmul/mm1/v3.1/unread-e212sw | wc -l)
say "files on main under tools/matmul/mm1/v3.1/unread-e212sw: $n (0 = all land files new)"
say "end $(TZ=America/Los_Angeles date '+%H:%M:%S %Z')"
