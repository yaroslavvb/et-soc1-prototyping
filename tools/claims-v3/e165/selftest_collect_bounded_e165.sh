#!/bin/bash
# E165 (Q141(g)), amendment A2-7: the bounded collector's desk test. It never reaches a lab box: a stand-in named ssh, first on PATH, takes every ssh
# the collector and its rsyncs make and runs the remote command locally in a stand-in box directory (or hangs, or prints a Tailscale check link, by case).
# The real rsync, timeout(1), the code-path check, the scorer and the D report run as they will at collection. From the top of the lab tree:
#
#   bash tools/claims-v3/e165/selftest_collect_bounded_e165.sh <a new, empty scratch dir> <a dry queue's dir: runs/, queue.out, slot.txt>
#
# Cases: (a) the probe meets a Tailscale check link: stopped in about 15 s, exit 5, nothing written; (b) the probe hangs: the same; (c) the probe
# answers and the first rsync's remote side hangs: stopped at the per-call bound (E165_REMOTE_TIMEOUT_S=4 here), exit 3, no process left;
# (d) a non-empty scratch dir and an existing data dir are refused, exit 2; (e) the whole collection of a dry queue's records through the stand-in:
# exit 0, the box's files checked (the three binaries are desk stand-ins, so exactly those 3 differ), the path check kept, scored, the D report;
# (f) A2-8: the registered collect_e165.sh on the same records: its session list takes s1.out, its scorer stops there, and it still exits 0.
# SPDX-License-Identifier: Apache-2.0
set -u
T=${1:?usage: selftest_collect_bounded_e165.sh <new empty scratch dir> <dry queue dir>}
DRY=${2:?usage: selftest_collect_bounded_e165.sh <new empty scratch dir> <dry queue dir>}
[ -d "$T" ] && [ -n "$(ls -A "$T" 2>/dev/null)" ] && { echo "refused: $T is not empty"; exit 2; }
[ -d tools/claims-v3/e165 ] || { echo "refused: run from the top of the lab tree"; exit 2; }
TOP=$(pwd)
mkdir -p "$T/bin" "$T/box/claude/et-soc1-prototyping/build/e165" "$T/box/claude/work" || exit 2
cat > "$T/bin/ssh" <<'EOS'
#!/bin/bash
# the desk test's stand-in for ssh: it never connects anywhere
[ -n "${E165_FAKE_LOG:-}" ] && [ -n "${E165_FAKE_HOME:-}" ] || { echo "fake ssh: not inside the desk test" >&2; exit 255; }
echo "ssh $*" >> "$E165_FAKE_LOG"
while [ $# -gt 0 ]; do case "$1" in -o|-p|-i|-l|-F) shift 2 ;; -*) shift ;; *) break ;; esac; done
host=$1; shift
[ "$host" = aifoundry2 ] || { echo "fake ssh: unexpected host $host" >&2; exit 255; }
case "${E165_FAKE_SSH:-ok}" in
  tailscale) echo "# Tailscale SSH requires an additional check." >&2
             echo "# To authenticate, visit: https://login.tailscale.com/a/desk-test-only" >&2; exec sleep 3617 ;;
  hang) exec sleep 3617 ;;
  hang-remote) [ "$*" = true ] && exit 0; exec sleep 3617 ;;
esac
[ "$*" = true ] && exit 0
[ "$*" = "bash -s" ] && { HOME="$E165_FAKE_HOME" exec bash -s; }
# as a real ssh does: the words joined into one command line, split again by the remote side's shell (rsync's --rsync-path is one word)
cd "$E165_FAKE_HOME" && eval "exec $*"
EOS
chmod +x "$T/bin/ssh"
H="$T/box/claude/et-soc1-prototyping"
ln -s "$TOP/tools" "$H/tools"
ln -s "$TOP/docs" "$H/docs"
rsync -a "$DRY/runs/" "$H/build/e165/runs/"
cp "$DRY/queue.out" "$H/build/e165/queue.out"
cp "$DRY/slot.txt" "$T/box/claude/work/q141-a2-e165-slot.txt"
for b in build/ccheck/b/host/sparsity_host build/sparsity_t2/kernel/sparsity.elf build/ettelem-hpl/ettelem; do
  mkdir -p "$(dirname "$H/$b")" && echo "desk test stand-in" > "$H/$b"
done
export PATH="$T/bin:$PATH" E165_FAKE_LOG="$T/ssh-calls.txt" E165_FAKE_HOME="$T/box"
[ "$(command -v ssh)" = "$T/bin/ssh" ] || { echo "refused: the stand-in is not the ssh on PATH"; exit 2; }
echo "# E165 bounded collector, desk test: $(date '+%a %d %b %Y %H:%M:%S %Z'); ssh on PATH is the stand-in; rsync $(rsync --version | head -1 | awk '{print $3}'); timeout $(command -v timeout gtimeout | head -1)"
fails=0
check() { if [ "$1" = 1 ]; then echo "ok   $2"; else echo "FAIL $2"; fails=$((fails + 1)); fi; }
left() { pgrep -f 'sleep 3617' > /dev/null && echo yes || echo no; }
run() {   # $1 case, then env assignments; prints rc and seconds
  local c=$1; shift
  local t0=$(date +%s)
  env "$@" bash tools/claims-v3/e165/collect_e165_bounded.sh "$T/$c/raw" "$T/$c/data" > "$T/$c.out" 2>&1
  local rc=$?
  echo "$rc $(( $(date +%s) - t0 ))"
}
mkdir -p "$T/a" "$T/b" "$T/c" "$T/d" "$T/e"

read rc s < <(run a E165_FAKE_SSH=tailscale)
check $([ "$rc" = 5 ] && [ "$s" -le 20 ] && grep -q 'asks for a Tailscale check' "$T/a.out" && [ ! -e "$T/a/raw" ] && [ ! -e "$T/a/data" ] && [ "$(left)" = no ] && echo 1 || echo 0) \
  "(a) the probe meets a Tailscale check link: rc $rc after $s s; '$(grep -m1 'stopped' "$T/a.out" | cut -c1-120)'; nothing written; no ssh left: $( [ "$(left)" = no ] && echo yes || echo NO)"
read rc s < <(run b E165_FAKE_SSH=hang)
check $([ "$rc" = 5 ] && [ "$s" -le 20 ] && grep -q 'did not answer' "$T/b.out" && [ ! -e "$T/b/raw" ] && [ "$(left)" = no ] && echo 1 || echo 0) \
  "(b) the probe hangs: rc $rc after $s s; '$(grep -m1 'stopped' "$T/b.out" | cut -c1-100)'; nothing written; no ssh left"
read rc s < <(run c E165_FAKE_SSH=hang-remote E165_REMOTE_TIMEOUT_S=4)
check $([ "$rc" = 3 ] && [ "$s" -le 20 ] && grep -q 'rsync of the runs failed or ran past 4 s' "$T/c.out" && [ ! -e "$T/c/data" ] && [ "$(left)" = no ] && echo 1 || echo 0) \
  "(c) the probe answers, the first rsync's remote side hangs: rc $rc after $s s (bound 4 s + 10 s kill); '$(grep -m1 'stopped' "$T/c.out")'; no data dir; no ssh or rsync left"
mkdir -p "$T/d/raw" && touch "$T/d/raw/x"
read rc s < <(run d)
r1=$rc; o1=$(head -1 "$T/d.out")
rm -f "$T/d/raw/x"; mkdir -p "$T/d/data/aifoundry2"
read rc s < <(run d)
check $([ "$r1" = 2 ] && [ "$rc" = 2 ] && grep -q 'aifoundry2 exists' "$T/d.out" && echo 1 || echo 0) "(d) refusals: a non-empty scratch dir rc $r1 ('$o1'), an existing data dir rc $rc ('$(head -1 "$T/d.out")')"
read rc s < <(run e)
ok=1
[ "$rc" = 0 ] || ok=0
grep -q 'CHECK-PATH: PASS' "$T/e/data/logs/path-check.txt" 2>/dev/null || ok=0
grep -q '^box files: 3 differ' "$T/e/data/logs/box-files-check.txt" 2>/dev/null || ok=0
nd=$(grep -c '^DIFFERS build/' "$T/e/data/logs/box-files-check.txt" 2>/dev/null); [ "$nd" = 3 ] || ok=0
[ -f "$T/e/data/results.json" ] && [ -f "$T/e/data/d-both.json" ] || ok=0
nr=$(python3 -B -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["runs"], d["runs_complete"], d["dry"], d["score"].get("tiles_scored"))' "$T/e/data/results.json" 2>/dev/null)
nd2=$(python3 -B -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["passes_counted"], d.get("everything_but_D_identical"), {k: v["passes_below"] for k, v in d["anchors"].items()})' "$T/e/data/d-both.json" 2>/dev/null)
[ "$nr" = "114 114 True 52" ] || ok=0
check $ok "(e) a dry queue's records collected through the stand-in: rc $rc after $s s; path check '$(tail -1 "$T/e/data/logs/path-check.txt" 2>/dev/null | cut -c1-40)'; box files: $nd differ, the 3 desk stand-in binaries; scored: runs, complete, dry, tiles scored = $nr; D report: passes, identical outside D, anchors' passes below 795 MHz = $nd2"
# (f) A2-8: the registered collect_e165.sh on the same records through the same stand-in (it has no bound, but the stand-in answers at once)
mkdir -p "$T/f"
t0=$(date +%s)
bash tools/claims-v3/e165/collect_e165.sh "$T/f/raw" "$T/f/data" > "$T/f.out" 2>&1
rc=$?; s=$(( $(date +%s) - t0 ))
sl=$(grep -c . "$T/f/data/score.txt" 2>/dev/null)
check $([ -f "$T/f/data/score.txt" ] && [ "$sl" = 0 ] && [ ! -f "$T/f/data/results.json" ] && grep -q 'NotADirectoryError' "$T/f.out" && grep -q 's1.out/session.json' "$T/f.out" && echo 1 || echo 0) \
  "(f) A2-8 shown: the registered collect_e165.sh on the same records: rc $rc after $s s, yet its scorer stopped on s1.out ('$(grep -m1 -o 'NotADirectoryError.*' "$T/f.out" | sed "s#$T#<scratch>/cbtest#g" | cut -c1-110)'): score.txt has $sl lines, results.json $( [ -f "$T/f/data/results.json" ] && echo exists || echo 'not written'); it ends '$(tail -1 "$T/f.out" | sed "s#$T#<scratch>/cbtest#g" | cut -c1-90)'"
echo "## the collector's output in case (e)"
cat "$T/e.out"
echo "## every ssh the collector made, all to the stand-in ($(wc -l < "$T/ssh-calls.txt" | tr -d ' ') calls)"
sed "s#$T#<scratch>#g" "$T/ssh-calls.txt"
echo "BOUNDED COLLECTOR DESK TEST: $([ $fails = 0 ] && echo ALL PASS || echo "$fails FAIL")"
exit $fails
