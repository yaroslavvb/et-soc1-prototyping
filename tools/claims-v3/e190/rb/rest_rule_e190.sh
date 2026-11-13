# E190 (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): THE REST RULE, the lines step 9 (rb/s11_session_e190.sh) sends to the
# arm's box before it launches E190 there. E189's rest rule (tools/claims-v3/e189/rb/rest_rule_e189.sh, E188 v2's) with E190's words and
# ONE change, marked "E190": the blocks' trees are read under the box's card names (build/claims-v3/<card>/<run>[-*]: aifoundry2;
# aifoundry1-c0 and aifoundry1-c1, both, so a session of ours on either card of aifoundry1 counts). Its reading, unchanged: no E190 session
# starts within 40 minutes of the end of our last real session on that box, read from every session log of ours in the box's tree,
# whatever its form:
#   build/eNNN/session.log            E178-E182 (and earlier kits)
#   build/eNNN/session-*.log          E183's session-t<T0>.log and E184's session-<arm>-t<T0>.log
#   build/eNNN/T<T0>/session.log      E185's, E186's, E188's and E189's T0-named directories, and E190's T<T0>-<arm>
#   build/eNNN/T<T0>/session-*.log   (any later kit's)
# A real block with no "session end" (a session whose shell died, or one cut mid-queue) is counted as ended at the LATEST of its last
# timestamped line, its log's last write (the log's final block only) and the latest write of any regular file of the same run outside
# the dry paths. Dry paths ("-dry" or "dry-t" in the path) are skipped; inside a log, a block that is dry by the kits' own markers (a line
# whose words begin "DRY " or "DRY:" or "DESK: ", a "session start" line ending " DRY" or "; DRY)") or that opened no device ("no device
# opened") is skipped. Over-reading a cut session's end only delays a launch. On aifoundry1 this makes E190's arm B wait 40 minutes after
# any session of ours there (E191's on card 1 among them); E190.md registers no rest rule: this is the kit's, stated before any datum
# (KIT.md section 4), so that "the card at rest" the forecast prices is a rested card.
# Prints "rest: <m> minutes since ...", or "rest: no real session of ours ...", or "REFUSED: <m> minutes since ..." and exits 3 (step 9
# then stops with 10, nothing launched). Run from the box's tree, under the prelude's set -u (BOX set); GNU date, find.
# SPDX-License-Identifier: Apache-2.0
case "$BOX" in aifoundry2) CARDS="aifoundry2" ;; aifoundry1) CARDS="aifoundry1-c0 aifoundry1-c1" ;; *) CARDS="$BOX" ;; esac   # E190
latest_write() {  # latest_write <run, e.g. e190>: the newest write (epoch seconds) of a regular file of that run's real paths, or nothing
  local d p="" c
  for d in "build/$1"; do [ -d "$d" ] && p="$p $d"; done
  for c in $CARDS; do for d in "build/claims-v3/$c/$1" build/claims-v3/"$c"/"$1"-*; do [ -d "$d" ] && p="$p $d"; done; done
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
if [ -n "$last" ]; then
  what="session end"; [ "$lastkind" = NOEND ] && what="last real session activity (no 'session end': the latest of its last line and its run's latest write)"
  [ "$lastkind" = NOEND ] && echo "note: $lastw's last real session block has no 'session end': counted as ended at $last"
  rest=$(( ($(date +%s) - lastt) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E190 starts on a rested card, at least 40 minutes after our last real session on $BOX (the kit's rest rule)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log or T*/session*.log on $BOX"
fi
