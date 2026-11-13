# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): THE REST RULE, the lines step 9 (rb/s11_a3_session_e189.sh) sends to
# aifoundry3 before it launches E189. It is E188's rest rule v2 (tools/claims-v3/e188/rb/rest_rule_e188_v2.sh, its kit's dated note 1,
# 16b41cf2) line for line but its words (E189 for E188) and ONE addition, marked "E189": energy.sh's output folders, the form sparse
# parity's card runs of 29 Sep wrote (build/sparseparity-energy/<host>-<preset>-<time>/, its energy.log carrying clock times only), read in
# every tree of ours on the box (~/aifoundry, ~/nekko, ~/claude/et-soc1-prototyping): such a run ends at its folder's latest file write;
# "-dry" folders are skipped (energy.sh --dry names them so). E188 v2's reading, unchanged: no E189 session starts within 40 minutes of the
# end of our last real session on the card (E189.md section 13: "E189's first card command at least 40 minutes after E183's session end
# (or after that run's latest file write, if it ended without 'session end')"), read from every session log of ours on the box, whatever
# its form:
#   build/eNNN/session.log            E178, E180, E181, E182 (and earlier kits)
#   build/eNNN/session-*.log          E183's session-t<T0>.log (its kit note 4) and E184's session-<arm>-t<T0>.log
#   build/eNNN/T<T0>/session.log      E185's, E186's, E188's and E189's T0-named directories
#   build/eNNN/T<T0>/session-*.log   (any later kit's)
# A real block with no "session end" (a session whose shell died, or one cut mid-queue) is counted as ended at the LATEST of its last
# timestamped line, its log's last write (the log's final block only) and the latest write of any regular file of the same run outside
# the dry paths, under build/<run>/ (its session directories, queue.out, its passes) and under build/claims-v3/aifoundry3/<run>[-*] (the
# blocks' trees). Dry paths ("-dry" or "dry-t" in the path) are skipped; inside a log, a block that is dry by the kits' own markers (a line
# whose words begin "DRY " or "DRY:" or "DESK: ", a "session start" line ending " DRY" or "; DRY)") or that opened no device ("no device
# opened") is skipped. Over-reading a cut session's end only delays a launch. On a day E183 also runs, E189 runs after it, so this rule
# makes E189 wait 40 minutes after E183's end.
# Prints "rest: <m> minutes since E<run>'s session end (<time>; ...)", or "rest: no real session of ours ...", or "REFUSED: <m> minutes
# since ..." and exits 3 (step 9 then stops with 10, nothing launched). Run from the box's tree, under the prelude's set -u; GNU date, find.
# Its desk test: rb/selftest_rest_e189.sh (a case for each form: E184's, E185's, E186's, E183's, E188's, E189's and energy.sh's; cut
# sessions; dry markers; a shared day).
# SPDX-License-Identifier: Apache-2.0
latest_write() {  # latest_write <run, e.g. e189>: the newest write (epoch seconds) of a regular file of that run's real paths, or nothing
  local d p=""
  for d in "build/$1" "build/claims-v3/aifoundry3/$1" build/claims-v3/aifoundry3/"$1"-*; do [ -d "$d" ] && p="$p $d"; done
  [ -n "$p" ] || return 0
  find $p -type f ! -path '*-dry*' ! -path '*dry-t*' 2>/dev/null | while IFS= read -r f; do date -r "$f" +%s 2>/dev/null; done | sort -n | tail -n 1
}
last=""; lastw=""; lastt=0; lastkind=""
for L in build/e[0-9]*/session.log build/e[0-9]*/session-*.log build/e[0-9]*/T[0-9]*/session.log build/e[0-9]*/T[0-9]*/session-*.log; do
  [ -f "$L" ] || continue
  case "$L" in *-dry*|*dry-t*) continue ;; esac
  w=$(echo "$L" | cut -d/ -f2)
  mt=$(date -r "$L" +%s 2>/dev/null || echo 0)
  ends=$(awk '
    function flush(final) {
      if (inblk && !dry && !nodev) {
        if (endts != "") print "END 0 " endts
        else if (lastts != "") print "NOEND " final " " lastts
      }
    }
    { m = $0; sub(/^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [A-Z][A-Z]* /, "", m) }
    /session start/ { flush(0); inblk = 1; dry = 0; nodev = 0; endts = ""; lastts = "" }
    inblk && (m ~ /^DRY[ :]/ || m ~ /^DESK: / || (m ~ /^session start/ && m ~ /( DRY|; DRY\))$/)) { dry = 1 }
    inblk && /no device opened/ { nodev = 1 }
    inblk && /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [A-Z][A-Z]* / { lastts = $1 " " $2 " " $3 }
    inblk && /session end( \(T0 [0-9]+\))?$/ && $0 !~ /DRY session end/ { endts = $1 " " $2 " " $3 }
    END { flush(1) }' "$L" 2>/dev/null)
  while read -r kind fin d1 d2 d3; do
    [ -n "$kind" ] || continue
    t=$(date -d "$d1 $d2 $d3" +%s 2>/dev/null) || continue
    ts="$d1 $d2 $d3"
    if [ "$kind" = NOEND ] && [ "$fin" = 1 ] && [ "$mt" -gt "$t" ]; then t=$mt; ts="$(date -d @"$mt" '+%F %T %Z') (the log's last write)"; fi
    if [ "$kind" = NOEND ]; then
      lw=$(latest_write "$w")
      case "$lw" in ''|*[!0-9]*) lw=0 ;; esac
      if [ "$lw" -gt "$t" ]; then t=$lw; ts="$(date -d @"$lw" '+%F %T %Z') (the latest write of E${w#e}'s files outside the dry paths)"; fi
    fi
    if [ -z "$last" ] || [ "$t" -gt "$lastt" ]; then last=$ts; lastt=$t; lastw=E${w#e}; lastkind=$kind; fi
  done <<< "$ends"
done
for T in "$HOME/aifoundry" "$HOME/nekko" "$HOME/claude/et-soc1-prototyping"; do                                   # E189: energy.sh's form
  for F in "$T"/build/sparseparity-energy/*/; do
    [ -d "$F" ] || continue
    case "$F" in *-dry/|*-dry*) continue ;; esac
    lw=$(find "$F" -type f 2>/dev/null | while IFS= read -r f; do date -r "$f" +%s 2>/dev/null; done | sort -n | tail -n 1)
    case "$lw" in ''|*[!0-9]*) continue ;; esac
    if [ -z "$last" ] || [ "$lw" -gt "$lastt" ]; then
      last="$(date -d @"$lw" '+%F %T %Z') (the latest write of an energy.sh run's folder, $(basename "$F"))"; lastt=$lw; lastw="energy.sh"; lastkind=ENERGY
    fi
  done
done
if [ -n "$last" ]; then
  what="session end"; [ "$lastkind" = NOEND ] && what="last real session activity (no 'session end': the latest of its last line and its run's latest write)"
  [ "$lastkind" = ENERGY ] && what="run"
  [ "$lastkind" = NOEND ] && echo "note: $lastw's last real session block has no 'session end': counted as ended at $last"
  rest=$(( ($(date +%s) - lastt) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E189 starts on a rested card, at least 40 minutes after our last real session there (E189.md section 13; the kit)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log, T*/session*.log or energy.sh's folders"
fi
