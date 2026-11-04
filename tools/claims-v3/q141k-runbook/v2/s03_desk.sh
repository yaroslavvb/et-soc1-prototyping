#!/usr/bin/env bash
# Q141(k), go checklist step 3: the desk check on the Intel, before anything reaches a box. No ssh to a lab box.
#   git pull --ff-only in the lab clone; HEAD descends from c31e7ae3; `git status --short tools/claims-v3` prints nothing;
#   the four hash lists: blind7 SHA256SUMS 91, frozen-sha256-e168.json 9 (score_e168.py check), frozen-sha256-e168-scorer.txt 18,
#   predict_q140e's 26 (parsed, not imported: frozen26.py).
#
#   RB_OUT=<day dir> RB_LOCK=<file> bash tools/claims-v3/q141k-runbook/s03_desk.sh
#
# Exit 0 all pass; 16 any differs (no card session until a dated amendment says why); 13/14 a call failed.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s03_desk
G4=docs/reports/data/2026-11-04-q140q-gemm-g4-stride
bad=""
rb_local copy github "git pull --ff-only (the public repo)" git -C "$RB_REPO" pull --ff-only || bad="$bad pull"
rb_local read local "HEAD descends from $RB_BASE" git -C "$RB_REPO" merge-base --is-ancestor "$RB_BASE" HEAD || bad="$bad ancestry"
rb_local read local "tools/claims-v3 clean" git -C "$RB_REPO" status --short tools/claims-v3
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
RB_CWD="$RB_REPO/tools/claims-v3/kinds/blind7" rb_local read local "blind7 SHA256SUMS (91)" sha256sum -c SHA256SUMS
if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq 91 ]; } || bad="$bad blind7($n)"; fi
rb_local read local "frozen-sha256-e168.json (9)" "$RB_PY" -B "$G4/score_e168.py" check
rb_has '^CHECK OK' || bad="$bad e168-frozen"
RB_CWD="$RB_REPO/$G4" rb_local read local "frozen-sha256-e168-scorer.txt (18)" shasum -a 256 -c frozen-sha256-e168-scorer.txt
if [ -z "${RB_DRY:-}" ]; then n=$(grep -c ': OK$' "$RB_CAP"); { [ "$RB_RC" -eq 0 ] && [ "$n" -eq 18 ]; } || bad="$bad e168-scorer($n)"; fi
rb_local read local "predict_q140e's 26 inputs" "$RB_PY" -B "$RB_DIR/frozen26.py" "$RB_REPO"
rb_has '^FROZEN 26 OK$' || bad="$bad q140e"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_say "desk check: pulled, HEAD descends from $RB_BASE, tools/claims-v3 clean, blind7 91, E168 9 and 18, predict_q140e 26"
