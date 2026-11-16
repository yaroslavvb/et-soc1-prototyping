# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE REST RULE, the lines step 9 (rb/s11_a1_session_e199.sh) and
# step 7 (rb/s09_a1_reads_e199.sh, before its config read) send to aifoundry1. It is E191's rest rule (tools/claims-v3/e191/rb/
# rest_rule_e191.sh, unchanged beside it: E189's rule with every tree of ours on aifoundry1 and either card) LINE FOR LINE but its words
# (E199 for E191): no E199 card command within 40 minutes of the end of our last real session on aifoundry1, either card (E199.md section
# 9). E191's header, kept: it is E189's rest rule (tools/claims-v3/e189/rb/rest_rule_e189.sh: E188's rest rule v2 plus energy.sh's output
# folders) with the box's paths, marked "E191":
#   - every tree of ours on aifoundry1 is read, not only the one step 9 runs from: ~/nekko (k6's tree there: E164's, E172's, E190 arm B's
#     and E191's sessions), ~/aifoundry and ~/claude/et-soc1-prototyping when they exist (one read per real directory);
#   - a cut session's latest write is read under build/<run>/ and under lib.sh's block trees on aifoundry1, build/claims-v3/aifoundry1*/<run>
#     (lib.sh's DATA_ROOT there is build/claims-v3/aifoundry1-c0 or -c1), not aifoundry3's;
#   - either card counts: our last real session on aifoundry1, on card 0 or card 1, starts the 40 minutes (E191.md 2 and 13: never two
#     sessions of ours on aifoundry1; over-reading only delays a launch).
# E189's reading, unchanged: no E199 session starts within 40 minutes of the end of our last real session there, read from every session
# log of ours, whatever its form:
#   build/eNNN/session.log            E164's and the earlier kits'
#   build/eNNN/session-*.log          E183's session-t<T0>.log and E184's session-<arm>-t<T0>.log (E184 arm B ran on aifoundry1)
#   build/eNNN/T<T0>/session.log      E185's, E186's, E188's, E189's, E191's (both sessions) and E199's own T0-named directories
#   build/eNNN/T<T0>-<arm>/session.log E190's (arm B: build/e190/T<T0>-B/, Fri 13 Nov 2026 on aifoundry1 card 1)
#   build/eNNN/T<T0>/session-*.log    any later kit's
# A real block with no "session end" is counted as ended at the LATEST of its last timestamped line, its log's last write (the log's final
# block only) and the latest write of any regular file of the same run outside the dry paths. Dry paths ("-dry" or "dry-t" in the path) are
# skipped; inside a log, a block that is dry by the kits' own markers or that opened no device ("no device opened") is skipped.
# Prints "rest: <m> minutes since E<run>'s session end (<time>; ...)", or "rest: no real session of ours ...", or "REFUSED: <m> minutes
# since ..." and exits 3 (step 9 then stops with 10, nothing launched). Run from the box's tree, under the prelude's set -u; GNU date, find.
# Its desk test: rb/selftest_rest_e199.sh (E190 arm B's, E191's and E199's forms on aifoundry1, cut sessions, dry markers, refusals).
# SPDX-License-Identifier: Apache-2.0
TREES=""                                                                                                   # E191: every tree of ours, once
for T in "$PWD" "$HOME/nekko" "$HOME/aifoundry" "$HOME/claude/et-soc1-prototyping"; do
  [ -d "$T" ] || continue
  r=$(cd "$T" && pwd -P)
  case " $TREES " in *" $r "*) ;; *) TREES="$TREES $r" ;; esac
done
latest_write() {  # latest_write <tree> <run, e.g. e191>: the newest write (epoch seconds) of a regular file of that run's real paths
  local d p=""
  for d in "$1/build/$2" "$1"/build/claims-v3/aifoundry1*/"$2" "$1"/build/claims-v3/aifoundry1*/"$2"-*; do [ -d "$d" ] && p="$p $d"; done
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
  [ "$lastkind" = NOEND ] && echo "note: $lastw's last real session block has no 'session end': counted as ended at $last"
  rest=$(( ($(date +%s) - lastt) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E199 starts on a rested card, its first card command at least 40 minutes after our last real session on aifoundry1, either card (E199.md section 9; the kit)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped; every tree of ours on aifoundry1 read)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log, T*/session*.log or energy.sh's folders, in any tree of ours on aifoundry1"
fi
