# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): THE REST RULE, the lines step 9
# (rb/s11_session_e194.sh) and step 7 (rb/s09_reads_e194.sh, before its config read: E192's note 1 lesson) send to aifoundry2. It is E191's
# rest rule (tools/claims-v3/e191/rb/rest_rule_e191.sh, unchanged beside it: E189's, E188's v2 plus energy.sh's output folders) line for
# line but its words (E194) and this box's paths:
#   - every tree of ours on aifoundry2 is read, not only the one step 9 runs from: ~/claude/et-soc1-prototyping (k6's tree here: E190 arm
#     A's sessions and E194's), ~/nekko and ~/aifoundry when they exist, and the lab clone ~/git/et-soc1-prototyping (one read per real
#     directory; over-reading only delays a launch);
#   - a cut session's latest write is read under build/<run>/ and under lib.sh's block trees on aifoundry2, build/claims-v3/aifoundry2*/<run>;
#   - the box's one card: our last real session on aifoundry2 starts the 40 minutes (E194.md 13).
# E189's reading, unchanged: no E194 session starts within 40 minutes of the end of our last real session there, read from every session
# log of ours, whatever its form:
#   build/eNNN/session.log            E164's and the earlier kits'
#   build/eNNN/session-*.log          E183's session-t<T0>.log and E184's session-<arm>-t<T0>.log
#   build/eNNN/T<T0>/session.log      E185's, E186's, E188's, E189's, E191's and E194's T0-named directories
#   build/eNNN/T<T0>-<arm>/session.log E190's (arm A: build/e190/T1794614878-A/, Fri 13 Nov 2026 on this card)
#   build/eNNN/T<T0>/session-*.log    any later kit's
# and, fix-e194 (verify-e194's nit 4), the older claims-v3 forms of this card, read by their LAST WRITE (they carry no "session end" line
# in the kits' words): build/eNNN/runs/<x>/run.log (beside its session.json: E96's, E100's, E144b's, E146's) and build/eNNN/run/run.log
# (E77's, E120's); a run.log's last write is at or after its run's end, so reading it can only delay a launch.
# A real block with no "session end" is counted as ended at the LATEST of its last timestamped line, its log's last write (the log's final
# block only) and the latest write of any regular file of the same run outside the dry paths. Dry paths ("-dry" or "dry-t" in the path) are
# skipped; inside a log, a block that is dry by the kits' own markers or that opened no device ("no device opened") is skipped.
# Prints "rest: <m> minutes since E<run>'s session end (<time>; ...)", or "rest: no real session of ours ...", or "REFUSED: <m> minutes
# since ..." and exits 3 (step 9 or step 7 then stops with 10, nothing launched or read). Run from the box's tree, under the prelude's
# set -u; GNU date, find. Its desk test: rb/selftest_rest_e194.sh.
# SPDX-License-Identifier: Apache-2.0
TREES=""                                                                                                   # E194: every tree of ours, once
for T in "$PWD" "$HOME/claude/et-soc1-prototyping" "$HOME/nekko" "$HOME/aifoundry" "$HOME/git/et-soc1-prototyping"; do
  [ -d "$T" ] || continue
  r=$(cd "$T" && pwd -P)
  case " $TREES " in *" $r "*) ;; *) TREES="$TREES $r" ;; esac
done
latest_write() {  # latest_write <tree> <run, e.g. e194>: the newest write (epoch seconds) of a regular file of that run's real paths
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
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E194 starts on a rested card, at least 40 minutes after our last real session on aifoundry2 (the kit)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped; every tree of ours on aifoundry2 read)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log, T*/session*.log, runs/*/run.log, run/run.log or energy.sh's folders, in any tree of ours on aifoundry2"
fi
