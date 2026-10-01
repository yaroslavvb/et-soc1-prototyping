#!/bin/bash
# install.sh: install, check or remove et-usaged (the card-usage logger) on this host. Run as root.
#
#   sudo ./install.sh [--skip-counters N[,N]|none] [--skip-pci ADDR[,ADDR]|none] [--trust-source]
#                                                     install or update, enable, start, verify (idempotent)
#   sudo ./install.sh --check                         compare installed files with these, service state, journal
#   sudo ./install.sh --uninstall                     stop, disable, remove programs and unit (keeps logs, config)
#   sudo ./install.sh --purge                         also remove /var/log/et-usage, /etc/default/et-usaged, the user
#   ./install.sh --check-source                       (any user) could anyone but root and you change these files?
#
# --skip-counters and --skip-pci are written to /etc/default/et-usaged only when that file does not exist yet. On
# aifoundry1 the lab's rule is to touch nothing of card 0 (0000:01:00.0) beyond link and err_stats: there a first
# install refuses without --skip-counters 0 --skip-pci 0000:01:00.0. The service runs as the et-usage system user.
# Root copies these files and systemd runs them: install refuses when anyone but root and the admin who ran sudo
# could have changed them (a file, or a directory above it, writable by another user); --trust-source overrides.
set -eu

ARGS="$*"
HERE=$(cd "$(dirname "$0")" && pwd -P)
UNIT=et-usaged.service
SVCUSER=et-usage
DEFAULTS=/etc/default/et-usaged
LOGDIR=/var/log/et-usage
NOWJSON=/run/et-usage/now.json
# source|destination|mode
FILES="et-usaged|/usr/local/sbin/et-usaged|0755 et-usage|/usr/local/bin/et-usage|0755 et-usaged.service|/etc/systemd/system/et-usaged.service|0644"

say() { printf 'install.sh: %s\n' "$*"; }
die() { printf 'install.sh: %s\n' "$*" >&2; exit 1; }
run() { printf '  + %s\n' "$*"; "$@"; }

mode=install
skip=
skip_pci=
trust=0
while [ $# -gt 0 ]; do
  case $1 in
    --check) mode=check ;;
    --check-source) mode=check-source ;;
    --uninstall) mode=uninstall ;;
    --purge) mode=purge ;;
    --trust-source) trust=1 ;;
    --skip-counters) [ $# -ge 2 ] || die "--skip-counters needs a value (e.g. 0, 0,1 or none)"; skip=$2; shift ;;
    --skip-counters=*) skip=${1#*=} ;;
    --skip-pci) [ $# -ge 2 ] || die "--skip-pci needs a value (e.g. 0000:01:00.0 or none)"; skip_pci=$2; shift ;;
    --skip-pci=*) skip_pci=${1#*=} ;;
    -h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
  shift
done
if [ -n "$skip" ] && [ "$skip" != none ]; then
  printf '%s' "$skip" | grep -Eq '^[0-9]+(,[0-9]+)*$' || die "--skip-counters: expected card numbers like 0 or 0,1, or none"
fi
if [ -n "$skip_pci" ] && [ "$skip_pci" != none ]; then
  printf '%s' "$skip_pci" | grep -Eq '^[0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-7](,[0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-7])*$' \
    || die "--skip-pci: expected PCI addresses like 0000:01:00.0, or none"
fi

# ---- who could change what root installs and runs
admin=${SUDO_UID:-$(id -u)}
group_private() {    # gid owner-uid: true when no account but the owner is in the group
  local gid=$1 uid=$2 m
  for m in $(getent group "$gid" | cut -d: -f4 | tr ',' ' '); do
    [ "$(id -u "$m" 2>/dev/null)" = "$uid" ] || return 1
  done
  getent passwd | awk -F: -v g="$gid" -v u="$uid" '$4 == g && $3 != u { f = 1 } END { exit f }'
}
path_ok() {          # owned by root or the admin, and writable by no one else (a sticky root directory like /tmp is fine)
  local p=$1 uid gid m
  read -r uid gid m <<EOF
$(stat -c '%u %g %a' "$p" 2>/dev/null)
EOF
  if [ -z "$uid" ]; then echo "  $p: cannot stat"; return 1; fi
  if [ "$uid" != 0 ] && [ "$uid" != "$admin" ]; then echo "  $p: owned by uid $uid"; return 1; fi
  m=$((8#$m))
  if [ $((m & 8#0002)) != 0 ] && ! { [ -d "$p" ] && [ $((m & 8#1000)) != 0 ] && [ "$uid" = 0 ]; }; then
    echo "  $p: writable by every user"; return 1
  fi
  if [ $((m & 8#0020)) != 0 ] && ! group_private "$gid" "$uid"; then
    echo "  $p: writable by group $(getent group "$gid" | cut -d: -f1) ($gid), which has other members"; return 1
  fi
  return 0
}
check_source() {
  local bad=0 d f
  for f in et-usaged et-usage et-usaged.service install.sh; do path_ok "$HERE/$f" || bad=1; done
  d=$HERE
  while :; do
    path_ok "$d" || bad=1
    [ "$d" = / ] && break
    d=$(dirname "$d")
  done
  return $bad
}
if [ "$mode" = check-source ]; then
  if check_source; then say "source OK: only root and uid $admin can change $HERE and the files installed from it"; exit 0; fi
  say "source NOT trusted: someone else could change what root installs (see above)"; exit 1
fi

[ "$(uname -s)" = Linux ] || die "refusing: not Linux"
[ -d /run/systemd/system ] || die "refusing: systemd is not running here"
command -v systemctl >/dev/null || die "refusing: no systemctl"
[ "$(id -u)" = 0 ] || die "refusing: run as root (sudo $0 $ARGS)"

sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }

if [ "$mode" = check ]; then
  bad=0
  for f in $FILES; do
    IFS='|' read -r src dst m <<EOF
$f
EOF
    if [ ! -e "$dst" ]; then say "MISSING   $dst"; bad=1
    elif [ "$(sha "$HERE/$src")" = "$(sha "$dst")" ]; then say "same      $dst ($(stat -c '%a %U' "$dst"))"
    else say "DIFFERENT $dst (installed $(sha "$dst" | cut -c1-12), here $(sha "$HERE/$src" | cut -c1-12))"; bad=1; fi
  done
  if [ -e "$DEFAULTS" ]; then say "$DEFAULTS: $(grep -v '^#' "$DEFAULTS" | tr '\n' ' ')"; else say "$DEFAULTS: absent"; fi
  if getent passwd "$SVCUSER" >/dev/null; then say "user $SVCUSER: $(id "$SVCUSER")"; else say "user $SVCUSER: MISSING"; bad=1; fi
  if [ -d "$LOGDIR" ]; then say "$LOGDIR: $(stat -c '%a %U:%G' "$LOGDIR"), $(ls "$LOGDIR" | wc -l) file(s), $(du -sh "$LOGDIR" | cut -f1)"
  else say "$LOGDIR: absent"; fi
  say "enabled: $(systemctl is-enabled "$UNIT" 2>/dev/null || true); active: $(systemctl is-active "$UNIT" 2>/dev/null || true)"
  [ "$(systemctl is-active "$UNIT" 2>/dev/null || true)" = active ] || bad=1
  pid=$(systemctl show -p MainPID --value "$UNIT" 2>/dev/null || echo 0)
  if [ "${pid:-0}" != 0 ]; then
    say "main pid $pid: user $(stat -c %U /proc/$pid), $(grep -E '^Cap(Eff|Bnd)' /proc/$pid/status | tr -s '\t\n' '  ')"
  fi
  if [ -e "$NOWJSON" ]; then
    say "now.json: $(( $(date +%s) - $(stat -c %Y "$NOWJSON") )) s old, $(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print("sees_all %s, cards %s, holds %d, paused %s, stats %s" % (d.get("sees_all"), d.get("cards"), len(d.get("holds", [])), d.get("paused"), d.get("stats")))' "$NOWJSON")"
  fi
  echo "--- journalctl -u $UNIT -n 15"
  journalctl -u "$UNIT" -n 15 --no-pager 2>/dev/null || true
  exit $bad
fi

if [ "$mode" = uninstall ] || [ "$mode" = purge ]; then
  if [ -e /etc/systemd/system/$UNIT ] || systemctl cat "$UNIT" >/dev/null 2>&1; then
    run systemctl disable --now "$UNIT" || true
  fi
  for f in $FILES; do
    dst=$(printf '%s' "$f" | cut -d'|' -f2)
    [ -e "$dst" ] && run rm -f "$dst"
  done
  run systemctl daemon-reload
  if [ "$mode" = purge ]; then
    [ -e "$DEFAULTS" ] && run rm -f "$DEFAULTS"
    [ -d "$LOGDIR" ] && run rm -rf "$LOGDIR"
    getent passwd "$SVCUSER" >/dev/null && run userdel "$SVCUSER"
    say "purged: programs, unit, $DEFAULTS, the logs and the $SVCUSER user"
  else
    say "uninstalled; kept $LOGDIR, $DEFAULTS and the $SVCUSER user (--purge removes them)"
  fi
  exit 0
fi

# ---- install
if ! check_source; then
  if [ "$trust" = 1 ]; then say "--trust-source: installing anyway"
  else die "refusing: someone but root and uid $admin could change the files in $HERE (above); fix the modes, or --trust-source"; fi
fi
host=$(hostname -s)
if [ ! -e "$DEFAULTS" ] && [ "$host" = aifoundry1 ]; then
  case ",$skip," in *,0,*) ok0=1 ;; *) ok0=0 ;; esac
  case ",$skip_pci," in *,0000:01:00.0,*) ok1=1 ;; *) ok1=0 ;; esac
  [ "$ok0" = 1 ] && [ "$ok1" = 1 ] || die "refusing on aifoundry1 without --skip-counters 0 --skip-pci 0000:01:00.0: the lab touches nothing of card 0 there beyond link and err_stats (not even devnum)"
fi
for f in et-usaged et-usage; do
  python3 -c 'import ast, sys; ast.parse(open(sys.argv[1]).read())' "$HERE/$f" || die "$f does not parse"
done
if ! getent passwd "$SVCUSER" >/dev/null; then
  run useradd --system --user-group --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin \
    --comment "et-usaged card-usage logger" "$SVCUSER"
fi
changed=0
for f in $FILES; do
  IFS='|' read -r src dst m <<EOF
$f
EOF
  if [ -e "$dst" ] && [ "$(sha "$HERE/$src")" = "$(sha "$dst")" ] && [ "$(stat -c '%a %U' "$dst")" = "${m#0} root" ]; then
    say "unchanged $dst"
  else
    run install -o root -g root -m "$m" "$HERE/$src" "$dst.new"
    run mv -f "$dst.new" "$dst"
    changed=1
  fi
done
if [ -e "$DEFAULTS" ]; then
  say "kept $DEFAULTS: $(grep -v '^#' "$DEFAULTS" | tr '\n' ' ')"
  { [ -n "$skip" ] || [ -n "$skip_pci" ]; } && say "note: --skip-counters/--skip-pci ignored because $DEFAULTS exists; edit it by hand"
else
  args=
  [ -n "$skip" ] && [ "$skip" != none ] && args="--skip-counters $skip"
  [ -n "$skip_pci" ] && [ "$skip_pci" != none ] && args="${args:+$args }--skip-pci $skip_pci"
  say "writing $DEFAULTS (ET_USAGED_ARGS=\"$args\")"
  printf '# Options for et-usaged on %s (tools/lab/et-usage/README.md). Written by install.sh.\n# Every et-usaged run on this host (the service, --once, --foreground) also skips what this file skips.\nET_USAGED_ARGS="%s"\n' \
    "$host" "$args" > "$DEFAULTS.new"
  chmod 0644 "$DEFAULTS.new"
  mv -f "$DEFAULTS.new" "$DEFAULTS"
  changed=1
fi
if [ ! -d "$LOGDIR" ]; then run install -d -o "$SVCUSER" -g "$SVCUSER" -m 0755 "$LOGDIR"
else run chown -R "$SVCUSER:$SVCUSER" "$LOGDIR"; run chmod 0755 "$LOGDIR"; fi
run systemctl daemon-reload
run systemctl enable "$UNIT"
t0=$(date +%s)
if systemctl is-active --quiet "$UNIT"; then
  if [ $changed = 1 ]; then run systemctl restart "$UNIT"; else say "running, nothing changed: not restarted"; fi
else
  run systemctl start "$UNIT"
fi

# ---- verify
ok=0
for _ in $(seq 1 20); do
  if systemctl is-active --quiet "$UNIT" && [ -e "$NOWJSON" ] && [ "$(stat -c %Y "$NOWJSON")" -ge "$((t0 - 60))" ]; then ok=1; break; fi
  sleep 0.5
done
if [ $ok = 0 ]; then
  systemctl status "$UNIT" --no-pager -n 20 || true
  die "FAILED: the service is not active or $NOWJSON did not appear within 10 s"
fi
pid=$(systemctl show -p MainPID --value "$UNIT")
problems=$(python3 - "$NOWJSON" "$LOGDIR" "$pid" <<'PY'
import glob, json, sys
now, logdir, pid = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = json.load(open(now))
bad = []
if d.get('sees_all') is not True:
    bad.append("it cannot read other users' fd links (sees_all is not true): check User= and AmbientCapabilities= "
               "in the unit, and the journal")
if (glob.glob('/dev/et[0-9]*_mgmt') or glob.glob('/dev/et[0-9]*_ops')) and not d.get('cards'):
    bad.append('it watches no card node although /dev/et* exist (the inotify watch was refused?)')
if d.get('pid') != pid:
    bad.append('now.json is from pid %s, the service is pid %s' % (d.get('pid'), pid))
if d.get('paused'):
    bad.append('it writes no records: %s' % d['paused'])
starts = []
for log in sorted(glob.glob(logdir + '/[0-9]*.jsonl'))[-2:]:      # today's, and yesterday's (a start at midnight)
    try:
        starts += [json.loads(l) for l in open(log) if '"t":"start"' in l]
    except (OSError, ValueError) as e:
        bad.append('cannot read %s: %s' % (log, e))
if not any(r.get('pid') == pid for r in starts):
    bad.append('no start record of pid %d in %s (cannot write the log?)' % (pid, logdir))
print('; '.join(bad))
PY
)
if [ -n "$problems" ]; then
  systemctl status "$UNIT" --no-pager -n 20 || true
  die "FAILED: $problems"
fi
say "OK: $UNIT active as $(stat -c %U /proc/$pid) (pid $pid; $(grep '^CapEff' /proc/$pid/status | tr -s '\t' ' ')), sees every process, logging to $LOGDIR"
journalctl -u "$UNIT" -n 3 --no-pager 2>/dev/null || true
echo "--- et-usage (as nobody: the log must be readable by every user)"
if command -v runuser >/dev/null; then runuser -u nobody -- /usr/local/bin/et-usage || die "et-usage failed as nobody"
else /usr/local/bin/et-usage; fi
