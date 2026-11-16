#!/usr/bin/env bash
# E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): THE PRIVATE /dev of E198.md section 3 ("THE TWO-CARD BOX").
# aifoundry1 has two cards, so the unchanged runner (run_x04.py one_card(), lines 362-368) and the unchanged host (main.cpp
# checkOneCard(), lines 88-103) each refuse it before anything is opened. This file runs ONE command in a private /dev that holds the
# standard nodes (null, zero, full, random, urandom, tty, ptmx, pts, shm, fd, std*: bubblewrap's --dev) and card 1's two nodes only,
# /dev/et1_ops and /dev/et1_mgmt, bound from the box's own /dev; everything else is the box's real filesystem, read-write, with the box's
# real /run/lock (card 1's lock is the box's), /proc and /sys, the box's network and the box's process-ID namespace (so the process IDs
# the box's et-who prints are the ones the runner knows). No card-0 node exists inside, so nothing started here can open card 0.
# It opens no device itself: bubblewrap binds the two nodes (a mount, not an open). Not --die-with-parent: a runner whose session is
# killed keeps its own deadline and clean-up (its sampler stopped with SIGTERM) instead of being killed with SIGKILL and orphaning its
# children. Bubblewrap sets no_new_privs, so sudo cannot run inside (the box's et-who uses `sudo -n /usr/local/sbin/et-holders`): the
# holder check inside asks the warden outside (holdercheck_e198.sh, warden_e198.py).
#   bash tools/claims-v3/e198/privdev_e198.sh <command> [args...]
# Exit: the command's own status; 2 and a "PRIVDEV-REFUSED: ..." line on stderr when bubblewrap or a card-1 character device is missing.
# SPDX-License-Identifier: Apache-2.0
set -u
[ $# -ge 1 ] || { echo "PRIVDEV-REFUSED: usage: privdev_e198.sh <command> [args...]" >&2; exit 2; }
B=/usr/bin/bwrap
[ -x "$B" ] || { echo "PRIVDEV-REFUSED: no $B on $(hostname)" >&2; exit 2; }
for n in /dev/et1_ops /dev/et1_mgmt; do
  [ -c "$n" ] || { echo "PRIVDEV-REFUSED: $n is not a character device on $(hostname): card 1 is not there to bind" >&2; exit 2; }
done
exec "$B" --dev-bind / / --dev /dev --dev-bind /dev/et1_ops /dev/et1_ops --dev-bind /dev/et1_mgmt /dev/et1_mgmt -- "$@"
