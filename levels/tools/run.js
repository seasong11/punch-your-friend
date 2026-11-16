const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage(); await pg.addInitScript(() => { const t0 = performance.now(); let n = 0; performance.now = () => 50000; });
  pg.on('pageerror', e => console.log('PAGEERR', e.message));
  await pg.goto('http://127.0.0.1:8765/proto.html?dbg=1&mock=1', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await pg.waitForFunction(() => window.__ldtk, null, { timeout: 20000 });
  await pg.waitForTimeout(500);
  const info = await pg.evaluate(() => __ldtk.info());
  fs.mkdirSync('out', { recursive: true }); fs.writeFileSync('out/info.json', JSON.stringify(info)); fs.writeFileSync('out/rooms.json', await pg.evaluate(() => JSON.stringify(__pyf.ROOMS)));
  const save = (n, d) => fs.writeFileSync('out/' + n + '.png', Buffer.from(d.split(',')[1], 'base64'));
  const jobs = [];
  for (const r of info) {
    const none = { props: [], decor: [], feat: {} };
    jobs.push(['bg_' + r.i, none]);
    jobs.push(['full_' + r.i, {}]);
    r.props.forEach((_, k) => jobs.push([`p_${r.i}_${k}`, { props: [k], decor: [], feat: {} }]));
    r.decor.forEach((_, k) => jobs.push([`d_${r.i}_${k}`, { props: [], decor: [k], feat: {} }]));
    if (r.climb) for (const key of ['stairs', 'ladders', 'hooks', 'pipes', 'ropes', 'plats', 'ledges', 'els']) (r.climb[key] || []).forEach((_, k) => jobs.push([`f_${r.i}_${key}_${k}`, { props: [], decor: [], feat: { [key]: [k] } }]));
  }
  for (const [n, cfg] of jobs) { const d = await pg.evaluate(([i, c]) => __ldtk.render(i, c), [+n.split('_')[1], cfg]); save(n, d); }
  console.log('rendered', jobs.length); await b.close();
})();
