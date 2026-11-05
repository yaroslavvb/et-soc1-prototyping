#!/usr/bin/env bash
# Q142(k6), step 3: the desk check before any box step of the pool-8 card day, on the Intel only: the lab clone pulled; HEAD descends from
# RB_BASE (this day's kits' commit); E171's, E172's and the scorer's paths clean; pool 8's SHA256SUMS (89 OK); the freeze's hash list (160
# OK, Q142(x)); the scorer's SHA256SUMS (5 OK); the predictor's own lists (predict_pool8_a2.check_lists: 16 and 9) and its 209 inputs
# (check_inputs). A port of ../v3.1/s03_desk.sh to these runs (its E163-E169 checks are not this day's).
#
#   bash tools/claims-v3/q141k-runbook/k6/s03_desk_k6.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s03_desk
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E171's, E172's and the scorer's paths clean" git -C "$RB_REPO" status --short tools/claims-v3/e171 tools/claims-v3/e172 \
  tools/claims-v3/p8-600 tools/claims-v3/kinds/blind8 tools/claims-v3/q141k-runbook/k6
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
RB_CWD="$RB_REPO/tools/claims-v3/kinds/blind8" rb_local read local "blind8 SHA256SUMS (89)" shasum -a 256 -c SHA256SUMS
if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq 89 ]; } || bad="$bad blind8($n)"; fi
rb_local read local "the freeze's SHA256SUMS (160)" shasum -a 256 -c docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS
if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq 160 ]; } || bad="$bad freeze($n)"; fi
rb_local read local "the scorer's SHA256SUMS (5)" shasum -a 256 -c tools/claims-v3/p8-600/SHA256SUMS
if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq 5 ]; } || bad="$bad scorer($n)"; fi
py=$(rb_file lists)
cat > "$py" <<'PY'
import sys
sys.path.insert(0, "docs/reports/data/2026-11-05-q142p-pool8-predictor")
import predict_pool8_a2 as A
n = A.check_lists()
print("PREDICTOR-LISTS", n["SHA256SUMS"], n["SHA256SUMS-a2"], "INPUTS", A.P().check_inputs())
PY
rb_local read local "the predictor's own lists and its 209 inputs" "$RB_PY" -B "$py"
rb_has '^PREDICTOR-LISTS 16 9 INPUTS 209$' || bad="$bad predictor"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_say "desk check: pulled, HEAD descends from $RB_BASE, the paths clean, blind8 89, the freeze 160, the scorer 5, the predictor 16 / 9 / 209"
