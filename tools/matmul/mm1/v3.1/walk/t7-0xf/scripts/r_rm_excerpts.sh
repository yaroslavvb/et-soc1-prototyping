#!/bin/bash
# t7-0xf (Q221), run ON aifoundry3 by a3.sh look: remove run u2's raw log excerpts by their literal paths (copies kept on the desk in
# work/u2, hashed in work/u2.SHA256SUMS.fetched), then show what stays in this lane's folder there. Nothing of v31-trace's or
# verify-v31trace's folders is touched.
rm -f ~/claude/work/q221-t7-0xf/runs/u2/excerpt-hart0.log.gz
rm -f ~/claude/work/q221-t7-0xf/runs/u2/excerpt-hart1.log.gz
rm -f ~/claude/work/q221-t7-0xf/runs/u2/excerpt-hart254.log.gz
rm -f ~/claude/work/q221-t7-0xf/runs/u2/excerpt-shire4.log.gz
rm -f ~/claude/work/q221-t7-0xf/runs/u2/excerpt-shire31.log.gz
du -sh ~/claude/work/q221-t7-0xf
ls ~/claude/work/q221-t7-0xf/runs/u2 | tr '\n' ' '; echo
echo "sim runs of this user: $(pgrep -u "$(id -u)" -f 'sparsity_host --sysemu' | wc -l)"
timeout 20 et-who 2>&1 | head -1
