set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
RP=${2:-}
LOCKFROM=${3:-}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
if [ -z "${E200_RB_INNER:-}" ]; then
  for p in /dev/et*; do [ -c "$p" ] && { echo "REFUSED: $p is a character device here: run this test inside the no-device sandbox"; exit 2; }; done
  [ "$(TZ=America/Los_Angeles date +%H%M)" -lt 2230 ] || { echo "REFUSED: run before 22:30 Pacific (step 7 needs the full plan's cap and 15 minutes before 23:59)"; exit 2; }
  [ "$(TZ=America/Los_Angeles date +%H%M)" -ge 0100 ] || { echo "REFUSED: run after 01:00 Pacific (the stand-in logs are dated 45 minutes back, today)"; exit 2; }
  mkdir -p "$S" && S=$(cd "$S" && pwd)
  [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  : > "$S/et0_ops"; : > "$S/et0_mgmt"
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --bind "$S/et0_ops" /dev/et0_ops --bind "$S/et0_mgmt" /dev/et0_mgmt \
    --unshare-pid --proc /proc --unshare-uts --hostname aifoundry2 --die-with-parent --setenv E200_RB_INNER 1 \
    -- /bin/bash "$SRC/tools/claims-v3/e200/rb/selftest_rb_e200.sh" "$S" "$RP" "$LOCKFROM"
fi
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK RB_WAIT_LOOP_S RB_E200_KITPIN RB_QUIET E200_DESKTEST E200_READER_SHA256; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
for c in timeout sha256sum shasum flock cmake rsync; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
: > /run/lock/etsoc-shire0.lock
T=$S/tree; BOXH=$S/box/aifoundry2; TREE=$BOXH/claude/et-soc1-prototyping; BIN=$S/bin; BB=$S/boxbin; ST=$S/box-state
mkdir -p "$TREE/build" "$BIN" "$BB" "$ST"
E=tools/claims-v3/e200
E7=tools/claims-v3/e197
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
cfgcalls() { local n; n=$(grep -c '"mode": "config"' "$ST/calls/sampler.log" 2>/dev/null); echo "${n:-0}"; }
restamp() {  # restamp <RB_OUT> <sitting>: step 7's stamp moved to now (the test's own pace passes the 120 s bound), its folder copied on the box
  local f=$1/e200-$2-first.txt o n
  o=$(sed -n 's/^FIRST=//p' "$f"); n=$(date +%s)
  [ -d "$TREE/build/e200/first-s$2-$o" ] && cp -rp "$TREE/build/e200/first-s$2-$o" "$TREE/build/e200/first-s$2-$n"
  sedi -e "s/^FIRST=.*/FIRST=$n/" -e "s#^FIRSTDIR=.*#FIRSTDIR=build/e200/first-s$2-$n#" "$f"
}
echo "E200 runbook desk test, $(date '+%F %T %Z'), $(/usr/bin/python3 --version 2>&1), $(cmake --version | head -n 1); inside its sandbox: host $(hostname), /dev/et*: $(ls /dev/et* | tr '\n' ' '); scratch outside the repository"
# ---- the scratch repository: a shared sparse clone at the registration, then the kit's files as one stand-in commit
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E200.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; exit 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || exit 2
G="git -C $T -c user.name=e200-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ '/docs/reports/data/*e200*' '/docs/reports/gate-stops/*e200*' '/docs/reports/data/*e197*' \
  /docs/reports/data/2026-11-15-e194-fwread-aifoundry2/ || exit 2   # E200's data stays on disk across resets
$G checkout -q -B main "$REG" || exit 2
$G branch -q -f e200-desktest-registration "$REG" && $G branch -q --set-upstream-to=e200-desktest-registration || exit 2   # step 2's pull: a no-op
( cd "$SRC" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
( cd "$SRC" && { git ls-files --cached --others --exclude-standard -- $E | grep -v -x -F -f "$S/reg-files.txt"; git diff --name-only HEAD -- $E; } ) |
  sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
[ -f "$T/$E/session_e200.sh" ] && [ -f "$T/$E/harness_e200.py" ] && [ -f "$T/$E/rb/s03_desk_e200.sh" ] && [ -f "$T/$E/KIT.md" ] || { echo "the kit's files (KIT.md among them: step 2 finds the kit's commit by it) did not reach the scratch tree"; exit 2; }
mkdir -p "$T/$E/logs"
for spec in "desktest-realpath-e200.txt DESKTEST-REALPATH-E200 0 of 0 PASS" "selftest-rb-e200.txt SELFTEST-RB-E200 0 of 0 PASS" \
            "selftest-rest-e200.txt SELFTEST-REST-E200 0 of 0 PASS" "realbytes-e200.txt REALBYTES-E200 0 of 0 PASS" \
            "checks-e200.txt CHECKS-E200 0 of 0 PASS" "selftest-fwgate-e200.txt SELFTEST-FWGATE-E200 0 of 0 PASS" \
            "dry-listing-e200.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls beyond aifoundry2" "dmcmd-audit-e200.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"     # always a stand-in line: this test never reads its own (or any) log being written
done
( cd "$T" && /usr/bin/python3 -I -B $E/harness_e200.py --make > /dev/null )   # before the stand-in record: a record added after the kit
FWREC=tools/claims-v3/fwgate/records/aifoundry2-c0-desktest-standin.json   # a stand-in record after this boot, added after the harness was
# made (a record a later commit adds): step 2's harness check names it and passes, step 2 reads it against its source (fwgate.py
# check-records: its one source E194's committed read 15cb0fcb, its seven fields re-read from it; fix-e200, F6), the sync carries it, and
# fwgate's look reads CONTINUITY (its read time is the test's own)
/usr/bin/python3 -I -B - "$T/$FWREC" <<'PY'
import datetime, json, sys
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8)))
json.dump({"schema": "fwgate-record/1", "box": "aifoundry2", "card": 0, "by": "a desk-test stand-in (never a lab file)",
           "read_at": now.isoformat(timespec="seconds"), "read_at_text": now.strftime("%Y-%m-%d %H:%M:%S PST"),
           "fields": {"release": "1.4.0", "bl1": "0.22.0", "bl2": "0.22.0", "pmic": "1.5.0", "mm": "0.25.1", "wm": "0.25.1", "machm": "0.25.1"},
           "k6_fwread": False, "sources": [{"path": "docs/reports/data/2026-11-15-e194-fwread-aifoundry2/fwread.stderr",
           "sha256": "dc48695344559e73e6e435d09b965d927cc7f29d412a139d24663815464bcde0", "form": "raw"}], "note": "desk test"},
          open(sys.argv[1], "w"), indent=1)
PY
rm -f "$T/$E/SHA256SUMS-e200-kit"
( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e200-kit' ! -path "$E/rb/s03_desk_e200.sh" ! -name '*.pyc' | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) |
  grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e200-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
export RB_E200_KITPIN="$E/SHA256SUMS-e200-kit:$KITN:$KITH:top"
$G add -A $E "$FWREC" && $G commit -q -m "E200 runbook desk test: the kit's files and a stand-in fwgate record (stand-in kit commit)" || { echo "the scratch kit commit failed"; exit 2; }
echo "scratch repository: a shared sparse clone at the registration ${REG:0:12}, the kit as one stand-in commit $($G rev-parse --short=12 HEAD) (its files from the clone, $([ -n "$KITC" ] && echo "the kit committed there at ${KITC:0:12}" || echo "the kit not committed there")); the stand-in kit list $KITN entries"
# ---- the stand-ins
REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry2) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e200desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'true' and 'bash -s', not '\$cmd'" >&2; exit 97; }
cd "$BOXH" || exit 1
exec /usr/bin/env HOME="$BOXH" PATH="$BB:/usr/bin:/bin" E200_STANDIN_DIR="$ST" USER=$(id -un) LOGNAME=$(id -un) bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry2) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$BOXH/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
FAKE=$T/$E/fake_card_e200.py
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s etwho "$@"\n' "$FAKE" > "$BB/et-who"
printf '#!/bin/sh\necho "et-lab-manifest: a desk-test stand-in (no sysfs read)"\n' > "$BB/et-lab-manifest"
printf '#!/bin/sh\necho aifoundry2\n' > "$BB/hostname"
cat > "$BB/pgrep" <<EOF
#!/bin/bash
# the stand-in box's pgrep: the real one, less every process whose working directory is outside the stand-in box's home
out=""
for q in \$("$REAL_PGREP" "\$@"); do
  c=\$(readlink "/proc/\$q/cwd" 2>/dev/null) || continue
  case "\$c/" in "$BOXH"/*) out="\$out\$q
" ;; esac
done
[ -n "\$out" ] || exit 1
printf '%s' "\$out"
EOF
cat > "$BB/ps" <<EOF_PS
#!/bin/bash
# the stand-in box's ps for the form k6's hold_read and the session's rules use (ps -eo uid=,pid=,comm=): the real one's lines, less every
# process outside the stand-in box (its working directory not under the box's home)
[ "\$*" = "-eo uid=,pid=,comm=" ] || exec /usr/bin/ps "\$@"
/usr/bin/ps -eo uid=,pid=,comm= | while read -r u p c; do d=\$(readlink "/proc/\$p/cwd" 2>/dev/null) || continue; case "\$d/" in "$BOXH"/*) echo "\$u \$p \$c" ;; esac; done
EOF_PS
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$BB/$n"; done
chmod +x "$BIN"/* "$BB"/*
mkdir -p "$TREE/build/ettelem-hpl"
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s sampler "$@"\n' "$FAKE" > "$TREE/build/ettelem-hpl/ettelem"; chmod +x "$TREE/build/ettelem-hpl/ettelem"
# the box's reader is the stand-in: the build, step 7 and the wrapper take its sha256 as the pin under E200_DESKTEST=1 (the card day never
# sets it; the session's start line names DESKTEST, and the collection refuses such a session outside a desk test)
export E200_DESKTEST=1 E200_READER_SHA256=$(sha256sum "$TREE/build/ettelem-hpl/ettelem" | cut -d' ' -f1)
export RB_QUIET="$S/quiet-flag"
echo '{}' > "$ST/scenario.json"
if [ -n "$LOCKFROM" ]; then cp "$LOCKFROM" "$S/lock.txt" || exit 2; else : > "$S/lock.txt"; fi   # RB_LOCK: a copy, never the round's own file
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$S/gitlock"
R=$T/$E/rb; K6=$T/tools/claims-v3/q141k-runbook/k6
bash "$R/quiet_e200.sh" raise e200-desktest > "$S/quiet-raise.txt" 2>&1 || { echo "the quiet flag could not be raised"; exit 2; }
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || exit 2
win() { mkdir -p "$1"; RB_OUT="$1" bash "$R/s02_window_e200.sh" "$2" "$TODAY" 21:59 23:59 > /dev/null 2>&1; }
s2() { RB_DESKTEST=1 RB_OUT="$1" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e200.sh"; }

step "A. the dry listing"
bash "$R/list_steps_e200.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing.txt"
ok "$rc.$(grep -c . "$S/calls.log")" "0.0" "A every step 0, no call to the stand-ins"

step "W1-W5, G. the window rule and the lab-git lock"
s2 "$S/out-k" > "$S/w1.txt" 2>&1; w1=$?
win "$S/out-w" 1; touch -d '-1 day' "$S/out-w/window.env"
s2 "$S/out-w" > "$S/w2.txt" 2>&1; w2=$?
win "$S/out-w" 1; sedi -e 's/^RB_PLAN=e200$/RB_PLAN=e194/' "$S/out-w/window.env"
s2 "$S/out-w" > "$S/w3.txt" 2>&1; w3=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e200.sh" 1 "$(date -d '+1 day' +%F)" 10:00 12:00 > "$S/w4.txt" 2>&1; w4=$?
win "$S/out-w" 1
RB_OUT="$S/out-w" bash "$R/s11_session_e200.sh" 2 > "$S/w5.txt" 2>&1; w5=$?
RB_OUT="$S/out-w" bash "$R/s03_desk_e200.sh" > "$S/g.txt" 2>&1; g=$?
ok "$w1.$(has 'no window in RB_OUT' "$S/w1.txt").$w2.$(has 'not written today' "$S/w2.txt").$w3.$(has 'written for e194' "$S/w3.txt").$w4.$(has 'is not today' "$S/w4.txt").$w5.$(has "sitting 1's, not sitting 2's" "$S/w5.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt").$(grep -c . "$S/calls.log")" \
  "10.1.10.1.10.1.10.1.10.1.10.1.0" "W1-W5, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested): its pull cannot take the lock"
RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_DESKTEST=1 RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e200.sh" > "$S/n.txt" 2>&1; n=$?
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull (never run step 2 inside the lock)"

step "P1. step 2 on the scratch repository"
mkdir -p "$S/out-p"; win "$S/out-p" 1
s2 "$S/out-p" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check|STOP' "$S/p1.txt" | cut -c1-500
grep -h -a '^CHECK PASS' "$S"/out-p/calls/*-local.out 2>/dev/null | head -n 1 | cut -c1-260
ok "$p1.$(has "the lists at their pinned counts and bytes (35, 39, 17, 19; the kit's $KITN)" "$S/p1.txt").$(has 'the paths clean, HISTORY OK' "$S/p1.txt").$(grep -l -a 'not pinned: aifoundry2-c0-desktest-standin.json' "$S"/out-p/calls/*-local.out 2>/dev/null | head -n 1 | grep -c .).$(grep -l -a '^aifoundry2-c0-desktest-standin.json: OK ' "$S"/out-p/calls/*-local.out 2>/dev/null | head -n 1 | grep -c .).$(has 'the freeze line 2eba6ef4b60241674628dde125273db4547b0ba17dd6d5a3e30935c7c6e89733 (E200.md 0)' "$S/p1.txt")" \
  "0.1.1.1.1.1" "P1 step 2 passes at every pin (E197's two lists, E200's registration and E197 references, the kit's), HISTORY OK, the registrations and the kits found by their content; the harness check names the fwgate record added after the kit and passes; fwgate's check-records reads it OK against its source; the freeze line checked and printed"

step "P2-P4, H1-H3. a short registration list; a short kit list; an unknown list; an edited registration file; shadows"
sedi -e '$d' "$T/$E/SHA256SUMS-e200-registration"; $G commit -q -am "desk test: the registration's list one line short"
s2 "$S/out-p" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sedi -e '$d' "$T/$E/SHA256SUMS-e200-kit"; $G commit -q -am "desk test: the kit's list one line short"
s2 "$S/out-p" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
( cd "$T" && sha256sum $E/E200.md > $E/notes-SHA256SUMS-x ); $G add $E/notes-SHA256SUMS-x; $G commit -q -m "desk test: an unknown list"
s2 "$S/out-p" > "$S/p4.txt" 2>&1; p4=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/$E7/proposal/src/trains.tsv"; $G commit -q -am "desk test: one of E197's registration files edited"
s2 "$S/out-p" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
printf '# desk test: a stand-in that would shadow json for dmcmd_audit.py\n' > "$T/tools/claims-v3/json.py"; $G add tools/claims-v3/json.py
$G commit -q -m "desk test: json.py beside dmcmd_audit.py"
s2 "$S/out-p" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e200.py tree ) > "$S/h2b.txt" 2>&1; $G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/tools/claims-v3/e194/re.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e200.py tree ) > "$S/h3.txt" 2>&1; h3=$?; rm -f "${T:?}/tools/claims-v3/e194/re.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e200.py tree ) > "$S/hc.txt" 2>&1; hc=$?
cut -c1-260 "$S/h2b.txt" "$S/h3.txt"
ok "$p2.$(has 'SHA256SUMS-e200-registration(16 OK of 16; pinned 17' "$S/p2.txt").$p3.$(has "SHA256SUMS-e200-kit($((KITN - 1)) OK of $((KITN - 1)); pinned $KITN" "$S/p3.txt").$p4.$(has 'notes-SHA256SUMS-x' "$S/out-p/runbook.log").$h1.$(has 'history' "$S/h1.txt").$h2.$(has 'json.py' "$S/h2b.txt").$h3.$(has 'HISTORY FAIL' "$S/h3.txt").$hc" \
  "16.1.16.1.0.1.16.1.16.1.16.1.0" "P2-P4, H1-H3: each pin refused and named; the unknown list reported; the edit and the shadows refused by the history check; clean again after"

step "P5. a fwgate record added since the kit that names no committed source (fix-e200, verify-e200's F6): step 2 refuses"
NOSRC=tools/claims-v3/fwgate/records/aifoundry2-c0-desktest-nosource.json
/usr/bin/python3 -I -B - "$T/$NOSRC" <<'PY'
import datetime, json, sys
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8)))
json.dump({"schema": "fwgate-record/1", "box": "aifoundry2", "card": 0, "by": "a desk-test stand-in with no source (never a lab file)",
           "read_at": now.isoformat(timespec="seconds"), "read_at_text": now.strftime("%Y-%m-%d %H:%M:%S PST"),
           "fields": {"release": "1.4.0", "bl1": "0.22.0", "bl2": "0.22.0", "pmic": "1.5.0", "mm": "0.25.1", "wm": "0.25.1", "machm": "0.25.1"},
           "k6_fwread": False, "sources": [], "note": "desk test"}, open(sys.argv[1], "w"), indent=1)
PY
$G add "$NOSRC"; $G commit -q -m "desk test: a fwgate record with no source"
s2 "$S/out-p" > "$S/p5.txt" 2>&1; p5=$?; $G reset -q --hard HEAD~1
stopline "$S/p5.txt"
ok "$p5.$(has 'fwgate-record(aifoundry2-c0-desktest-nosource.json: no committed source)' "$S/p5.txt").$(has 'desktest-standin.json: no committed source' "$S/p5.txt").$([ -e "$T/$NOSRC" ] && echo left || echo gone)" \
  "16.1.0.gone" "P5 a fwgate record added since the kit with no committed source: step 2 refuses (16) naming it (the record with E194's source passes beside it); clean again after"

step "D1-D4. no E200 datum in any ref"
D1P=docs/reports/data/2026-11-16-e200-regfile-sitting-1-aifoundry2
mkdir -p "$T/$D1P"; echo x > "$T/$D1P/x.txt"; $G add --sparse "$D1P/x.txt"; $G commit -q -m "desk test: sitting 1's data path"
s2 "$S/out-p" > "$S/d1.txt" 2>&1; d1=$?
mkdir -p "$S/out-p2"; win "$S/out-p2" 2
s2 "$S/out-p2" > "$S/d2.txt" 2>&1; d2=$?
D2P=docs/reports/data/2026-11-16-e200-regfile-sitting-2-aifoundry2
mkdir -p "$T/$D2P"; echo x > "$T/$D2P/x.txt"; $G add --sparse "$D2P/x.txt"; $G commit -q -m "desk test: a sitting 2 data path"
s2 "$S/out-p2" > "$S/d3.txt" 2>&1; d3=$?
rm -rf "${T:?}/$D1P" "${T:?}/$D2P"; $G reset -q --hard HEAD~2
GS=docs/reports/gate-stops/2026-11-16-e200-regfile-sitting-1-T1794700000-aifoundry2
mkdir -p "$T/$GS"; echo x > "$T/$GS/x.txt"; $G add --sparse "$GS/x.txt"; $G commit -q -m "desk test: a gate stop's record"
s2 "$S/out-p" > "$S/d4.txt" 2>&1; d4=$?
rm -rf "${T:?}/docs/reports/gate-stops"; $G reset -q --hard HEAD~1
stopline "$S/d1.txt"; stopline "$S/d3.txt"
ok "$d1.$(has 'e200-datum(1 paths before sitting 1)' "$S/d1.txt").$d2.$d3.$(has "e200-datum(1 paths besides sitting 1's before sitting 2)" "$S/d3.txt").$d4.$(has 'E200 data paths in any ref: 0 ' "$S/d4.txt")" \
  "16.1.0.16.1.0.1" "D1 a datum before sitting 1: 16; D2 sitting 1's own before sitting 2: 0; D3 a sitting-2 path before sitting 2: 16; D4 a gate stop's record: 0 (no datum)"

step "S, B. the sync, then THE REAL BUILD on the stand-in box"
mkdir -p "$S/out-a"; win "$S/out-a" 1
RB_OUT="$S/out-a" bash "$R/s07_sync_e200.sh" > "$S/s.txt" 2>&1; s=$?
tail -n 1 "$S/s.txt"
( cd "$TREE/build/claims-v3/aifoundry2/e200" && /usr/bin/python3 -I -B tools/claims-v3/e200/harness_e200.py --box --root . ) > "$S/s2.txt" 2>&1
RB_OUT="$S/out-a" bash "$R/s08_build_e200.sh" start > "$S/b1.txt" 2>&1; b1=$?
b2=17; k=0; while [ "$b2" -eq 17 ] && [ "$k" -lt 6 ]; do RB_OUT="$S/out-a" bash "$R/s08_build_e200.sh" wait > "$S/b2.txt" 2>&1; b2=$?; k=$((k + 1)); done
grep -E '^ +(COMPILER|ELF|CHECK|HOST|SIGNAL|LISTING|SAMPLER|REGFILE)|STOP|built today' "$S/b2.txt" | cut -c1-220
RB_OUT="$S/out-a" bash "$R/s08_build_e200.sh" start > "$S/b3.txt" 2>&1; b3=$?
BLT=$S/out-a/e200-built.txt
ok "$s.$(has 'HARNESS OK' "$S/s2.txt").$b1.$b2.$(grep -c '^LISTING SAME' "$BLT").$(grep -c '^CHECK ' "$BLT").$(has '^HOST-TABLE SAME' "$BLT").$(has '^HOST-BEHAVIOUR OK' "$BLT").$(has '^SIGNAL-READ host' "$BLT").$(has "^RUNNER E197's lab runner with W1: sha256 8774027b4bba78c6b532988c46446987f75eec6d32985bd7b400cbb963eb5a41" "$BLT").$(has '^REGFILE-BUILT rc=0' "$BLT").$b3.$(has 'was built today' "$S/b3.txt")" \
  "0.1.0.0.3.2.1.1.1.1.1.10.1" "S the sync, HARNESS OK in E200's root on the box; B the real build: make_images and check_elf, HOST-TABLE SAME, HOST-BEHAVIOUR OK, SIGNAL-READ, E200's runner made by W1 at its sha256, LISTING SAME x3 but W1, REGFILE-BUILT; B2 a second start refused (10)"

step "B3. NO-THIRD-BUILD"
AT=$TREE/build/claims-v3/aifoundry2/e200/build/e200-build-attempts.txt
cp -p "$AT" "$S/attempts.keep"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a2-build-e200 started" >> "$AT"
cp -p "$TREE/build/q141k/jobs/a2-build-e200.out" "$S/jobout.keep"; sedi -e 's/^REGFILE-BUILT rc=0/REGFILE-BUILD-FAILED desk test/' "$TREE/build/q141k/jobs/a2-build-e200.out"
RB_OUT="$S/out-a" bash "$R/s08_build_e200.sh" start > "$S/b4.txt" 2>&1; b4=$?
cp -p "$S/attempts.keep" "$AT"; cp -p "$S/jobout.keep" "$TREE/build/q141k/jobs/a2-build-e200.out"
stopline "$S/b4.txt"
ok "$b4.$(has 'NO-THIRD-BUILD' "$S/b4.txt")" "16.1" "B3 a third start the same day refused (16)"

step "SD, NB. the sync with a synced file not committed; steps 8, 7 and 9 with no build today"
printf '# desk test: one line more, not committed\n' >> "$T/$E/check_e200.py"
RB_OUT="$S/out-a" bash "$R/s07_sync_e200.sh" > "$S/sd.txt" 2>&1; sd=$?
$G checkout -q -- "$E/check_e200.py"
mkdir -p "$S/out-nb"; win "$S/out-nb" 1
RB_OUT="$S/out-nb" bash "$R/s10_dry_e200.sh" start > "$S/nb1.txt" 2>&1; nb1=$?
RB_OUT="$S/out-nb" bash "$R/s09_reads_e200.sh" 1 > "$S/nb3.txt" 2>&1; nb3=$?
RB_OUT="$S/out-nb" bash "$R/s11_session_e200.sh" 1 > "$S/nb2.txt" 2>&1; nb2=$?
stopline "$S/sd.txt"; stopline "$S/nb1.txt"; stopline "$S/nb3.txt"; stopline "$S/nb2.txt"
ok "$sd.$(has 'the synced paths have uncommitted changes' "$S/sd.txt").$nb1.$(has 'was not built today' "$S/nb1.txt").$nb3.$(has 'was not built today' "$S/nb3.txt").$nb2.$(has 'was not built today' "$S/nb2.txt")" \
  "16.1.10.1.10.1.10.1" "SD a synced file changed and not committed: refused (16); NB no build today: steps 8, 7 and 9 refused (10)"

step "L1-L3. a login link; a hang; a cut wait"
touch "$S/ssh-login"; RB_OUT="$S/out-a" bash "$R/s05_look_e200.sh" > "$S/l1.txt" 2>&1; l1=$?
touch "$S/ssh-hang"; RB_READ_S=4 RB_OUT="$S/out-a" bash "$R/s05_look_e200.sh" > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; RB_OUT="$S/out-a" bash "$R/s08_build_e200.sh" wait > "$S/l3.txt" 2>&1; l3=$?
stopline "$S/l1.txt"; stopline "$S/l2.txt"; stopline "$S/l3.txt"
ok "$l1.$(grep -c 'aifoundry2 needs a check' "$S/lock.txt" | awk '{print ($1 > 0) ? 1 : 0}').$l2.$l3.$(has 'no reading' "$S/l3.txt")" "11.1.13.14.1" \
  "L1 a login link: 11 and the lock line (in the COPY); L2 a hang killed at its bound: 13; L3 a cut wait: 14, no reading"

step "Y. step 8, the dry pass on the stand-in box (both of sitting 1's plans)"
RB_OUT="$S/out-a" bash "$R/s05_look_e200.sh" > "$S/look.txt" 2>&1; lk=$?
RB_OUT="$S/out-a" bash "$R/s10_dry_e200.sh" start > "$S/y1.txt" 2>&1; y1=$?
y2=17; k=0; while [ "$y2" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-a" bash "$R/s10_dry_e200.sh" wait > "$S/y2.txt" 2>&1; y2=$?; k=$((k + 1)); done
grep -E 'E200-DRY' "$S/y2.txt" | cut -c1-200
ok "$lk.$y1.$y2.$(grep -c '^E200-DRY sitting 1 plan .* rc=0 LISTING SAME' "$S/y2.txt").$([ -s "$S/out-a/e200-1-dry-ok.txt" ] && echo 1 || echo 0)" "0.0.0.2.1" "Y the look FREE; the dry pass: the wrapper's dry path for full and short, LISTING SAME x2; RB_OUT/e200-1-dry-ok.txt"

step "RS, R, R2. step 7: the rest BEFORE any card command; then the reads"
L=$TREE/build/e194/T1794620000/session.log; mkdir -p "$(dirname "$L")"
NOW=$(date +%s); tsm() { date -d @"$((NOW - $1 * 60))" '+%Y-%m-%d %H:%M:%S %Z'; }
{ echo "$(tsm 40) session start (T0 $((NOW - 2400)); E194, the blind day on aifoundry2 card 0, kit-e194)"; echo "$(tsm 10) session end (T0 $((NOW - 2400)))"; } > "$L"; touch -d @"$((NOW - 600))" "$L"
c0=$(cfgcalls)
RB_OUT="$S/out-a" bash "$R/s09_reads_e200.sh" 1 > "$S/rs.txt" 2>&1; rs=$?
c1=$(cfgcalls); rsf=$([ -e "$S/out-a/e200-1-first.txt" ] && echo stamped-early || echo ok)
stopline "$S/rs.txt"
touch -d @"$((NOW - 2700))" "$L"; sedi -e "s/^$(tsm 10 | cut -c1-19)/$(tsm 45 | cut -c1-19)/" "$L"
RB_OUT="$S/out-a" bash "$R/s09_reads_e200.sh" 1 > "$S/r.txt" 2>&1; r=$?
c2=$(cfgcalls); F0=$(sed -n 's/^FIRST=//p' "$S/out-a/e200-1-first.txt" 2>/dev/null)
grep -E 'sitting 1:|k6.s reads|STOP' "$S/r.txt" | cut -c1-220
RB_OUT="$S/out-a" bash "$R/s09_reads_e200.sh" 1 > "$S/r2.txt" 2>&1; r2=$?
F1v=$(sed -n 's/^FIRST=//p' "$S/out-a/e200-1-first.txt" 2>/dev/null)
ok "$rs.$(has 'REFUSED: 10 minutes since E194' "$S/rs.txt").$((c1 - c0)).$rsf.$r.$(has 'PLAN=full' "$S/out-a/e200-1-first.txt").$(has 'FWGATE=continuity' "$S/out-a/e200-1-first.txt").$([ -s "$TREE/build/e200/first-s1-$F0/config.out" ] && echo 1 || echo 0).$((c2 - c1)).$r2.$([ -n "$F0" ] && [ "$F0" = "$F1v" ] && echo kept || echo moved).$(has 'the first card command stays' "$S/r2.txt")" \
  "10.1.0.ok.0.1.1.1.1.0.kept.1" "RS the rest at step 7 (E194's session on this card ended 10 minutes ago): refused (10), NO config read sent, nothing stamped; R once rested: plan full, the stamp, fwgate's look CONTINUITY (no read), one config read kept in step 7's folder, 0; R2 again: the stamp kept"

step "F1. step 9 with the first card command 11 minutes back"
cp -p "$S/out-a/e200-1-first.txt" "$S/first.keep"; sedi -e "s/^FIRST=.*/FIRST=$(( $(date +%s) - 660 ))/" "$S/out-a/e200-1-first.txt"
RB_OUT="$S/out-a" bash "$R/s11_session_e200.sh" 1 > "$S/f1.txt" 2>&1; f1=$?
cp -p "$S/first.keep" "$S/out-a/e200-1-first.txt"
stopline "$S/f1.txt"
ok "$f1.$(has 'more than 120 s' "$S/f1.txt").$(has 'LAUNCHED' "$S/f1.txt")" "16.1.0" "F1 the first card command 11 minutes back: step 9 refused (16), nothing launched"

step "F1b. step 9 with the first card command 5 minutes back (the bound is 120 s, E197's kit's)"
cp -p "$S/out-a/e200-1-first.txt" "$S/first.keep"; sedi -e "s/^FIRST=.*/FIRST=$(( $(date +%s) - 300 ))/" "$S/out-a/e200-1-first.txt"
RB_OUT="$S/out-a" bash "$R/s11_session_e200.sh" 1 > "$S/f1b.txt" 2>&1; f1b=$?
cp -p "$S/first.keep" "$S/out-a/e200-1-first.txt"
stopline "$S/f1b.txt"
ok "$f1b.$(has 'more than 120 s' "$S/f1b.txt").$(has 'LAUNCHED' "$S/f1b.txt")" "16.1.0" "F1b the first card command 5 minutes back: step 9 refused (16) by the 120 s bound, nothing launched"

step "BA, BC, BS, SG. sitting 2's conditions at step 7; sitting 1 again on a day its smoke failed"
mkdir -p "$S/out-b"; win "$S/out-b" 2; cp -p "$S/out-a/e200-built.txt" "$S/out-b/e200-built.txt"
RB_OUT="$S/out-b" bash "$R/s10_dry_e200.sh" start > /dev/null 2>&1
yb=17; k=0; while [ "$yb" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-b" bash "$R/s10_dry_e200.sh" wait > "$S/ybw.txt" 2>&1; yb=$?; k=$((k + 1)); done
c0=$(cfgcalls)
RB_OUT="$S/out-b" bash "$R/s09_reads_e200.sh" 2 > "$S/ba.txt" 2>&1; ba=$?
mklog() {  # mklog <T0 offset s> <minutes ago it ended> <lines...>: a stand-in E200 sitting-1 log on the box
  local t=$((NOW - $1)) m=$2; shift 2; local d=$TREE/build/e200/T$t; mkdir -p "$d"
  { echo "$(tsm $((m + 40))) session start (T0 $t = x; E200 sitting 1, plan full; a desk-test stand-in log)"
    for ln in "$@"; do echo "$(tsm $((m + 1))) $ln"; done; echo "$(tsm "$m") session end (T0 $t)"; } > "$d/session.log"
  touch -d @"$((NOW - m * 60))" "$d/session.log"; echo "$d"
}
LC=$(mklog 5000 45 "train blocks started: 1 of 4 (A); complete: 0 (none); train processes recorded: 20" "the trains ended without a registered stop: run_session.sh rc 1, no stop recorded (a crash)")
RB_OUT="$S/out-b" bash "$R/s09_reads_e200.sh" 2 > "$S/bc.txt" 2>&1; bc=$?; rm -rf "${LC:?}"
LS=$(mklog 5100 45 "train blocks started: 2 of 4 (A B); complete: 1 (A); train processes recorded: 170" "stop: watch_e200: the clock (C3): 3 train processes in a row off 800 MHz after their first 1.5 s (the last: block A T1 process 7 read [700.0] MHz) (names the card)" "SITTING-RESULT: smoke passed; train blocks complete 1 (A); card stop yes: watch_e197: minion clock 500.0")
RB_OUT="$S/out-b" bash "$R/s09_reads_e200.sh" 2 > "$S/bs.txt" 2>&1; bs=$?; rm -rf "${LS:?}"
c1=$(cfgcalls)
LG=$(mklog 5200 45 "the runner's smoke gate: failed (14 launches, rates 5e+11-5e+11)" "GATE-STOP: no block of trains.tsv began (smoke gate failed (launches 14))")
RB_OUT="$S/out-a" bash "$R/s11_session_e200.sh" 1 > "$S/sg.txt" 2>&1; sg=$?; rm -rf "${LG:?}"
stopline "$S/ba.txt"; stopline "$S/bc.txt"; stopline "$S/bs.txt"; stopline "$S/sg.txt"
ok "$yb.$ba.$(has 'no E200 sitting 1 on this box' "$S/ba.txt").$bc.$(has 'a crash' "$S/bc.txt").$bs.$(has 'sitting 2 needs a dated amendment' "$S/bs.txt").$((c1 - c0)).$sg.$(has 'smoke failed today' "$S/sg.txt").$(has 'LAUNCHED' "$S/sg.txt")" \
  "0.10.1.10.1.10.1.0.10.1.0" "BA no sitting 1, BC a crashed sitting 1, BS a sitting 1 whose stop named the card: step 7 refused (10) each, no config read sent; SG sitting 1 again on a smoke-failed day: 10"

step "DG7, DG9. a day whose E200 log holds the die gate's GATE-STOP (E200.md 9: no sitting that day; fix-e200, verify-e200's F3)"
LD=$(mklog 5300 45 "the die gate, read 31 (rc 0): 5 sample(s), the highest minshire[0] 58 C: HELD (the gate: every sample at or below 57 C)" "GATE-STOP: the die gate: the shires' mean did not read 57 C or less within 600 s of reads after the first card command (E200.md 9): no sitting today, no train run")
mkdir -p "$S/out-dg"; win "$S/out-dg" 1; cp -p "$S/out-a/e200-built.txt" "$S/out-a/e200-1-dry-ok.txt" "$S/out-dg/"
c0=$(cfgcalls)
RB_OUT="$S/out-dg" bash "$R/s09_reads_e200.sh" 1 > "$S/dg7.txt" 2>&1; dg7=$?
c1=$(cfgcalls)
restamp "$S/out-a" 1
RB_OUT="$S/out-a" bash "$R/s11_session_e200.sh" 1 > "$S/dg9.txt" 2>&1; dg9=$?
rm -rf "${LD:?}"
stopline "$S/dg7.txt"; stopline "$S/dg9.txt"
ok "$dg7.$(has 'die gate held it off today' "$S/dg7.txt").$((c1 - c0)).$([ -e "$S/out-dg/e200-1-first.txt" ] && echo stamped || echo none).$dg9.$(has 'die gate held it off today' "$S/dg9.txt").$(has 'LAUNCHED' "$S/dg9.txt")" \
  "10.1.0.none.10.1.0" "DG7 step 7 on a day whose E200 log holds the die gate's GATE-STOP: refused (10), no card command, nothing stamped; DG9 step 9 that day: refused (10), nothing launched"

step "Q1-Q4. THE QUIET DESK FLAG and THE P2 COUNT"
bash "$R/quiet_e200.sh" lower e200-desktest > /dev/null 2>&1
RB_OUT="$S/out-a" bash "$R/s05_look_e200.sh" > "$S/q1.txt" 2>&1; q1=$?
RB_OUT="$S/out-a" bash "$R/s11_session_e200.sh" 1 > "$S/q1b.txt" 2>&1; q1b=$?
echo "e194 another-lane 2026-11-16 00:13:37 PST" > "$RB_QUIET"
bash "$R/quiet_e200.sh" raise e200-desktest > "$S/q2.txt" 2>&1; q2=$?; q2f=$(cut -d' ' -f1 "$RB_QUIET")
RB_OUT="$S/out-a" bash "$R/s07_sync_e200.sh" > "$S/q2b.txt" 2>&1; q2b=$?
bash "$R/quiet_e200.sh" lower e200-desktest > "$S/q3.txt" 2>&1; q3=$?; q3f=$([ -e "$RB_QUIET" ] && echo kept || echo removed)
rm -f "$S/quiet-flag"
bash "$R/quiet_e200.sh" raise e200-desktest > "$S/q4r.txt" 2>&1; q4r=$?
cp /bin/sleep "$BB/x_host"; ( cd "$BOXH" && exec "$BB/x_host" 30 ) > /dev/null 2>&1 &
XH=$!; sleep 1
c0=$(grep -c LAUNCHED "$S/calls.log" 2>/dev/null || echo 0)
restamp "$S/out-a" 1
RB_OUT="$S/out-a" bash "$R/s11_session_e200.sh" 1 > "$S/q4.txt" 2>&1; q4=$?
kill "$XH" 2>/dev/null; wait "$XH" 2>/dev/null; rm -f "$BB/x_host"
stopline "$S/q1.txt"; stopline "$S/q2b.txt"; stopline "$S/q4.txt"
ok "$q1.$(has 'THE QUIET DESK FLAG is not raised' "$S/q1.txt").$q1b.$q2.$(has 'another flag is up' "$S/q2.txt").$q2f.$q2b.$(has "not E200's" "$S/q2b.txt").$q3.$q3f.$q4r.$q4.$(has 'the P2 count is not 0 after 5 reads' "$S/q4.txt").$(has 'LAUNCHED' "$S/q4.txt")" \
  "10.1.10.10.1.e194.10.1.10.kept.0.10.1.0" "Q1 the look and the launch with the flag down: 10; Q2 another lane's flag never overwritten, and a step refuses beside it (10); Q3 never removed by E200 (10); Q4 a device-named process of ours on the box: step 9's P2 count refuses (10), nothing launched"

step "LA. step 9 launches THE REAL session_e200.sh; the wait finds it by its real script name"
echo '{"etwho_check_sleep_s": 25, "etwho_check_held": true}' > "$ST/scenario.json"   # under the wrapper's own 30 s bound on et-who
restamp "$S/out-a" 1
RB_OUT="$S/out-a" bash "$R/s11_session_e200.sh" 1 > "$S/la.txt" 2>&1; la=$?
grep -E '^rest:|LAUNCHED|STOP' "$S/la.txt" | cut -c1-200
RB_WAIT_LOOP_S=5 RB_OUT="$S/out-a" bash "$R/s20_wait_e200.sh" 1 > "$S/wa1.txt" 2>&1; wa1=$?
RB_OUT="$S/out-a" bash "$R/s11_session_e200.sh" 1 > "$S/la2.txt" 2>&1; la2=$?
wa2=17; k=0; while [ "$wa2" -eq 17 ] && [ "$k" -lt 6 ]; do RB_OUT="$S/out-a" bash "$R/s20_wait_e200.sh" 1 > "$S/wa2.txt" 2>&1; wa2=$?; k=$((k + 1)); done
grep -E 'GATE-STOP|RUN-|MANIFEST' "$S/wa2.txt" | cut -c1-220
T0=$(cat "$S/out-a/e200-1-T0.txt" 2>/dev/null)
ok "$la.$(has 'rest: ' "$S/la.txt").$wa1.$(has 'RUN-RUNNING e200-1' "$S/wa1.txt").$la2.$(has 'a card session of ours already runs' "$S/la2.txt").$wa2.$(has 'GATE-STOPPED e200-1' "$S/wa2.txt").$(has 'MANIFEST-WRITTEN' "$S/wa2.txt").$(has 'GATE-STOP: the card is not free: et-who --check exit 1 .*(no device opened by the session)' "$S/wa2.txt")" \
  "0.1.17.1.10.1.16.1.1.1" "LA launched; RUN-RUNNING by its real name; a second launch refused while it runs; then GATE-STOPPED at the holder check (no device opened by the session), the manifest written"

step "CD. step 11 on a session that ran with the wrapper's desk-test variables, outside a desk test"
mkdir -p "$S/out-cd"; cp -p "$S/out-a/window.env" "$S/out-a/e200-1-T0.txt" "$S/out-a/box-login-aifoundry2.txt" "$S/out-cd/"
rm -rf "${T:?}/docs/reports/gate-stops"
RB_OUT="$S/out-cd" bash "$R/s22_collect_e200.sh" 1 > "$S/cd.txt" 2>&1; cdr=$?
stopline "$S/cd.txt"
ok "$cdr.$(has 'the session ran with the wrapper.s desk-test variables' "$S/cd.txt").$(cd "$T" && find docs/reports/gate-stops -path '*e200*' -type f 2>/dev/null | grep -c .)" "16.1.0" \
  "CD a DESKTEST session collected outside a desk test: refused (16), nothing written"

step "C, C2-C5. step 11 on that session"
RB_DESKTEST=1 RB_OUT="$S/out-a" bash "$R/s22_collect_e200.sh" 1 > "$S/c.txt" 2>&1; c=$?
grep -E 'COPY-BACK|COLLECTED|STOP|collected ' "$S/c.txt" | cut -c1-240
GSD=docs/reports/gate-stops/$TODAY-e200-regfile-sitting-1-T$T0-aifoundry2
gsd=$([ -s "$T/$GSD/SHA256SUMS" ] && [ -s "$T/$GSD/facts-e200-1.json" ] && echo 1 || echo 0)
gsx=$(cd "$T" && find docs/reports/data -path '*e200*' 2>/dev/null | grep -c .)
RB_DESKTEST=1 RB_OUT="$S/out-a" bash "$R/s22_collect_e200.sh" 1 > "$S/c2.txt" 2>&1; c2=$?
mkdir -p "$S/out-c3"; cp -p "$S/out-a/window.env" "$S/out-a/e200-1-T0.txt" "$S/out-a/box-login-aifoundry2.txt" "$S/out-c3/"
DSD=$TREE/build/e200/T$T0; cp -p "$DSD/session.log" "$S/sl.keep"; printf 'x' >> "$DSD/session.log"
rm -rf "${T:?}/docs/reports/gate-stops"
RB_DESKTEST=1 RB_OUT="$S/out-c3" bash "$R/s22_collect_e200.sh" 1 > "$S/c3.txt" 2>&1; c3=$?
cp -p "$S/sl.keep" "$DSD/session.log"
RB_DESKTEST=1 RB_OUT="$S/out-c3" bash "$R/s22_collect_e200.sh" 1 > "$S/c4.txt" 2>&1; c4=$?
T5=$(( $(date +%s) - 3000 )); D5=$TREE/build/e200/T$T5; mkdir -p "$D5" "$S/out-c5"; win "$S/out-c5" 1; cp -p "$S/out-a/box-login-aifoundry2.txt" "$S/out-c5/"
{ echo "$(date -d @"$T5" '+%Y-%m-%d %H:%M:%S %Z') session start (T0 $T5 = x; E200 sitting 1, plan full; a desk-test stand-in log)"
  echo "$(date -d @"$((T5 + 60))" '+%Y-%m-%d %H:%M:%S %Z') train blocks started: 2 of 4 (A B); complete: 1 (A); train processes recorded: 170"
  echo "$(date -d @"$((T5 + 120))" '+%Y-%m-%d %H:%M:%S %Z') GATE-STOP: a desk-test stand-in line beside blocks begun"
  echo "$(date -d @"$((T5 + 180))" '+%Y-%m-%d %H:%M:%S %Z') session end (T0 $T5)"; } > "$D5/session.log"
( cd "$D5" && sha256sum session.log > MANIFEST.sha256 ); echo 8 > "$D5/wrapper.rc"; echo "$T5" > "$S/out-c5/e200-1-T0.txt"
RB_DESKTEST=1 RB_OUT="$S/out-c5" bash "$R/s22_collect_e200.sh" 1 > "$S/c5.txt" 2>&1; c5=$?
rm -rf "${D5:?}"
stopline "$S/c2.txt"; stopline "$S/c4.txt"; stopline "$S/c5.txt"
ok "$c.$(has 'COPY-BACK EXACT' "$S/c.txt").$(has 'COLLECTED ' "$S/c.txt").$(has "collected the gate stop's record $GSD" "$S/c.txt").$gsd.$gsx.$c2.$(has 'exists already' "$S/c2.txt").$c3.$(has 'COPY-BACK NOT EXACT' "$S/c3.txt").$c4.$(has 'e200-raw/T[0-9]* exists already' "$S/c4.txt").$c5.$(has 'does not say clearly how the session ended' "$S/c5.txt").$([ -e "$S/out-c5/e200-raw/T$T5" ] && echo copied || echo none)" \
  "0.1.1.1.1.0.10.1.16.1.10.1.16.1.none" "C COPY-BACK EXACT into the gate stop's record (nothing under docs/reports/data), the desk-path gate clean, HISTORY OK; C2 again: 10; C3 a changed box file: NOT EXACT (16); C4 its RB_OUT again: 10; C5 an unclear log: 16"

step "RT. the retry in a new RB_OUT"
mkdir -p "$S/out-rt"; win "$S/out-rt" 1
RB_OUT="$S/out-rt" bash "$R/s05_look_e200.sh" > /dev/null 2>&1
rb6=17; k=0; while [ "$rb6" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-rt" bash "$R/s08_build_e200.sh" wait > "$S/rt6.txt" 2>&1; rb6=$?; k=$((k + 1)); done
RB_OUT="$S/out-rt" bash "$R/s10_dry_e200.sh" start > /dev/null 2>&1
ry=17; k=0; while [ "$ry" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-rt" bash "$R/s10_dry_e200.sh" wait > "$S/rty.txt" 2>&1; ry=$?; k=$((k + 1)); done
RB_OUT="$S/out-rt" bash "$R/s09_reads_e200.sh" 1 > "$S/rt7.txt" 2>&1; r7=$?
RB_OUT="$S/out-rt" bash "$R/s11_session_e200.sh" 1 > "$S/rt.txt" 2>&1; rt=$?
grep -E '^rest:|LAUNCHED|STOP|sitting 1:' "$S/rt7.txt" "$S/rt.txt" | cut -c1-200
rw=17; k=0; while [ "$rw" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-rt" bash "$R/s20_wait_e200.sh" 1 > "$S/rtw.txt" 2>&1; rw=$?; k=$((k + 1)); done
T0R=$(cat "$S/out-rt/e200-1-T0.txt" 2>/dev/null)
echo '{}' > "$ST/scenario.json"
ok "$rb6.$ry.$r7.$(has 'rest: ' "$S/rt7.txt").$rt.$([ -n "$T0R" ] && [ "$T0R" != "$T0" ] && echo 1 || echo 0).$rw.$(has 'GATE-STOPPED e200-1' "$S/rtw.txt")" "0.0.0.1.0.1.16.1" \
  "RT the retry: the build's wait, the dry pass, step 7 (the rest rule skips the session that opened no device), step 9 launched anew; its wait GATE-STOPPED (16)"

if [ -n "$RP" ] && [ -d "$RP/P" ]; then
  step "WR. the wait on the real-path desk test's own sessions"
  mkdir -p "$S/out-wr"; win "$S/out-wr" 1
  wr_run() {  # wr_run <case>: copy that case's session onto the stand-in box, write its T0, run the wait
    local src t
    src=$(ls -d "$RP/$1"/tree/build/e200/T[0-9]* 2>/dev/null | grep -v -- '-dry$' | head -n 1)
    [ -n "$src" ] || { echo "   (no real-path session for $1)"; WR=99; return; }
    t=$(basename "$src"); t=${t#T}
    rm -rf "${TREE:?}/build/e200/T$t"; cp -rp "$src" "$TREE/build/e200/T$t"
    mkdir -p "$TREE/build/q141k"; echo "$t" > "$TREE/build/q141k/e200-1.T0"; echo "$t" > "$S/out-wr/e200-1-T0.txt"
    RB_OUT="$S/out-wr" bash "$R/s20_wait_e200.sh" 1 > "$S/wr-$1.txt" 2>&1; WR=$?
    grep -E 'RUN-|MANIFEST|GATE-STOPPED|STOPPED|CRASHED|HUNG|has ended' "$S/wr-$1.txt" | cut -c1-200 | sed 's/^/   /'
    WRT=$t
  }
  wr_run P; wp=$WR; tp=${WRT:-}
  wr_run S1; ws=$WR
  wr_run G1; wg=$WR
  wr_run X1; wx=$WR
  wr_run HG; wh=$WR
  ok "$wp.$ws.$(has 'STOPPED e200-1' "$S/wr-S1.txt").$wg.$(has 'GATE-STOPPED e200-1' "$S/wr-G1.txt").$wx.$(has 'CRASHED e200-1' "$S/wr-X1.txt").$wh.$(has 'HUNG e200-1' "$S/wr-HG.txt")" "0.0.1.16.1.16.1.16.1" \
    "WR the real sessions: P whole (0); S1 a stop by hand: STOPPED (0); G1 the kit's smoke check: GATE-STOPPED (16); X1 a crash: CRASHED (16); HG a hung host: HUNG (16)"
  step "CR, CR3-CR5. step 11 on the real-path P session, its data committed in the scratch repository, then step 13"
  mkdir -p "$S/out-cr"; win "$S/out-cr" 1; cp -p "$S/out-a/box-login-aifoundry2.txt" "$S/out-cr/"
  echo "$tp" > "$S/out-cr/e200-1-T0.txt"
  RB_DESKTEST=1 RB_OUT="$S/out-cr" bash "$R/s22_collect_e200.sh" 1 > "$S/cr1.txt" 2>&1; cr1=$?
  grep -E 'COPY-BACK|COLLECTED|STOP' "$S/cr1.txt" | cut -c1-220
  DD=docs/reports/data/$TODAY-e200-regfile-sitting-1-aifoundry2
  RB_OUT="$S/out-cr" bash "$R/s24_reduce_e200.sh" 1 > "$S/cr0.txt" 2>&1; cr0=$?
  stopline "$S/cr0.txt"
  printf '# E200 sitting 1: a desk test stand-in README (never a lab file)\n' > "$T/$DD/README.md"
  $G add --sparse "$DD" > /dev/null 2>&1; $G commit -q -m "desk test: the real-path sitting 1's data committed"
  RB_OUT="$S/out-cr" bash "$R/s24_reduce_e200.sh" 1 > "$S/cr2.txt" 2>&1; cr2=$?
  grep -E 'CHECKS READ|reduced after|STOP|box.s manifest' "$S/cr2.txt" | cut -c1-260
  ok "$cr0.$(has 'is not committed' "$S/cr0.txt").$cr1.$(has 'COLLECTED ' "$S/cr1.txt").$cr2.$([ -s "$S/out-cr/regfile-e200-s1.json" ] && echo 1 || echo 0).$([ -s "$S/out-cr/checks-e200-1.json" ] && echo 1 || echo 0)" "10.1.0.1.0.1.1" \
    "CR step 13 before the data commit refused (10); the real session collected; after its data commit the registered reducer and the checker ran (regfile-e200-s1.json, checks-e200-1.json)"
  cp -p "$T/$DD/run/stderr.txt" "$S/stderr.keep"; printf 'x' >> "$T/$DD/run/stderr.txt"
  mkdir -p "$S/out-cr3"; win "$S/out-cr3" 1
  RB_OUT="$S/out-cr3" bash "$R/s24_reduce_e200.sh" 1 > "$S/cr3.txt" 2>&1; cr3=$?
  cp -p "$S/stderr.keep" "$T/$DD/run/stderr.txt"
  awk '/^## Re-make it/ {f = 1; next} f && /^## / {f = 0} f && /^    / {print}' "$T/$E/DATA-README-FORM-e200.md" | sed -n '2,$p' | sed 's/^    //' > "$S/remake.sh"
  echo "   the form's re-make commands ($(grep -c . "$S/remake.sh") lines after its first, which sets D and R):"; sed 's/^/     | /' "$S/remake.sh"
  rm -rf "${S:?}/remake"; mkdir -p "$S/remake"
  ( cd "$T" && D="$DD" R="$S/remake" bash -e "$S/remake.sh" ) > "$S/cr5.txt" 2>&1; cr5=$?
  grep -E 'CHECKS READ|box.s bytes|Error' "$S/cr5.txt" | cut -c1-200
  printf 'x' >> "$T/$DD/run/stderr.txt"; $G add --sparse "$DD/run/stderr.txt"; $G commit -q -m "desk test: a committed change to a data file, SHA256SUMS left"
  cr4c=$($G log -1 --format=%s | grep -c 'SHA256SUMS left')
  mkdir -p "$S/out-cr4"; win "$S/out-cr4" 1
  RB_OUT="$S/out-cr4" bash "$R/s24_reduce_e200.sh" 1 > "$S/cr4.txt" 2>&1; cr4=$?
  [ "$cr4c" -eq 1 ] && $G reset -q --hard HEAD~1
  stopline "$S/cr3.txt"; stopline "$S/cr4.txt"
  ok "$cr3.$(has 'uncommitted changes' "$S/cr3.txt").$cr4.$(has 'does not read every entry OK' "$S/cr4.txt").$cr5.$(has 'CHECKS READ: ' "$S/cr5.txt").$(has "not the box's bytes" "$S/cr5.txt").$(cmp -s "$S/remake/regfile-e200-s1.json" "$S/out-cr/regfile-e200-s1.json" && echo SAME || echo DIFFERENT)" \
    "16.1.16.1.0.1.0.SAME" "CR3 a data file changed, not committed: 16; CR4 a committed change SHA256SUMS does not hold: 16; CR5 the README form's own commands: the box's bytes, the checker, regfile-e200-s1.json the same as step 13's, byte for byte"
  if [ -d "$RP/P2" ]; then
    step "CR2. the real-path P2 session as sitting 2's data, then step 13 for sitting 2: the pooled reduction"
    src=$(ls -d "$RP/P2"/tree/build/e200/T[0-9]* | grep -v -- '-dry$' | head -n 1); t2=$(basename "$src"); t2=${t2#T}
    rm -rf "${TREE:?}/build/e200/T$t2"; cp -rp "$src" "$TREE/build/e200/T$t2"
    mkdir -p "$S/out-cr2"; win "$S/out-cr2" 2; cp -p "$S/out-a/box-login-aifoundry2.txt" "$S/out-cr2/"; echo "$t2" > "$S/out-cr2/e200-2-T0.txt"
    RB_DESKTEST=1 RB_OUT="$S/out-cr2" bash "$R/s22_collect_e200.sh" 2 > "$S/cr21.txt" 2>&1; cr21=$?
    DD2=docs/reports/data/$TODAY-e200-regfile-sitting-2-aifoundry2
    printf '# E200 sitting 2: a desk test stand-in README (never a lab file)\n' > "$T/$DD2/README.md"
    $G add --sparse "$DD2" > /dev/null 2>&1; $G commit -q -m "desk test: the real-path sitting 2's data committed"
    RB_OUT="$S/out-cr2" bash "$R/s24_reduce_e200.sh" 2 > "$S/cr22.txt" 2>&1; cr22=$?
    grep -E 'CHECKS READ|reduced after|STOP' "$S/cr22.txt" | cut -c1-260
    u=$(/usr/bin/python3 -I -B -c 'import json,sys; t=json.load(open(sys.argv[1]))["trains"]; print(t["T1"]["units"], t["T7"]["units"], t["T14"]["units"])' "$S/out-cr2/regfile-e200.json" 2>/dev/null)
    ok "$cr21.$cr22.$u" "0.0.182 9 9" "CR2 sitting 2 collected and committed; step 13 for sitting 2: the pooled reduction, T1 67 + 115 = 182 units, T7 and T14 9 each"
    rm -rf "${T:?}/$DD2"; $G reset -q --hard HEAD~1
  fi
  rm -rf "${T:?}/$DD"; $G reset -q --hard HEAD~1
else
  echo; echo "== WR, CR, CR2: NOT RUN (no real-path desk test scratch given)"
fi

step "Z. nothing of this test left on the stand-in box"
left=$("$REAL_PGREP" -u "$(id -u)" -f 'session_e200\.sh|run_trains\.py|fake_card_e200\.py' | while read -r q; do c=$(readlink "/proc/$q/cwd" 2>/dev/null); case "$c/" in "$BOXH"/*) echo "$q" ;; esac; done | grep -c .)
ok "$left" "0" "Z no session, runner or stand-in of this test left running on the stand-in box"
echo; echo "SELFTEST-RB-E200 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
[ "$fail" -eq 0 ]
