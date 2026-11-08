#!/usr/bin/env bash
# E186 kit note 4 (Q158, fix-arms), KIT.md box step 11 v4 (this file is s22 v4): the collection with october-forecast-model's note M2 read
# by its reader v2 (arm_m2_read_e186_v2.py; E186.md.dated-note-M2.md.dated-note-1.md, section 2) after note M1. It is step 11 v3
# (rb/s22_collect_e186_v3.sh, which stays as committed and is never run that day) line for line, with four changes, each marked "kit
# note 4": its step's name; note M2's list v2 (SHA256SUMS-e186-m2-v2, which names the reader v2) pinned at its count and its own sha256
# (M2PIN) in place of v1's list; note M2's gate v2 (rb/check_m2_e186_v2.py, which runs the reader v2) in place of v1's gate; and the
# reading's words, which name the reader v2. So it runs
# step 11 v2 (rb/s22_collect_e186_v2.sh) FIRST and UNCHANGED (the window rule, the used-output refusal, the copies by name, COPY-BACK EXACT,
# the history check v2, the collector v2 with the pairing check, the C-session gate, the desk-path gate, the login scrub, then note M1's
# reader through its gate), and stops with v2's exit code if v2 does not read 0: nothing of note M2 runs then. On v2's 0 it adds:
#   - NOTE M2'S GATE V2 (rb/check_m2_e186_v2.py): note M2's list v2 at the count and its own sha256 pinned here (M2PIN), every entry at its
#     bytes, the reader v2 and its json among them, nothing uncommitted, the scorer's file there;
#   - NOTE M2'S READER V2 (arm_m2_read_e186_v2.py) by its own run line, on a copy of the scorer's file in RB_OUT (the reader never sees the
#     data directory); only its two outputs, arm-m2-e186.json and .txt, are put into the data directory.
# A refusal by the gate or by the reader reads "M2 NOT READ" in the step's last line and in <out>/arm-m2-e186.status.txt: it never stops
# the step and never changes the session's scoring (a reported arm; no E186 rule depends on it), and the step exits 0 as step 11 v2 did.
# A change to any file note M2's list v2 names, or to the list, is refused first by the history check (16) inside step 11 v2 (and before
# that in step 2 v2), so the gate's "M2 NOT READ" comes from its other causes (kit note 4, section 3). One thing stops this step (16)
# before the data commit: M2-WROTE-OTHER, a data directory that changed beside the reader's two outputs. The gate runs in the desk class
# (its own bounds: the reader 50 s, git status 60 s), so no bound of the runbook's can stop the step after v2. Desk-test stand-ins, read
# only with RB_DESKTEST=1 (else 10 before any call): K6E186_S22V2 (for step 11 v2) and K6E186_M2READER (for the reader, read by the gate).
# The card day sets neither.
#
#   bash tools/claims-v3/e186/rb/s22_collect_e186_v4.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e186.sh"
rb_init s22_collect_v4                                                                                # kit note 4: the step's name
e186_window
M2PIN=tools/claims-v3/e186/SHA256SUMS-e186-m2-v2:9:db3b69256b39edadb62d7a487744a7f4df4501a5220f1fc86a255fdcdd78f941   # kit note 4: note M2's list v2, count:its own sha256
if [ "${RB_DESKTEST:-}" != 1 ]; then
  for v in K6E186_S22V2 K6E186_M2READER; do
    [ -n "${!v:-}" ] && rb_die $RB_E_USAGE "$v is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
  done
fi
V2=${K6E186_S22V2:-$RB_E186_DIR/s22_collect_e186_v2.sh}
bash "$V2"
r=$?
if [ "$r" -ne 0 ]; then
  echo "[$RB_STEP] STOP: step 11 v2 exited $r (its lines above): note M2's gate and reader were not run"
  echo "$(date '+%F %T %Z') step=$RB_STEP exit=$r step 11 v2 exited $r; note M2 not run" >> "$RB_LOG"; exit "$r"
fi
DAY=$RB_DAY
OUT=build/e186-out/$DAY-e186-one-number-r3-aifoundry3
l=${M2PIN%%:*}; rest=${M2PIN#*:}; pin=${rest%%:*}; hpin=${rest#*:}
rb_local desk local "october-forecast-model's note M2 through its gate v2: $(basename "$l") at $pin entries and its pinned bytes, then its reader v2 on a copy of the scorer's file, after note M1's (a refusal reads M2 NOT READ, never a stop)" \
  /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_m2_e186_v2.py --list "$l" --count "$pin" --sha256 "$hpin" --data "$OUT" --work "$RB_OUT/m2-work"   # kit note 4: the gate v2
m2="read (arm-m2-e186.json and .txt, by note M2's reader v2)"                                       # kit note 4: the words
if [ -z "${RB_DRY:-}" ]; then
  rb_has '^M2-WROTE-OTHER ' && rb_die $RB_E_GATE "$(grep -m1 '^M2-WROTE-OTHER ' "$RB_CAP" | cut -c1-300): nothing is committed; read the data directory first"
  if rb_has '^M2-READ '; then :
  else m2="M2 NOT READ ($(grep -m1 '^M2 NOT READ' "$RB_CAP" | cut -c14-260)): recorded for the data README; no E186 rule depends on it"; fi
  [ ! -d "$OUT" ] || echo "$(date '+%F %T %Z') M2 arm: $m2" > "$OUT/arm-m2-e186.status.txt"
fi
rb_say "step 11 v2 read 0 (its last line above); october-forecast-model's note M2 arm $m2; before the data commit, scan its message with the files"
