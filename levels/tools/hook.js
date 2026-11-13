  window.__ldtk = (() => {
    const pal = cv2 => { const g = cv2.getContext('2d'), img = g.getImageData(0, 0, cv2.width, cv2.height), px = new Uint32Array(img.data.buffer);
      for (let i = 0; i < px.length; i++) { const v = px[i]; if ((v >>> 24) === 0) continue; px[i] = LUT[((v & 0xf8) << 7) | ((v >> 6) & 0x3e0) | ((v >> 19) & 0x1f)]; } g.putImageData(img, 0, 0); };
    const levelH = i => ROOMS[i].climb ? ROOMS[i].climb.top * FH - 170 + H : H;
    function info() {
      return ROOMS.map((rm, i) => ({ i, name: rm.name, LH: levelH(i), pairD: i < ROOMS.length - 1 ? pairD(i) : 0, edgeIn: edgeH(i, 0), edgeOut: edgeH(i, 1),
        props: rm.props, decor: rm.decor || [], climb: rm.climb || null, hill: rm.hill || null, ramp: rm.ramp || null, water: rm.water || null, lava: rm.lava || null,
        heights: Array.from({ length: W / 10 }, (_, c) => rm.void ? null : rampAt(c * 10 + 5, rm)) }));
    }
    // cfg: { props: [idx] | null (all), decor: [idx] | null, feat: { stairs: [idx], ... } | null (all) }
    function render(i, cfg) {
      cfg = cfg || {};
      loadRoom(i); R.t = 0; R.t0 = 0;
      const rm = ROOMS[i], keepD = rm.decor, keepC = rm.climb;
      if (cfg.decor && rm.decor) rm.decor = rm.decor.filter((_, k) => cfg.decor.includes(k));
      if (cfg.feat && rm.climb) { const c = { ...rm.climb }; for (const key of ['stairs', 'ladders', 'hooks', 'pipes', 'ropes', 'plats', 'ledges', 'els']) c[key] = (rm.climb[key] || []).filter((_, k) => (cfg.feat[key] || []).includes(k)); rm.climb = c; }
      R.props = R.props.filter((_, k) => !cfg.props || cfg.props.includes(k)); for (const p of R.props) p.x = p.x0;
      R.el = ((rm.climb || {}).els || []).map(e => ({ y: e.lv * 200, st: 'idle', t: 0, stall: 0 }));
      const LH = levelH(i), big = document.createElement('canvas'); big.width = W / PX; big.height = LH / PX; const bg = big.getContext('2d');
      const ch = document.createElement('canvas'); ch.width = W / PX; ch.height = H / PX;
      const cs = []; for (let c = LH - H; c > 0; c -= H) cs.push(c); cs.push(0);
      const saved = ctx;
      try {
        for (const c of cs) {
          const g = ch.getContext('2d', { willReadFrequently: true }); g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, ch.width, ch.height);
          g.scale(1 / PX, 1 / PX); g.translate(0, c); g.fillText = () => {};
          CAMV.y = c; CAMV.rm = R.i; VIEW.x = 0; VIEW.oy = 0; VIEW.dy = 0; VIEW.nb = 1; VIEW.rm = R.i;
          ctx = g; drawRoom(); ctx = saved; TXT.length = 0;
          pal(ch); bg.drawImage(ch, 0, (LH - H - c) / PX);
        }
      } finally { ctx = saved; rm.decor = keepD; rm.climb = keepC; VIEW.nb = 0; }
      return big.toDataURL('image/png');
    }
    return { info, render };
  })();
