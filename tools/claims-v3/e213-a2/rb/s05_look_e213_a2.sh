#!/usr/bin/env bash
# E213 Amendment A2 (Q219, lane a2-e213, Wed 18 Nov 2026, before any datum of E213's arm B), STEP 4 FOR ARM B, in place of k6's look
# (tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh aifoundry1, whose box half, tools/claims-v3/e172/box/look_e172.sh, carries the firmware
# identity by continuity and stops every boot after E82's firmware read of 2026-10-31 13:45:24 PDT; aifoundry1 booted 2026-11-17 16:46:32 PST).
# Each call, in this order (nothing is synced or read before the gate above it passes):
#   1. the window rule (written today for E213 arm B; now before the last start); arm A is refused (10): A2 is arm B's alone;
#   2. THE PINS at the desk: fwgate.py (landed d5beec9b), its six records and A2's box helper committed, unmodified and at their sha256 in the lab
#      clone (rb/rb_e213_a2.sh), else 16;
#   3. THE HOLDER RULE by k6's look itself, unchanged, with --wait (k6 skips look_e172.sh under --wait: no identity is read there): FREE (0) goes
#      on; its other exits are this step's (17 held: call this step again, bounded; 15 held 30 minutes in all: no session today; 11, 12, 13, 14);
#      it writes RB_OUT/box-login-aifoundry1.txt, the login file the collection's scrub reads;
#   4. A2's box files into the box's tree by ONE rsync -a -c -R -i (at their committed bytes), then their sha256 on the box: A2-PINS OK, else 16;
#   5. FWGATE'S LOOK on the box (fwgate_e213a2.py look: `fwgate.py look --box aifoundry1 --card 1 --extra <the read's folder>`, no device):
#      CONTINUITY passes (no read); NEEDS-READ goes on; anything else is 16 (STOPPED, NO-RECORD, or an earlier read attempt of this boot that
#      did not end EQUAL);
#   6. ON NEEDS-READ ONLY, in ONE bounded call (600 s, so that the desk's bound never cuts the read): THE REST RULE first (E213's
#      rest_rule_e213.sh, unchanged: the read is a card command, so it waits for the rest like step 7's config read; a REFUSED there sends
#      nothing: 10, wait in bounded chunks and run this step again); then BOTH CARDS FREE: `et-who --check` (a read of the holders, no node
#      opened) polled every 10 s for at most 400 s until it reads free (exit 0), because fwgate's read needs it free and both cards' locks, and a
#      holder on card 0 (another login's work there) would otherwise end the day at the read: still held, nothing is read (17: call this step
#      again, bounded; 15 once it has read held for 30 minutes in all, RB_OUT/hold-a2-aifoundry1.since: no session today); then at once ONE
#      read (fwgate_e213a2.py read: `fwgate.py read --box aifoundry1 --card 1 --both-nodes-ok --out <the read's folder>`, ET_DEVICES removed
#      from its environment). EQUAL passes; ANYTHING ELSE IS 16 AND ENDS ARM B'S DAY (DIFFERENT, UNREADABLE, a cut-off read, a busy lock,
#      et-who --check not free at the read itself, a missing lock file, a refusal, an unreadable answer): never a second read on this boot, by
#      fwgate, by this kit or by any lane;
#   7. the read's folder, when the box holds one, copied back read-only into RB_OUT/e213-a2-fwgate-B/ by ONE rsync and checked file by file
#      against the box's own sha256 list (exact, else 16), then THE SCRUB CHECK on it (collect_e213.py scrub-check, unchanged, with the box's home
#      in every form read in the same call and the look's login file): SCRUB-CHECK CLEAN, else 16 (the record could not be committed: no session
#      today, E209's lesson);
#   7e. THE EVIDENCE OF THE ONE CALL (fix-a2e213, before A2 landed: verify-a2e213's finding 2), read only in the same box call as item 7's
#      listing: this boot's lines of fwgate's ledger and of the kit's attempt log (fwgate_e213a2.py evidence, under a plain timeout 20; no
#      device), written verbatim into RB_OUT/e213-a2-evidence-B/ (fwgate-ledger-aifoundry1-c1-this-boot.jsonl and
#      a2-fwgate-attempts-aifoundry1-c1-this-boot.jsonl) with their sha256 list RB_OUT/e213-a2-evidence-B.sha256, for the data verifier;
#      A2's step 12 adds them to fwgate/ after the kit's scrub. NEVER A GATE: a capture that fails is said in the runbook log and the look
#      file, an earlier capture in RB_OUT is kept, and the step goes on (fwgate's guard at step 9 reads the same ledger and stops on it);
#   8. RB_OUT/e213-a2-look-B.txt ("A2-LOOK-B: CONTINUITY ..." or "A2-LOOK-B: EQUAL <record> ..."), which A2's step 9 requires from today.
# The firmware read (item 6) is a card command for THE REST RULE alone (applied before it): for E213.md section 4's never-run scan and step 7's
# 30-minute check of step 6n's report, the day's first card command stays step 7's config read (fix-a2e213, verify-a2e213's finding 1).
# A call after an EQUAL read the same day finds fwgate's look CONTINUITY (this boot's EQUAL record of today, read with --extra) and reads nothing.
# Exits: 0 pass; 10 refused (usage, arm A, the window, the rest not open before the read); 11 a login link; 12 no answer; 13 past a bound;
# 14 a call failed; 15 held 30 minutes in all (k6's holder rule, or both cards before the read); 16 a gate says stop (no session on this boot:
# row E); 17 held: call again (nothing read).
#   bash tools/claims-v3/e213-a2/rb/s05_look_e213_a2.sh B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e213_a2.sh"
rb_init s05_look_a2
e213_arm "${1:-}"
e213a2_only_B
e213_window
rb_need_start
FWDIR=$(e213a2_dir)
e213a2_check_desk
# 3. THE HOLDER RULE: k6's look, unchanged, with --wait (no identity read; the login file for the scrub)
bash "$RB_REPO/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" "$BOX" --wait
r=$?
[ "$r" -eq 0 ] || { echo "[$RB_STEP] k6's holder rule exited $r: nothing synced, nothing read (17: call this step again, bounded; 15: no session today)"
                    [ -n "${RB_LOG:-}" ] && echo "$(date '+%F %T %Z') step=$RB_STEP exit=$r k6's holder rule" >> "$RB_LOG"; exit "$r"; }
# 4. A2's box files into the box's tree, then their sha256 there
rb_probe "$BOX"
rb_local copy "$BOX" "$BOX's rsync: A2's box files (fwgate.py, its six records, A2's helper), itemized" \
  rsync -a -c -R -i --exclude __pycache__ -e "$RB_RSH" $E213A2_BOXFILES "$BOX:$(rb_tree "$BOX")/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rsync of A2's box files exited $RB_RC"
f=$(rb_file a2pins)
{ rb_prelude "$BOX"; e213a2_pins_box_text; } > "$f"
rb_remote read "$BOX" "A2's box files at their pinned sha256 in the box's tree" "$f"
[ -n "${RB_DRY:-}" ] || rb_has '^A2-PINS OK ' || rb_die $RB_E_GATE "A2's box files are not at their pinned sha256 on $BOX: $(grep -m1 '^A2-PINS' "$RB_CAP" | cut -c1-200)"
# 5. fwgate's look on the box (no device)
f=$(rb_file a2look)
{ rb_prelude "$BOX"
  echo "FWDIR=$(printf '%q' "$FWDIR")"
  cat <<'EOF'
python3 -I -B tools/claims-v3/e213-a2/fwgate_e213a2.py look --box "$BOX" --card 1 --dir "$FWDIR"; echo "A2-LOOK-RC $?"
EOF
} > "$f"
rb_remote read "$BOX" "fwgate's look for card 1 (no device): CONTINUITY, NEEDS-READ or a stop" "$f"
lrc=$(rb_val '^A2-LOOK-RC ([0-9]+)$')
[ -n "${RB_DRY:-}" ] && lrc=17
verdict=""
case "$lrc" in
  0)  verdict="CONTINUITY: $(grep -m1 '^A2-LOOK: CONTINUITY: ' "$RB_CAP" | sed 's/^A2-LOOK: CONTINUITY: //' | cut -c1-240)" ;;
  17) ;;
  *)  rb_die $RB_E_GATE "fwgate's look says stop (exit ${lrc:-none}): $(grep -m1 -E '^A2-LOOK: ' "$RB_CAP" | cut -c1-300): no read and no launch on this boot; tell the orchestrator" ;;
esac
if [ "$lrc" = 17 ]; then
  # 6. THE REST RULE, then the ONE read, in one bounded call
  f=$(rb_file a2read)
  { rb_prelude "$BOX"
    echo "FWDIR=$(printf '%q' "$FWDIR")"
    cat "$RB_E213_DIR/rest_rule_e213.sh"
    flim=400; [ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E213A2_DESK_FLIM:-}" ] && flim=$E213A2_DESK_FLIM     # the desk test's short wait only
    echo "FLIM=$flim; FPOLL=10"
    cat <<'EOF'
timeout 20 et-who --check > /dev/null 2>&1; w=$?
while [ "$w" -ne 0 ] && [ "$SECONDS" -lt "$FLIM" ]; do sleep "$FPOLL"; timeout 20 et-who --check > /dev/null 2>&1; w=$?; done
if [ "$w" -ne 0 ]; then echo "A2-HELD: et-who --check has not read free on $BOX (either card) after $SECONDS s (last exit $w): nothing read"; exit 0; fi
echo "A2-BOTH-FREE: et-who --check reads free on $BOX (both cards) after $SECONDS s: the one read follows at once"
python3 -I -B tools/claims-v3/e213-a2/fwgate_e213a2.py read --box "$BOX" --card 1 --dir "$FWDIR"; echo "A2-READ-RC $?"
EOF
  } > "$f"
  rb_remote wait "$BOX" "THE REST RULE, both cards free (et-who --check), then fwgate's ONE firmware read of card 1 (both cards' locks held; the owner's word for it, A2)" "$f"
  rb_refused
  if [ -z "${RB_DRY:-}" ] && rb_has '^A2-HELD: '; then
    st="$RB_OUT/hold-a2-$BOX.since"
    [ -f "$st" ] || date +%s > "$st"
    held=$(( $(date +%s) - $(cat "$st") ))
    echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 '^A2-HELD: ' "$RB_CAP" | cut -c1-200) (held $((held / 60)) minutes in all)" >> "$RB_LOG"
    [ "$held" -lt "$RB_HOLD_MAX_S" ] || rb_die $RB_E_SKIP "$BOX's cards held for $((held / 60)) minutes in all by et-who --check before the read: no read, no session today"
    rb_say "$BOX: et-who --check still reads held (either card): nothing read; call this step again (bounded; skip at $((RB_HOLD_MAX_S / 60)) minutes in all)"
    exit $RB_E_AGAIN
  fi
  if [ -z "${RB_DRY:-}" ]; then
    rm -f "$RB_OUT/hold-a2-$BOX.since"
    for k in rest note; do rb_has "^$k: " && echo "$(date '+%F %T %Z') step=$RB_STEP $(grep -m1 "^$k: " "$RB_CAP")" >> "$RB_LOG"; done
    rrc=$(rb_val '^A2-READ-RC ([0-9]+)$')
    echo "$(date '+%F %T %Z') step=$RB_STEP fwgate read rc=${rrc:-none}: $(grep -m1 -E '^A2-(READ|STOP): ' "$RB_CAP" | cut -c1-240)" >> "$RB_LOG"
    { [ "$rrc" = 0 ] && rb_has '^A2-READ: EQUAL fwgate-aifoundry1-c1-[0-9]{8}-[0-9]{6}\.json '; } ||
      rb_die $RB_E_GATE "the one firmware read did not end EQUAL (exit ${rrc:-none}): $(grep -m1 -E '^A2-(STOP|READ): ' "$RB_CAP" | cut -c1-300): no session on this boot, never a second read on it; tell the orchestrator"
    verdict="EQUAL $(rb_val '^A2-READ: EQUAL (fwgate-aifoundry1-c1-[0-9]{8}-[0-9]{6}\.json) .*$')"
  else
    verdict="EQUAL (dry listing)"
  fi
fi
# 7. the read's folder, if the box holds one: copied back, checked exact, scrubbed on a private copy
f=$(rb_file a2list)
{ rb_prelude "$BOX"
  echo "FWDIR=$(printf '%q' "$FWDIR")"
  cat <<'EOF'
if [ -d "$FWDIR" ]; then
  echo "A2-DIR $(find "$FWDIR" -type f | wc -l | tr -d ' ') files"
  ( cd "$FWDIR" && find . -type f | LC_ALL=C sort | while IFS= read -r x; do sha256sum "$x"; done ) | sed 's/^/A2-SUM /'
else
  echo "A2-DIR none"
fi
timeout 20 python3 -I -B tools/claims-v3/e213-a2/fwgate_e213a2.py evidence --box "$BOX" --card 1 --dir "$FWDIR"; echo "A2-EVIDENCE-RC $?"
EOF
  e213_homes_text
} > "$f"
rb_remote read "$BOX" "the read's folder on the box (its files' sha256), this boot's lines of fwgate's ledger and of the kit's attempt log (read only), and the box's home in every form" "$f"
if [ -n "${RB_DRY:-}" ]; then
  echo "--- then: the A2-LEDGER and A2-ATTEMPT lines into <RB_OUT>/e213-a2-evidence-B/ with their sha256 list (evidence, never a gate); and (on 'A2-DIR <n> files') one rsync of the folder into <RB_OUT>/e213-a2-fwgate-B/, each file checked against the box's sha256, and collect_e213.py scrub-check on it: SCRUB-CHECK CLEAN"
  exit 0
fi
rb_has '^A2-DIR ' || rb_die $RB_E_FAIL "the box did not list the read's folder"
# 7e. THE EVIDENCE OF THE ONE CALL (fix-a2e213: verify-a2e213's finding 2), from the call above, before any other call: never a gate
EV="$RB_OUT/e213-a2-evidence-B"
evrc=$(rb_val '^A2-EVIDENCE-RC ([0-9]+)$')
evline=$(grep -m1 '^A2-EVIDENCE: ' "$RB_CAP" | cut -c1-400)
if [ "$evrc" = 0 ] && [ -n "$evline" ]; then
  mkdir -p "$EV"
  sed -n 's/^A2-LEDGER //p' "$RB_CAP" > "$EV/fwgate-ledger-aifoundry1-c1-this-boot.jsonl"
  sed -n 's/^A2-ATTEMPT //p' "$RB_CAP" > "$EV/a2-fwgate-attempts-aifoundry1-c1-this-boot.jsonl"
  ( cd "$EV" && sha256sum fwgate-ledger-aifoundry1-c1-this-boot.jsonl a2-fwgate-attempts-aifoundry1-c1-this-boot.jsonl ) > "$EV.sha256"
  evnote="evidence: ${evline#A2-EVIDENCE: } (RB_OUT/e213-a2-evidence-B/)"
else
  evnote="evidence NOT CAPTURED by this call (exit ${evrc:-none}: ${evline:-no A2-EVIDENCE line}): fwgate's ledger and the kit's attempt log stay on the box$( [ -s "$EV.sha256" ] && echo '; an earlier capture kept in RB_OUT')"
fi
echo "$(date '+%F %T %Z') step=$RB_STEP A2-EVIDENCE-B: $evnote" >> "$RB_LOG"
CP="$RB_OUT/e213-a2-fwgate-B"
if rb_has '^A2-DIR none$'; then
  [ "$lrc" = 0 ] || rb_die $RB_E_GATE "fwgate's read reported EQUAL but its folder $FWDIR is not on the box"
  note="no read made on this boot (continuity): nothing to copy back"
else
  sed -nE 's/^A2-SUM ([0-9a-f]{64})  \.\/(.*)$/\1  \2/p' "$RB_CAP" > "$RB_OUT/e213-a2-fwgate-B.sha256"
  nl=$(grep -c . "$RB_OUT/e213-a2-fwgate-B.sha256"); nb=$(rb_val '^A2-DIR ([0-9]+) files$')
  [ "$nl" -gt 0 ] && [ "$nl" = "$nb" ] || rb_die $RB_E_FAIL "the box's list of the read's folder is not whole ($nl of ${nb:-?} lines)"
  grep -E '^BOXHOME /' "$RB_CAP" | sed 's/^BOXHOME //' | awk '!seen[$0]++' > "$RB_OUT/box-home-B-a2.txt"
  [ -s "$RB_OUT/box-home-B-a2.txt" ] || rb_die $RB_E_FAIL "the box's home path did not come back: the scrub cannot be checked"
  mkdir -p "$CP"
  rb_probe "$BOX"
  rb_local copy "$BOX" "the read's folder, copied from the box (read-only there)" rsync -a -e "$RB_RSH" "$BOX:$(rb_tree "$BOX")/$FWDIR/" "$CP/"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy of the read's folder exited $RB_RC: run this step again (the look will read CONTINUITY: no second read)"
  RB_CWD="$CP" rb_local read local "the copy of the read's folder against the box's sha256" sha256sum -c "$RB_OUT/e213-a2-fwgate-B.sha256"
  nc=$(find "$CP" -type f | wc -l | tr -d ' ')
  { [ "$RB_RC" -eq 0 ] && [ "$(grep -c ': OK$' "$RB_CAP")" = "$nl" ] && [ "$nc" = "$nl" ]; } ||
    rb_die $RB_E_GATE "the copy of the read's folder is not exact ($nc files here, $nl on the box): no session today until it is"
  rb_local desk local "THE SCRUB CHECK on the read's folder (collect_e213.py scrub-check, unchanged)" /usr/bin/python3 -B tools/claims-v3/e213/collect_e213.py \
    scrub-check "$CP" "$RB_OUT/box-home-B-a2.txt" "$RB_OUT/box-login-$BOX.txt"
  rb_has '^SCRUB-CHECK CLEAN' || rb_die $RB_E_GATE "the scrub check refused the read's folder ($(grep -m1 '^SCRUB-CHECK' "$RB_CAP" | cut -c1-200)): its record could not be committed after the session: no session today; a kit note first"
  note="the read's folder copied back exact ($nl files in RB_OUT/e213-a2-fwgate-B/), SCRUB-CHECK CLEAN"
fi
echo "$(date '+%F %T %Z') A2-LOOK-B: $verdict; $note; FWDIR $FWDIR; $evnote" > "$RB_OUT/e213-a2-look-B.txt"
echo "$(date '+%F %T %Z') step=$RB_STEP A2-LOOK-B: $verdict; $note" >> "$RB_LOG"
rb_say "aifoundry1 FREE (k6's holder rule) and card 1's firmware identity shown on this boot (Amendment A2): $verdict; $note; $evnote"
exit 0
