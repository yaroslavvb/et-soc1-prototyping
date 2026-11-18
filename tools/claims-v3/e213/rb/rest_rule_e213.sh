# E213 (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): THE REST RULE, the lines step 7 (rb/s09_reads_e213.sh, before its config
# read) and step 9 (rb/s11_session_e213.sh, before the launch) send to the arm's box (aifoundry3 for arm A, aifoundry1 for arm B). It is E211's
# rest rule (tools/claims-v3/e211/rb/rest_rule_e211.sh, landed in 2b7f261f: E206's, E202's, E195's, E193's and E189's, with fix-e202's activity
# floor and E206's addition, the model session's folders) LINE FOR LINE from its first line of code, with two changes: its refusal's words name
# E213; and the activity floor leaves out E213's own folders (build/e213, build/e213rgm) where E211's left out E211's, so every other kit's session
# folders on the box count. E213.md 6: arm A "the first card command at least 40 minutes after our previous session on aifoundry3 ended"; arm B
# "at least 40 minutes after the last session on aifoundry1 ended, either card, ours or the model session's" (its sessions run under the same
# login and write ~/claude/work/ee-*/: the newest write of any file there counts; over-reading only delays a launch). Every card command counts:
# step 7's config read is a card command, so it too waits for the rest (E192's data note 1). It reads every session log of ours on the box,
# whatever its form:
#   build/eNNN/session.log, build/eNNN/session-*.log, build/eNNN/T<T0>/session.log, build/eNNN/T<T0>/session-*.log
# and energy.sh's output folders in every tree of ours (~/aifoundry, ~/nekko, ~/claude/et-soc1-prototyping), the activity floor (the newest write
# in a T0-named folder of ours under build/, outside the dry paths and E213's own folders and the runbook's build/q141k) and the model session's
# folders (~/claude/work/ee-*/: it runs its own sweeps under the same login on aifoundry1 and aifoundry2; over-reading only delays a launch). A
# real block with no "session end" is counted as ended at the latest of its last timestamped line, its log's last write and its run's latest
# write. Dry paths and blocks are skipped; a block opened no device only by "refused, no device opened: ..." or "GATE-STOP: ... (no device
# opened)" at a line's start after its stamp (E213's runner ends such a block with "...: no device opened", which is NOT one of those two forms,
# so E213's own refusals count as sessions here: that only delays a launch).
# Prints "rest: <m> minutes since ...", or "rest: no real session of ours ...", or "REFUSED: <m> minutes since ..." and exits 3 (steps 7 and 9
# then stop with 10, nothing read or launched). Run from the box's tree, under the prelude's set -u; GNU date, find.
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
fl=$(find build -path build/e213 -prune -o -path build/e213rgm -prune -o -path build/q141k -prune -o \
  -type f -path '*/T[0-9]*/*' ! -path '*-dry*' ! -path '*dry-t*' -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -n 1)   # fix-e202's floor (E213's own folders left out)
if [ -n "$fl" ]; then
  ft=${fl%%.*}; fp=${fl#* }
  case "$ft" in ''|*[!0-9]*) ft=0 ;; esac
  fw=$(printf '%s\n' "$fp" | tr '/' '\n' | grep -m1 -E '^e[0-9]+' || true)
  if [ "$ft" -gt 0 ] && { [ -z "$last" ] || [ "$ft" -gt $((lastt + 60)) ]; }; then   # more than a minute past the log rule's reading
    last="$(date -d @"$ft" '+%F %T %Z') (the newest write in a session folder of ours: $fp)"; lastt=$ft
    lastw=$( [ -n "$fw" ] && echo "E${fw#e}" || echo "a session of ours" ); lastkind=FLOOR
  fi
fi
for F in "$HOME"/claude/work/ee-*/; do                                                       # E206's addition: the model session's folders
  [ -d "$F" ] || continue
  lw=$(find "$F" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -n 1)
  lw=${lw%%.*}
  case "$lw" in ''|*[!0-9]*) continue ;; esac
  if [ -z "$last" ] || [ "$lw" -gt "$lastt" ]; then
    last="$(date -d @"$lw" '+%F %T %Z') (the newest write in the model session's folder $(basename "$F"))"; lastt=$lw; lastw="the model session"; lastkind=MODEL
  fi
done
if [ -n "$last" ]; then
  what="session end"; [ "$lastkind" = NOEND ] && what="last real session activity (no 'session end': the latest of its last line and its run's latest write)"
  [ "$lastkind" = ENERGY ] && what="run"
  [ "$lastkind" = FLOOR ] && what="last write (THE ACTIVITY FLOOR: a session folder's newest file, whatever its log's form)"
  [ "$lastkind" = MODEL ] && what="last write (a folder of the model session's own sweeps)"
  [ "$lastkind" = NOEND ] && echo "note: $lastw's last real session block has no 'session end': counted as ended at $last"
  rest=$(( ($(date +%s) - lastt) / 60 ))
  [ "$rest" -ge 40 ] || { echo "REFUSED: $rest minutes since $lastw's $what ($last): E213's first card command comes on a rested card, at least 40 minutes after our last real session there (E213.md 6; the kit)"; exit 3; }
  echo "rest: $rest minutes since $lastw's $what ($last; dry sessions and blocks that opened no device skipped)"
else
  echo "rest: no real session of ours in build/e*/session.log, session-*.log, T*/session*.log, energy.sh's folders, any T0-named folder under build/ or the model session's folders"
fi
