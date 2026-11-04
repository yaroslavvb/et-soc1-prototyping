# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 15:40 PST: Q141(k)'s verifier, and v2

*Added after Q141(k)'s commit `e962227a` (14:08:36 PST). README.md and every file `e962227a` added stay as they are: the card half of
4 Nov ran them from 14:18 PST on all three boxes, and E170's box kit sources `rb_common.sh`. The corrections are new files, in
[`v2/`](v2/README.md).*

Q141(k)'s adversarial verifier (about 14:15-14:40 PST) re-derived the runbook (the desk test 152 of 152, the dry listing 50 of 50,
`dmcmd_audit` GO with E128's guard scanned beside it, the public-text scan clean, the four hash lists) and found it **holds with
fixes**: five minor faults and four nits, none touching a device command, a stop or a frozen number.

| # | what the verifier found in this directory's files | v2 |
|---|---|---|
| 1 | `s13_a1_launch.sh` launches E164 while s12's detached box check (V3_DRY 16410, 16401, 16402) may still run: no `jobs_live` guard, which every other launch has | a guard read first, and s12's clean read required |
| 2 | `rb_common.sh:287-299`: a lost dry job (no process, no exit status) reads JOB-RUNNING after JOB-LOST, so `rb_job_wait` returns 17 ("call again") on every call | JOB-LOST alone, exit 14 |
| 3 | `s11_a3_session.sh e166` without `--later-try` reuses an earlier E166 smoke (`p16601`): its old gate reads GO and the five stop tests do not run | a plain retry is refused |
| 4 | `s22_collect.sh e167` probes only aifoundry2, though `collect_e167_bounded.sh` reads all three boxes' history, and a link from aifoundry1 or aifoundry3 is written as "aifoundry2 needs a check" | three probes; the lock line names the collector's box |
| 5 | nothing gates aifoundry2's firmware identity (BL2 0.22.0): `et-lab-manifest` reads sysfs only, and `s14_a2_tree.sh` compares `uptime -s` with nothing | the boot must precede E69's firmware read (2026-10-27 13:56:26 PDT), else 16 |
| nits | `s09_a3_reads.sh` reads card 0 with no check for a session of ours; this README's "each launch refuses otherwise" is not so for E163; "dmcmd_audit GO (no send site of its own)" in the commit message holds only with E128's guard scanned beside the runbook (one call site, `s09_a3_reads.sh:21`, a READ); the box-side state carries no date | each fixed or restated in v2 |

On 4 Nov faults 1 and 2 did not bite (s12's wait read rc 0 at 14:19:02, before s13 at 14:19:42; all six dry jobs that day read
JOB-DONE rc=0), step 14 read aifoundry2's boot as `2026-10-26 15:13:03` both times (fault 5's rule holds), and step 9 ran before
E166's session (14:18:55; the session launched at 14:20:56). Fault 4 concerns E167's collection, after E167's session.

**For any later step or card day, use [`v2/`](v2/README.md)**: the same steps, arguments and exit codes, called as
`bash tools/claims-v3/q141k-runbook/v2/<script>`. It reads the same state on the boxes and takes what was written that day, so a lane
can switch at any step.

SPDX-License-Identifier: Apache-2.0
