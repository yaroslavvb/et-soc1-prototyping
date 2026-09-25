// Render TeX to standalone SVG at build time, so reports carry no external script.
// stdin:  {"items":[{"tex":"...","display":true}, ...]}
// stdout: {"svg":["<svg .../>", ...]}
// mathjax-full is pinned in package.json (run `npm ci` at the repo root); scripts/build-report.py calls this script.
const {mathjax} = require('mathjax-full/js/mathjax.js');
const {TeX} = require('mathjax-full/js/input/tex.js');
const {SVG} = require('mathjax-full/js/output/svg.js');
const {liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js');
const {AllPackages} = require('mathjax-full/js/input/tex/AllPackages.js');

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', {InputJax: new TeX({packages: AllPackages}), OutputJax: new SVG({fontCache: 'local'})});

let buf = '';
process.stdin.on('data', d => (buf += d));
process.stdin.on('end', () => {
  const items = JSON.parse(buf).items;
  const svg = items.map(it => {
    const node = doc.convert(it.tex, {display: !!it.display, em: 16, ex: 8, containerWidth: 900});
    return adaptor.innerHTML(node);  // the <svg> itself; MathJax colours it with currentColor
  });
  process.stdout.write(JSON.stringify({svg}));
});
