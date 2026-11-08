#!/usr/bin/env bash
# E185, the runbook's step 2 (the desk check), v3: the kit's dated note 2 (KIT.md.dated-note-2.md, Sun 8 Nov 2026). It is
# s03_desk_e185_v2.sh (ad2ed873, which stays as committed) with E185's own lists pinned, each change marked v3:
#   - E185's five lists, each checked OK in full AND at its pinned count AND at its own committed sha256, with no override: the
#     registration's 8, the kit's 13, this runbook's 21, A1's 5 and the kit note 1's 28. v2 read them only as "every entry OK", so a
#     list a later commit cut short, or rewrote with a file and its line together, would pass (critic-q155's nit 2; verify-d2's fault 2,
#     shown there on a throwaway branch: the kit note 1's list cut to 27 lines, v2 rc 0);
#   - the kit note 2's own list, SHA256SUMS-e185-kit-note2, at its pinned count (it lists this file, so it cannot pin its own bytes here);
#   - HEAD also descends from E185's kit note 1 (ad2ed873);
#   - october-forecast-model's note M1 (E185.md.dated-note-M1.md, 2f6a4440): its list SHA256SUMS-e185-m1 is read at its count (21) and
#     its committed sha256 and REPORTED, never a gate: the M1 arm is reported, never one of E185's rules, so its list cannot stop E185
#     (verify-d2's fault 3). The last line says "present, its list 21 of 21 at its pinned bytes" or names the miss ("the M1 arm is not
#     read on this day").
# Everything else is v2's, line for line: it refuses (10) without a window written today by s02_window_e185.sh; the lab clone pulled;
# HEAD descends from E185's registration (98fe28b7, RB_BASE), M11's A10 (5e708747) and E185's A1 (df4e6763); E185's, M11's and the
# footing law's paths clean; M11's seventeen lists and the footing law's two at their counts; the repo entries of the box list (27 of 30).
# On the card day it runs twice (the kit's dated note 2): as step 2, and again just before step 14, so that the lists step 14 v2 reads
# (by shasum's exit status alone) are read at their pins on the same tree an hour or two later.
#
#   bash tools/claims-v3/e185/rb/s03_desk_e185_v3.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common_e185.sh"
rb_init s03_desk_v3
A10=5e708747
A1=df4e6763
KN1=ad2ed873                                                  # v3: E185's kit note 1
E=tools/claims-v3/e185
PINS="SHA256SUMS-e185-registration:8:dd772a171155a07cf5d00f8dc781951255c086f52d30de56c3f5456aa70adcc2
SHA256SUMS-e185-kit:13:79fdc9288e194719dc86e5e38c592f916773cd623e0b0ce17eaeebe52bc8b622
rb/SHA256SUMS-rb-e185:21:2f5371e8a290f7349292cc37e33e93f08c3d6856adcd118f46eed58d3266fe8a
SHA256SUMS-e185-a1:5:8757f508e88d633804d8448ab9706e0c6fd9da006dcdffe6bb45fc872a9f9670
SHA256SUMS-e185-kit-note1:28:0eeedd7c2f0724c30c705006f0439bfda91544992a02e8c720bed56eab38a780"   # v3: list:count:its own sha256
NOTE2=SHA256SUMS-e185-kit-note2:16                            # v3: the kit note 2's list, at its count (no M1 file in it)
M1PIN=SHA256SUMS-e185-m1:21:52a6c1622fcf5f31b7e14e5b332f3a29ae8e5456998b74e30404d1094df7222c   # v3: reported, never a gate
rb_window                                                     # E182's lesson: no desk check before the go's window
[ -n "${RB_DRY:-}" ] || [ "$(TZ=America/Los_Angeles date -r "$RB_OUT/window.env" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
  rb_die $RB_E_USAGE "the window in RB_OUT was not written today: run s02_window_e185.sh with his go's day, last start and last end first"
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_BASE" HEAD || bad="$bad ancestry"
rb_local read local "HEAD descends from M11's A10 ($A10)" git -C "$RB_REPO" merge-base --is-ancestor "$A10" HEAD || bad="$bad ancestry-A10"
rb_local read local "HEAD descends from E185's A1 ($A1)" git -C "$RB_REPO" merge-base --is-ancestor "$A1" HEAD || bad="$bad ancestry-A1"
rb_local read local "HEAD descends from E185's kit note 1 ($KN1)" git -C "$RB_REPO" merge-base --is-ancestor "$KN1" HEAD || bad="$bad ancestry-KN1"   # v3
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
# v3: E185's five lists, each OK in full, at its pinned count and at its own committed bytes (no override)
paths=""; for spec in $PINS; do paths="$paths $E/${spec%%:*}"; done
rb_local read local "the own sha256 of E185's five lists (pinned)" shasum -a 256 $paths
own=$RB_CAP
for spec in $PINS; do
  l=${spec%%:*}; rest=${spec#*:}; pin=${rest%%:*}; hpin=${rest#*:}
  rb_local read local "E185's list $(basename "$l") (pinned at $pin entries and its own sha256)" shasum -a 256 -c "$E/$l"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$E/$l" 2>/dev/null); m=${m:-0}
    h=$(awk -v p="$E/$l" '$2 == p {print $1}' "$own")
    why=""; [ "$h" = "$hpin" ] || why="; its own bytes differ from the pin"
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ] && [ -z "$why" ]; } || bad="$bad $(basename "$l")($n OK of $m; pinned $pin$why)"
  fi
done
# v3: the kit note 2's own list, at its pinned count
l=${NOTE2%%:*}; pin=${NOTE2##*:}
rb_local read local "E185's list $l (the kit's dated note 2; pinned at $pin entries)" shasum -a 256 -c "$E/$l"
if [ -z "${RB_DRY:-}" ]; then
  n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$E/$l" 2>/dev/null); m=${m:-0}
  { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ]; } || bad="$bad $l($n OK of $m; pinned $pin)"
fi
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
# v3: october-forecast-model's note M1, REPORTED (never a gate): its list at its count and its own bytes
l=${M1PIN%%:*}; rest=${M1PIN#*:}; pin=${rest%%:*}; hpin=${rest#*:}
m1="absent (not read)"
if [ -f "$E/E185.md.dated-note-M1.md" ] || [ -n "${RB_DRY:-}" ]; then
  rb_local read local "october-forecast-model's note M1: its list $l (21 entries and its own sha256; REPORTED, never a gate)" shasum -a 256 -c "$E/$l"
  if [ -n "${RB_DRY:-}" ]; then
    m1="(its list read at $pin entries and its own bytes)"
  else
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$E/$l" 2>/dev/null); m=${m:-0}
    h=$(shasum -a 256 "$E/$l" 2>/dev/null | awk '{print $1}')
    if [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ] && [ "$h" = "$hpin" ]; then
      m1="present, its list $n of $pin at its pinned bytes (read beside, by its reader, after step 14)"
    else
      m1="present, but its list is off its pin ($n OK of $m; pinned $pin$([ "$h" = "$hpin" ] || echo '; its own bytes differ')): the M1 arm is not read on this day (a reported arm: no E185 rule depends on it; the data README records it)"
    fi
  fi
fi
echo "$(date '+%F %T %Z') step=$RB_STEP october-forecast-model note M1 $m1" >> "$RB_LOG"
rb_say "desk check v3: the window written today; pulled, HEAD descends from $RB_BASE, A10 ($A10), A1 ($A1) and kit note 1 ($KN1), the paths clean, M11's seventeen lists and the footing law's two, E185's five lists at their pinned counts and bytes (8, 13, 21, 5 and 28) and the kit note 2's at its count (${NOTE2##*:}), its box list's 27 repo entries; october-forecast-model note M1 $m1"
