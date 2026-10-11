// Liest die gerenderten Kataloge (VRF/PV/Großanlagen, DE/EN) aus – Eingabe fuer seo_build.py.
// Aufruf: node tools/extract_catalog.mjs /tmp/catalog-data.json   (benoetigt playwright)
import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const b = await chromium.launch();
const out = {};
const cards = () => [...document.querySelectorAll('#grid article.card')].map(c=>{
  const spec={}; const dts=c.querySelectorAll('dl.spec dt'); dts.forEach(dt=>spec[dt.textContent.trim()]=dt.nextElementSibling.textContent.trim());
  const rows=[...c.querySelectorAll('table.vt tbody tr')].map(r=>[...r.cells].map(td=>td.textContent.trim()));
  return {mf:c.querySelector('.mf')?.textContent.trim(), series:c.querySelector('h3')?.textContent.trim(), code:c.querySelector('.code')?.textContent.trim(),
    models:[...c.querySelectorAll('.models span')].map(s=>s.textContent.trim()), spec, rows, price:c.querySelector('.price')?.childNodes[0]?.textContent.trim(),
    note:c.querySelector('.price')?'':[...c.querySelectorAll('p')].map(x=>x.textContent.trim()).join(' ')};
});
async function click(pg, sel){ await pg.click(sel); await pg.waitForTimeout(300); }
for (const p of ['vrf/index.html','en/vrf/index.html','pv/index.html','en/pv/index.html','grossanlagen/index.html','en/grossanlagen/index.html','index.html','en/index.html']){
  const pg = await b.newPage();
  await pg.goto('file://'+ROOT+'/'+p); await pg.waitForTimeout(800);
  const r = {};
  r.dataT = await pg.evaluate(()=>{const o={}; document.querySelectorAll('[data-t]').forEach(e=>{o[e.dataset.t]=e.innerHTML;}); return o;});
  r.title = await pg.title();
  if (p.includes('vrf') || p.includes('grossanlagen')) {
    r.std = await pg.evaluate(cards);
    await click(pg,'button[data-v="pro"]'); r.pro = await pg.evaluate(cards);
  }
  if (p.includes('pv')) {
    for (const m of ['wall','free']) { await click(pg,`button[data-m="${m}"]`);
      for (const v of ['plus','pro']) { await click(pg,`button[data-v="${v}"]`); r[m+'_'+v]=await pg.evaluate(cards); } }
  }
  out[p]=r; await pg.close();
}
fs.writeFileSync(process.argv[2] || 'catalog-data.json', JSON.stringify(out,null,1));
await b.close();
for (const [k,v] of Object.entries(out)) console.log(k, Object.keys(v).map(x=>x+':'+(Array.isArray(v[x])?v[x].length:'')).join(' '));
