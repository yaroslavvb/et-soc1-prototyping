#!/bin/bash
# v31-trace (Q217), run ON aifoundry3 (sent by a3_send.sh only while no lane books it): replace this lane's scripts in
# ~/claude/work/q217-v31-trace by those of a newer payload (~/claude/work/q217-v31-trace-<v>.tgz) and check the sums; bin/ and runs/ kept.
#   bash r_update.sh <version>
set -u
v=${1:?version}
D="$HOME/claude/work/q217-v31-trace"; T="$HOME/claude/work/q217-v31-trace-$v.tgz"
[ -f "$T" ] && [ -d "$D" ] || { echo "no payload $v or no lane folder"; exit 3; }
S="$D/staging-$v"; [ -e "$S" ] && { echo "staging exists"; exit 3; }
mkdir -p "$S" && tar xzf "$T" -C "$S" --strip-components=1 || exit 3
( cd "$S" && sha256sum -c --quiet SHA256SUMS ) || { echo "PAYLOAD $v SHA MISMATCH"; exit 4; }
for f in trace_run.py r_prep.sh r_trace.sh SHA256SUMS SOURCE.txt; do cp "$S/$f" "$D/$f"; done
cd "$D" && sha256sum -c --quiet SHA256SUMS && echo "payload $v installed; sums OK" || { echo "SUMS FAIL after install"; exit 5; }
sha256sum trace_run.py r_trace.sh
