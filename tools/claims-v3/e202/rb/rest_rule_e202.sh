# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): THE REST RULE, the lines step 7 (rb/s09_a3_reads_e202.sh, before its
# config read) and step 9 (rb/s11_a3_session_e202.sh, before the launch) send to aifoundry3. It is E195's rest rule
# (tools/claims-v3/e195/rb/rest_rule_e195.sh: E193's, itself E189's with energy.sh's output folders, with verify-e195's finding 4 answered)
# LINE FOR LINE from its first line of code, but its refusal's words (E202 for E195). E202.md 3 and 10: after E201 (and every other session
# of ours on aifoundry3 card 0) its 40-minute rest first; one session of ours on aifoundry3 at a time. Every card command counts: step 7's
# config read is a card command, so it too waits for the rest (E192's data note 1); the next session of ours there waits 40 minutes after
# E202's end, read the same way from E202's log. It reads every session log of ours on the box, whatever its form:
#   build/eNNN/session.log            E178, E180, E181, E182 (and earlier kits)
#   build/eNNN/session-*.log          E183's session-t<T0>.log (its kit note 4) and E184's session-<arm>-t<T0>.log
#   build/eNNN/T<T0>/session.log      E185's, E186's, E188's, E189's, E192's, E193's, E195's, E196's and E197's T0-named directories,
#                                     and E202's own (run_e202.py writes the kits' form there), and any later kit's in that form (E201's)
#   build/eNNN/T<T0>/session-*.log   (any later kit's)
# and energy.sh's output folders in every tree of ours (~/aifoundry, ~/nekko, ~/claude/et-soc1-prototyping). A real block with no
# "session end" (a session whose shell died, or one cut mid-queue) is counted as ended at the LATEST of its last timestamped line, its
# log's last write and the latest write of any regular file of the same run outside the dry paths, under build/<run>/ and under
# build/claims-v3/aifoundry3/<run>[-*]. Dry paths ("-dry" or "dry-t" in the path) are skipped; inside a log, a block that is dry by the
# kits' own markers (a line whose words begin "DRY " or "DRY:" or "DESK: ", a "session start" line ending " DRY" or "; DRY)") or that
# opened no device is skipped. A block opened no device ONLY by the two forms E195's rule reads, each at the line's start after its time
# stamp: "refused, no device opened: ..." (E202's runner writes exactly this for every refusal before its first card command) or
# "GATE-STOP: ... (no device opened)"; any other text (another kit's no-device ending, a tool's text in a log) counts as a session, which
# only delays a launch. Over-reading a cut session's end only delays a launch.
# THE ACTIVITY FLOOR (fix-e202, verify-e202's finding 6: a later kit's log one folder deeper, named otherwise (runner.log), under
# build/claims-v3/aifoundry3/<run>/ or stamped in ISO form was not read): beside the forms above, the NEWEST WRITE of any regular file in a
# T0-named folder of ours (a path component T<digits>..., at any depth under build/), outside the dry paths and outside E202's own
# folders (build/e202, build/e202mnist, build/e202files: the log rule reads E202's own form, its refusals skipped) and the runbook's
# build/q141k, counts as a session's end too, whatever the log's name, depth or stamps, when it is more than a minute past what the log
# forms read (a session the forms do read writes its manifest a moment after its "session end": the forms' words stand for it). A real
# session writes its folder to its end, so the floor is never earlier than the session's end; it can be later (a file written after
# it), which only delays a launch.
# Prints "rest: <m> minutes since E<run>'s session end (<time>; ...)", or "rest: no real session of ours ...", or "REFUSED: <m> minutes
# since ..." and exits 3 (steps 7 and 9 then stop with 10, nothing read or launched). Run from the box's tree, under the prelude's set -u;
# GNU date, find. Its desk test: rb/selftest_rest_e202.sh.
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
    inblk && (m ~ /^refused, no device opened: / || (m ~ /^GATE-STOP: / && m ~ /\(no device opened\)$/)) { nodev = 1 }
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
for T in "$HOME/aifoundry" "$HOME/nekko" "$HOME/claude/et-soc1-prototyping"; do                                   # E189's addition, kept: energy.sh's form
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
fl=$(find build -path build/e202 -prune -o -path build/e202mnist -prune -o -path build/e202files -prune -o -path build/q141k -prune -o \
  -type f -path '*/T[0-9]*/*' ! -path '*-dry*' ! -path '*dry-t*' -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -n 1)   # fix-e202: the floor
if [ -n "$fl" ]; then
  ft=${fl%%.*}; fp=${fl#* }
  case "$ft" in ''|*[!0-9]*) ft=0 ;; esac
  fw=$(printf '%s\n' "$fp" | tr '/' '\n' | grep -m1 -E '^e[0-9]+' || true)
  if [ "$ft" -gt 0 ] && { [ -z "$last" ] || [ "$ft" -gt $((lastt + 60)) ]; }; then   # more than a minute past the log rule's reading
    last="$(date -d @"$ft" '+%F %T %Z') (the newest write in a session folder of ours: $fp)"; lastt=$ft
    lastw=$( [ -n "$fw" ] && echo "E${fw#e}" || echo "a session of ours" ); lastkind=FLOOR
  fi
fi
if [ -n "$last" ]; then
  what="session end"; [ "$lastkind" = NOEND ] && what="last real session activity (no 'session end': the latest of its last line and its run's latest write)"
  [ "$lastkind" = ENERGY ] && what="run"
  [ "$lastkind" = FLOOR ] && what="last write (THE ACTIVITY FLOOR: a session folder's newest file, whatever its log's form)"
  [ "$lastkind" = NOEND ] && echo "note: $lastw's last real session block has no 'session end': counted as ended at $last"
  rest=$(( ($(date +%s) - lastt) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E202's first card command comes on a rested card, at least 40 minutes after our last real session there (E202.md 3 and 10; the kit)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log, T*/session*.log, energy.sh's folders or any T0-named folder under build/"
fi
