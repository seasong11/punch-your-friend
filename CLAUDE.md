# Punch Your Friend — project notes for Claude

## What this is
A pixel-art party game in a single file, `index.html`, hosted on GitHub Pages
(intended URL: https://seasong11.github.io/punch-your-friend/).

- The player who opens the page without a `?room=` code creates a room and plays **我** (the dodger).
- Anyone who opens the invite link (`?room=<code>`) joins as a **兄弟** and throws punches from above.
- Originally built as a Claude artifact; this standalone build swaps the artifact's live room for a
  browser-to-browser layer.

## How index.html is laid out
1. `<head>`: PeerJS 1.5.4 from unpkg, then the **network layer** script.
   - It defines `window.claude.use('room' | 'user')`, a shim with the same API the game was written against
     (`room.presence/peers/onPeers/onConnection`, `user.isOwner/id/profiles`).
   - Star topology: the host's browser (peer id `pyf-<room>`) holds the authoritative presence map and
     rebroadcasts it about 30 times a second. Guests send presence patches to the host.
   - Invite bar UI (name box, copy-link button, status line) is injected into `.wrap`.
   - Opened from `file://`, it warns that the invite link only points to the local disk.
2. `<body>`: the game itself (canvas, HUD, controls, how-to card, wardrobe), then a small CSS block for the
   invite bar and the reset styles (`[hidden]{display:none!important}` etc.).

## Game systems (all inside the main game script)
- Look: simple flat pixel art (Stardew-like techniques, no assets from any game). The world is drawn straight onto
  a 400x160 canvas, i.e. a 4x art-pixel grid (`PX = 4`), then blown up with hard pixels. 我 is about 16x32 art
  pixels; the face is drawn in whole art pixels. Every line is at least one art pixel wide (`lineWidth` floor).
- Palette: `palettize()` snaps every art pixel to Endesga 64 (`PAL`) through a 15-bit lookup table each frame,
  which also removes soft anti-aliasing. `nearest()` matches in OKLab with hue and colourfulness weighted 3x, so muted
  greens and browns keep their hue instead of turning into the palette's neutral greys. Canvas text colours go through `palCol()`. `glow()` is a no-op (soft
  glows only band into rings on a palette).
- Hoodie Guy (`COS` id `hoodie`) is a hand-made pixel sprite from PixelLab (`HOODIE`, east and west, 20x47 art pixels,
  embedded as base64 PNGs). It is drawn 1 sprite pixel = 1 art pixel by `hoodieSprite()` and skips `litSprite()` because
  it is already shaded with its own near-black navy outline. It has one pose per side; run tilt, squash and the block
  arms are added in code until animation frames exist. The other costumes are still drawn in code.
- Sprites: `litSprite()` draws 我 (and fists) on a small art-pixel canvas (`ctx` is temporarily swapped to it),
  then adds flat shading from the top-left (`SHADE`: warm highlight on up-left edges, purple shadow on
  down-right edges) and an outline that is a darker shade of the neighbouring colour. Lit fists are cached in
  `HAND_CACHE` (motion streaks drawn fresh by `handMotion`).
- Text: recorded `fillText` calls are replayed crisp on top. Chinese and UI text use "PYF Pixel", a subset of the
  Cubic 11 pixel font (OFL, embedded as base64 in a `<style>` in `<head>`). If you add new Chinese characters,
  re-subset the font (fontTools, from Cubic_11.woff2 in TakWolf/fusion-pixel-font assets/fonts/cubic-11) with every
  non-ASCII character in index.html, or the new ones fall back to a system font.
- UI: wood panels with stepped borders and parchment buttons, all in palette colours (CSS variables in `:root`
  and the "cozy pixel UI" block at the end of the last `<style>`).
- Music: recorded loops in `music/<id>.ogg` (one per stage in `STAGE_TRACKS`, plus `menu` and `game-over`), each an
  exact whole number of bars so `AudioBufferSourceNode.loop` plays them gaplessly. The game loop calls
  `sfx.scene('stage' | 'over' | 'menu' | null)` every frame; `setLevel` picks the stage track by level, or
  `sfx.setSection(id)` picks it by relay section (`SECTION_TRACKS`: house, dojo, bamboo, rooftop-climb, rooftop-jumps,
  lake-dive, lake, volcano, snow, elevator, space). Only the playing track and the likely next one are fetched
  (OGG Vorbis q2, about 0.75 MB each), starting after the first tap. If a file can't load (e.g. opened from `file://`), stages fall back to the synthesized
  `THEMES` and the lobby/game over stay quiet. The tracks were made by an offline synth script (kept outside the repo).
- Mix: music (`musicOut`, ducked) and effects (`sfxOut`) meet on a master bus with a limiter. Effects are in three
  tiers (`TIER`, `TIER_DB`); big moments dip the music ~5 dB. Pitched effects (marked `P`) snap to the playing track's
  scale (`KEYS`). `sfx.at(x)` pans the next effect to its world position. `MUSIC_LEVEL` sets music against effects.
  Each effect is capped at two starts per 80 ms.
- Levels: `levelOf(score)` — LV2 at 25 points, LV3 at 75, then triangular growth. Speed curve caps around 4.2.
  A fairness check (`fairSpot`) stops the practice bot from throwing unescapable punches.
- Six stages by level (living room, dojo, rooftop, bamboo, volcano with fire dragon, space with ships),
  stage-themed punch skins (`PUNCH`), layered music intensity (`setLevel`).
- 我 (dodger): move, block/perfect block (↓/S/Space), dash (Shift), Golden Bell (E, Rage meter),
  perfect-block stun, on-fire streak buff (5/10/20 combo → +10/20/30% speed), taunts, six unlockable
  costumes (`COS`) each with its own move set (`MOVES`).
- On-fire speed look: only `feetFx` (a pixel dust puff per step while on fire). Daniel turned down afterimages,
  flame aura, sparks, lightning, manga stamp and combo meter as too busy: keep the speed effect minimal.
- Fire caption: `ticker(tier, sub)` reuses `#caption` under the arena as a wood strip (`.caption.tick`) with a stepped
  pixel flame (`.tkf`) and typed text; `banner()` resets it. A small `streakTag` "xN" sits over 我's head.
- 兄弟 (puncher): tap to chop, formations (1/2/3), feint (F), homing (H), 黄泉指 Underworld Finger (Y),
  如来神掌 Buddha Palm (charged super), Punch Rain ultimate (R).
- 黄泉指: the portal chases 我 during the warning (`YQ_TRACK` px/s), the finger snakes down at 2x speed, and
  the landing sends a ghost-fire wave `YQ_REACH` px each way (`c.wave`); dash, bell or block stop the wave.
- Switch sides: between rounds the overlay shows "⇄ Switch sides". 我 hands the role to a 兄弟 (the one who
  asked, else the top hitter) by setting presence `hand: '<peer>:<nonce>'`; a 兄弟 asks with presence `sw`.
- Stop: `#pauseBtn` (or P / Esc) stops a round in play. 我's page holds the pause (`S.paused`, update skipped) and
  sends presence `pz: 1, pzm: 1`; a 兄弟 asks with presence `pq: '<nonce>:<p|r|e>'` (pause, resume, end round).
  The pause menu (Resume / End round) uses `ovMode = 'paused'` on the overlay buttons.
- Controls sit in one compact `.dock` under the arena; a round start scrolls the HUD, arena and dock into view.

## Journey prototype: the house (branch `house-prototype`)
- House look (from Daniel's indoor references): a cutaway wooden house. `drawRoomShell` draws the wall by `style`
  (`plank`, `plaster` default, `block`) with a darker lower band, rail and baseboard; `drawRoomFrame` adds the ceiling
  beam, joists, corner posts and a cobweb. Wall decor kinds: `win` (hazy day and far city, curtains, light patch on the
  floor), `lamp` (warm `glowPx` dither glow, no blur), `pic`, `clock`, `books`, `pots`, `shelf`, `tiles`, `rug`, `tree`.
  Furniture is drawn through `litSprite`, so it gets the same lit edges and dark outline as 我. The garden is a hazy
  day with the house's half-timbered wall on the left and the neon tower ahead on the right.
- `JOURNEY = true` turns the single arena into a section made of rooms (`ROOMS`): living room, kitchen, stairs up,
  hallway, bedroom, stairs down, garage. Each room is one arena wide; walking out of the right-hand door loads the
  next (`nextRoom`), and the garage door ends the section (`houseDone`, hearts refill).
- 我 has height now: `P.y`/`P.vy`/`P.air`, `tryJump` (↑ / W, the ▲ button, or a swipe up), `movePlayer`. `surfAt(x)`
  is the height of the ramp or tallest prop at x. Props are solid boxes; ones with `hp` break under punches
  (`hitProps`), and `elec` ones spark for a second (still solid) before they clear. A fist that lands on something
  taller than 我 cannot hit 我 (cover).
- 我's page owns the room and sends `rm` (room), `y`, `pp` (prop states, `propCode`) and `won` in presence; the
  兄弟 side mirrors them in `syncRoom`.
- Level is fixed at 1 while `JOURNEY` is on (`levelOf`), so punches stay slow and there are no level-up hearts.
- Relay: at zero hearts `gameOver` sets `S.handT`; `relayHand` then hands the role to the top hitter who has not
  been 我 this round (`S.was`, passed along in presence `was`). The new 我 starts the house from room 1.
- A garden (`outdoor`, `gate`) follows the garage and ends the house section.
- Rooftop climb (the last entry of `ROOMS`, built by `buildClimb(16)` from a fixed seed into `climb: { top, stairs, ladders, hooks }` plus pillar props): floors are one-way platforms
  `FH` apart (`climbGround`, `moveClimb`). ↑ at a ladder's foot climbs it in one go (← → lets go), a jump into a
  hook pulls 我 up a floor, ↓ drops through a floor (`tryDrop`). The view scrolls with 我 (`CAMV`, `camFollow`,
  `camY`); everything in the world is drawn under `translate(0, camY())`.
- Side punches (`addSide`, `updateSide`, `sideWarn`, `sideFist`) live in `S.chops` with `side` (+1 from the left,
  -1 from the right) and `row`. They run along one floor until a pillar (prop `k: 'pillar'`, `lv`, 3 hp) or 我
  stops them. Never two neighbouring rows at once. A 兄弟 tap sends its height (`chop.h`); the tapped half of the
  arena picks the side. Entering the climb refills hearts and sets `S.startRm`, so a lost turn (presence `sec`)
  restarts the climb, not the house.
- Glass tower: inside floors have glass curtain walls on both sides (`R.gl` bitmasks, `glassWhole`, `glassFx`). A side
  punch through whole glass cracks it during a longer wind-up (1.05s instead of 0.75s) and shatters it for good.
  Rows `climb.out` (6 to 10) are outside on the facade (`outsideRow`): no glass, AC units (`ac: 1` pillars, 2 hp) as
  cover, and the only way up is timed sliding windows (ladders with `timed`, `off`; `ladderOpen`: open 3s, shut 2s,
  lamp green/red). Presence carries `gl` and `gt` (`R.t`) so the 兄弟 side shows the same glass and windows.
- Climb look ("blue haze", Daniel's pick): one blue ramp (#181425 to #c0cbdc). `cityLayers()` pre-draws four skyline
  silhouette layers at art-pixel size; `drawClimb` blits them with parallax (farther = paler and slower), over a pale
  screen-fixed sky with one moon. The tower is dark navy with lit edges; things 我 can use are lighter than the city
  behind them (pillars, stair treads, steel ladders with orange handles). Keep backdrops quiet and low-detail.
  Detail level follows Daniel's references: irregular 1px window grids, wings, crowns, panel lines, a dark near frame at
  the screen edges, walkways, dither haze (`ditherBand`), blinking windows (`L.blink`), and pixel neon (cyan #2ce8f5 /
  #0099db bands, magenta #f6757a / #68386c edges; near layers only). Stairs have cyan tread lights and a magenta rail;
  each pillar has a three-segment neon strip that loses a segment per hit.
- More ways up (`climb.pipes/ropes/plats/ledges/els`, plus `wall: 1` pillar props), placed by `PLAN` in `buildClimb`:
  drain pipes outside (`P.grip`, auto-climb, ↓ sets `P.slide`), ropes (caught in the air, `grip.rope`, ← → leaps off via
  `P.kt`/`P.kd`), half-height ledges and the window-cleaning lift (`platY`, both handled in `climbGround`), wall kicks
  (↑ in the air near a shaft wall, max 2, `P.kicks`), and an elevator (`R.el[]`, `tickElevators`, `P.el`; a side fist
  stops at the car and stalls it; car heights go out in presence `ey`). Orange always marks "climb here".
- Dojo test section (rooms with `sec: 'dojo'`, between the garden and the climb; `secOf(i)` names a room's section and a
  section change refills hearts and sets `S.startRm`). Fists fall 1.25x faster there (`dropV`). Daniel had the `shoji` paper doors removed from the rooms as unclear (2026-11-13; the code is still there, do not bring them back without a clearer design), and had the wall scrolls redrawn as mounted scrolls with ink paintings (`drawDecor('scroll', x, v)`: circle, mountain, bamboo). Props: `shoji` paper doors
  (block the way; ↑ slides one open = `p.open`, a dash tears it, a fist tears it and is absorbed), `dummy` (a fist spins
  it, `spinT`, and shoves 我 a step, no heart lost), `beam` planks (`plat: 1`, one-way via `surfAt(x, half, y)`; ↓ drops
  through, no block on it; a fist breaks only the plank under it). `propCode` 7 = open, 6 = spinning. The crooked-scroll
  secret is not built. Each stage is meant to get one unique stage punch (designed in the punch thread): leave room.
- Rough sections after the dojo (first pass, all rules are Claude's placeholders for Daniel to revise). Room order:
  house, garden, dojo x3, bamboo x2, ROOFTOP CLIMB, rooftop run x5, lake dive, lake, volcano x2, snow x2, tower lift,
  space elevator, space arena x2. A room's `sec` is also its music id; `secOf` gives `climb` / `space` for the two towers; `SEC_INFO`
  holds each section's banner. Rooms with `scene` are drawn by `drawScene(rm)` (flat backdrops) instead of the house shell.
  - Terrain: `hill` (polyline of `[x, height]`, read by `rampAt`), `void: 1` (no floor, only props such as `roof`),
    `ghost: 1` props (not solid: `stalk`, `shroom`), `raw: 1` props (drawn without `litSprite`), `drift` props (move
    with `R.t`, `driftProps`), `hh` (visible height of a rock standing on a slope), `enterY` (start height).
  - Bamboo: ↑ at a `stalk` or ↓ on a `shroom` is a high jump (vy 1280); `thick` thickets block the path; `leaf` canopy
    planks are one-way cover that take two fists.
  - Roof jumps: falling below the screen costs a heart and returns 我 to the last safe spot (`P.sx`, `P.sy`, `loseHeart`).
  - Lake dive / lake: `water: { x0, top }`, `inWater()`. Slow sink, ↑ is a swim stroke, 0.6x sideways speed; a fist slows
    down with depth and lands on a swimmer under it; `turtle` plats are cover.
  - Volcano: `lava` zones burn (one heart, and always a bounce); `slab` stepping stones have 2 hp, `rock` ones are safe.
  - Snow: `slide: 1`, on a slope anything but pushing uphill slides 我 back (`slopeAt`); flat ledges are rests.
    Punches at a right angle to the slope are not built.
  - Space (Daniel, 2026-11-13: "elevators and primarily the space stage", using the original space stage): section
    `space` = TOWER LIFT and SPACE ELEVATOR (`scene: 'lift'`, `ride` seconds, `rideLeft()`, `R.t0`, `music: 'elevator'`;
    the exit only opens when the ride is over) then SPACE ARENA x2 (`scene: 'space'` draws the old `stSpace()`,
    `grav: 0.5`, `pod` cover, `panel` plats). The last arena's door ends the journey (`houseDone`, "JOURNEY DONE!").
    The earlier space-station climb room is gone (`buildClimb`'s `space` option is unused).
- Focus (Daniel, 2026-11-13): the design centres on high-speed rooftop combat (高速屋顶战斗). The rooftop run is five
  generated screens (`roofRun(n)`, `fast: 1.35` scales `moveMax` and acceleration, fists 1.2x in `dropV`). What "combat"
  means for 我 is still an open question in the stage design doc.
- Follow camera (Daniel: 我 fixed on screen, one spatial map): `VIEW.x` (`viewFollow`, `viewX()`) keeps 我 centred and the
  world is drawn under `translate(-viewX(), camY())`. `drawWorld` draws the previous / next room beside the current one
  (`drawNb`, props of left rooms kept in `NBP`), offset by `exitX/entryX` and by `pairD(i)` (height difference at the seam;
  two water rooms align by surface). On a room change `roomShift` keeps the picture still and `VIEW.oy` eases the height
  offset away; 我 keeps their height across the seam. `camY()` includes `VIEW.oy` and, while a neighbour is drawn,
  `VIEW.dy`. Room title plates are screen-fixed and skipped for neighbours (`VIEW.nb`). Pointer x adds `viewX()`; the
  portrait `CAM` follows 我's screen position. Side punches in the climb come from the side of 我 that was tapped.
  我 cannot walk back into the room on the left. Scene rooms have no door boxes; only the last room has an exit door.
- Stage design document for Daniel: https://claude.ai/artifact/YUAeoRmNTQtoG3Hc4erU4G (labels every rule Daniel / Agreed /
  Proposal; keep it in step with the prototype).
- Test hook: `?dbg=1` exposes `window.__pyf = { S, P, R, ROOMS, loadRoom }`.
- The hoodie no longer has 我 printed on the chest.

## Publishing (GitHub Pages)
The site is served by GitHub Pages from **Deploy from a branch → main → / (root)** (Settings → Pages).
As of 2026-11-12 the repo had zero Actions runs, which means Pages had never built: the source setting
was not saved, so the URL returned 404. Once the source is saved, every push to `main` shows a
"pages build and deployment" run in the Actions tab and the site updates about a minute later.

## Multiplayer notes
- Guests keep retrying the join every few seconds (and rejoin by themselves if the host reloads), so
  an invite link opened before the host is ready still connects.
- While the host's tab is hidden the game loop stops; the host's presence carries `pz: 1` and guests
  see a "paused" overlay.
- **Relay fallback:** when a guest has no direct link after 8s (or PeerJS can't load or reach its server),
  it joins through a public MQTT broker over WSS (`broker.emqx.io:8084`, then `broker.hivemq.com:8884`), using
  topics `pyf2/<room>/up` (guest → host: `hi`/`hb`/`p`/`bye` with the guest id) and `pyf2/<room>/down`
  (host → guests: the state, ~15/s, at least every 1.5s). The host always listens on both brokers.
  mqtt.js 5.10.4 is lazy-loaded from unpkg. Guests that miss the host's state for 8s show "rejoining".
- Local relay test: run an aedes broker over WebSocket and add `&relay=ws://localhost:8883` (only honored
  with `?mock=1`); the mock can block direct links with `&nodirect=1`.
- Test without the PeerJS cloud: open with `?mock=1` and inject a `window.MockPeer` (BroadcastChannel)
  before the page scripts run.

## Phones
- Landscape phones (`orientation: landscape` and `max-height: 540px`) switch `.wrap` to a two-column grid:
  the arena on the left at the largest size that fits, one button column on the right (挡/打!, dash/bell or
  feint/formation), 兄弟 tools under the arena, the rest of the page below. ◀ ▶ are hidden: 我 moves by
  dragging on the arena, 兄弟 aim by tapping it. `.pads`, `#meSkills` and `#broMoves` are `display: contents`.
  `body.is-bro` reserves room for the tool row (`--chrome`).
- `#fsBtn` (touch + Fullscreen API, i.e. Android) goes full screen and locks landscape. iPhones can't do
  element full screen; the page has apple-mobile-web-app-capable so "Add to Home Screen" runs full screen.
- Portrait phones get a compact header and invite bar and a tip to turn the phone sideways. The arena there
  shows an 860-wide slice of the 1600-wide world (`CAM`, `layoutCam`, `followCam`) that follows 我 (or the
  兄弟's aim), so it is about twice as tall; `offscreenArrows()` marks chops outside the view. Taps map
  through `CAM.x`/`CAM.w`.
- On touch devices (`pointer: coarse`) the world canvas is drawn directly at half size (`LOWRES`),
  skipping the shrink pass; recorded text is replayed with a 2x base transform (`TXT_BASE`).
- The invite button uses the system share sheet on phones; hits vibrate (Android); a screen wake lock
  is taken on the first tap.

## Working on it
- Edit `index.html` directly; there is no build step.
- To test multiplayer locally, serve the folder (`python3 -m http.server`) and open two browser windows:
  one at `/` (host) and one at the invite link it shows.
- Keep the game working inside a single file so it can be dropped onto any static host. The only extra files are
  the optional music loops in `music/`; without them the game still runs with its synthesized fallback music.
