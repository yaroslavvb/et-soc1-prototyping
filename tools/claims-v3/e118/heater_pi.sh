#!/usr/bin/env bash
# E118's heater for the 800 MHz control: run_hl.py's heater command with fp32 `pi` (anchor_pi's own built-in values)
# in place of `randn`, because aifoundry1 card 0's PMIC alarm trips on fp32 random data at 800 MHz (E84) and E60's
# heater probe on this card logged 33 300 MHz episodes (E84 correction C6). Every other argument passes unchanged,
# --stop-file included. Card 0 only: refuses unless ET_DEVICES=0.
[ "${ET_DEVICES:-}" = 0 ] || { echo "heater_pi: ET_DEVICES must be 0" >&2; exit 2; }
args=()
for a in "$@"; do [ "$a" = randn ] && a=pi; args+=("$a"); done
exec build/sparsity/host/sparsity_host "${args[@]}"
