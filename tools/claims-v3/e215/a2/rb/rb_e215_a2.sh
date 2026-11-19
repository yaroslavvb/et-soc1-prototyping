# E215's arm B in E213's Amendment A2 form (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum; E213's A2 by Q219's lane a2-e213, landed 8b675547, run by card-e213b2 on Wed 18 Nov 2026): the part A2's runbook steps source (bash 3.2 or later;
# the desk is aifoundry2). It sources E215's runbook file, tools/claims-v3/e215/rb/rb_e215.sh, UNCHANGED (and through it k6's rb_common.sh,
# unchanged: the bounded runner, the probe, the login-link stop, the prelude, the holder rule, the exit codes), and adds only:
#   - e215a2_only_B: A2 is ARM B's alone (aifoundry1 card 1); arm A keeps the kit's steps as landed (a call for arm A is refused, 10);
#   - e215a2_dir: the box folder fwgate's one read writes into, build/e215/fwgate-B-<the window's day> in the box's tree (nekko): E215's own box
#     folder, which THE REST RULE's activity floor leaves out and whose session-log patterns it never matches;
#   - THE PINS: fwgate.py (landed d5beec9b) and its six records, and A2's box helper fwgate_e215a2.py, each at its sha256 below. e215a2_check_desk
#     reads them in the lab clone (committed, unmodified, at their sha256) before anything is synced; e215a2_pins_box_text checks the same list in
#     the box's tree (step 4, after the sync), and the launch guard checks it again before fwgate's guard;
#   - e215a2_guard_text: THE LAUNCH GUARD of A2's step 9, in place of k6's rb_guard_text: k6's first lines verbatim (no session during a dry pass of
#     the runbook, none beside another session of ours), then the pins on the box, then `fwgate.py guard --box aifoundry1 --card 1 --extra
#     <the read's folder>`: "identity: ... ok" (exit 0) or IDENTITY-STOP and nothing launched - in place of k6's identity by continuity, which
#     passes only a boot before E82's firmware read of 2026-10-31 13:45:24 PDT.
# Exit codes: k6's (0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate
# says stop; 17 call again).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../../rb/rb_e215.sh"
RB_E215A2_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
E215A2_HELPER=tools/claims-v3/e215/a2/fwgate_e215a2.py
E215A2_BOXFILES="tools/claims-v3/fwgate/fwgate.py tools/claims-v3/fwgate/records/aifoundry1-c0-2026-10-31-e84.json tools/claims-v3/fwgate/records/aifoundry1-c0-2026-11-01-e114.json tools/claims-v3/fwgate/records/aifoundry1-c1-2026-10-31-e82.json tools/claims-v3/fwgate/records/aifoundry2-c0-2026-10-27-e69.json tools/claims-v3/fwgate/records/aifoundry2-c0-2026-10-27-e72.json tools/claims-v3/fwgate/records/aifoundry3-c0-2026-10-31-e79.json $E215A2_HELPER"

e215a2_pins_text() {  # the pinned list, in sha256sum's form (fwgate as landed in d5beec9b; the helper as A2 commits it)
  cat <<'EOF'
4d529a5764a97373f451544821f0432ce31d6afaecad0f1e254d18d76e736b95  tools/claims-v3/fwgate/fwgate.py
6651036f0f5de5615a1bbdd203f428a206abab47d848548977807e3ad50b8186  tools/claims-v3/fwgate/records/aifoundry1-c0-2026-10-31-e84.json
4b8a87c12f59a822b71f6e4608938cce145e4b69fb6a8731da00259f63111e7f  tools/claims-v3/fwgate/records/aifoundry1-c0-2026-11-01-e114.json
2742a9cd6c27e8e39e82232dd07be4c0c5f120ad998a36f8dc91706448e0a150  tools/claims-v3/fwgate/records/aifoundry1-c1-2026-10-31-e82.json
f912b7ebc39c3cf0079acdd690236d3785867c524a9022349437328cba507460  tools/claims-v3/fwgate/records/aifoundry2-c0-2026-10-27-e69.json
91fbdfe0626bfe9dba26ee5532c26316840ed0dc0e1fde6026ccfd0f5ed1092a  tools/claims-v3/fwgate/records/aifoundry2-c0-2026-10-27-e72.json
77d13228feeb49ef5e95cc1daa15ab439318520567ffac9106e0576cbb1e4783  tools/claims-v3/fwgate/records/aifoundry3-c0-2026-10-31-e79.json
c8080292859a5fb2617815d3fd69f51a266385f7161915fabc5b20721e3b920e  tools/claims-v3/e215/a2/fwgate_e215a2.py
EOF
}

e215a2_only_B() {  # A2 is arm B's alone
  [ "${ARM:-}" = B ] || rb_die $RB_E_USAGE "Amendment A2 is E215 arm B's alone (aifoundry1 card 1); arm A runs the kit's own steps as landed"
}

e215a2_dir() {  # the read's folder in the box's tree, by the window's day (e215_window has set RB_DAY to today)
  echo "build/e215/fwgate-B-${RB_DAY:-DAY}"
}

e215a2_check_desk() {  # the pins in the lab clone: the box files committed and unmodified, each at its sha256; else 16, nothing synced or read
  rb_local read local "A2's box files unmodified in the lab clone (fwgate.py, its six records, A2's helper)" git -C "$RB_REPO" status --short --untracked-files=all $E215A2_BOXFILES
  [ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "A2's box files have uncommitted changes in the lab clone: nothing is synced or read"
  local f="$RB_OUT/e215-a2-pins.txt"
  e215a2_pins_text > "$f"
  RB_CWD="$RB_REPO" rb_local read local "A2's box files at their pinned sha256 in the lab clone" sha256sum -c "$f"
  [ -n "${RB_DRY:-}" ] && return 0
  [ "$RB_RC" -eq 0 ] && [ "$(grep -c ': OK$' "$RB_CAP")" -eq "$(grep -c . "$f")" ] ||
    rb_die $RB_E_GATE "A2's box files are not at their pinned sha256 in the lab clone (the lines above): nothing is synced or read"
  return 0
}

e215a2_pins_box_text() {  # the remote lines that check the pinned list in the box's tree: "A2-PINS OK <n> of <n>", else "A2-PINS FAILED: ..." (exit 3)
  echo "mkdir -p build/e215"
  echo "cat > build/e215/a2-pins.sha256 <<'A2PINS'"
  e215a2_pins_text
  echo "A2PINS"
  cat <<'EOF'
pins=$(sha256sum -c build/e215/a2-pins.sha256 2>&1); prc=$?
nok=$(printf '%s\n' "$pins" | grep -c ': OK$'); nall=$(grep -c . build/e215/a2-pins.sha256)
if [ "$prc" -ne 0 ] || [ "$nok" -ne "$nall" ]; then
  echo "A2-PINS FAILED: $(printf '%s\n' "$pins" | grep -v ': OK$' | head -n 3 | tr '\n' ';' | cut -c1-300)"; exit 3
fi
echo "A2-PINS OK $nok of $nall"
EOF
}

e215a2_guard_text() {  # A2's launch guard (step 9), in place of k6's rb_guard_text; FWDIR is set before these lines
  cat <<'EOF'
mkdir -p build/q141k/jobs
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: a dry pass of the runbook still runs on $BOX (no session during a dry pass)"; exit 3; fi
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours already runs on $BOX (one at a time)"; exit 3; fi
EOF
  echo "mkdir -p build/e215"
  echo "cat > build/e215/a2-pins.sha256 <<'A2PINS'"
  e215a2_pins_text
  echo "A2PINS"
  cat <<'EOF'
pins=$(sha256sum -c build/e215/a2-pins.sha256 2>&1); prc=$?
nok=$(printf '%s\n' "$pins" | grep -c ': OK$'); nall=$(grep -c . build/e215/a2-pins.sha256)
if [ "$prc" -ne 0 ] || [ "$nok" -ne "$nall" ]; then
  echo "IDENTITY-STOP: A2's box files are not at their pinned sha256 on $BOX ($(printf '%s\n' "$pins" | grep -v ': OK$' | head -n 2 | tr '\n' ';' | cut -c1-200)): fwgate's guard cannot be read: nothing launched"
  exit 3
fi
echo "A2-PINS OK $nok of $nall"
fg=$(python3 -I -B tools/claims-v3/fwgate/fwgate.py guard --box "$BOX" --card 1 --extra "$FWDIR" 2>&1); fgr=$?
printf '%s\n' "$fg" | sed 's/^/  | /'
if [ "$fgr" -ne 0 ] || ! printf '%s\n' "$fg" | grep -q '^identity: .*: ok$'; then
  if printf '%s\n' "$fg" | grep -q '^IDENTITY-STOP'; then printf '%s\n' "$fg" | grep '^IDENTITY-STOP' | head -n 1
  else echo "IDENTITY-STOP: fwgate's guard exited $fgr without its identity line: nothing launched"; fi
  exit 3
fi
printf '%s\n' "$fg" | grep '^identity: .*: ok$' | head -n 1
echo "A2-GUARD: fwgate's guard shows the firmware identity on this boot (Amendment A2): ok"
EOF
}
