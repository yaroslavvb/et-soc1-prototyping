# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): THE REST RULE, the lines step 7's wrapper (rb/s09_reads_e200.sh)
# sends to aifoundry2 BEFORE the sitting's first card command, and step 9 (rb/s11_session_e200.sh) again before the launch. It is E194's rest
# rule (tools/claims-v3/e194/rb/rest_rule_e194.sh, unchanged beside it: E191's, E189's and E188's v2 with energy.sh's output folders, this
# box's trees and the older claims-v3 run logs) LINE FOR LINE from its first line of code, but its refusal's and its report's words (E200
# sitting $SIT for E194; the caller sets SIT before these lines). E200.md 11: at least 40 minutes between the end of E194's session on this
# card (or of any earlier session of ours on it) and sitting 1's first card command; between sitting 1's end and sitting 2's first card
# command; and after E200's end before the next session of ours on this card; the rest is read on the box before anything reaches the card
# for a sitting. It reads every tree of ours on aifoundry2 (~/claude/et-soc1-prototyping, the box tree, where E190 arm A's, E194's and
# E200's own sessions write; ~/nekko and ~/aifoundry when they exist; the lab clone ~/git/et-soc1-prototyping; one read per real
# directory) and every session-log form of ours there:
#   build/eNNN/session.log            E164's and the earlier kits'
#   build/eNNN/session-*.log          E183's session-t<T0>.log and E184's session-<arm>-t<T0>.log
#   build/eNNN/T<T0>/session.log      E185's, E186's, E188's, E189's, E191's, E194's (build/e194/T<T0>/, Mon 16 Nov 2026 on this card) and
#                                     E200's own T0-named directories (sitting 1 is read here before sitting 2)
#   build/eNNN/T<T0>-<arm>/session.log E190's (arm A: build/e190/T1794614878-A/, Fri 13 Nov 2026 on this card)
#   build/eNNN/T<T0>/session-*.log    any later kit's
# and the older claims-v3 forms by their LAST WRITE (build/eNNN/runs/<x>/run.log, build/eNNN/run/run.log) and energy.sh's output folders.
# A real block with no "session end" is counted as ended at the LATEST of its last timestamped line, its log's last write (the log's final
# block only) and the latest write of any regular file of the same run outside the dry paths, under build/<run>/ and under lib.sh's block
# trees build/claims-v3/aifoundry2*/<run>[-*] (for E200 that is also E200's root, build/claims-v3/aifoundry2/e200: a cut E200 session is
# then counted at least at the day's last sync or build, which only delays a launch). Dry paths ("-dry" or "dry-t" in the path) are
# skipped; inside a log, a block that is dry by the kits' own markers or that opened no device ("no device opened": E200's gate stops
# before its session's run opened a node say so) is skipped. Over-reading a cut session's end only delays a launch.
# Prints "rest: <m> minutes since E<run>'s session end (<time>; ...)", or "rest: no real session of ours ...", or "REFUSED: <m> minutes
# since ..." and exits 3 (the caller then stops with 10, nothing sent). Run from the box's tree, under the prelude's set -u; GNU date,
# find. Its desk test: rb/selftest_rest_e200.sh (E194's committed session on this card and its forms, E190 arm A's, E200's own sittings,
# a cut session, dry and no-device sessions, the older run logs, energy.sh's folders, the two sittings in a row).
# SPDX-License-Identifier: Apache-2.0
TREES=""                                                                                                   # E194's: every tree of ours, once
for T in "$PWD" "$HOME/claude/et-soc1-prototyping" "$HOME/nekko" "$HOME/aifoundry" "$HOME/git/et-soc1-prototyping"; do
  [ -d "$T" ] || continue
  r=$(cd "$T" && pwd -P)
  case " $TREES " in *" $r "*) ;; *) TREES="$TREES $r" ;; esac
done
latest_write() {  # latest_write <tree> <run, e.g. e200>: the newest write (epoch seconds) of a regular file of that run's real paths
  local d p=""
  for d in "$1/build/$2" "$1"/build/claims-v3/aifoundry2*/"$2" "$1"/build/claims-v3/aifoundry2*/"$2"-*; do [ -d "$d" ] && p="$p $d"; done
  [ -n "$p" ] || return 0
  find $p -type f ! -path '*-dry*' ! -path '*dry-t*' 2>/dev/null | while IFS= read -r f; do date -r "$f" +%s 2>/dev/null; done | sort -n | tail -n 1
}
last=""; lastw=""; lastt=0; lastkind=""
for TR in $TREES; do
for L in "$TR"/build/e[0-9]*/session.log "$TR"/build/e[0-9]*/session-*.log "$TR"/build/e[0-9]*/T[0-9]*/session.log "$TR"/build/e[0-9]*/T[0-9]*/session-*.log; do
  [ -f "$L" ] || continue
  case "${L#$TR/}" in *-dry*|*dry-t*) continue ;; esac
  w=$(echo "${L#$TR/}" | cut -d/ -f2)
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
      lw=$(latest_write "$TR" "$w")
      case "$lw" in ''|*[!0-9]*) lw=0 ;; esac
      if [ "$lw" -gt "$t" ]; then t=$lw; ts="$(date -d @"$lw" '+%F %T %Z') (the latest write of E${w#e}'s files outside the dry paths)"; fi
    fi
    if [ -z "$last" ] || [ "$t" -gt "$lastt" ]; then last=$ts; lastt=$t; lastw=E${w#e}; lastkind=$kind; fi
  done <<< "$ends"
done
done
for T in $TREES; do                                                         # fix-e194 (nit 4): the older claims-v3 run logs, by their last write
  for F in "$T"/build/e[0-9]*/runs/*/run.log "$T"/build/e[0-9]*/run/run.log; do
    [ -f "$F" ] || continue
    case "${F#$T/}" in *-dry*|*dry-t*) continue ;; esac
    lw=$(date -r "$F" +%s 2>/dev/null)
    case "$lw" in ''|*[!0-9]*) continue ;; esac
    if [ -z "$last" ] || [ "$lw" -gt "$lastt" ]; then
      w=$(echo "${F#$T/}" | cut -d/ -f2)
      last="$(date -d @"$lw" '+%F %T %Z') (the last write of E${w#e}'s run log, ${F#$T/build/})"; lastt=$lw; lastw="E${w#e}"; lastkind=RUNLOG
    fi
  done
done
for T in $TREES; do                                                                                   # E189's energy.sh form, every tree
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
  [ "$lastkind" = RUNLOG ] && what="run (its run.log's last write)"
  [ "$lastkind" = NOEND ] && echo "note: $lastw's last real session block has no 'session end': counted as ended at $last"
  rest=$(( ($(date +%s) - lastt) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E200 sitting $SIT starts on a rested card, at least 40 minutes after our last real session on aifoundry2 (E200.md 11)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped; every tree of ours on aifoundry2 read)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log, T*/session*.log, runs/*/run.log, run/run.log or energy.sh's folders, in any tree of ours on aifoundry2"
fi
