#!/usr/bin/env bash
# E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): run one of E188's committed desk
# tests that requires `gdate` on PATH (the Intel's Homebrew name of GNU date) on a desk where GNU date is plain `date` (Linux: aifoundry2).
# Those tests stay as committed: rb/selftest_rest_e188.sh, rb/selftest_rest_e188_v2.sh and dry_intel_e188.sh each refuse to start without
# `gdate` ("no gdate (GNU date) on PATH") and then call it, or a stand-in `date` that execs it, for every date they compute.
#   - `gdate` already on PATH (the Intel): the command runs unchanged, nothing is made;
#   - else, when `date --version` names GNU coreutils: a symbolic link `gdate` to that date in a new directory of its own, put first on
#     PATH for the command alone, removed after it;
#   - else: refused (2), nothing run (a BSD date reads none of the tests' -d forms).
# Exit: the command's own status, or 2.
#   bash tools/claims-v3/e188/desk/gnudate_e188.sh <command> [<arg> ...]
#   e.g. bash tools/claims-v3/e188/desk/gnudate_e188.sh bash tools/claims-v3/e188/rb/selftest_rest_e188_v2.sh <scratch dir>
# SPDX-License-Identifier: Apache-2.0
set -u
[ $# -ge 1 ] || { echo "usage: gnudate_e188.sh <command> [<arg> ...]"; exit 2; }
if command -v gdate > /dev/null 2>&1; then
  "$@"; exit $?
fi
d=$(command -v date) || { echo "gnudate_e188: no date on PATH"; exit 2; }
"$d" --version 2> /dev/null | head -n 1 | grep -q 'GNU coreutils' || { echo "gnudate_e188: no GNU date here (neither gdate nor a GNU date): refused"; exit 2; }
t=$(mktemp -d "${TMPDIR:-/tmp}/gnudate-e188.XXXXXX") || { echo "gnudate_e188: no temporary directory"; exit 2; }
ln -s "$d" "$t/gdate" || { rmdir "${t:?}"; echo "gnudate_e188: the link could not be made"; exit 2; }
echo "gnudate_e188: gdate is $d ($("$d" --version | head -n 1)), for this command only" >&2
PATH="$t:$PATH" "$@"; rc=$?
rm -f "${t:?}/gdate"; rmdir "${t:?}"
exit "$rc"
