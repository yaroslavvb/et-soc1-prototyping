# E188 (Q165, the kit, Thu 12 Nov 2026, before any E188 datum): THE REST RULE, the lines step 9 (rb/s11_a3_session_e188.sh) sends to
# aifoundry3 before it launches a session: no E188 session starts within 40 minutes of the end of our last real session on the card, read
# from every session log of ours on the box, whatever its form (E188.md section 6: "E188's launch at least 40 minutes after the end of our
# last session on aifoundry3 (E183's rest rule; heat carries over)"). It is E183's rest rule (tools/claims-v3/e183/rb/rest_rule_e183.sh,
# E183's kit dated note 4, 24b9b99e) line for line but its words (E188 for E183), so its reading is E183's: E185's step 10 v2 rule (its
# 40-minute gate, its block reading and both end forms) with the log patterns widened to every form our kits write:
#   build/eNNN/session.log            E178, E180, E181, E182 (and earlier kits)
#   build/eNNN/session-*.log          E183's session-t<T0>.log (as its kit note 4 writes it) and E184's session-<arm>-t<T0>.log
#   build/eNNN/T<T0>/session.log      E185's, E186's and E188's T0-named directories
#   build/eNNN/T<T0>/session-*.log   (any later kit's)
# where eNNN is any run's directory (build/e[0-9]*). Dry logs are skipped by name (E183's session-dry-t<T0>.log, E184's
# session-<arm>-dry-t<T0>.log, E185's T<T0>-dry/session-dry.log, E186's and E188's T<T0>-dry/session.log), and inside a log a dry block or a
# block that opened no device ("no device opened") is skipped too. A block is dry only by the markers the kits write: a line whose words,
# after its time stamp if any, begin "DRY " or "DRY:" (the kits' "DRY config ...", "DRY: the smoke gate ...", "DRY session end"; lib.sh's
# untimed "DRY ettelem config", "DRY hold10: ...") or "DESK: ", or a "session start" line ending " DRY" (E181's and E185's) or "; DRY)"
# (E172's). A real block without its "session end" counts as ended at its last timestamped line (the log's final block: or its last write,
# the later). On a day E183 also runs, E188 runs after it: this rule then reads E183's session log, so E188 waits 40 minutes after E183's
# end. E185's hour (A7-4) is E185's plan, not E188's.
# Prints "rest: <m> minutes since E<run>'s session end (<time>; ...)", or "rest: no real session of ours ...", or
# "REFUSED: <m> minutes since ..." and exits 3 (step 9 then stops with 10, nothing launched). Run from the box's tree; GNU date.
# Its desk test: rb/selftest_rest_e188.sh (E182's, E183's own, E184's, E185's, E186's and E188's own forms; dry and no-device blocks; a cut
# session; the kits' markers).
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
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E188 starts on a rested card, at least 40 minutes after our last real session there (E188.md section 6; the kit)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log or T*/session*.log"
fi
