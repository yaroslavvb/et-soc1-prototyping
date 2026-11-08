#!/usr/bin/env bash
# E185, the runbook's step 2 (the desk check), v2: the kit's dated note 1 (KIT.md.dated-note-1.md, Sat 7 Nov 2026). It is
# s03_desk_e185.sh (460c352f, which stays as committed) with the note's lists added, each marked v2:
#   - HEAD also descends from E185's dated amendment A1 (df4e6763);
#   - E185's lists read in full: v1's three (the registration's, the kit's, this runbook's) and A1's SHA256SUMS-e185-a1 (5) and the kit
#     note's SHA256SUMS-e185-kit-note1, so a step file the note adds (step 2 v2, step 10 v2, step 14 v2, the collector v2) is checked before
#     any box step.
# Everything else is v1's, line for line: it refuses (10) without a window written today by s02_window_e185.sh; the lab clone pulled;
# HEAD descends from E185's registration (98fe28b7, RB_BASE) and from M11's A10 (5e708747); E185's, M11's and the footing law's paths
# clean; M11's seventeen lists and the footing law's two at their counts; the repo entries of the box list (27 of 30).
#
#   bash tools/claims-v3/e185/rb/s03_desk_e185_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e185.sh"
rb_init s03_desk_v2
A10=5e708747
A1=df4e6763                                                   # v2: E185's dated amendment A1
rb_window                                                     # E182's lesson: no desk check before the go's window
[ -n "${RB_DRY:-}" ] || [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
  rb_die $RB_E_USAGE "the window in RB_OUT was not written today: run s02_window_e185.sh with his go's day, last start and last end first"
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_BASE" HEAD || bad="$bad ancestry"
rb_local read local "HEAD descends from M11's A10 ($A10)" git -C "$RB_REPO" merge-base --is-ancestor "$A10" HEAD || bad="$bad ancestry-A10"
rb_local read local "HEAD descends from E185's A1 ($A1)" git -C "$RB_REPO" merge-base --is-ancestor "$A1" HEAD || bad="$bad ancestry-A1"   # v2
rb_local read local "E185's, M11's and the footing law's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e185 tools/claims-v3/m11 \
  tools/claims-v3/footing-law
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for pair in SHA256SUMS:58 SHA256SUMS-m11:6 SHA256SUMS-a1:9 SHA256SUMS-a2:7 SHA256SUMS-a3:7 SHA256SUMS-a4:6 SHA256SUMS-a5:6 SHA256SUMS-a8:4 \
            SHA256SUMS-a9:4 SHA256SUMS-a10:4 SHA256SUMS-score-m11:4 SHA256SUMS-score-m11-v2:6 SHA256SUMS-score-m11-v3:6 SHA256SUMS-score-m11-v4:5 \
            SHA256SUMS-score-m11-v5:4; do
  L=${pair%%:*}; want=${pair##*:}
  rb_local read local "M11's $L ($want)" shasum -a 256 -c "tools/claims-v3/m11/$L"
  if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$want" ]; } || bad="$bad $L($n)"; fi
done
for pair in m11/SHA256SUMS-a6:9 m11/SHA256SUMS-a7:7 footing-law/SHA256SUMS:7 footing-law/SHA256SUMS-note1:4; do   # lists whose paths sit beside them
  L=${pair%%:*}; want=${pair##*:}
  RB_CWD="$RB_REPO/tools/claims-v3/$(dirname "$L")" rb_local read local "$L ($want), read beside the list" shasum -a 256 -c "$(basename "$L")"
  if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$want" ]; } || bad="$bad $L($n)"; fi
done
for l in tools/claims-v3/e185/SHA256SUMS-e185-registration tools/claims-v3/e185/SHA256SUMS-e185-kit tools/claims-v3/e185/rb/SHA256SUMS-rb-e185 \
         tools/claims-v3/e185/SHA256SUMS-e185-a1 tools/claims-v3/e185/SHA256SUMS-e185-kit-note1; do                                   # v2: A1's and the note's
  rb_local read local "E185's list $(basename "$l")" shasum -a 256 -c "$l"
  if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); w=$(grep -c . "$l"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$w" ]; } || bad="$bad $(basename "$l")($n of $w)"; fi
done
py=$(rb_file boxlist)
cat > "$py" <<'PY'
import hashlib
ok = n = 0
for line in open("tools/claims-v3/e185/frozen-e185.sha256"):
    h, p = line.split()
    if p.startswith("build/"):
        continue
    n += 1
    ok += hashlib.sha256(open(p, "rb").read()).hexdigest() == h
print("BOX-LIST-REPO", ok, "of", n)
PY
rb_local read local "the repo entries of E185's box list (27 of 30)" "$RB_PY" -B "$py"
rb_has '^BOX-LIST-REPO 27 of 27$' || bad="$bad boxlist"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_say "desk check v2: the window written today; pulled, HEAD descends from $RB_BASE, A10 ($A10) and A1 ($A1), the paths clean, M11's seventeen lists and the footing law's two, E185's registration, kit, runbook, A1 and kit-note-1 lists, its box list's 27 repo entries"
