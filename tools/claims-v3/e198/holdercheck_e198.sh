#!/usr/bin/env bash
# E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): the runner's --holder-check INSIDE the private /dev (E198.md
# section 3: "through its own --holder-check option the kit may give a wrapper of the box's et-who"). The box's et-who runs
# `sudo -n /usr/local/sbin/et-holders`, which bubblewrap's no_new_privs refuses inside (et-who exits 2 there: desk-shown), and a process
# inside cannot read the /proc/<pid>/fd links of a process outside its user namespace. So this file asks the warden OUTSIDE
# (warden_e198.py, started by the session before the identity sampler) to run the box's own `et-who --check` for it, and prints that
# answer unchanged: et-who's stdout on stdout, its stderr on stderr, its exit status as its own. The box's et-who outside lists every
# holder of either card (fuser on /dev/et0_* and /dev/et1_*, both lock files), so the runner's others_holding() sees both cards.
# The request: an empty file <E198_HOLDERD>/req/<id> made by a rename; the answer: <id>.out, <id>.err and, last, <id>.rc in
# <E198_HOLDERD>/rsp/. No answer within 28 s (inside the runner's 30 s bound), no warden, or an unreadable answer: exit 2, which the runner
# reads as "holder check failed (exit 2)": the card is not free, it polls every 30 s and stops after 10 minutes. Never "free" by default.
#   E198_HOLDERD=<dir> <E198 root>/tools/claims-v3/e198/holdercheck_e198.sh --check
# SPDX-License-Identifier: Apache-2.0
set -u
[ "${1:-}" = --check ] && [ $# -eq 1 ] || { echo "holdercheck_e198: usage: holdercheck_e198.sh --check" >&2; exit 2; }
D=${E198_HOLDERD:-}
[ -n "$D" ] && [ -d "$D/req" ] && [ -d "$D/rsp" ] && [ -e "$D/ready" ] ||
  { echo "holdercheck_e198: no warden (E198_HOLDERD '${D}' has no req/, rsp/ and ready)" >&2; exit 2; }
id=$$-$(date +%s%N)
: > "$D/req/.$id" && mv -f "$D/req/.$id" "$D/req/$id" || { echo "holdercheck_e198: cannot write the request" >&2; exit 2; }
i=0
while [ "$i" -lt 280 ]; do
  if [ -e "$D/rsp/$id.rc" ]; then
    rc=$(cat "$D/rsp/$id.rc")
    case "$rc" in ''|*[!0-9]*) echo "holdercheck_e198: an unreadable answer ('$rc')" >&2; rc=2 ;;
      *) cat "$D/rsp/$id.out" 2>/dev/null; cat "$D/rsp/$id.err" >&2 2>/dev/null ;; esac
    rm -f "$D/rsp/$id.out" "$D/rsp/$id.err" "$D/rsp/$id.rc"
    exit "$rc"
  fi
  sleep 0.1
  i=$((i + 1))
done
rm -f "$D/req/$id"
echo "holdercheck_e198: the warden gave no answer in 28 s" >&2
exit 2
