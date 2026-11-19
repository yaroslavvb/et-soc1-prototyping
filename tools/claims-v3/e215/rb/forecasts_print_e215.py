#!/usr/bin/env python3
"""E215's forecasts print for step 2, PRINT ONLY (Q224, lane fix-e215, Thu 19 Nov 2026, before any E215 datum; verify-e215's finding 1).

The frozen scorer's `--forecasts` mode prints its forecasts and the given() self-check AND writes them over the registered
tools/claims-v3/e215/forecasts-e215.txt (score_e215.py's main()). Step 2 runs in the shared lab clone, where it must never rewrite a registered
file (E213's lesson), and comparing that print with the file the same call has just rewritten checks nothing. This file loads the registered
scorer unchanged, by its path (score_e215.py beside this folder), and calls its own forecasts_print(), which checks the scorer's pinned inputs
(exit 4 if a byte changed, the scorer's own refusal) and prints the same bytes to stdout - and writes nothing: no file in the lab clone, and no
bytecode (sys.dont_write_bytecode, with the caller's -B). Step 2 compares this print with the committed bytes (`git show HEAD:...`) and with the
file in the lab clone.

    /usr/bin/python3 -I -B tools/claims-v3/e215/rb/forecasts_print_e215.py > <RB_OUT>/forecasts-e215-check.txt

Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCORER = os.path.normpath(os.path.join(HERE, "..", "score_e215.py"))


def main():
    spec = importlib.util.spec_from_file_location("score_e215", SCORER)
    if spec is None or spec.loader is None:
        print(f"forecasts_print_e215: REFUSED, no scorer at {os.path.basename(SCORER)} beside rb/", file=sys.stderr)
        return 2
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    scorer.forecasts_print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
