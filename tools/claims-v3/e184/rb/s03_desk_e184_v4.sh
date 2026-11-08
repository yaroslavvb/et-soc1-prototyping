#!/usr/bin/env bash
# E184 (Q156), kit note 4 (../KIT.md.dated-note-4.md section 2), step 2 v4: s03_desk_e184_v3.sh (v3, which stays as committed) with
# kit note 4's hash list, its count pinned here (10), beside v3's eight, so step 2 checks NINE lists: 11, 44, 6, 45, 3, 20, 1, 18 and
# 10. Nothing else changed. v3's words follow:
# E184 (Q155), kit note 3 (../KIT.md.dated-note-3.md section 3), step 2 v3: s03_desk_e184_v2.sh (v2, which stays as committed) with two more
# hash lists, each with its count pinned here (dated amendment A4's 1 and kit note 3's 18), beside v2's six, so step 2 checks EIGHT lists:
# 11, 44, 6, 45, 3, 20, 1 and 18. One more change, critic-q154's nit 3: like E182's step 2, it refuses (10) unless this runbook's window was
# written today in RB_OUT (s02_window_e184.sh first; kit v5's lesson). Nothing else changed. v2's words follow:
# E184 (Q154), kit note 2 (../KIT.md.dated-note-2.md section 3), step 2 v2: s03_desk_e184.sh (v1, which stays as committed) with the two hash lists
# dated amendment A3 and kit note 2 add, each with its count pinned here (A3's 3 and kit note 2's 20), beside v1's four, and nothing else
# changed. v1's words follow:
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 2: the desk check before any box step, on the Intel only (KIT.md's box
# step 2, made code). ../../e180/rb/s03_desk_e180_v3.sh's form: the pull; HEAD descends from 65f844be (the kit); E184's paths clean; the four
# hash lists, each with its count (the registration's 11, the kit's 44, dated amendment A2's and kit note 1's, which pin every file A2, kit
# v2 and this runbook add); harness-e184-v2.json rebuilt; the plan and the image list re-made; HARNESS OK (v2) without binaries; any E184
# data in any ref reported, not gated (none may exist before the first session).
#
#   bash tools/claims-v3/e184/rb/s03_desk_e184_v4.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s03_desk
if [ -z "${RB_DRY:-}" ]; then   # v3 (critic-q154's nit 3): the window first, as E182's step 2 does
  [ -f "$RB_OUT/window.env" ] || rb_die $RB_E_USAGE "no window in RB_OUT: run s02_window_e184.sh first (kit v5: s02 before s03)"
  [ "$(date -r "$RB_OUT/window.env" +%F)" = "$(date +%F)" ] || rb_die $RB_E_USAGE "RB_OUT's window was not written today: run s02_window_e184.sh first"
fi
LISTS="SHA256SUMS-e184-registration:11 SHA256SUMS-e184-kit:44 SHA256SUMS-e184-a2:6 SHA256SUMS-e184-kit-note1:45 SHA256SUMS-e184-a3:3 SHA256SUMS-e184-kit-note2:20 SHA256SUMS-e184-a4:1 SHA256SUMS-e184-kit-note3:18 SHA256SUMS-e184-kit-note4:10"   # v3: A4's and kit note 3's; v4: kit note 4's
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_E184_BASE (the kit)" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E184_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E184's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e184
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
for spec in $LISTS; do
  name=${spec%%:*}; want=${spec##*:}
  rb_local read local "the hash list $name" shasum -a 256 -c "tools/claims-v3/e184/$name"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "tools/claims-v3/e184/$name")
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -gt 0 ] && [ "$n" -eq "$want" ]; } || bad="$bad $name($n of $m, want $want)"
  fi
done
rb_local read local "harness-e184-v2.json rebuilt" "$RB_PY" -B tools/claims-v3/e184/make_harness_e184_v2.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "the plan re-made (plan_e184.py --check)" "$RB_PY" -B tools/claims-v3/e184/plan_e184.py --check tools/claims-v3/e184/plan-e184.json
rb_has 'IDENTICAL' || bad="$bad plan"
rb_local read local "the image list re-made (make_images_e184.py --check)" "$RB_PY" -B tools/claims-v3/e184/make_images_e184.py --check tools/claims-v3/e184/images-e184.sha256
rb_has 'IDENTICAL \(467 images\)' || bad="$bad images"
rb_local read local "the harness without binaries (check_e184_v2.py harness)" "$RB_PY" -B tools/claims-v3/e184/check_e184_v2.py harness
rb_has '^HARNESS OK: ' || bad="$bad harness"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_local read local "E184 data in any ref (want none before the first session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e184*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
rb_say "desk check (v4): the window written today, pulled, HEAD descends from $RB_E184_BASE (the kit), E184's paths clean, the nine hash lists ($LISTS), harness v2 rebuilt, the plan and the images re-made, HARNESS OK (v2); commits naming E184 data: $nd"
