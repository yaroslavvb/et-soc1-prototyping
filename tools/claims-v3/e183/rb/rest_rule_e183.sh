# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): THE REST RULE, the lines step 9 v2
# (rb/s11_a3_session_e183_v2.sh) sends to aifoundry3 before it launches a session: no E183 session starts within 40 minutes of the end of
# our last real session on the card, read from every session log of ours on the box, whatever its form. Until this note E183's launch step
# had no rest rule of its own (k6's guard refuses only beside a LIVE session of ours; CARD-LANE-BRIEF.md section 2 item 2 says so), so it
# read no session log at all. The rule is E185's step 10 v2 rest rule (rb/s11_a3_launch_e185_v2.sh lines 48-89, ad2ed873; its 40-minute
# gate, its block reading and both end forms), with its log patterns widened to every form our kits write:
#   build/eNNN/session.log            E178, E180, E181, E182 (and earlier kits)
#   build/eNNN/session-*.log          E183's session-t<T0>.log and E184's session-<arm>-t<T0>.log
#   build/eNNN/T<T0>/session.log      E185's and E186's T0-named directories (E185's v2 read E185's alone, never E186's: verify-e185d)
#   build/eNNN/T<T0>/session-*.log   (any later kit's)
# where eNNN is any run's directory (build/e[0-9]*). Dry logs are skipped by name (E183's session-dry-t<T0>.log, E184's
# session-<arm>-dry-t<T0>.log, E185's T<T0>-dry/session-dry.log, E186's T<T0>-dry/session.log), and inside a log a dry block or a block
# that opened no device ("no device opened") is skipped too. A block is dry only by the markers the kits write (set before the land, after
# verify-kit183's nit: E185's v2 reading took ANY "DRY" or "DESK:" in a line, so a real session whose log printed such a word was skipped):
# a line whose words, after its time stamp if any, begin "DRY " or "DRY:" (the kits' "DRY config ...", "DRY: the smoke gate ...", "DRY
# session end"; lib.sh's untimed "DRY ettelem config", "DRY hold10: ...") or "DESK: ", or a "session start" line ending " DRY" (E181's and
# E185's) or "; DRY)" (E172's). A block this reading calls dry E185's v2 reading calls dry too, so it counts every session that one counts.
# A real block without its "session end" counts as
# ended at its last timestamped line (the log's final block: or its last write, the later). E185's hour (A7-4) is E185's plan, not E183's.
# Prints "rest: <m> minutes since E<run>'s session end (<time>; ...)", or "rest: no real session of ours ...", or
# "REFUSED: <m> minutes since ..." and exits 3 (step 9 v2 then stops with 10, nothing launched). Run from the box's tree; GNU date.
# Its desk test: rb/selftest_rest_e183.sh (E184's, E185's, E186's, E182's and E183's own forms; dry and no-device blocks; a cut session).
# SPDX-License-Identifier: Apache-2.0
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
    if [ -z "$last" ] || [ "$t" -gt "$lastt" ]; then last=$ts; lastt=$t; lastw=E${w#e}; lastkind=$kind; fi
  done <<< "$ends"
done
if [ -n "$last" ]; then
  what="session end"; [ "$lastkind" = NOEND ] && what="last real session line (its block has no session end: counted as ended at its last line)"
  [ "$lastkind" = NOEND ] && echo "note: $lastw's last real session block has no 'session end': counted as ended at $last"
  rest=$(( ($(date +%s) - lastt) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E183 starts on a rested card, at least 40 minutes after our last real session there (the kit's dated note 4)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log or T*/session*.log"
fi
