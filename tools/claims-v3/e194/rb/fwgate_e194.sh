#!/usr/bin/env bash
# E194, dated amendment A1 (Q187, Sun 15 Nov 2026, before any E194 datum): E194's OWN FIRMWARE GATE. It takes the place, for E194's look
# (rb/s05_look_e194_v2.sh) and launch (rb/s11_session_e194_v2.sh), of k6's identity-by-continuity rule for aifoundry2 (k6's rb_guard_text:
# "booted before E69's firmware read of record, 2026-10-27 13:56:26 PDT"), which stays as committed in k6's file, as do the v1 look and
# launch. The gate PASSES ONLY WHEN BOTH HOLD:
#   (1) THE RECORD (read on the desk, in the lab clone the step runs from, RB_REPO): fwread-e194's firmware read of aifoundry2 card 0,
#       committed in 15cb0fcb (docs/reports/data/2026-11-15-e194-fwread-aifoundry2/; read 2026-11-15 15:22:02.877 PST, one
#       DM_CMD_GET_MODULE_FIRMWARE_REVISIONS query, rc 0), is there AS COMMITTED and reads EQUAL to E69's read of record in all seven
#       fields. Each of these must hold, and every one that fails is named:
#         - the directory and its ten files are there; its own list SHA256SUMS reads 8 of 8 OK and has its pinned bytes; README.md has
#           its pinned bytes; host aifoundry2 in its etiquette read;
#         - 15cb0fcb is an ancestor of HEAD, the directory's tree at HEAD is 15cb0fcb's (6d1c3802...), nothing uncommitted in it;
#         - E69's two statements of its read (tools/claims-v3/knob/CHANGE-RECORD.md lines 67-69, E69's data README lines 209-210) have
#           their pinned bytes;
#         - the record's own comparison, re-run from the top (compare_fwread.py, /usr/bin/python3 -I -B), exits 0, prints
#           "VERDICT: EQUAL" and reproduces comparison.txt byte for byte;
#         - THE GATE'S OWN READING, independent of that script: the raw output (fwread.stdout and fwread.stderr) holds one command line
#           (code 14), one "Service request succeeded" and exactly one line per field, each EQUAL to E69's value pinned below; the meta
#           reads rc 0, card 0 (-n 0) under card 0's lock, and the read's start at the pinned epoch.
#   (2) THE BOOT (read on the box, aifoundry2, inside the step's own box call): the box booted (uptime -s) STRICTLY BEFORE that read's
#       start, 2026-11-15 15:22:02 PST (epoch 1794784922, the read's 15:22:02.877 floored to the second), so the card has not restarted
#       since the read that showed its firmware. A boot at or after that second, an unreadable boot, or a box that is not aifoundry2: STOP.
# Reads only: git, sha256sum, the record's files, /usr/bin/python3 on the record's own comparison, and uptime. No device is opened, no
# card command is sent, nothing is written. The firmware-revisions query is never sent here: the gate reads the committed read.
# Sourced (after rb/rb_e194.sh) by the v2 look, launch and step 2; also run by itself:
#   bash tools/claims-v3/e194/rb/fwgate_e194.sh record [<lab clone top>]  the record (1): "FWGATE-E194 RECORD EQUAL ..." 0, or
#                                                                          "FWGATE-E194 RECORD REFUSED: <every reason>" 16
#   bash tools/claims-v3/e194/rb/fwgate_e194.sh boot '<YYYY-MM-DD HH:MM:SS>'  the boot rule (2) on a given boot time, by the very lines
#                                                                          the box runs (uptime stood in): 0 ok, 16 STOP
#   bash tools/claims-v3/e194/rb/fwgate_e194.sh text look|launch          print the box lines (the look's form; the launch's form)
# Exit codes (k6's): 0 passes; 16 the gate says stop; 10 a usage error.
# SPDX-License-Identifier: Apache-2.0

E194_FW_DIR=docs/reports/data/2026-11-15-e194-fwread-aifoundry2
E194_FW_COMMIT=15cb0fcbfb118aac10d09b6a2eca674a838edf9e          # fwread-e194's data commit (pushed 17:11:59 PST Sun 15 Nov 2026)
E194_FW_TREE=6d1c38022ef013c16727e0ea6ff5d092c881d8c4            # its directory's tree in that commit
E194_FW_SUMS_SHA=daa088c8af935923ca3fb8654f84eee9b4f9311462b48484560928af4ee6772c   # its SHA256SUMS (8 entries)
E194_FW_README_SHA=96fb19c558c20eb0c5070aaaf6716832718aa459e560028013082b0af07374e2 # its README.md
E194_FW_FILES="README.md SHA256SUMS compare_fwread.py comparison.txt etiquette-after.txt etiquette-before.txt fwread.meta.txt fwread.stderr fwread.stdout kernel-log-after.txt"
E194_FW_EPOCH=1794784922                                          # the read's start, 2026-11-15 15:22:02.877 PST, floored
E194_FW_AT='2026-11-15 15:22:02 PST'
E194_E69_CR=tools/claims-v3/knob/CHANGE-RECORD.md
E194_E69_CR_SHA=7faefb6a255cf8dd3edc0f6787831f84404b4bb8f38734cd5926a58482e96637
E194_E69_RM=docs/reports/data/2026-10-27-e69-governor-knob/README.md
E194_E69_RM_SHA=934919a116f79161a35027eb2f77fee57e9ead56e8ffc93a584c7d900e8c10ef
# E69's read of record (Tue 27 Oct 2026 13:56:26 PDT), as its two statements give it: the tool's label | the short name | the value
E194_E69_FIELDS="Firmware release revision|release|1.4.0
BL1 Firmware versions|BL1|0.22.0
BL2 Firmware versions|BL2|0.22.0
PMIC Firmware versions|PMIC|1.5.0
Master Minion Firmware versions|Master Minion|0.25.1
Worker Minion versions|Worker Minion|0.25.1
Machine Minion versions|Machine Minion|0.25.1"

e194_fwgate_record() {  # e194_fwgate_record [<lab clone top>]: the record (1); prints its lines; 0 EQUAL, 16 REFUSED
  local top=${1:-${RB_REPO:-.}} d f n m h t s rc out raw label short want vals bad="" fields=""
  d="$top/$E194_FW_DIR"
  echo "FWGATE-E194 the record: $E194_FW_DIR (fwread-e194's data commit ${E194_FW_COMMIT:0:12}, the read at $E194_FW_AT); E69's statements: $E194_E69_CR lines 67-69, $E194_E69_RM lines 209-210"
  if [ ! -d "$d" ]; then
    bad="$bad missing(the record's directory $E194_FW_DIR is not there)"
  else
    for f in $E194_FW_FILES; do [ -f "$d/$f" ] || bad="$bad missing($f)"; done
  fi
  if [ -z "$bad" ]; then
    n=$(cd "$d" && sha256sum -c SHA256SUMS 2> /dev/null | grep -c ': OK$'); m=$(grep -c . "$d/SHA256SUMS")
    { [ "$n" = 8 ] && [ "$m" = 8 ]; } || bad="$bad list(SHA256SUMS $n OK of $m; pinned 8 of 8)"
    h=$(sha256sum "$d/SHA256SUMS" | cut -d' ' -f1); [ "$h" = "$E194_FW_SUMS_SHA" ] || bad="$bad list-bytes(SHA256SUMS ${h:0:8}, pinned ${E194_FW_SUMS_SHA:0:8})"
    t=$(sha256sum "$d/README.md" | cut -d' ' -f1); [ "$t" = "$E194_FW_README_SHA" ] || bad="$bad readme-bytes(README.md ${t:0:8}, pinned ${E194_FW_README_SHA:0:8})"
    grep -q '^host: aifoundry2;' "$d/etiquette-before.txt" || bad="$bad host(the etiquette read does not name aifoundry2)"
    echo "FWGATE-E194   its list: $n of $m OK; SHA256SUMS sha256 ${h:0:12}, README.md sha256 ${t:0:12} (pinned ${E194_FW_SUMS_SHA:0:12}, ${E194_FW_README_SHA:0:12})"
    if git -C "$top" rev-parse --git-dir > /dev/null 2>&1; then
      git -C "$top" merge-base --is-ancestor "$E194_FW_COMMIT" HEAD 2> /dev/null || bad="$bad commit(${E194_FW_COMMIT:0:12} is not an ancestor of HEAD)"
      t=$(git -C "$top" rev-parse "HEAD:$E194_FW_DIR" 2> /dev/null); [ "$t" = "$E194_FW_TREE" ] || bad="$bad tree(HEAD's tree for the record ${t:0:12}, not ${E194_FW_TREE:0:12} as committed)"
      s=$(git -C "$top" status --porcelain --untracked-files=all -- "$E194_FW_DIR" 2> /dev/null | grep -c .)
      [ "$s" -eq 0 ] || bad="$bad uncommitted($s path(s) in the record's directory)"
      echo "FWGATE-E194   git: HEAD $(git -C "$top" rev-parse --short=12 HEAD 2> /dev/null), the record's tree ${t:0:12}, uncommitted paths there $s"
    else
      bad="$bad git($top is not a git checkout)"
    fi
    h=$(sha256sum "$top/$E194_E69_CR" 2> /dev/null | cut -d' ' -f1); [ "$h" = "$E194_E69_CR_SHA" ] || bad="$bad e69-change-record(${h:0:8}, pinned ${E194_E69_CR_SHA:0:8})"
    h=$(sha256sum "$top/$E194_E69_RM" 2> /dev/null | cut -d' ' -f1); [ "$h" = "$E194_E69_RM_SHA" ] || bad="$bad e69-readme(${h:0:8}, pinned ${E194_E69_RM_SHA:0:8})"
    out=$(cd "$top" && /usr/bin/python3 -I -B "$E194_FW_DIR/compare_fwread.py" "$E194_FW_DIR" 2>&1); rc=$?
    [ "$rc" -eq 0 ] || bad="$bad compare(rc $rc)"
    printf '%s\n' "$out" | grep -qx 'VERDICT: EQUAL' || bad="$bad compare-verdict($(printf '%s\n' "$out" | grep -m1 -E '^(VERDICT|PARSE-FAILED)' | cut -c1-80))"
    if (cd "$top" && /usr/bin/python3 -I -B "$E194_FW_DIR/compare_fwread.py" "$E194_FW_DIR" 2> /dev/null) | cmp -s - "$d/comparison.txt"; then :; else
      bad="$bad compare-bytes(the re-run does not reproduce comparison.txt)"
    fi
    echo "FWGATE-E194   the record's comparison re-run: rc $rc, $(printf '%s\n' "$out" | grep -m1 -E '^(VERDICT|PARSE-FAILED)')"
    raw=$(cat "$d/fwread.stdout" "$d/fwread.stderr" | LC_ALL=C sed 's/\x1b\[[0-9;]*m//g')
    n=$(printf '%s\n' "$raw" | grep -cE 'command: DM_CMD_GET_MODULE_FIRMWARE_REVISIONS code 14$')
    [ "$n" -eq 1 ] || bad="$bad own-reading(command lines $n, want 1)"
    n=$(printf '%s\n' "$raw" | grep -cE 'Service request succeeded$')
    [ "$n" -eq 1 ] || bad="$bad own-reading(succeeded lines $n, want 1)"
    while IFS='|' read -r label short want; do
      [ -n "$label" ] || continue
      vals=$(printf '%s\n' "$raw" | LC_ALL=C sed -nE "s/^.*\]: $label: Major: ([0-9]+) Minor: ([0-9]+) Revision: ([0-9]+)$/\1.\2.\3/p")
      n=$(printf '%s' "$vals" | grep -c .)
      if [ "$n" -ne 1 ]; then bad="$bad own-reading($short: $n lines, want 1)"
      elif [ "$vals" != "$want" ]; then bad="$bad DIFFERENT($short reads $vals, E69's $want)"; fields="$fields $short=$vals"
      else fields="$fields $short=$vals"; fi
    done <<EOF
$E194_E69_FIELDS
EOF
    echo "FWGATE-E194   the gate's own reading of the raw output:$fields (E69's: release 1.4.0, BL1 0.22.0, BL2 0.22.0, PMIC 1.5.0, minions 0.25.1)"
    grep -qx 'rc 0' "$d/fwread.meta.txt" || bad="$bad meta(the read's rc is not 0)"
    grep -qE '^argv: .*/run/lock/etsoc-shire0\.lock .* -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 ' "$d/fwread.meta.txt" || bad="$bad meta(not card 0 under card 0's lock)"
    t=$(sed -nE 's/^start .*\(epoch ([0-9]+)\.[0-9]+\)$/\1/p' "$d/fwread.meta.txt" | head -n 1)
    [ "$t" = "$E194_FW_EPOCH" ] || bad="$bad meta(the read's start epoch ${t:-none}, pinned $E194_FW_EPOCH)"
  fi
  if [ -n "$bad" ]; then
    echo "FWGATE-E194 RECORD REFUSED:$bad"
    return 16
  fi
  echo "FWGATE-E194 RECORD EQUAL: the firmware read of record of aifoundry2 card 0 ($E194_FW_AT, ${E194_FW_COMMIT:0:12}) is there as committed and reads EQUAL to E69's in all seven fields (its comparison re-run and the gate's own reading)"
  return 0
}

e194_fwgate_text() {  # e194_fwgate_text look|launch: the box lines of the boot rule (2), for the box script after k6's prelude (BOX set)
  echo "FWREAD_EPOCH=$E194_FW_EPOCH; FWREAD_AT='$E194_FW_AT'   # E194's firmware read of record (E194.md A1; fwread-e194, ${E194_FW_COMMIT:0:12}): EQUAL to E69's"
  cat <<'EOF'
BOOTED=$(uptime -s 2>/dev/null); boot=$(date -d "$BOOTED" +%s 2>/dev/null); FWOK=0
case "$boot" in ''|*[!0-9]*) ;; *) [ "$BOX" = aifoundry2 ] && [ -n "$BOOTED" ] && [ "$boot" -lt "$FWREAD_EPOCH" ] && FWOK=1 ;; esac
EOF
  case "$1" in
    look) cat <<'EOF'
if [ "$FWOK" = 1 ]; then echo "identity: the host booted $BOOTED, before E194's firmware read of record of $FWREAD_AT (EQUAL to E69's; E194.md A1): ok"
else echo "identity: the host $BOX booted '$BOOTED', NOT before E194's firmware read of record of $FWREAD_AT (E194.md A1): STOP"; fi
EOF
      ;;
    launch) cat <<'EOF'
if [ "$FWOK" != 1 ]; then
  echo "IDENTITY-STOP: $BOX booted '$BOOTED', not before E194's firmware read of record of $FWREAD_AT (E194.md A1): its firmware identity is not carried by that read: nothing launched"; exit 3
fi
echo "identity: $BOX booted $BOOTED, before E194's firmware read of record of $FWREAD_AT (EQUAL to E69's; E194.md A1): ok"
EOF
      ;;
    *) echo "echo 'REFUSED: e194_fwgate_text needs look or launch'; exit 3" ;;
  esac
}

e194_guard_text_a1() {  # the remote lines E194's v2 launch starts with: k6's rb_guard_text's first three lines, verbatim (never during
  #                     a dry pass, never beside another session of ours), then E194's boot rule (2) in place of k6's firmware block
  cat <<'EOF'
mkdir -p build/q141k/jobs
if [ "$(jobs_live)" -gt 0 ]; then echo "REFUSED: a dry pass of the runbook still runs on $BOX (no session during a dry pass)"; exit 3; fi
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours already runs on $BOX (one at a time)"; exit 3; fi
EOF
  e194_fwgate_text launch
}

e194_fwgate_desk() {  # e194_fwgate_desk: inside a v2 step (rb_e194.sh sourced, rb_init run): the record (1) on the desk through k6's
  #                   bounded runner, before any box call; 16 and nothing reaches the box unless it reads EQUAL
  rb_local read local "E194's firmware gate, the record: fwread-e194's read of aifoundry2 card 0 as committed, EQUAL to E69's (E194.md A1)" \
    bash "$RB_E194_DIR/fwgate_e194.sh" record "$RB_REPO"
  [ -n "${RB_DRY:-}" ] && return 0
  rb_has '^FWGATE-E194 RECORD EQUAL: ' && return 0
  rb_die $RB_E_GATE "E194's firmware gate refuses (E194.md A1): $(grep -m1 '^FWGATE-E194 RECORD REFUSED' "$RB_CAP" 2> /dev/null || echo 'no reading'): nothing reaches the box"
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  set -u
  case "${1:-}" in
    record) e194_fwgate_record "${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"; exit $? ;;
    boot)
      [ -n "${2:-}" ] || { echo "usage: fwgate_e194.sh boot '<YYYY-MM-DD HH:MM:SS>'"; exit 10; }
      FWGATE_BOOT=$2; BOX=${3:-aifoundry2}
      uptime() { [ "${1:-}" = -s ] && printf '%s\n' "$FWGATE_BOOT"; }   # the box's `uptime -s`, stood in by the given time
      eval "$(e194_fwgate_text look)"
      [ "$FWOK" = 1 ] && exit 0
      exit 16 ;;
    text)
      case "${2:-}" in look|launch) e194_fwgate_text "$2"; exit 0 ;; *) echo "usage: fwgate_e194.sh text look|launch"; exit 10 ;; esac ;;
    *) echo "usage: fwgate_e194.sh record [<lab clone top>] | boot '<YYYY-MM-DD HH:MM:SS>' [<box>] | text look|launch"; exit 10 ;;
  esac
fi
