#!/usr/bin/env bash
# collect_val.sh SRC [LOGS] : add aifoundry1 card 1's validation blocks to raw/aifoundry1-c1/hp/, the same way the
# committed development, R0 and V0 blocks were added. Nothing here touches a card or a lab machine.
#
# SRC is a local, read-only copy of aifoundry1's ~/nekko/build/claims-v3/aifoundry1-c1/hp, taken only after the
# card-1 queue log says "queue ends" (build/claims-v3/queue-hp-aifoundry1-c1-val2.log there):
#     rsync -a aifoundry1:nekko/build/claims-v3/aifoundry1-c1/hp/ SRC/
#     rsync -a 'aifoundry1:nekko/build/claims-v3/queue-hp-aifoundry1-c1-val*.log' \
#              aifoundry1:nekko/build/claims-v3/hp-val2-waiter.log LOGS/          # the waiter's log, if it is there
# It copies every validation directory (p9<type><k>, and the aborted p9101.guard-stop-27sep of the tools' README,
# departure 39) and session-widle.json; leaves out who.txt, et-who.txt and ps.txt (logins and other users'
# processes: never in this public repository); gzips mgmt.log as the committed blocks have it (gzip -n -9); and
# refuses to overwrite a block that is already here. With LOGS it also copies the validation queue logs into logs/.
# Afterwards: README.md, "The verdict step".
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
src=${1:?usage: collect_val.sh SRC [LOGS]}
dst=$here/raw/aifoundry1-c1/hp
[ -d "$src" ] || { echo "no such directory: $src" >&2; exit 2; }
shopt -s nullglob
n=0
for d in "$src"/p9[1-4][0-9][0-9]*; do        # 9xxx: validation passes (pass = 9000 + type x 100 + k)
    b=$(basename "$d")
    [ -d "$d" ] || continue
    if [ -e "$dst/$b" ]; then echo "$b: already here, left as it is" >&2; continue; fi
    rsync -a --exclude who.txt --exclude et-who.txt --exclude ps.txt "$d/" "$dst/$b/"
    [ -f "$dst/$b/mgmt.log" ] && gzip -n -9 "$dst/$b/mgmt.log"
    n=$((n + 1)); echo "copied $b"
done
[ -f "$src/session-widle.json" ] && cp -p "$src/session-widle.json" "$dst/"
if [ $# -ge 2 ]; then
    for f in "$2"/queue-hp-aifoundry1-c1-val*.log "$2"/hp-val2-waiter.log; do
        cp -p "$f" "$here/logs/" && echo "copied logs/$(basename "$f")"
    done
    # the waiter's start decision records `who` (other people's logins): keep only the fact that it was read
    w=$here/logs/hp-val2-waiter.log
    [ -f "$w" ] && sed -i -E 's/([;|] )who: .*$/\1who: (logins removed: not for this public repository)/' "$w"
fi
# anything left that must not be public, or large and uncompressed
left=$(find "$dst" \( -name who.txt -o -name et-who.txt -o -name ps.txt \) | head -5)
[ -z "$left" ] || { echo "REFUSE: remove these before committing: $left" >&2; exit 1; }
if grep -l -E ' pts/[0-9]' "$here"/logs/*.log 2>/dev/null; then echo "REFUSE: logins left in the logs above" >&2; exit 1; fi
find "$dst" -type f -size +256k ! -name '*.gz' -printf 'large and uncompressed (gzip -n -9 it if the reducer reads .gz): %p\n'
echo "$n validation directories copied into ${dst#"$here"/}"
