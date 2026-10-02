#!/bin/bash
# publish-gh-pages.sh: mirror the interactive pages to GitHub Pages (branch gh-pages of this repository).
#
#   tools/publish-gh-pages.sh            build the site from the committed pages on main and push branch gh-pages
#   tools/publish-gh-pages.sh --dry-run  build it into ~/claude/work/gh-pages-site and stop
#
# The site is https://yaroslavvb.github.io/et-soc1-prototyping/ (the owner asked on 1 Oct 2026 for the chip diagram to be
# mirrored there, where links with #anchors work directly). The canonical copies stay on spacesheep.dev; MIRROR.md lists
# both. The site holds only built pages that are already public, with the files they load beside them:
#   /chip-diagram/   docs/reports/2026-09-27-et-soc1-chip-diagram.html as index.html, and docs/reports/ladder-img/
#   /memory-levels/  docs/reports/2026-09-28-et-soc1-memory-levels.html as index.html
#   /                a short index linking both and their spacesheep originals
# gh-pages is generated: each run replaces it with one fresh commit (force-push), so never edit it by hand.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
REV=$(git rev-parse --short HEAD)
OUT=${GHP_OUT:-$HOME/claude/work/gh-pages-site}
rm -rf "$OUT"; mkdir -p "$OUT/chip-diagram" "$OUT/memory-levels"

# Build from the committed files of HEAD, never from the working tree, so the mirror equals a commit.
git show "HEAD:docs/reports/2026-09-27-et-soc1-chip-diagram.html" > "$OUT/chip-diagram/index.html"
mkdir -p "$OUT/chip-diagram/ladder-img"
for f in $(git ls-tree --name-only "HEAD:docs/reports/ladder-img"); do
  git show "HEAD:docs/reports/ladder-img/$f" > "$OUT/chip-diagram/ladder-img/$f"
done
git show "HEAD:docs/reports/2026-09-28-et-soc1-memory-levels.html" > "$OUT/memory-levels/index.html"
touch "$OUT/.nojekyll"
cat > "$OUT/index.html" <<EOF
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ET-SoC-1, interactively</title>
<style>
:root{color-scheme:light dark;--ink:#1a1a1f;--muted:#5c5c68;--page:#fafafa;--link:#2f5fd0}
@media (prefers-color-scheme:dark){:root{--ink:#eceef3;--muted:#a2aab8;--page:#16181d;--link:#8fb0ff}}
body{margin:0;background:var(--page);color:var(--ink);font:17px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:640px;margin:0 auto;padding:40px 16px}
h1{font-size:1.6rem;margin:0 0 6px}p{margin:8px 0}.muted{color:var(--muted);font-size:.9rem}
a{color:var(--link)}ul{padding-left:1.2em}li{margin:10px 0}
</style></head><body><main>
<h1>ET-SoC-1, interactively</h1>
<p class="muted">A mirror of two interactive pages about Esperanto's ET-SoC-1, from
<a href="https://github.com/yaroslavvb/et-soc1-prototyping">github.com/yaroslavvb/et-soc1-prototyping</a> (commit ${REV}).
The originals, with comments and versions, are on spacesheep.dev.</p>
<ul>
<li><a href="chip-diagram/"><b>The ET-SoC-1, interactively</b></a>: the chip, its flows, and a zoom from the rack down to atoms
(<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram">original</a>)</li>
<li><a href="memory-levels/"><b>Anatomy of a memory access, interactively</b></a>: each level of the memory system, down to the
transistors (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-levels">original</a>)</li>
</ul>
<p class="muted">All the measurement reports: <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability">the ET-SoC-1 reports hub</a>.</p>
</main></body></html>
EOF
echo "built $OUT from $REV: $(find "$OUT" -type f | wc -l) files, $(du -sh "$OUT" | cut -f1)"
[ $DRY = 1 ] && exit 0

# One fresh orphan commit on gh-pages, made in a temporary worktree so the main checkout is never touched.
WT=$(mktemp -d -p "$HOME/claude/work" ghp-wt.XXXXXX); rmdir "$WT"
cleanup() { git worktree remove --force "$WT" >/dev/null 2>&1 || true; git branch -D ghp-build >/dev/null 2>&1 || true; }
trap cleanup EXIT
git branch -D ghp-build >/dev/null 2>&1 || true
git worktree add -q --orphan -b ghp-build "$WT"
cp -a "$OUT/." "$WT/"
git -C "$WT" add -A
git -C "$WT" commit -q -m "GitHub Pages mirror of the interactive pages, built from $REV by tools/publish-gh-pages.sh"
git -C "$WT" push -q -f origin ghp-build:gh-pages
echo "pushed gh-pages ($(git -C "$WT" rev-parse --short HEAD)); the site: https://yaroslavvb.github.io/et-soc1-prototyping/"
