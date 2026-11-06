#!/usr/bin/env bash
# E181, step 3: the desk check before any box step of M11's session 2, on the Intel only: the lab clone pulled; HEAD descends from RB_BASE
# (M11's A8, 80b92990); E181's, M11's and the footing law's paths clean; M11's lists (SHA256SUMS 58, -m11 6, -a1 9, -a2 7, -a3 7, -a4 6,
# -a5 6, -a6 9 and -a7 7 read beside the lists, -a8 4, -score-m11 4, -score-m11-v2 6, -score-m11-v3 6); the footing law's two lists (7, 4);
# E181's kit list (kit-e181.sha256) and the repo entries of its box list (27 of 30; the three box binaries are checked on the box by step 8);
# this runbook's own list (SHA256SUMS-rb-e181). A port of ../../q143k-runbook/s03_desk_q143k.sh (92a1b27f) to M11's session 2: every list
# the session, the collection and the score read is checked here, so the go needs no separate list command.
#
#   bash tools/claims-v3/e181/rb/s03_desk_e181.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e181.sh"
rb_init s03_desk
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E181's, M11's and the footing law's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e181 tools/claims-v3/m11 \
  tools/claims-v3/footing-law
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for pair in SHA256SUMS:58 SHA256SUMS-m11:6 SHA256SUMS-a1:9 SHA256SUMS-a2:7 SHA256SUMS-a3:7 SHA256SUMS-a4:6 SHA256SUMS-a5:6 SHA256SUMS-a8:4 \
            SHA256SUMS-score-m11:4 SHA256SUMS-score-m11-v2:6 SHA256SUMS-score-m11-v3:6; do
  L=${pair%%:*}; want=${pair##*:}
  rb_local read local "M11's $L ($want)" shasum -a 256 -c "tools/claims-v3/m11/$L"
  if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$want" ]; } || bad="$bad $L($n)"; fi
done
for pair in m11/SHA256SUMS-a6:9 m11/SHA256SUMS-a7:7 footing-law/SHA256SUMS:7 footing-law/SHA256SUMS-note1:4; do   # lists whose paths sit beside them
  L=${pair%%:*}; want=${pair##*:}
  RB_CWD="$RB_REPO/tools/claims-v3/$(dirname "$L")" rb_local read local "$L ($want), read beside the list" shasum -a 256 -c "$(basename "$L")"
  if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$want" ]; } || bad="$bad $L($n)"; fi
done
rb_local read local "E181's kit list" shasum -a 256 -c tools/claims-v3/e181/kit-e181.sha256
if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); w=$(grep -c . tools/claims-v3/e181/kit-e181.sha256); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$w" ]; } || bad="$bad kit($n of $w)"; fi
rb_local read local "this runbook's list" shasum -a 256 -c tools/claims-v3/e181/rb/SHA256SUMS-rb-e181
if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); w=$(grep -c . tools/claims-v3/e181/rb/SHA256SUMS-rb-e181); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$w" ]; } || bad="$bad rb($n of $w)"; fi
py=$(rb_file boxlist)
cat > "$py" <<'PY'
import hashlib
ok = n = 0
for line in open("tools/claims-v3/e181/frozen-e181.sha256"):
    h, p = line.split()
    if p.startswith("build/"):
        continue
    n += 1
    ok += hashlib.sha256(open(p, "rb").read()).hexdigest() == h
print("BOX-LIST-REPO", ok, "of", n)
PY
rb_local read local "the repo entries of E181's box list (27 of 30)" "$RB_PY" -B "$py"
rb_has '^BOX-LIST-REPO 27 of 27$' || bad="$bad boxlist"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_say "desk check: pulled, HEAD descends from $RB_BASE, the paths clean, M11's thirteen lists and the footing law's two, E181's kit list, this runbook's list, its box list's 27 repo entries"
