# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 20:15 PST: v2 read adversarially, and v3

*Added after v2's commit `16771f36` (15:34:42 PST). README.md and every file `16771f36` added stay as they are. On 4 Nov they ran
from 16:21 PST on aifoundry2: its later waits and looks, E169's launch, and the E167, E168 and E169 collections. The corrections
are new files, in [`../v3/`](../v3/README.md).*

No verifier had read v2. The card half's critic (Q141's card half, 4 Nov 2026) asked for one in its next step 4. Q142(s)'s
adversarial read found 12 faults, none touching a device command, a stop or a frozen number:
- **3 moderate:**
  - `s22 e163`'s absolute raw copy, which would put the Intel's home path into E163's `e163.json` and `runs.csv`;
  - `s22 e166` reporting a partial copy as collected and scored;
  - no launch re-checking the host's firmware identity.
- **6 minor and 3 nits:** the rest, listed with their fixes in v3's README, § What v3 changes.

None bit on 4 Nov, as far as the committed records show. E163 was collected by hand over a repo-relative copy (its D1). E166's,
E167's, E168's and E169's copies completed, and E167's committed `history/` holds no raw file. Both identity reads that day read ok.

**For any later step or card day, use [`../v3/`](../v3/README.md)**: the same steps, arguments and exit codes, called as
`bash tools/claims-v3/q141k-runbook/v3/<script>`. It reads the same state on the boxes. Its desk test passes 453 of 453 checks, and
`dmcmd_audit` reads GO on its files with E128's guard beside them.

SPDX-License-Identifier: Apache-2.0
