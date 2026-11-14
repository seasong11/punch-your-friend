include("spectrum.px.js")
// Punch Your Friend: rooftop section test set. Endesga 64 only.
pal({
  k: "#0e071b", n: "#1a1932", N: "#2a2f4e", b: "#424c6e", B: "#657392", s: "#92a1b9", S: "#c7cfdd", w: "#ffffff",
  p: "#3b1443", P: "#622461", q: "#93388f", Q: "#ca52c9", m: "#c85086", M: "#f68187", i: "#fdd2ed",
  r: "#ea323c", R: "#891e2b", d: "#571c27",
  u: "#391f21", U: "#5d2c28", t: "#8a4836", T: "#bf6f4a", o: "#e69c69",
  a: "#ffa214", y: "#ffc825", Y: "#ffeb57",
  f: "#03193f", E: "#00396d", e: "#0069aa", C: "#0098dc", c: "#0cf1ff",
  j: "#272727", g: "#3d3d3d", G: "#5d5d5d", h: "#858585", H: "#b4b4b4",
  x: "#1c121c", v: "#33984b", V: "#1e6f50",
})
ramps("knNbBsSw", "kpPqQi", "xuUtTo", "kdRr", "fEeCc", "jgGhH", "ayY")

// ---------- 16 px tiles ----------
const brick = (c, hi = true) => {
  c.rect(0, 0, 16, 16, "U")
  for (let r = 0; r < 4; r++) {
    const y = r * 4, off = r % 2 ? 4 : 0
    c.hline(0, y + 3, 16, "u")
    for (let x = off; x < 16; x += 8) {
      c.vline(x, y, 3, "u")
      if (hi) c.hline(x + 1, y, 7, "t")
    }
  }
}
const cap = (c) => {            // concrete parapet cap on top of brick
  c.rect(0, 0, 16, 5, "B")
  c.hline(0, 0, 16, "S"); c.hline(0, 1, 16, "s")
  c.hline(0, 4, 16, "b"); c.hline(0, 5, 16, "x")
}
sprite("roof_m", { w: 16, h: 16 }, (c) => { brick(c); cap(c); c.vline(7, 2, 2, "b") })
sprite("roof_l", { w: 16, h: 16 }, (c) => {
  brick(c); cap(c); c.vline(0, 0, 16, "k"); c.vline(1, 6, 10, "t"); c.px(0, 0, "_"); c.px(1, 0, "S")
})
sprite("roof_r", { w: 16, h: 16 }, (c) => {
  brick(c); cap(c); c.vline(15, 0, 16, "k"); c.vline(14, 5, 11, "u"); c.vline(13, 6, 10, "u"); c.px(15, 0, "_")
})
sprite("wall_m", { w: 16, h: 16 }, (c) => brick(c))
sprite("wall_b", { w: 16, h: 16 }, (c) => {      // weathered variant: rain stain + missing highlights
  brick(c, false); c.hline(1, 0, 7, "t"); c.hline(5, 12, 7, "t")
  c.vline(10, 0, 9, "u"); c.vline(11, 0, 5, "u")
})
sprite("wall_l", { w: 16, h: 16 }, (c) => { brick(c); c.vline(0, 0, 16, "k"); c.vline(1, 0, 16, "t") })
sprite("wall_r", { w: 16, h: 16 }, (c) => { brick(c); c.vline(15, 0, 16, "k"); c.vline(14, 0, 16, "u"); c.vline(13, 0, 16, "u") })
// windows: 16x32 (two tiles tall), each cut into a top and a bottom tile
const winBase = (c) => {
  c.rect(1, 2, 14, 3, "s"); c.hline(1, 2, 14, "S"); c.hline(1, 4, 14, "b"); c.px(8, 3, "b")   // stone lintel with keystone joint
  c.hline(2, 5, 12, "x")
  c.rect(2, 6, 12, 20, "k")                                   // recess
  c.box(3, 6, 10, 20, "S"); c.vline(12, 6, 20, "s"); c.hline(3, 25, 10, "s")   // painted frame
  c.rect(0, 26, 16, 3, "s"); c.hline(0, 26, 16, "S"); c.hline(0, 28, 16, "b")  // sill
  c.hline(1, 29, 14, "x"); c.dither(1, 30, 14, 1, "U", "u", 0.5)                // sill shadow on the brick
}
const sash = (c) => { c.hline(4, 15, 8, "S"); c.hline(4, 16, 8, "k"); c.vline(8, 7, 8, "S"); c.vline(8, 17, 8, "s") }
const winSprite = (name, paint, glowKeys) => {
  const items = [stamp("wall_m", 0, 0), stamp("wall_m", 0, 16), (c) => { winBase(c); paint(c); sash(c) }]
  if (glowKeys) items.push(glow(glowKeys, { r: 3, ramp: 1 }))
  sprite(name, { w: 16, h: 32 }, ...items)
  sprite(name + "_top", { w: 16, h: 16 }, stamp(name, 0, 0))
  sprite(name + "_bot", { w: 16, h: 16 }, stamp(name, 0, -16))
}
winSprite("win_curtain", (c) => {          // warm room, red curtains, plant on the sill
  c.rect(4, 7, 8, 18, "y"); c.rect(4, 7, 8, 4, "Y"); c.rect(4, 20, 8, 5, "a")
  c.rect(4, 7, 2, 18, "R"); c.vline(4, 7, 18, "r"); c.rect(10, 7, 2, 18, "R"); c.vline(11, 7, 18, "d")
  c.px(6, 7, "R"); c.px(9, 7, "R"); c.hline(4, 7, 8, "d")   // curtain rod
  c.rect(6, 22, 3, 3, "t"); c.hline(6, 22, 3, "T"); c.px(7, 21, "V"); c.px(6, 20, "v"); c.px(8, 20, "v"); c.px(7, 19, "v"); c.px(9, 21, "V")
}, "yY")
winSprite("win_blinds", (c) => {           // half-raised blinds, someone looking out
  c.rect(4, 7, 8, 18, "Y")
  for (let y = 7; y < 15; y++) c.hline(4, y, 8, y % 2 ? "a" : "y")
  c.hline(4, 14, 8, "T")
  c.rect(6, 19, 4, 3, "u"); c.rect(5, 22, 6, 3, "u"); c.px(6, 19, "Y"); c.px(9, 19, "Y")   // head and shoulders
  c.vline(11, 17, 8, "y")
}, "yY")
winSprite("win_tv", (c) => {               // dark room lit by a TV, cat on the sill
  c.rect(4, 7, 8, 18, "E"); c.rect(4, 7, 8, 8, "f")
  c.rect(4, 17, 8, 4, "e"); c.rect(5, 18, 5, 2, "C"); c.px(6, 18, "c"); c.px(8, 19, "c")
  c.rect(8, 22, 3, 3, "k"); c.rect(9, 20, 2, 2, "k"); c.px(9, 19, "k"); c.px(10, 19, "k"); c.px(7, 24, "k"); c.px(6, 23, "k")   // cat
  c.px(9, 21, "Y")
}, "Cc")
winSprite("win_dark", (c) => {             // nobody home: reflections of the moon and sky
  c.rect(4, 7, 8, 18, "f")
  c.line(4, 13, 7, 10, "E"); c.line(5, 14, 7, 12, "E"); c.line(9, 24, 11, 22, "E"); c.line(9, 22, 11, 20, "E"); c.line(4, 22, 6, 20, "E")
  c.rect(9, 9, 2, 2, "i"); c.px(10, 9, "M")
  c.rect(4, 17, 8, 8, "n"); c.vline(5, 17, 8, "N"); c.vline(7, 17, 8, "N"); c.vline(10, 17, 8, "N")   // drawn curtain
})
winSprite("win_ac", (c) => {               // dim window with an AC unit hanging out and a drip stain
  c.rect(4, 7, 8, 18, "f"); c.line(4, 12, 7, 9, "E"); c.line(9, 13, 11, 11, "E")
  c.rect(2, 18, 12, 8, "h"); c.hline(2, 18, 12, "S"); c.box(2, 18, 12, 8, "k"); c.hline(3, 19, 10, "H")
  for (let y = 21; y < 25; y += 2) c.hline(4, y, 8, "g")
  c.px(12, 20, "r")
  c.vline(7, 29, 3, "u"); c.vline(8, 29, 2, "u")
})
// stone belt course: marks the floor line between storeys
const belt = (c) => { c.rect(0, 0, 16, 4, "s"); c.hline(0, 0, 16, "S"); c.hline(0, 3, 16, "b"); c.hline(0, 4, 16, "x"); c.px(8, 1, "b"); c.px(8, 2, "b") }
sprite("belt_m", { w: 16, h: 16 }, (c) => { brick(c); belt(c) })
sprite("belt_r", { w: 16, h: 16 }, (c) => { brick(c); belt(c); c.vline(15, 0, 16, "k"); c.vline(14, 4, 12, "u"); c.vline(13, 4, 12, "u") })
const WINS = ["win_curtain", "win_dark", "win_blinds", "win_tv", "win_ac"]

// one-way platform: steel I-beam (top 7 px solid, rest empty)
const beam = (c) => {
  c.rect(0, 0, 16, 2, "H"); c.hline(0, 0, 16, "S"); c.hline(0, 2, 16, "G")
  c.rect(0, 3, 16, 2, "g"); c.hline(0, 5, 16, "h"); c.hline(0, 6, 16, "j")
  c.px(3, 3, "h"); c.px(11, 3, "h")      // rivets
}
sprite("plat_m", { w: 16, h: 16 }, (c) => beam(c))
sprite("plat_l", { w: 16, h: 16 }, (c) => { beam(c); c.vline(0, 0, 7, "k"); c.rect(1, 0, 3, 7, "a"); c.vline(2, 1, 5, "j"); c.px(1, 0, "Y") })
sprite("plat_r", { w: 16, h: 16 }, (c) => { beam(c); c.vline(15, 0, 7, "k"); c.rect(12, 0, 3, 7, "a"); c.vline(13, 1, 5, "j"); c.px(12, 0, "Y") })

sheet("rooftop_tiles", ["roof_l", "roof_m", "roof_r", "plat_l", "plat_m", "wall_l", "wall_m", "wall_r", "wall_b", "plat_r",
  ...WINS.map((n) => n + "_top"), ...WINS.map((n) => n + "_bot"), "belt_m", "belt_r"], { cols: 5, pad: 0 })

// ---------- props ----------
sprite("water_tower", { w: 36, h: 54, outline: "k" }, (c) => {
  // legs + cross bracing
  for (const x of [5, 29]) { c.rect(x, 34, 2, 20, "g"); c.vline(x, 34, 20, "G") }
  c.line(6, 38, 29, 52, "g"); c.line(29, 38, 6, 52, "g"); c.hline(5, 44, 26, "G")
  c.rect(2, 32, 32, 3, "G"); c.hline(2, 32, 32, "h")
  // barrel
  c.rect(4, 10, 28, 22, "t")
  for (let x = 4; x < 32; x += 4) c.vline(x, 10, 22, "U")
  c.rect(4, 10, 5, 22, "U"); c.rect(26, 10, 6, 22, "U"); c.rect(29, 10, 3, 22, "u")
  c.rect(13, 10, 6, 22, "T"); c.vline(15, 10, 22, "o")
  for (const y of [14, 26]) { c.hline(4, y, 28, "g"); c.hline(10, y, 10, "h") }
  // cone roof
  c.poly([18, 0, 35, 10, 1, 10], "G"); c.poly([18, 0, 18, 10, 1, 10], "h"); c.line(18, 1, 6, 9, "H")
  c.hline(1, 9, 34, "g"); c.px(17, 0, "H")
})
sprite("ac_unit", { w: 26, h: 15, outline: "k" }, (c) => {
  c.rect(0, 0, 26, 15, "h"); c.hline(0, 0, 26, "S"); c.hline(0, 1, 26, "H"); c.rect(0, 12, 26, 3, "G")
  c.rect(20, 2, 6, 13, "G")
  c.circ(8, 7, 5, "j"); c.ring(8, 7, 5, "g"); c.line(4, 7, 12, 7, "G"); c.line(8, 3, 8, 11, "G"); c.px(8, 7, "H")
  for (let y = 4; y < 11; y += 2) c.hline(15, y, 4, "g")
  c.px(22, 4, "r")
})
sprite("vent", { w: 12, h: 20, outline: "k" }, (c) => {
  c.rect(3, 6, 6, 14, "h"); c.vline(3, 6, 14, "H"); c.rect(7, 6, 2, 14, "G"); c.hline(3, 12, 6, "g")
  c.rect(0, 2, 12, 4, "G"); c.hline(0, 2, 12, "H"); c.poly([6, 0, 12, 2, 0, 2], "h")
  c.rect(1, 18, 10, 2, "g")
})
sprite("antenna", { w: 15, h: 44, outline: "k" }, (c) => {
  c.vline(7, 2, 42, "h"); c.hline(1, 8, 13, "G"); c.hline(3, 14, 9, "G"); c.hline(5, 20, 5, "G")
  c.line(7, 30, 2, 43, "g"); c.line(7, 30, 12, 43, "g")
  c.rect(6, 0, 3, 3, "r"); c.px(7, 0, "M")
})
sprite("neon_sign", { w: 50, h: 40, outline: "k" }, (c) => {
  for (const x of [6, 42]) { c.rect(x, 17, 2, 23, "g"); c.vline(x, 17, 23, "G") }
  c.line(8, 30, 42, 20, "g")
  c.rect(0, 0, 50, 18, "n"); c.box(0, 0, 50, 18, "N"); c.box(2, 2, 46, 14, "Q")
  c.text(25, 5, "PUNCH", "i", { scale: 2, align: "c", shadow: "m" })
}, glow("Qi", { r: 5, ramp: 1 }))

// ---------- background, three parallax layers ----------
const skyline = (c, seed, base, hmin, hmax, body, edge, wins, density) => {
  const r = c.rng(seed)
  let x = -6
  while (x < 400) {
    const w = 18 + Math.floor(r() * 30), h = hmin + Math.floor(r() * (hmax - hmin)), top = base - h
    c.rect(x, top, w, h + 80, body)
    c.vline(x, top, h + 80, edge); c.hline(x, top, w, edge)
    const kind = r()
    if (kind < 0.3) { c.rect(x + 3, top - 5, w - 6, 5, body); c.hline(x + 3, top - 5, w - 6, edge) }   // setback
    else if (kind < 0.5) { c.vline(x + (w >> 1), top - 12, 12, body); c.px(x + (w >> 1), top - 13, "r") } // mast
    else if (kind < 0.62) { c.rect(x + 4, top - 7, 7, 7, body); c.poly([x + 3, top - 7, x + 8, top - 11, x + 12, top - 7], body) } // tank
    if (wins) {
      const lit = 0.15 + r() * density
      for (let wy = top + 4; wy < base + 40; wy += 6)
        for (let wx = x + 3; wx < x + w - 3; wx += 5)
          if (r() < lit) c.rect(wx, wy, 2, 3, wins[Math.floor(r() * wins.length)])
    }
    x += w + (r() < 0.3 ? 2 + Math.floor(r() * 6) : 0)
  }
}
// ---- beat helpers: one loop = one bar of 4 beats (rooftop track "Neon Ledge" is 146 BPM) ----
const BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
const beatOf = (c) => { const t = (c.frame ?? 0) * 0.05 * 146 / 60, i = Math.floor(t) % 4; return { i, e: c.frames > 1 ? Math.exp(-3.5 * (t % 1)) : 0 } }  // e: 1 on the beat, decays
const drawSky = (c) => {
  const { i, e } = beatOf(c)
  // smooth sky: every pixel is dithered between its two nearest colors. On each beat the horizon glow swells upward.
  const keys = "knpPqm", H = 190 - 14 * e * (i % 2 ? 0.6 : 1)
  for (let y = 0; y < 224; y++) {
    const t = Math.min(1, y / H) ** 1.25 * (keys.length - 1), k = Math.min(keys.length - 2, Math.floor(t)), fr = t - k
    for (let x = 0; x < 400; x++) c.px(x, y, fr > (BAYER[y & 3][x & 3] + 0.5) / 16 ? keys[k + 1] : keys[k])
  }
  c.noise(0, 0, 400, 70, "S", 0.002, 5)
  if (c.frames > 1 ? i % 2 === 0 : true) c.noise(0, 0, 400, 40, "w", 0.001, 9)      // stars twinkle on alternate beats
  if (i === 0 && e > 0.25) c.ring(318, 44, 17 + Math.round((1 - e) * 8), e > 0.55 ? "m" : "q")   // moon ripple on the downbeat
  c.circ(318, 44, 15, "i"); c.circ(313, 40, 3, "M"); c.circ(324, 50, 4, "M"); c.circ(322, 36, 2, "M")
}
// far layer: same building language as the mid layer, but smaller, dimmer and hazier.
// On the beat the towers bob like an equalizer: even ones on beats 1 and 3, odd ones on 2 and 4.
const drawFar = (c) => {
  const { i, e } = beatOf(c)
  const r = c.rng(3), base = 150
  let x = -4, n = 0
  while (x < 400) {
    const w = 4 * (3 + Math.floor(r() * 5)) + 5, h0 = 24 + Math.floor(r() * 50)   // width always fits whole window columns
    const amp = 2 + Math.floor(r() * 3), h = h0, top = base - h   // buildings never move
    n++
    c.rect(x, top, w, h + 80, "P")
    c.rect(x + w - 3, top, 3, h + 80, "p")                 // shaded right side gives volume
    c.hline(x, top, w - 3, "q")                             // moonlit roof edge only
    const kind = r()
    if (kind < 0.35) { c.rect(x + 3, top - 4, w - 8, 4, "P"); c.hline(x + 3, top - 4, w - 8, "q"); c.rect(x + w - 7, top - 4, 2, 4, "p") }
    else if (kind < 0.55) { c.vline(x + (w >> 1), top - 10, 10, "p"); c.px(x + (w >> 1), top - 11, "r") }
    else if (kind < 0.7) { c.rect(x + 3, top - 5, 5, 5, "p"); c.poly([x + 2, top - 5, x + 6, top - 8, x + 9, top - 5], "p") }
    // one window language for the whole city: the same even grid on every building, edge to edge, top to bottom
    for (let wy = top + 3; wy < base + 40; wy += 5)
      for (let wx = x + 2; wx < x + w - 5; wx += 4) c.rect(wx, wy, 2, 3, "p")
    x += w
  }
}
const drawMid = (c, unlit) => {
  const rects = []
  const r = c.rng(8), wr = c.rng(21), base = 196, spec = c.frames > 1 ? SPEC[c.frame % SPEC.length] : null
  let x = -6
  while (x < 400) {
    const w = 14 + 5 * Math.floor(r() * 3), h = 26 + Math.floor(r() * 74), top = base - h
    c.rect(x, top, w, h + 80, "p"); c.vline(x, top, h + 80, "P"); c.hline(x, top, w, "P")
    const kind = r()
    if (kind < 0.3) { c.rect(x + 3, top - 5, w - 6, 5, "p"); c.hline(x + 3, top - 5, w - 6, "P") }
    else if (kind < 0.5) { c.vline(x + (w >> 1), top - 12, 12, "p"); c.px(x + (w >> 1), top - 13, "r") }
    else if (kind < 0.62) { c.rect(x + 4, top - 7, 7, 7, "p"); c.poly([x + 3, top - 7, x + 8, top - 11, x + 12, top - 7], "p") }
    c.rect(x + w - 2, top, 2, h + 80, "k")                              // shadow side separates neighbours
    const rows = Math.max(1, Math.floor((176 - (top + 4)) / 6))          // rows above the foreground roofs
    const band = Math.max(0, Math.min(23, Math.floor((x + w / 2) / 400 * 24)))
    const on = spec ? Math.max(1, Math.round(spec[band] * rows)) : 0
    const lit = 0.15 + wr() * 0.3
    if (unlit) rects.push({ band, x: x + 3, y: top + 4, cols: Math.floor((w - 7 - 3) / 5) + 1, rows, rowsToBottom: Math.ceil((224 - (top + 4)) / 6), cell: [3, 4], pitch: [5, 6] })
    for (let j = 0, wy = top + 4; wy < 224; wy += 6, j++) {
      const up = rows - 1 - j                                            // 0 = lowest visible row
      for (let wx = x + 3; wx < x + w - 4; wx += 5) {
        let k
        if (spec) k = up >= on ? "n" : up === on - 1 ? "i" : up >= rows * 0.6 ? "M" : "Q"   // the scene's own neon: magenta, pink higher up, palest at the peak
        else k = !unlit && wr() < lit ? "yacQ"[Math.floor(wr() * 4)] : "n"
        c.rect(wx, wy, 3, 4, k)
      }
    }
    x += w + (r() < 0.15 ? 2 : 0)
  }
  if (unlit) console.log("WINRECTS " + JSON.stringify(rects))
}
const SKYGLOW = glow("i", { r: 10, ramp: 1, where: [318, 44, 17] })
scene("bg_sky", { w: 400, h: 224, bg: "k" }, drawSky, SKYGLOW)
scene("bg_far", { w: 400, h: 224 }, drawFar)
scene("bg_mid", { w: 400, h: 224 }, drawMid)
scene("bg_mid_unlit", { w: 400, h: 224 }, (c) => drawMid(c, true))
scene("rooftop_bg", { w: 400, h: 224 }, stamp("bg_sky", 0, 0), stamp("bg_far", 0, 0), stamp("bg_mid", 0, 0))

// animated background: 4 bars of the rooftop track at 20 frames per second
anim("rooftop_bg_groove", { w: 400, h: 224, frames: SPEC.length, fps: 20 },
  drawSky, SKYGLOW, layer("far", drawFar), layer("mid", drawMid))

// ---------- mockup of a play screen ----------
scene("rooftop_mock", { w: 400, h: 224 },
  stamp("rooftop_bg", 0, 0),
  layer("crane", (c) => {   // the beams hang from a tower crane jib, not from the sky
    for (const x of [130, 189, 210, 253]) c.vline(x, 14, (x < 200 ? 112 : 128) - 14, "N")
    c.rect(96, 3, 304, 2, "a"); c.hline(96, 3, 304, "y"); c.hline(96, 12, 304, "a"); c.hline(96, 13, 304, "u")
    for (let x = 96; x < 400; x += 12) { c.line(x, 5, x + 6, 11, "a"); c.line(x + 6, 11, x + 12, 5, "a") }
    c.rect(94, 2, 3, 13, "a"); c.px(95, 1, "r")
    for (const [x0, x1] of [[130, 189], [210, 253]]) { c.rect(x0 - 2, 13, x1 - x0 + 5, 3, "g"); c.hline(x0 - 2, 13, x1 - x0 + 5, "h") }   // trolleys
  }),
  layer("props_back", stamp("neon_sign", 40, 119), stamp("water_tower", 330, 121), stamp("antenna", 176, 115)),
  tilemap(`
.........................
.........................
.........................
.........................
.........................
.........................
.........................
........abbc.............
.............abc.........
.........................
TTTTTTTTTTTTR............
w1ww2ww3ww4wr...LTTTTTTTT
w6ww7ww8ww9wr...lw5ww1ww2
eeeeeeeeeeeeE...lw0ww6ww7`, {
    size: 16,
    map: { e: "belt_m", E: "belt_r", T: "roof_m", L: "roof_l", R: "roof_r", w: "wall_m", v: "wall_b", l: "wall_l", r: "wall_r", 1: "win_curtain_top", 6: "win_curtain_bot", 2: "win_dark_top", 7: "win_dark_bot", 3: "win_blinds_top", 8: "win_blinds_bot", 4: "win_tv_top", 9: "win_tv_bot", 5: "win_ac_top", 0: "win_ac_bot", a: "plat_l", b: "plat_m", c: "plat_r" },
  }),
  layer("props_front", stamp("ac_unit", 10, 144), stamp("vent", 284, 155)))

scene("rooftop_mock_groove", { w: 400, h: 224 },
  stamp("rooftop_bg_groove", 0, 0),
  layer("crane", (c) => {   // the beams hang from a tower crane jib, not from the sky
    for (const x of [130, 189, 210, 253]) c.vline(x, 14, (x < 200 ? 112 : 128) - 14, "N")
    c.rect(96, 3, 304, 2, "a"); c.hline(96, 3, 304, "y"); c.hline(96, 12, 304, "a"); c.hline(96, 13, 304, "u")
    for (let x = 96; x < 400; x += 12) { c.line(x, 5, x + 6, 11, "a"); c.line(x + 6, 11, x + 12, 5, "a") }
    c.rect(94, 2, 3, 13, "a"); c.px(95, 1, "r")
    for (const [x0, x1] of [[130, 189], [210, 253]]) { c.rect(x0 - 2, 13, x1 - x0 + 5, 3, "g"); c.hline(x0 - 2, 13, x1 - x0 + 5, "h") }   // trolleys
  }),
  layer("props_back", stamp("neon_sign", 40, 119), stamp("water_tower", 330, 121), stamp("antenna", 176, 115)),
  tilemap(`
.........................
.........................
.........................
.........................
.........................
.........................
.........................
........abbc.............
.............abc.........
.........................
TTTTTTTTTTTTR............
w1ww2ww3ww4wr...LTTTTTTTT
w6ww7ww8ww9wr...lw5ww1ww2
eeeeeeeeeeeeE...lw0ww6ww7`, {
    size: 16,
    map: { e: "belt_m", E: "belt_r", T: "roof_m", L: "roof_l", R: "roof_r", w: "wall_m", v: "wall_b", l: "wall_l", r: "wall_r", 1: "win_curtain_top", 6: "win_curtain_bot", 2: "win_dark_top", 7: "win_dark_bot", 3: "win_blinds_top", 8: "win_blinds_bot", 4: "win_tv_top", 9: "win_tv_bot", 5: "win_ac_top", 0: "win_ac_bot", a: "plat_l", b: "plat_m", c: "plat_r" },
  }),
  layer("props_front", stamp("ac_unit", 10, 144), stamp("vent", 284, 155)))

// ---------- gameplay sprites named after their LDtk entities ----------
sprite("RoofVent", { w: 16, h: 12 }, (c) => {        // fan housing; the game adds the updraft
  c.rect(0, 2, 16, 10, "G"); c.hline(0, 2, 16, "H"); c.hline(0, 3, 16, "h"); c.box(0, 2, 16, 10, "k"); c.rect(2, 5, 12, 5, "j")
  for (let x = 3; x < 13; x += 3) c.vline(x, 5, 5, "g"); c.rect(1, 0, 14, 2, "a"); c.hline(1, 0, 14, "Y"); for (let x = 2; x < 14; x += 4) c.rect(x, 0, 2, 2, "j")
})
sprite("Billboard", { w: 7, h: 58 }, (c) => {        // a billboard seen edge-on; a fist knocks it down into a bridge
  c.rect(2, 0, 3, 58, "g"); c.vline(2, 0, 58, "h"); c.vline(4, 0, 58, "j"); c.rect(0, 2, 7, 30, "N"); c.vline(0, 2, 30, "Q"); c.vline(6, 2, 30, "k"); c.vline(1, 3, 28, "b")
  for (let y = 5; y < 30; y += 6) c.px(0, y, "i"); c.rect(0, 0, 7, 2, "h"); c.rect(1, 54, 5, 4, "G"); c.hline(1, 54, 5, "H"); c.line(2, 40, 5, 46, "g"); c.line(5, 40, 2, 46, "g")
})
sprite("billboard_plank_m", { w: 16, h: 16 }, (c) => { c.rect(0, 0, 16, 5, "N"); c.hline(0, 0, 16, "Q"); c.hline(0, 1, 16, "b"); c.hline(0, 4, 16, "k"); c.px(5, 0, "i"); c.px(13, 0, "i"); c.rect(7, 5, 2, 2, "g") })
sprite("ZipPost", { w: 8, h: 22 }, (c) => { c.rect(3, 4, 3, 18, "G"); c.vline(3, 4, 18, "H"); c.vline(5, 4, 18, "g"); c.rect(1, 20, 7, 2, "g"); c.circ(4, 3, 3, "a"); c.ring(4, 3, 3, "k"); c.px(4, 3, "j"); c.px(3, 1, "Y") })
sprite("Sign", { w: 22, h: 15 }, (c) => {            // small hanging sign used as a one-way platform; top edge is the standing line
  c.rect(0, 0, 22, 4, "H"); c.hline(0, 0, 22, "S"); c.hline(0, 3, 22, "G"); c.hline(0, 4, 22, "k"); c.rect(1, 5, 20, 9, "n"); c.box(1, 5, 20, 9, "Q"); c.rect(4, 8, 3, 3, "i"); c.rect(9, 8, 3, 3, "i"); c.rect(14, 8, 4, 3, "M"); c.hline(1, 14, 20, "k")
})
