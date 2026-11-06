# Dated note beside `gen-a1.sha256` (Thu 5 Nov 2026; the records round Q143(r)): it lists amendment A1's generator tree, so its `manifest.json` is this directory's `manifest-a1.json`; not a mismatch

*Written on the Intel at about 19:55 PST on Thu 5 Nov 2026, desk only. [`gen-a1.sha256`](gen-a1.sha256) and every file of this directory
stay as committed. This answers the pool-8 card day's critic, whose records list counted it among three legacy lists that a
checker reads as mismatched (E171's verifier found it); the critic of Q142(h2), (a2) and (r3) had read it as a path-resolution artefact.*

`gen-a1.sha256` (64 lines) was committed with amendment A1 in lab `f43be959` (Tue 20 Oct 2026, 20:28 PDT). It lists the A1 generator's
own output tree: that tree's `manifest.json` and 63 tiles, which are not in this repository. In this directory that manifest is committed
as **`manifest-a1.json`**, and its sha256 is the listed `26b4d9ca…`. A checker that resolves the entry `manifest.json` here reads instead the
original [`manifest.json`](manifest.json) (`39b0507a…`, the one [`gen.sha256`](gen.sha256) lists, committed in `df69634e`, 20:19 PDT), and
reports a mismatch. **None exists:** neither file has changed since its commit, and no later commit touched this list. Read the list against
`manifest-a1.json` and A1's generator tree.

SPDX-License-Identifier: Apache-2.0
