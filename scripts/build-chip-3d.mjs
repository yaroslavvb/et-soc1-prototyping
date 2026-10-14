// npm ci && node scripts/build-chip-3d.mjs
// Keep one portable artifact: no CDN, runtime downloads, or auxiliary files.
import {build} from 'esbuild';
import {readFileSync, writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {Script} from 'node:vm';
const root=resolve(import.meta.dirname,'..');
const dir=resolve(root,'docs/reports/sources/chip-3d');
const result=await build({entryPoints:[resolve(dir,'app.js')],bundle:true,minify:true,format:'iife',target:['es2020'],write:false,legalComments:'inline'});
const license=readFileSync(resolve(root,'node_modules/three/LICENSE'),'utf8');
// Three's embedded shader literals contain insignificant trailing whitespace.
const code=result.outputFiles[0].text.replace(/[ \t]+\n/g,'\n').replaceAll('</script','<\\/script');
new Script(code); // Validate the actual embedded output, not only its sources.
const html=readFileSync(resolve(dir,'shell.html'),'utf8')
 .replace('/* INLINE_STYLES */',()=>readFileSync(resolve(dir,'style.css'),'utf8'))
 .replace('/* INLINE_APP */',()=>code)
 .replace('<!-- THIRD_PARTY_LICENSE -->',()=>`<!-- Three.js 0.180.0 — ${license.replaceAll('--','—')} -->`);
new Script(html.slice(html.indexOf('<script>')+8,html.lastIndexOf('</script>')));
writeFileSync(resolve(root,'docs/reports/chip-3d.html'),html);
console.log(`Built chip-3d.html: ${Buffer.byteLength(html)} bytes, self-contained.`);
