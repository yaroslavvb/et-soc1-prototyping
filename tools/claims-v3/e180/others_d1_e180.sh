# E180 (Q146(f); the kit's dated note 1, KIT.md.dated-note-1.md section 1): departure D1's other-user test, sourced AFTER lib.sh by
# block_e180_v2.sh (the block's own check, before the block and before the sampler) and by run_e180_v2.py (its check before every run),
# so the block and the runner apply one rule, defined once. The case block below is tools/claims-v3/e178/block_e178.sh lines 35-50, with
# its comment (lines 32-34), verbatim, and so is block_e171.sh lines 34-49, which E171 ran on aifoundry3 on 5 Nov 2026.
# v1's block and runner used lib.sh's stock others_present, which with no V3_DEVICE counts every other user `who` lists, so aifoundry3's
# standing idle logins of other lab users would have stopped E180 at its first block (the adversarial verifier's fault 1).
# Under V3_DRY lib.sh's own stub (no one present) stays: the function is defined only outside a dry run, as in E178's block.
# Departure D1 (hl/README.md, kept by E60-E171): on aifoundry1 and aifoundry3 a user who is only logged in does not block (other lab
# users keep idle tmux logins there); another user on THIS card does, and so does any other user's device process. Fails closed when
# et-holders is unreadable.
# SPDX-License-Identifier: Apache-2.0
case "$CARD" in aifoundry3|aifoundry1-c*)
  if [ -z "${V3_DRY:-}" ]; then
  others_present() {
    local procs= holders= out n=${V3_DEVICE:-0}
    if [ -z "${V3_DEVICE:-}" ]; then
      procs=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {print $1":"$2":"$3}' | tr '\n' ' ')
    fi
    out=$(sudo -n /usr/local/sbin/et-holders 9>&- 8>&- 2>&1) || { log "others present: et-holders unreadable: ${out:0:120}"; return 0; }
    holders=$(printf '%s\n' "$out" | grep -v 'et-holders' |
              awk -v me="$USER" -v d="/dev/et${n}_" -v l="lock:etsoc-shire${n}.lock" \
                  'index($1, d) == 1 || $1 == l { if ($2 != me && $2 != "") print $2":"$3 }' | tr '\n' ' ')
    if [ -n "${procs// /}${holders// /}" ]; then log "others present: procs=[$procs] holders=[$holders]"; return 0; fi
    return 1
  }
  fi ;;
esac
