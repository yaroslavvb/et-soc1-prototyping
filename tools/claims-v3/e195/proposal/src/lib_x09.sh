# x09: this request's changes to the public lab repo's tools/claims-v3/lib.sh, sourced by block_x09.sh right after it
# (lib.sh has set -u and has gone to its own tree). Four changes, each as the lab's own kits make it:
#  1. Device commands, as the lab's e180/block_e180_v2.sh and e183/block_e183_v3.sh: every telemetry call goes through
#     tools/claims-v3/e128/ettelem_guard.sh (`ettelem config` and `ettelem sample --seconds N --every-ms N` only), and
#     lib.sh's drain of the management queue is refused, so nothing else is sent whatever fails: a sampler that does
#     not start, or one that ignores SIGTERM for 30 s (lib.sh then kills it, and its reply stays queued; if the next
#     block's sampler cannot start, that block fails and the session ends). DEVMNGT is emptied too, so nothing in
#     lib.sh can reach the management tool.
#  2. The tree: lib.sh sets V3_ROOT to the tree it sits in, and everything is written under that tree's build/. The
#     block runs only when X9_ROOT, an absolute path set by whoever runs it, names that same tree (exit 2 otherwise; a
#     relative one would be read from the tree lib.sh has already gone to, and always match).
#  3. The login: the holder test compares each holder's user with this login (id -un), never with USER (unset, under
#     set -u an awk -v of it ended the pipeline and no holder line was read). An unset USER is set to this login, for
#     runitems.py's own holder check before every item, which reads it; a USER naming anyone else refuses (exit 2).
#  4. The other-user test of the lab's kits since 20 Oct (e180/others_d1_e180.sh; the owner's ruling of 1 Nov: an idle
#     login does not block), on every host: another user's device process, or another holder of THIS card's nodes or
#     lock, blocks; a user who is only logged in does not. It fails closed when the holder helper is unreadable. Under
#     V3_DRY lib.sh's own stub (no one present) stays.
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh
DEVMNGT=
drain_mgmt() { log "x09: drain of the management queue refused: only the guard's reads are sent"; return 0; }

X9_ME=$(id -un 2>/dev/null)
if [ -z "$X9_ME" ]; then echo "x09: no login name for uid $(id -u)" >&2; exit 2; fi
if [ -z "${USER:-}" ]; then USER=$X9_ME; export USER; fi
if [ "$USER" != "$X9_ME" ]; then
  echo "x09: USER is '$USER', not this login ($X9_ME): the holder checks compare with it" >&2; exit 2
fi

x9_tree() { (cd "$1" 2>/dev/null && pwd -P); }
case "${X9_ROOT:-}" in
  /*) [ "$(x9_tree "$X9_ROOT")" = "$(x9_tree "$V3_ROOT")" ] ||
        { echo "x09: X9_ROOT='$X9_ROOT' must name the tree lib.sh writes into ($V3_ROOT)" >&2; exit 2; } ;;
  *) echo "x09: X9_ROOT='${X9_ROOT:-}' must be the absolute path of the tree lib.sh writes into ($V3_ROOT)" >&2; exit 2 ;;
esac

# The device kernel the host launches, in tools/claims-v3/text_hash.sh's two lines: the file, and its disassembly
# (the code that runs, whatever its sections are called).
x9_kernel_hash() {
  local k=$1 od=/opt/et/riscv64-unknown-elf/bin/objdump
  if [ ! -f "$k" ]; then echo "MISSING kernel $k"; return 0; fi
  echo "file   kernel $(sha256sum "$k" | cut -d' ' -f1) $(stat -c %s "$k") $k"
  if [ -x "$od" ]; then echo "code   kernel $("$od" -d "$k" 2>/dev/null | tail -n +3 | sha256sum | cut -d' ' -f1) $k"; fi
  return 0
}

if [ -z "${V3_DRY:-}" ]; then
others_present() {
  local procs= holders= out n=${V3_DEVICE:-0}
  if [ -z "${V3_DEVICE:-}" ]; then
    procs=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {print $1":"$2":"$3}' | tr '\n' ' ')
  fi
  out=$(sudo -n /usr/local/sbin/et-holders 9>&- 8>&- 2>&1) || { log "others present: et-holders unreadable: ${out:0:120}"; return 0; }
  holders=$(printf '%s\n' "$out" | grep -v 'et-holders' |
            awk -v me="$X9_ME" -v d="/dev/et${n}_" -v l="lock:etsoc-shire${n}.lock" \
                'index($1, d) == 1 || $1 == l { if ($2 != me && $2 != "") print $2":"$3 }' | tr '\n' ' ')
  if [ -n "${procs// /}${holders// /}" ]; then log "others present: procs=[$procs] holders=[$holders]"; return 0; fi
  return 1
}
fi
