#!/usr/bin/env bash
# Q143(k), step 3: the desk check before any box step of an M11 session, on the Intel only: the lab clone pulled; HEAD descends from RB_BASE
# (E176's kit and M11's scorer, 03582d2f); E176's, M11's and this runbook's paths clean; M11's lists (SHA256SUMS 58, -m11 6, -a1 9, -a2 7,
# -a3 7, -a4 6, -score-m11 4); E176's kit list (7) and the repo entries of its box list (26 of 29; the three box binaries are checked on the
# box by step 8). A port of ../q141k-runbook/k6/s03_desk_k6.sh to M11's run.
#
#   bash tools/claims-v3/q143k-runbook/s03_desk_q143k.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s03_desk
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E176's, M11's and this runbook's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e176 tools/claims-v3/m11 \
  tools/claims-v3/q143k-runbook
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for pair in SHA256SUMS:58 SHA256SUMS-m11:6 SHA256SUMS-a1:9 SHA256SUMS-a2:7 SHA256SUMS-a3:7 SHA256SUMS-a4:6 SHA256SUMS-score-m11:4; do
  L=${pair%%:*}; want=${pair##*:}
  rb_local read local "M11's $L ($want)" shasum -a 256 -c "tools/claims-v3/m11/$L"
  if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$want" ]; } || bad="$bad $L($n)"; fi
done
rb_local read local "E176's kit list (7)" shasum -a 256 -c tools/claims-v3/e176/kit-e176.sha256
if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq 7 ]; } || bad="$bad kit($n)"; fi
py=$(rb_file boxlist)
cat > "$py" <<'PY'
import hashlib
ok = n = 0
for line in open("tools/claims-v3/e176/frozen-e176.sha256"):
    h, p = line.split()
    if p.startswith("build/"):
        continue
    n += 1
    ok += hashlib.sha256(open(p, "rb").read()).hexdigest() == h
print("BOX-LIST-REPO", ok, "of", n)
PY
rb_local read local "the repo entries of E176's box list (26 of 29)" "$RB_PY" -B "$py"
rb_has '^BOX-LIST-REPO 26 of 26$' || bad="$bad boxlist"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_say "desk check: pulled, HEAD descends from $RB_BASE, the paths clean, M11's seven lists, E176's kit list 7, its box list's 26 repo entries"
