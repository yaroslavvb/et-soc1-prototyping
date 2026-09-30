#!/bin/bash
# remote.sh: the lab dashboard's read-only probe of one lab host (tools/lab/dashboard/DESIGN.md §2.3).
#
# collect.py sends it to each host as `nice -n 10 ionice -c3 bash -s` (over ssh, or locally on aifoundry2), after a
# preamble that sets the DASH_* variables below and ETLH, the text of tools/lab/et-lab-health rev 3. By hand:
#   DASH_ETLH_FILE=tools/lab/et-lab-health bash tools/lab/dashboard/remote.sh
# It prints "@@<section>" headers and plain lines, and ends with "@@end".
#
# What it never does: open a /dev/et* node, read a card attribute outside DESIGN.md §2.4 (never
# utilization_percent, resource*, config, and nothing but the link, err_stats and the root port's AER counters of a
# card in DASH_EXCLUDE_PCI), write anything (except the optional sample's stamp file), call tmux, or read anyone's
# files, command lines, groups or where they log in from (no RemoteHost, no `who -u`). Process names (ps comm) are
# turned into coarse categories here, on the host; only the categories leave it (DESIGN.md §6), except a card
# holder's program name, which et-who and et-usage show to every user of the host anyway. Every command runs under
# `timeout` with stdin from /dev/null, so one slow command costs its own section only and nothing reads this script
# from stdin by mistake.
#
# Parameters (all optional; collect.py validates them and quotes them):
#   DASH_TREE             the experiment tree under $HOME (nekko, or claude/et-soc1-prototyping)
#   DASH_EXCLUDE_PCI      PCI addresses of cards that are never touched (aifoundry1 card 0): driver counters only
#   DASH_HEALTH           1 (default): run et-lab-health; 0: skip it this run (collect.py runs it hourly)
#   DASH_SAMPLE_CARD      card id to sample (the optional telemetry step, DESIGN.md §2.6); empty: no sample
#   DASH_SAMPLE_PCI, DASH_SAMPLE_DEVNUM, DASH_SAMPLE_ETDEV, DASH_SAMPLE_LOCK, DASH_SAMPLE_BIN, DASH_SAMPLE_EVERY_MIN
#   DASH_SAMPLE_BOOT      on a host with several cards: the boot id a person confirmed the card numbering for
#   DASH_SAMPLE_SQ_PREV, DASH_SAMPLE_SQ_BOOT   the card's submission count at the last run, and that run's boot id
#   DASH_SAMPLE_DRY       1: run every gate and print the command, run nothing
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin; export PATH
LC_ALL=C; export LC_ALL
umask 077
set +e

# t <seconds> <command...>: no stdin, no stderr, stopped after <seconds> (and killed 2 s later)
t() { _ts=$1; shift; timeout -k 2 "$_ts" "$@" </dev/null 2>/dev/null; }
sec() { printf '@@%s\n' "$*"; }

ME=$(id -un); MYUID=$(id -u)
TREE=$HOME/${DASH_TREE:-nekko}
BOOT=$(cat /proc/sys/kernel/random/boot_id 2>/dev/null)
# The logind session this probe runs in (Tailscale SSH gives each command one), left out of the people counts.
MYSESS=$(sed -n 's#.*/session-\([A-Za-z0-9]*\)\.scope.*#\1#p' /proc/self/cgroup 2>/dev/null | head -1)
# The probe's own processes are left out of the process counts and categories too: its process session (everything
# it starts) and its ancestors: over ssh, the ssh server's chain; on aifoundry2 the collector's chain up to
# DASH_ANC_STOP (update.sh, or cron's sh above it), and no further, so that a person who runs update.sh now from a
# shell, an agent or tmux keeps those counted.
MYSID=$(cut -d' ' -f6 /proc/$$/stat 2>/dev/null)
ANC=" $$ "; _p=$PPID; _n=0
while [ -n "$_p" ] && [ "$_p" -gt 1 ] 2>/dev/null && [ $_n -lt 30 ]; do
  ANC="$ANC$_p "
  [ "$_p" = "${DASH_ANC_STOP:-}" ] && break
  _p=$(sed -n 's/^PPid:[[:space:]]*//p' "/proc/$_p/status" 2>/dev/null); _n=$((_n + 1))
done
# Device processes by executable name (ps comm), never by command line, as tools/claims-v3/lib.sh does.
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'
# The collector account's own framework runners and the workloads' run scripts, which take a card lock per launch:
# only the card sample's "experiment" gate uses this (bracketed, so the pattern never matches the `timeout ... pgrep`
# that carries it).
FW_RE='[t]ools/claims-v3|[q]ueue\.sh|[r]un_passes|[s]eries\.sh|[c]ard_run|[e]nergy\.sh|[w]orkloads/[^ ]*/run_|[t]ools/ettelem/[A-Za-z0-9_]+\.sh|(^|[ /])[r]un_[A-Za-z0-9_]+\.(sh|py)'
[ -z "${ETLH:-}" ] && [ -r "${DASH_ETLH_FILE:-}" ] && ETLH=$(cat "$DASH_ETLH_FILE")

sec meta
echo "host $(hostname)"
echo "now $(date +%s) $(date +%z)"
echo "uptime $(cut -d' ' -f1 /proc/uptime)"
echo "loadavg $(cut -d' ' -f1-4 /proc/loadavg)"
echo "nproc $(nproc 2>/dev/null)"
echo "boot $BOOT"
echo "kernel $(uname -r)"
echo "me $ME $MYUID"
echo "probe_session ${MYSESS:--}"
echo "tree $([ -d "$TREE" ] && echo yes || echo no)"

sec mem
awk '/^(MemTotal|MemAvailable):/ {print $1, $2}' /proc/meminfo

sec disk
t 10 df -P -B1 / /home | awk 'NR > 1 {print $6, $2, $3, $4}'

sec kernel
if [ -e /var/run/reboot-required ]; then
  echo "reboot_required $(stat -c %Y /var/run/reboot-required)"
  [ -r /var/run/reboot-required.pkgs ] && sort -u /var/run/reboot-required.pkgs | head -20 | sed 's/^/pkg /'
fi

sec systemd
echo "state $(t 10 systemctl is-system-running)"
t 10 systemctl --failed --no-legend --plain | awk 'NF {print "failed", $1}' | head -20

sec temps
for h in /sys/class/hwmon/hwmon*; do
  [ -r "$h/name" ] || continue
  n=$(cat "$h/name" 2>/dev/null)
  case "$n" in coretemp|k10temp|nvme) ;; *) continue ;; esac
  for i in "$h"/temp*_input; do
    [ -r "$i" ] || continue
    l=$(cat "${i%_input}_label" 2>/dev/null | tr ' ' '_')
    echo "$n ${l:-${i##*/}} $(cat "$i" 2>/dev/null)"
  done
done | head -40

sec sessions
t 10 loginctl list-sessions -o json | head -c 65536; echo
sec pts
for p in /dev/pts/[0-9]*; do [ -e "$p" ] && stat -c '%u %U %X' "$p" 2>/dev/null; done
sec procs
# Per user: processes, device processes (counts), and what the processes are, as coarse categories (DESIGN.md §6):
# agent (AI coding agents), build (compilers, linkers, make), sim (sys_emu), python, editor, shell (a shell, tmux or
# screen). The names are matched here and never printed. Left out: the probe's own logind session (its cgroup scope),
# process session and ancestors; and the user manager's own plumbing, which linger keeps running for an account nobody
# is using (systemd --user and (sd-pam) in init.scope, and services such as dbus, pipewire and the xdg portals: every
# .service unit under user@<uid>.service), unless it is a device process. What a person starts from a login or a tmux
# pane (a tmux server is a .scope unit under user@<uid>.service, or stays in the login's session scope) is counted.
# The cgroup column is given 512 characters: a column that is not the last is cut to its default width otherwise.
# "sessage <id> <s>": the age of each logind session's oldest process, so that a session with no terminal that is
# seconds old (an scp, an `ssh host cmd`) does not make its owner active.
t 10 ps -eo pid=,sid=,uid=,etimes=,user:32=,cgroup:512=,comm= | awk -v s="${MYSESS:-none}" -v sid="${MYSID:-none}" -v anc="$ANC" -v re="$DEV_COMM" '
  function cat(c) {
    if (c ~ /^(claude|codex|aider|gemini|goose|cursor-agent|opencode|crush|qwen|cline)$/) return "agent"
    if (c ~ /^(cc1|cc1plus|cc1obj|as|ld|ld\.[a-z]+|lld|mold|collect2|make|gmake|cmake|ctest|ninja|meson|gcc|g\+\+|c\+\+|cc|clang|clang\+\+|clang-[0-9]+|rustc|cargo|ccache|riscv64-.*|riscv32-.*|x86_64-linux-.*)$/) return "build"
    if (c == "sys_emu") return "sim"
    if (c ~ /^(python|python[23]|python[23]\.[0-9]+|ipython|ipython3|jupyter.*)$/) return "python"
    if (c ~ /^(vi|vim|nvim|emacs|emacs-.*|nano|micro|hx|helix|kak|joe|mcedit|code-server)$/) return "editor"
    if (c ~ /^(bash|sh|dash|zsh|fish|ksh|mksh|tcsh|csh|tmux.*|screen|SCREEN|mosh-server)$/) return "shell"
    return ""
  }
  index($6, "/session-" s ".scope") || $2 == sid || index(anc, " " $1 " ") {next}
  {c = $7; for (i = 8; i <= NF; i++) c = c " " $i
   if (c == "Runner.Worker") ci++
   if ($3 < 1000 || $3 == 65534) next
   if (match($6, /\/session-[^\/]*\.scope/)) {x = substr($6, RSTART + 9, RLENGTH - 15); if (!(x in age) || $4 + 0 > age[x]) age[x] = $4 + 0}
   if (($6 ~ /\/user@[0-9]+\.service\/init\.scope$/ || $6 ~ /\/user@[0-9]+\.service\/.*\.service$/) && c !~ re) next
   k = $3 " " $5; n[k]++; if (c ~ re) d[k]++
   x = cat(c); if (x != "" && !((k, x) in seen)) {seen[k, x] = 1; cats[k] = cats[k] (cats[k] == "" ? "" : ",") x}}
  END {for (k in n) print "procs", k, n[k], d[k] + 0, (cats[k] == "" ? "-" : cats[k])
       for (x in age) print "sessage", x, age[x]
       print "ci_jobs", ci + 0}'
sec etwho
# node, user, elapsed time and the program's name (the base name of its first argument, at most 15 characters, as
# ps comm): the rest of the command line is cut off here, before the output leaves the host
ew=$(t 10 et-who); ec=$?
echo "exit $ec"
printf '%s\n' "$ew" | awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {p = $5; sub(/.*\//, "", p); gsub(/[^A-Za-z0-9._+-]/, "", p)
  print "held", $1, $2, $4, (p == "" ? "-" : substr(p, 1, 15))}'
printf '%s\n' "$ew" | grep -q '^No process holds' && echo "idle"

sec usage
# et-usage (tools/lab/et-usage): who held each card, from the logger's files, as one JSON object: the last 26 hours
# (the page shows 24) and the daily totals of the last 7 days. Readable by every user, like et-who; "absent" until
# the logger is installed on this host. The output is cut at 2 MB; "rc" is et-usage's exit status (124: timed out).
if command -v et-usage >/dev/null 2>&1; then
  t 20 nice -n 10 et-usage --json --since 26h | head -c 2000000 | tr -d '\r'; rc=${PIPESTATUS[0]}; echo
  echo "rc $rc"
else
  echo "absent"
fi

sec cards
# DESIGN.md §2.4: the driver's own counters in host memory. A card in DASH_EXCLUDE_PCI gets only what et-lab-health
# already reads (link, err_stats, the root port's corrected-error count).
for dev in /sys/bus/pci/drivers/ET/0000:*; do
  [ -e "$dev" ] || continue
  b=${dev##*/}
  ex=0; for x in ${DASH_EXCLUDE_PCI:-}; do [ "$x" = "$b" ] && ex=1; done
  echo "card $b excluded=$ex"
  if [ "$ex" = 1 ]; then attrs="current_link_speed current_link_width"
  else attrs="devnum vendor device current_link_speed current_link_width max_link_speed max_link_width power_state enable"; fi
  for a in $attrs; do printf '%s %s %s\n' "$b" "$a" "$(tr '\n' ' ' < "$dev/$a" 2>/dev/null | sed 's/ *$//')"; done
  awk -v b="$b" -F': *' 'NF == 2 {print b, "ce", $1, $2 + 0}' "$dev/err_stats/ce_count" 2>/dev/null
  awk -v b="$b" -F': *' 'NF == 2 {print b, "uce", $1, $2 + 0}' "$dev/err_stats/uce_count" 2>/dev/null
  if [ "$ex" = 0 ]; then
    # submissions only (SQ*, HpSQ*): the completion queues also count the card's own asynchronous events
    awk -v b="$b" '$1 ~ /SQ[0-9]*:$/ {s += $2} END {print b, "mgmt_sq", s + 0}' "$dev/mgmt_vq_stats/msg_count" 2>/dev/null
    awk -v b="$b" '$1 ~ /SQ[0-9]*:$/ {s += $2} END {print b, "ops_sq", s + 0}' "$dev/ops_vq_stats/msg_count" 2>/dev/null
    awk -v b="$b" '$1 == "TOTAL_ERR_COR" {print b, "aer_card", $2}' "$dev/aer_dev_correctable" 2>/dev/null
  fi
  rp=$(readlink -f "$dev/..")
  awk -v b="$b" -v r="${rp##*/}" '$1 == "TOTAL_ERR_COR" {print b, "aer_port", $2, r}' "$rp/aer_dev_correctable" 2>/dev/null
done
for n in /dev/et*_mgmt; do [ -e "$n" ] && echo "node ${n#/dev/}"; done   # names only: nothing is opened
for l in /run/lock/etsoc-shire*.lock; do [ -e "$l" ] && echo "lockfile ${l##*/} $(stat -c %U "$l")"; done

sec guard
g=/run/et-board-clock-guard.ok
if [ -e "$g" ]; then
  if [ -r "$g" ]; then set -- $(cat "$g"); echo "marker $([ "${1:-}" = "$BOOT" ] && echo this_boot || echo other_boot) ${2:-} ${3:-} ${4:-}"
  else echo "marker unreadable"; fi
fi

sec nodewatch
nw=$HOME/nodewatch
if [ -r "$nw/heartbeat.log" ]; then
  echo "present"
  # one row per ten-minute slot (the first 15 characters of the time): lines, max load, min memavail (G), max
  # sessions (all users). Only these leave the host: nothing from the path[...] fields, and not the tmux, Claude and
  # own-session columns, which are about the account that runs nodewatch.
  t 10 tail -n 2900 "$nw/heartbeat.log" | awk '
    {k = substr($1, 1, 15); off = substr($1, 20, 5)
     ld = ""; mem = ""; sa = ""
     for (i = 2; i <= NF; i++) {
       split($i, kv, "=")
       if (kv[1] == "load") ld = kv[2] + 0
       else if (kv[1] == "memavail") {m = kv[2]; sub(/G$/, "", m); mem = m + 0}
       else if (kv[1] == "sessions") {split(kv[2], ss, "/"); sa = ss[2] + 0}
     }
     if (!(k in n)) {order[++no] = k; offs[k] = off; ml[k] = -1; mm[k] = 1e9; ma[k] = -1}
     n[k]++
     if (ld != "" && ld > ml[k]) ml[k] = ld
     if (mem != "" && mem < mm[k]) mm[k] = mem
     if (sa != "" && sa > ma[k]) ma[k] = sa
     last = $0}
    END {
     for (i = 1; i <= no; i++) {k = order[i]
       printf "b %s %s %d %s %s %s\n", k, offs[k], n[k], (ml[k] < 0 ? "-" : ml[k]), (mm[k] == 1e9 ? "-" : mm[k]), (ma[k] < 0 ? "-" : ma[k])}
     if (last != "") {
       split(last, f, " "); out = "last " f[1]
       for (i = 2; i in f; i++) if (f[i] ~ /^(boot|load|memavail)=/) out = out " " f[i]
         else if (f[i] ~ /^sessions=/) {v = f[i]; sub(/^sessions=[^\/]*\//, "", v); out = out " sessions=" v}
       print out}}'
  if [ -r "$nw/events.log" ]; then
    since=$(date -d '-48 hours' +%FT%T)
    # the time, the type and one word for the host's own events; LOGIN and LOGOUT only as counts (never from=, the
    # machine/login or argv)
    t 10 tail -n 5000 "$nw/events.log" | awk -v s="$since" '
      substr($1, 1, 19) < s {next}
      $2 == "LOGIN" {li++; next}
      $2 == "LOGOUT" {lo++; next}
      $2 == "REBOOT" {print "ev", $1, $2, "reboot"; next}
      $2 == "START" {print "ev", $1, $2, "start"; next}
      $2 == "WARN" {print "ev", $1, $2, "warn"; next}
      END {print "logins", li + 0, lo + 0}' | tail -n 200
  fi
else
  echo "absent"
fi

sec telemetry
# the newest experiment telemetry per card directory (build/claims-v3/<card>/...) and kind, from the last 7 days
for base in "$TREE/build/claims-v3" "$TREE/build/sparseparity-energy"; do
  [ -d "$base" ] || continue
  t 10 find "$base" -maxdepth 5 -mmin -10080 -type f \( -name 'tel-*.jsonl' -o -name tel.jsonl -o -name marks.jsonl -o -name energy.json \) -printf '%T@ %P\n' |
    grep -v -e '-dry/' -e '-raw/' | sort -rn |
    awk -v base="${base##*/}" '{split($2, p, "/"); card = (base == "claims-v3" ? p[1] : "host")
      f = p[length(p)]; kind = (f ~ /^tel-/ ? "ettelem" : (f == "tel.jsonl" ? "tel" : (f == "marks.jsonl" ? "marks" : "energy")))
      if (!((card, kind) in seen)) {seen[card, kind] = 1; print int($1), card, kind, base "/" $2}}'
done | head -40 | while read -r mt card kind rel; do
  echo "file $card $kind $mt $rel"
  # the newest line that carries a reading (a marks file ends with an "end" line that may have none)
  t 5 tail -n 60 "$TREE/build/$rel" | grep -E '"(die_c|board_w|summary|temp_c)"' | tail -n 1 | head -c 2048 | tr -d '\r' | sed 's/^/line /'; echo
done

sec manifest
t 10 et-lab-manifest | awk '$1 == "cpu" || $1 == "et_soc1" || $1 == "sha256" || $1 == "power" {print}' | cut -c1-200

sec health
if [ -n "${ETLH:-}" ] && [ "${DASH_HEALTH:-1}" = 1 ]; then
  t 20 env -i PATH=/usr/bin:/bin HOME="$HOME" LC_ALL=C nice -n 10 sh -c "$ETLH"
  echo "@@health-exit $?"
elif [ -n "${ETLH:-}" ]; then
  echo "@@health-exit skipped"   # collect.py keeps the last run's lines (it runs the check hourly)
else
  echo "@@health-exit none"
fi

if [ -n "${DASH_SAMPLE_CARD:-}" ]; then
  sec sample
  # The optional telemetry sample (DESIGN.md §2.6): every gate, in order; the first that fails stops it. A gate whose
  # own command fails (times out, errors) fails too. The slow checks come first and et-who last, so the moment the
  # card was seen free is as close as it can be to the lock.
  gate() { echo "gate $1 $2 ${3:-}"; }
  fail() { gate "$1" fail "$2"; s_ok=0; }
  s_ok=1
  ETD=/sys/bus/pci/drivers/ET
  b=${DASH_SAMPLE_PCI:-}
  ncards=0; for x in "$ETD"/0000:*; do [ -e "$x" ] && ncards=$((ncards + 1)); done
  multi=0; if [ "$ncards" -gt 1 ] || [ "$(hostname)" = aifoundry1 ]; then multi=1; fi
  # 1. the card: bound, not excluded, at the expected devnum; on a host with several cards only through ET_DEVICES
  if [ -z "$b" ] || [ ! -e "$ETD/$b" ]; then fail card "no card at ${b:-?}"; fi
  if [ $s_ok = 1 ]; then for x in ${DASH_EXCLUDE_PCI:-}; do [ "$x" = "$b" ] && fail card "excluded card"; done; fi
  if [ $s_ok = 1 ] && [ $multi = 1 ]; then
    if [ -z "${DASH_SAMPLE_ETDEV:-}" ] || [ "$DASH_SAMPLE_ETDEV" != "${DASH_SAMPLE_DEVNUM:-x}" ]; then
      fail card "$ncards cards here: only through ET_DEVICES naming the card"
    elif [ "$(hostname)" = aifoundry1 ] && [ "$DASH_SAMPLE_DEVNUM" != 1 ]; then fail card "aifoundry1: card 1 only"; fi
  fi
  if [ $s_ok = 1 ]; then
    dn=$(cat "$ETD/$b/devnum" 2>/dev/null)
    if [ "$dn" != "${DASH_SAMPLE_DEVNUM:-x}" ]; then fail card "devnum at $b is '$dn', expected ${DASH_SAMPLE_DEVNUM:-?}"
    else gate card ok "$b devnum $dn, $ncards card(s) bound"; fi
  fi
  # 2. with several cards, only on the boot a person confirmed the numbering for: moving a card needs a power cycle,
  #    and a power cycle changes the boot id
  if [ $s_ok = 1 ] && [ $multi = 1 ]; then
    if [ -z "${DASH_SAMPLE_BOOT:-}" ]; then fail boot "this boot ($BOOT) is not confirmed (config.json sample_boot)"
    elif [ "$DASH_SAMPLE_BOOT" != "$BOOT" ]; then fail boot "confirmed for another boot; this boot is $BOOT"
    else gate boot ok "$BOOT"; fi
  fi
  # 3. the lock file must be the lab's (root's, made at boot): it is opened read-only below and never created, because
  #    a lock file we created would be ours, mode 0600, and lock everyone else out of the card until a reboot
  LOCK=${DASH_SAMPLE_LOCK:-}
  if [ $s_ok = 1 ]; then
    case "$LOCK" in /run/lock/etsoc-shire[0-9].lock) ;; *) fail lock "bad lock path" ;; esac
  fi
  if [ $s_ok = 1 ]; then
    if [ "${LOCK##*shire}" != "${DASH_SAMPLE_DEVNUM:-x}.lock" ]; then fail lock "lock does not match the card"
    elif [ -L "$LOCK" ] || [ ! -f "$LOCK" ]; then fail lock "no lock file $LOCK"
    elif [ "$(stat -c %U "$LOCK" 2>/dev/null)" != root ]; then fail lock "$LOCK is not root's"
    else gate lock ok; fi
  fi
  # 4. the host-side rate limit (a second one, beside collect.py's state)
  stamp=$HOME/.cache/lab-dashboard/sample-$DASH_SAMPLE_CARD.stamp
  every=${DASH_SAMPLE_EVERY_MIN:-30}; [ "$every" -ge 10 ] 2>/dev/null || every=10
  if [ $s_ok = 1 ]; then
    if [ -e "$stamp" ]; then
      sa=$(( $(date +%s) - $(stat -c %Y "$stamp" 2>/dev/null || echo 0) ))
      if [ "$sa" -lt $(( every * 60 )) ]; then fail stamp "too soon: last try $(( sa / 60 )) min ago"; else gate stamp ok; fi
    else gate stamp ok "first try"; fi
  fi
  # 5. the binary: the host's own build, against /opt/et. With ET_DEVICES (a host with several cards) the variable
  #    must reach a device layer that knows it, or the sample goes to card 0: the binary must be this directory's
  #    own CMake build (CMakeCache.txt beside it, naming this directory), and both the binary and /opt/et's static
  #    device layer must carry the name ET_DEVICES (a stock device layer has no such string)
  bin=$HOME/${DASH_SAMPLE_BIN:-}
  if [ $s_ok = 1 ]; then
    if [ -z "${DASH_SAMPLE_BIN:-}" ] || [ -L "$bin" ] || [ ! -f "$bin" ] || [ ! -x "$bin" ]; then fail binary "no ettelem build"
    else
      ld=$(LD_LIBRARY_PATH=/opt/et/lib t 10 ldd "$bin"); lrc=$?
      bdir=$(cd "$(dirname "$bin")" 2>/dev/null && pwd -P)
      cc=$bdir/CMakeCache.txt
      if [ $lrc -ne 0 ]; then fail binary "ldd failed ($lrc)"
      elif printf '%s\n' "$ld" | grep -q 'not found'; then fail binary "a library is missing"
      elif ! printf '%s\n' "$ld" | grep -q 'libDM.so => /opt/et/lib/'; then fail binary "libDM is not /opt/et's"
      elif [ -r "$cc" ] && ! grep -q '^deviceLayer_DIR:PATH=/opt/et/' "$cc"; then fail binary "not built against /opt/et"
      elif [ -n "${DASH_SAMPLE_ETDEV:-}" ]; then
        ccd=$(sed -n 's/^CMAKE_CACHEFILE_DIR:INTERNAL=//p' "$cc" 2>/dev/null | head -n 1)
        if [ ! -r "$cc" ]; then fail binary "ET_DEVICES: no CMakeCache.txt beside the binary"
        elif [ -z "$ccd" ] || [ "$(cd "$ccd" 2>/dev/null && pwd -P)" != "$bdir" ]; then fail binary "ET_DEVICES: CMakeCache.txt is not this directory's build"
        elif ! t 10 grep -qa ET_DEVICES "$bin"; then fail binary "ET_DEVICES: the binary has no ET_DEVICES"
        elif ! t 10 grep -qa ET_DEVICES /opt/et/lib/libdeviceLayer.a; then fail binary "ET_DEVICES: /opt/et's device layer has no ET_DEVICES"
        else gate binary ok "honours ET_DEVICES"; fi
      else gate binary ok; fi
    fi
  fi
  # 6. none of our runners and none of our device processes (a plain pgrep: any mention of a runner counts here)
  if [ $s_ok = 1 ]; then
    fwp=$(t 10 pgrep -u "$MYUID" -f "$FW_RE"); prc=$?
    pso=$(t 10 ps -eo uid=,comm=); psrc=$?
    if [ $prc -gt 1 ]; then fail experiment "pgrep failed ($prc)"
    elif [ $psrc -ne 0 ] || [ -z "$pso" ]; then fail experiment "ps failed ($psrc)"
    else
      fw=$(printf '%s' "$fwp" | grep -c .)
      od=$(printf '%s\n' "$pso" | awk -v me="$MYUID" -v re="$DEV_COMM" '$1 == me && $2 ~ re' | wc -l)
      if [ "$fw" -gt 0 ] || [ "$od" -gt 0 ]; then fail experiment "ours running ($fw framework, $od device)"; else gate experiment ok; fi
    fi
  fi
  # 7. no other user's device process and no CI job
  if [ $s_ok = 1 ]; then
    xo=$(printf '%s\n' "$pso" | awk -v me="$MYUID" -v re="$DEV_COMM" '$1 != me && ($2 ~ re || $2 == "Runner.Worker")' | wc -l)
    if [ "$xo" -gt 0 ]; then fail others "$xo device or CI process(es) of other users"; else gate others ok; fi
  fi
  # 8. no other user active: a session that is not closing, with no terminal or one used in the last 30 minutes
  if [ $s_ok = 1 ]; then
    lsn=$(t 10 loginctl list-sessions --no-legend --no-pager); lsrc=$?
    if [ $lsrc -ne 0 ]; then fail people "loginctl failed ($lsrc)"
    else
      nowt=$(date +%s)
      act=$(printf '%s\n' "$lsn" | while read -r sid uid user rest; do
        [ -n "$sid" ] || continue
        [ "$uid" -ge 1000 ] 2>/dev/null || continue; [ "$uid" = "$MYUID" ] && continue
        st=$(t 5 loginctl show-session "$sid" -p State --value); [ "$st" = closing ] && continue
        tty=$(t 5 loginctl show-session "$sid" -p TTY --value)
        if [ -z "$tty" ]; then echo "$user"; continue; fi
        at=$(stat -c %X "/dev/$tty" 2>/dev/null || echo 0)
        [ $(( nowt - at )) -lt 1800 ] && echo "$user"
      done | sort -u | wc -l)
      if [ "$act" -gt 0 ]; then fail people "$act other user(s) active"; else gate people ok; fi
    fi
  fi
  # 9. the card itself quiet since the last run: its submission counters must equal the last run's (this catches a
  #    runner between two launches, which holds nothing and shows in no process list)
  d=$ETD/$b
  sq_now() { cat "$d/mgmt_vq_stats/msg_count" "$d/ops_vq_stats/msg_count" 2>/dev/null |
             awk '$1 ~ /SQ[0-9]*:$/ {s += $2; n++} END {if (n) print s + 0}'; }
  if [ $s_ok = 1 ]; then
    c0=$(sq_now)
    if [ -z "$c0" ]; then fail quiet "cannot read the message counters"
    elif [ -z "${DASH_SAMPLE_SQ_PREV:-}" ]; then fail quiet "no count from the last run to compare with"
    elif [ "${DASH_SAMPLE_SQ_BOOT:-}" != "$BOOT" ]; then fail quiet "the last run's count is from another boot"
    elif [ "$c0" != "$DASH_SAMPLE_SQ_PREV" ]; then fail quiet "used since the last run ($DASH_SAMPLE_SQ_PREV to $c0)"
    else gate quiet ok "$c0"; fi
  fi
  # 10. nothing held on any card of the host, right before the lock
  if [ $s_ok = 1 ]; then
    t 10 et-who --check > /dev/null; wc=$?
    case $wc in 0) gate etwho ok ;; 1) fail etwho held ;; *) fail etwho "check failed ($wc)" ;; esac
  fi
  # 11. the probe's own time: a sample starts only in its first 10 s, so collect.py (45 s) never stops the probe mid-sample
  if [ $s_ok = 1 ]; then
    if [ "$SECONDS" -gt 10 ]; then fail time "the probe is already $SECONDS s old"; else gate time ok "$SECONDS s"; fi
  fi
  if [ $s_ok = 1 ]; then
    envs="LD_LIBRARY_PATH=/opt/et/lib"; [ -n "${DASH_SAMPLE_ETDEV:-}" ] && envs="$envs ET_DEVICES=$DASH_SAMPLE_ETDEV"
    cmd="cd /tmp; exec 9<$LOCK; flock -n 9; exec env $envs timeout -k 3 10 nice -n 10 $bin sample --seconds 2 --every-ms 500"
    if [ "${DASH_SAMPLE_DRY:-0}" = 1 ]; then
      echo "would_run $cmd"
    elif ! { mkdir -p "$HOME/.cache/lab-dashboard" && touch "$stamp"; } 2>/dev/null; then
      fail stamp "cannot write the stamp file"
    else
      echo "start"
      # the lock is opened read-only (never created) on fd 9, which timeout and ettelem inherit; 97: the lock is
      # held, 98: it could not be opened, 96: no /tmp. timeout: 124 stopped by SIGTERM, 137 killed 3 s later.
      out=$(exec 2>/dev/null </dev/null; cd /tmp || exit 96; exec 9<"$LOCK" || exit 98; flock -n 9 || exit 97
            exec env $envs timeout -k 3 10 nice -n 10 "$bin" sample --seconds 2 --every-ms 500)
      rc=$?
      c1=$(sq_now)
      echo "ran rc=$rc msgs_before=$c0 msgs_after=${c1:-}"
      printf '%s\n' "$out" | grep '^{"t_ms"' | tail -n 8 | cut -c1-4000 | sed 's/^/tel /'
    fi
  fi
fi

sec end
