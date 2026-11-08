#!/usr/bin/env bash
# E184 (Q154), kit note 2 (../KIT.md.dated-note-2.md section 3), step 2 v2: s03_desk_e184.sh (v1, which stays as committed) with the two hash lists
# dated amendment A3 and kit note 2 add, each with its count pinned here (A3's 3 and kit note 2's 20), beside v1's four, and nothing else
# changed. v1's words follow:
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3), step 2: the desk check before any box step, on the Intel only (KIT.md's box
# step 2, made code). ../../e180/rb/s03_desk_e180_v3.sh's form: the pull; HEAD descends from 65f844be (the kit); E184's paths clean; the four
# hash lists, each with its count (the registration's 11, the kit's 44, dated amendment A2's and kit note 1's, which pin every file A2, kit
# v2 and this runbook add); harness-e184-v2.json rebuilt; the plan and the image list re-made; HARNESS OK (v2) without binaries; any E184
# data in any ref reported, not gated (none may exist before the first session).
#
#   bash tools/claims-v3/e184/rb/s03_desk_e184_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e184.sh"
rb_init s03_desk
LISTS="SHA256SUMS-e184-registration:11 SHA256SUMS-e184-kit:44 SHA256SUMS-e184-a2:6 SHA256SUMS-e184-kit-note1:45 SHA256SUMS-e184-a3:3 SHA256SUMS-e184-kit-note2:20"
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
rb_say "desk check (v2): pulled, HEAD descends from $RB_E184_BASE (the kit), E184's paths clean, the six hash lists ($LISTS), harness v2 rebuilt, the plan and the images re-made, HARNESS OK (v2); commits naming E184 data: $nd"
