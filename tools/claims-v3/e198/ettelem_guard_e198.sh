#!/usr/bin/env bash
# E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): the runner's --sampler and the session's config reads, through
# E191's guard UNCHANGED (E198.md section 3: "the runner's --sampler through E191's guard (aifoundry1 and ET_DEVICES=1 only; card 1's reader
# at its pin, 8008f96f...)"). The runner execs its --sampler directly ([a.sampler, "sample", "--seconds", N, "--every-ms", "100"]), and E191's
# guard is committed without an exec bit (mode 100644), so this executable file (100755) execs it under bash: the tree's own copy,
# <tree>/tools/claims-v3/e191/ettelem_guard_e191.sh (E191's guard reads the reader as <its folder>/../../../build/ettelem/ettelem, so it
# must sit at its repository path in the box's tree, ~/nekko on aifoundry1, where E191's sync put it and step 5 checks it at its sha256
# 6fd26f51...). Two execs and no fork: the process keeps this file's process ID to the reader (`ettelem`), so the runner's one exempt holder
# (its sampler, by process ID, on /dev/et1_mgmt) is the process that holds the management node. The guard refuses (97) every word but
# `config` and `sample --seconds N --every-ms N`, any box but aifoundry1 and any ET_DEVICES but 1, before the device opens.
#   <E198 root>/tools/claims-v3/e198/ettelem_guard_e198.sh config | sample --seconds N --every-ms N
# SPDX-License-Identifier: Apache-2.0
TREE=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../../.." && pwd -P) || exit 97
exec /bin/bash "$TREE/tools/claims-v3/e191/ettelem_guard_e191.sh" "$@"
