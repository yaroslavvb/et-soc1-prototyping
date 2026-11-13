# E183 (the kit's dated note 5, KIT.md.dated-note-5.md, Fri 13 Nov 2026, before any E183 datum; revised before its land by the lane
# fix-note5 of Q170, after the verifier verify-note5): step 11's desk-path gate for a desk whose home has the box account's shape. Sourced
# by rb/s22_collect_e183_v3.sh after rb_e183.sh (bash 3.2 or later). It defines nopath_desk_ready (step 11 v3's first check, before any
# copy), nopath_desk (the gate, at the step's end) and their helpers.
#
# WHY. k6's rb_nopath runs v3.1's nopath_q142s.py (unchanged), which forbids "this user's home" (os.path.expanduser("~")) beside the lab
# clone and RB_OUT. On the Intel that home was a Mac home, which no box writes. On aifoundry2 it is /home/<login>, and aifoundry3's
# own paths, which the boxes write into every session's logs and runs (E180's, E185's and E186's committed data hold
# /home/<login>/aifoundry/... thousands of times), carry the same prefix when the box account has the same name (it does: the lab's user
# on every box). So on aifoundry2 the unchanged gate reads every real E183 collection as a desk path and step 11 v2 stops (16) before
# the data commit. nopath's own docstring says a box's own path is not a desk path; the gate cannot tell them apart by "the home" here.
#
# THE DESK'S HOME is this account's home from the account database (never HOME alone), at its physical path. When it is not under
# /home/ (the Intel's Mac home), nopath_desk is k6's rb_nopath, unchanged, and nopath_desk_ready checks nothing. Else:
#   - nopath_desk_ready stops the step before any copy: 10 when HOME is set but empty, not absolute, or does not resolve to that home;
#     16 when the home holds an entry named as the box's tree (rb_tree aifoundry3: aifoundry), since such a desk cannot tell its own paths
#     from the box's. nopath_desk makes the same checks again;
#   - nopath_desk runs nopath_q142s.py, unchanged, with HOME set to RB_OUT for that one call (its "home" needle becomes RB_OUT, which is
#     forbidden anyway) and, in place of the whole home, each entry of the home forbidden by name (--forbid <home>/<entry>, hidden ones
#     too) under each spelling of the home (its physical path, the account database's, HOME as set), and the session scratch root
#     /tmp/claude-<uid> when it exists; an entry that is a symbolic link (nopath would also forbid its target, which may be a short system
#     path) or whose name begins the box's tree (nopath matches substrings: <home>/a would match <home>/aifoundry/...) is left out by name;
#   - then rb/nopath_spell_e183.py over the same output: a path written from the home with a '.', '..' or empty component that resolves
#     under the home and outside the box's tree (<home>/../<login>/x, <home>/./x, <home>//x, <home>/aifoundry/../x, /home//<login>/x), and
#     a path under an entry left out by name, read as a whole path component (<home>/a/x stops; <home>/aifoundry/x does not): each a hit.
#   A desk path under the home's entries however it is spelled, the lab clone, RB_OUT, a Mac home or temp path or a session scratch root
#   (nopath's own needles, the Intel's form among them) stops the step; aifoundry3's own tree, /home/<login>/aifoundry/..., does not,
#   however it is spelled, while it stays inside that tree.
# Exit codes and messages are rb_nopath's: 0 clean; 16 a hit or a missing output (the step's STOP line names which); 10 HOME not this
# account's home.
# SPDX-License-Identifier: Apache-2.0

nopath_desk_account_home() {  # this account's home from the account database (pwd.getpwuid), never HOME; a desk test may redefine it
  "$RB_PY" -I -B -c 'import os, pwd; print(pwd.getpwuid(os.getuid()).pw_dir)'
}

npd_trim() {  # a path without its trailing slashes
  local p=$1
  while [ "${#p}" -gt 1 ] && [ "${p%/}" != "$p" ]; do p=${p%/}; done
  printf '%s\n' "$p"
}

nopath_desk_homes() {  # sets NPD_SHAPE (home or other), NPD_AH (the home's physical path) and NPD_SP (its spellings, one a line); 10 on a bad HOME
  local a hp hv
  NPD_SHAPE=other; NPD_AH=""; NPD_SP=""
  a=$(nopath_desk_account_home 2>/dev/null) || a=""
  case "$a" in /?*) ;; *) rb_die $RB_E_USAGE "the desk-path gate (note 5): this account's home could not be read from the account database" ;; esac
  NPD_AH=$(CDPATH= cd -- "$a" 2>/dev/null && pwd -P) || NPD_AH=""
  [ -n "$NPD_AH" ] || rb_die $RB_E_USAGE "the desk-path gate (note 5): this account's home (the account database's) is not a directory this step can enter"
  case "$NPD_AH" in /home/?*) NPD_SHAPE=home ;; *) return 0 ;; esac
  NPD_SP=$NPD_AH
  a=$(npd_trim "$a")
  [ "$a" = "$NPD_AH" ] || NPD_SP="$NPD_SP
$a"
  [ -n "${RB_DRY:-}" ] && return 0
  [ "${HOME+set}" = set ] || return 0                               # unset: bash and Python both read the account database's home
  [ -n "$HOME" ] || rb_die $RB_E_USAGE "the desk-path gate (note 5): HOME is set but empty: set it to this account's home (the account database's) and run this step again"
  case "$HOME" in /*) ;; *) rb_die $RB_E_USAGE "the desk-path gate (note 5): HOME is not an absolute path: set it to this account's home and run this step again" ;; esac
  hp=$(CDPATH= cd -- "$HOME" 2>/dev/null && pwd -P) || hp=""
  [ "$hp" = "$NPD_AH" ] || rb_die $RB_E_USAGE "the desk-path gate (note 5): HOME does not resolve to this account's home (the account database's): set it so and run this step again"
  hv=$(npd_trim "$HOME")
  case "
$NPD_SP
" in
    *"
$hv
"*) ;;
    *) NPD_SP="$NPD_SP
$hv" ;;
  esac
  return 0
}

npd_no_tree_entry() {  # npd_no_tree_entry <the box's tree>: 16 when the desk's home holds an entry by that name
  if [ -e "$NPD_AH/$1" ] || [ -L "$NPD_AH/$1" ]; then
    rb_die $RB_E_GATE "the desk's home holds an entry named as $E183_BOX's tree ('$1'): this desk cannot tell its own paths from the box's; move that entry aside, or collect from another desk, then run this step again"
  fi
}

nopath_desk_ready() {  # step 11 v3's first check (note 5): what the gate at the step's end needs, before any copy
  local bt
  nopath_desk_homes
  [ "$NPD_SHAPE" = home ] || return 0
  bt=$(rb_tree "$E183_BOX") || rb_die $RB_E_USAGE "no tree for $E183_BOX"
  bt=${bt%%/*}
  if [ -n "${RB_DRY:-}" ]; then
    rb_disp "--- check (note 5), before any copy: HOME resolves to this account's home (the account database's), and that home holds no entry named '$bt' (the box's tree)"
    return 0
  fi
  npd_no_tree_entry "$bt"
  rb_say "the desk-path gate's inputs (note 5): HOME is this account's home, and no entry of it is named '$bt' (the box's tree)"
}

nopath_desk() {  # nopath_desk <dir or file> ...
  local bt e s k n=0 skipped="" fb=() sp=() lo=()
  nopath_desk_homes
  [ "$NPD_SHAPE" = home ] || { rb_nopath "$@"; return; }
  bt=$(rb_tree "$E183_BOX") || rb_die $RB_E_USAGE "no tree for $E183_BOX"
  bt=${bt%%/*}
  if [ -n "${RB_DRY:-}" ]; then
    rb_disp "--- gate (note 5): no desk path (the lab clone's, RB_OUT's, each entry of the desk's home but the box's tree '$bt', a Mac home or temp path, a session scratch root) in $(rb_q "$@"), and each of them there; then no path written from the desk's home with '.', '..' or '//' that leaves the box's tree, nor under an entry left out by name (nopath_spell_e183.py)"
    return 0
  fi
  npd_no_tree_entry "$bt"
  while IFS= read -r s; do [ -n "$s" ] && sp+=(--home "$s"); done <<EOF_NPD_HOMES
$NPD_SP
EOF_NPD_HOMES
  k=$(( ${#sp[@]} / 2 ))
  while IFS= read -r e; do
    [ -n "$e" ] || continue
    case "$bt" in "$e"*) lo+=(--left-out "$e"); skipped="$skipped $e"; continue ;; esac
    if [ -L "$NPD_AH/$e" ]; then lo+=(--left-out "$e"); skipped="$skipped $e(link)"; continue; fi
    while IFS= read -r s; do [ -n "$s" ] && fb+=(--forbid "$s/$e"); done <<EOF_NPD_ENTRY
$NPD_SP
EOF_NPD_ENTRY
    n=$((n + 1))
  done <<EOF_NOPATH_DESK
$(ls -A "$NPD_AH")
EOF_NOPATH_DESK
  [ -d "/tmp/claude-$(id -u)" ] && fb+=(--forbid "/tmp/claude-$(id -u)")
  rb_say "the desk-path gate (note 5): the desk's home has the box account's shape, so its $n entries are forbidden one by one ($k spelling(s) of the home); left out by name, read as whole path components instead:${skipped:- none}"
  rb_local desk local "no desk path in what was written (nopath_q142s.py; note 5: the desk's home entries by name, the box's tree left out)" \
    env HOME="$RB_OUT" "$RB_PY" -B "$RB_V31/nopath_q142s.py" --forbid "$RB_REPO" --forbid "$RB_OUT" ${fb[@]+"${fb[@]}"} "$@"
  if [ "$RB_RC" -ne 0 ]; then
    rb_has '^MISSING ' && rb_die $RB_E_GATE "an output this step should have written is not there (the MISSING lines above): the collector wrote somewhere else, or nothing; commit nothing, and read its output above"
    rb_die $RB_E_GATE "a desk path reached what this step wrote (the HIT lines above): commit nothing; fix the route, remove the outputs, collect again"
  fi
  rb_local desk local "no path written from the desk's home with '.', '..' or '//' that leaves the box's tree, nor under an entry left out by name (nopath_spell_e183.py; note 5)" \
    "$RB_PY" -B "$RB_REPO/tools/claims-v3/e183/rb/nopath_spell_e183.py" "${sp[@]}" --tree "$bt" ${lo[@]+"${lo[@]}"} "$@"
  [ "$RB_RC" -eq 0 ] && return 0
  rb_has '^MISSING ' && rb_die $RB_E_GATE "an output this step should have written is not there (the MISSING lines above): the collector wrote somewhere else, or nothing; commit nothing, and read its output above"
  rb_die $RB_E_GATE "a desk path reached what this step wrote, written through the desk's home with '.', '..' or '//', or under an entry left out by name (the HIT lines above): commit nothing; fix the route, remove the outputs, collect again"
}
