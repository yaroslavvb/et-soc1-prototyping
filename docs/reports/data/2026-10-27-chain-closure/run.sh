#!/bin/sh
# Q128(f) — rebuild every number in this directory from the committed data in this repo.
#   sh run.sh <repo-root> <this-dir>
set -e
R="${1:?repo root}"; O="${2:?out dir}"
{
  /usr/local/bin/python3.12 "$O/chain.py"     "$R" "$O"
  /usr/local/bin/python3.12 "$O/models.py"    "$R" "$O"
  /usr/local/bin/python3.12 "$O/effective.py" "$R" "$O"
  /usr/local/bin/python3.12 "$O/position.py"  "$R" "$O"
} | tee "$O/report.txt"
