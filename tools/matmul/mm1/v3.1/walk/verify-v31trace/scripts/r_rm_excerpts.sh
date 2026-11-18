#!/bin/bash
# verify-v31trace (Q217), run ON aifoundry3 by a3.sh look: remove run u1's raw log excerpts by their literal paths (copies kept on the
# desk in work/u1, hashed), then show what stays in this lane's folder there. Nothing of v31-trace's folder is touched.
rm -f ~/claude/work/q217-verify-v31trace/runs/u1/excerpt-hart0.log.gz
rm -f ~/claude/work/q217-verify-v31trace/runs/u1/excerpt-hart1.log.gz
rm -f ~/claude/work/q217-verify-v31trace/runs/u1/excerpt-hart830.log.gz
rm -f ~/claude/work/q217-verify-v31trace/runs/u1/excerpt-shire1.log.gz
rm -f ~/claude/work/q217-verify-v31trace/runs/u1/excerpt-shire31.log.gz
du -sh ~/claude/work/q217-verify-v31trace
ls ~/claude/work/q217-verify-v31trace/runs/u1 | tr '\n' ' '; echo
echo "sim runs of this user: $(pgrep -u "$(id -u)" -f 'sparsity_host --sysemu' | wc -l)"
timeout 20 et-who 2>&1 | head -1
