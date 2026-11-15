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
  a 400x224 canvas (Daniel's choice, 2026-11-14; the world is 1600x896), i.e. a 4x art-pixel grid (`PX = 4`), with the floor line at art y 208 (`FLOOR = H - 64`, the top of the bottom 16 px tile row), then blown up with hard pixels. 我 is about 16x32 art
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
- Rooftop climb (the last entry of `ROOMS`, built by `buildClimb(28)` from a fixed seed into `climb: { top, stairs, ladders, hooks }` plus pillar props): floors are one-way platforms
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
- Tower interior (Daniel, 2026-11-14: stairs and building looked invisible, remove the glazing art, focus on interior design with
  spatial depth; references: industrial sci-fi corridors with lift doors and hazard stripes). Inside floors now have a solid back
  wall in 190 px bays (windows onto the city, lift doors, a corridor recess, lockers, pipes, plates), a ceiling soffit, lamps, a
  darker lower wall, pale stairs / pillars / ledges / slabs, and concrete side walls with open hazard-striped bays where side
  fists come in. `GLASS = false` turns the glass mechanic off (`glassWhole`); the glass notes below describe the dormant code.
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
  house x15, garden, dojo x18, bamboo x18, ROOFTOP CLIMB, rooftop run x36, lake dive, lake x9, volcano x24, snow x20, tower lift,
  space elevator, space x28. A room's `sec` is also its music id; `secOf` gives `climb` / `space` for the two towers; `SEC_INFO`
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
    the exit only opens when the ride is over) then the space screens (`scene: 'space'` draws the old `stSpace()`,
    `grav: 0.5`; see "Space finale" below). The last screen's door ends the journey (`houseDone`, "JOURNEY DONE!").
    The earlier space-station climb room is gone (`buildClimb`'s `space` option is unused).
- Focus (Daniel, 2026-11-13): the design centres on high-speed rooftop combat (高速屋顶战斗). Daniel then found plain roof
  jumping redundant and asked for more features, for every stage to last at least a few minutes, and for more design in
  the space finale. What "combat" means for 我 is still an open question in the stage design doc.
- Generated screens (all layouts are Claude's proposals): the hand-made rooms sit in `BASE` (looked up by `B_(name)`); the rest
  come from seeded generators (`rngOf`, `pk`, `seq(n, fn)`): `genHouse`, `genDojo` (15), `genBamboo` (18), `roofRun` (36),
  `genLake` (9), `genVolcano` (24), `genSnow` (20), `genSpace(n, kind)`. `ROOMS` has 173 screens. `cp: 1` marks every
  fourth screen of a section as a checkpoint (`nextRoom` sets `S.startRm`, banner CHECKPOINT). A scripted 我 with no punches
  needs roughly 1.5 to 3.5 minutes per stage; change the `seq` counts to retune length.
- Map seed (Daniel, 2026-11-14: randomize the terrain with a seed): `SEED` is picked by 我's page when a journey starts from
  the first screen (`newSeed`, or `?seed=N`), sent in presence as `sd` with the map mode `sm`, and `buildRooms(seed, mode)`
  rebuilds `ROOMS` the same way on every page. A relay turn keeps the seed (`S.keepSeed`). Seed 0 is the fixed test layout.
  `rngOf(k)` mixes the seed in; `modOf` picks a generator's layout; rooftop roofs get seeded widths and gaps (`Jw`, `Jg`,
  `Jp`: gaps only shrink, the gap after a vent is fixed, landing roofs stay 200+ wide and roofs after a vent only widen; each of
  these rules comes from a seed that dead-ended the test bot).
- LDtk chunks (Daniel authors building blocks in LDtk; the "Create LDtk files for prototype" thread owns
  `levels/punch-your-friend.ldtk` and `levels/README.md`, branch `ldtk-levels`, PR #23): the game fetches that file when the
  page opens (`readLdtk`, `chunkOf`). With it, `MODE` is 1 and `chunkList` swaps each section's code-built screens for chunks:
  the first screen takes a `Warmup` chunk, then `BEAT_LOOP`; picks are weighted, never the same chunk twice in a row;
  `chunkRoom` keeps the replaced screen's look (walls, scene, decor) and takes the layout from the chunk (props, `hill` from
  Terrain and `Slope` entities, water, lava, flags), then rolls `VariantZone` groups and `HazardSpawn` chances. Prop flags per
  kind come from the code-built rooms (`KF`, `learnKinds`); entity names map through `ENT_K`. Not read yet: Decor entities,
  Terrain platform cells, the Climb chunk and the lifts (still built by the game). Without the file, or with `?gen=1`, the
  code generators are used (`MODE` 0). The file is about 0.8 MB; a build step that slims it is a later option.
- Placement (Daniel, 2026-11-14): Daniel no longer places things by hand in LDtk. Claude decides where things go, from Daniel's
  references and the art thread's sets (thread now named "Create art for all levels"; approved look = layered misty silhouettes like
  the bamboo art in `pxl-art/bamboo/pixellab/`). The LDtk file stays as the layout format and is frozen; the code-drawn tower
  interior is disliked and waits for a drawn set. Asked the art thread for tiling transparent layers without baked ground, ground
  and platform tiles, and sprites for the placed props per level.
- Level sets wired (Daniel, 2026-11-14: "build the prototypes ... make it impressive ... the art style should be consistent", no
  per-set approval needed for this pass; he reviews at the end). Sets come from `pxl-art/levels/<section>/` (art thread) and live in
  `art/<set>/`: bamboo, dojo, house, lake, volcano, snow, elevator, space, climb (rooftop stays on its approved set). `SETS` lists each
  set's layers as `[name, factor]` (0 = fixed to the screen, 1 = part of the room, between = parallax) and its sprites; `artOf(i)`
  names a room's set (garden uses bamboo, lifts use elevator). `artBack(set, dusk, skip)` draws the layers; `artScene(rm, set)` draws a
  whole room (backdrop, `groundArt` = floor and hills from `top_a/top_b/fill` tile slices cached per room, lava tiles, water surface,
  snow, lift progress) and is called from `drawScene` and `drawRoom`; `artProp(p)` draws props from sprites or tiles (`tileRow` for
  one-way platforms, `tileBlock` for solid blocks) and returns false for kinds it does not cover, which then use the old `drawProp`.
  `FIT` + `fitProps` (run in `buildRooms`, before the rooms are used) resize props to their sprite so what is drawn is what blocks.
  The lake shows the rooftop night sky above the surface; the dive room is a brick roof over the lake set. Daniel (2026-11-15): water never rises up a
  building; the dive is a jump from the last roof (560 high) into a pond whose surface is at ground level (200 above its bed), with the
  building standing on a bank. `fitProps` sets that hill and water on the dive room in both map modes. `drawClimb` uses the climb
  sprites (`CA`): wall bays and openings, floor slabs, pillars, stair steps. The house draws only `bg_sky` + `bg_far` (its painted furniture sits in `bg_mid`, which the game skips, because anything that
  looks like an object must be one).
  A set's `V` lists layers with a second look (`<name>_b.png`: house `bg_far_b` kitchen wall, dojo `bg_mid_b`), used on odd screens.
  Old code backdrops remain only as the fallback when a file is missing or with `?art=0`.
- Art sets (Daniel, 2026-11-14: revise the prototype from his references in the private repo `seasong11/punch-your-friend-art-refs`;
  the "Set up Claude art generator" thread draws each section with claude-pxl into project files `pxl-art/<section>/`, this
  thread copies approved sets to `art/<section>/` and wires them in). Layout agreed with that thread: `tiles.png` +
  `tiles.json` (frame names), `bg_sky/bg_far/bg_mid(/bg_near).png` (400x224, tileable, transparent), `sprites/<LDtk identifier>.png`
  sized to the LDtk entity boxes, plus a window-rect JSON for music-reactive layers. `loadArt(sec, sprites)` loads a set;
  `artBack(sec)` draws the layers screen-fixed with slow parallax; `roofArt` builds a brick building from tiles (cached in
  `ROOF_CACHE`); every use falls back to the old code drawing while a file is missing (`?art=0` forces that). Only the rooftop
  set is approved and wired: background layers, brick buildings, and sprites `RoofVent`, `Sign`, `ZipPost`, `Billboard`,
  `billboard_plank_m` (`spr()`). Do not wire the house, dojo and bamboo drafts until Daniel approves them. The skyline windows
  are a music spectrum: an AnalyserNode on the music bus (`sfx.spectrum(n)`), window grids from `bg_mid_windows.json`
  (`ART.rooftop.win`), drawn in `artBack` (Daniel's rules: buildings never move, one aligned window grid per building, bass left
  to treble right). The layers must tile at 400 art px. `artBack(sec, [h0, h1])` fades the set in by dither between two heights: `drawClimb`
  uses it so night falls over the climb's last floors and the roof run starts under the same sky (Daniel, 2026-11-14: make the
  transition smoother; the dusk fade itself is Claude's proposal). `VIEW.gi` is the current room, so neighbours share one backdrop.
- Rooftop run features (`fast: 1.2`): momentum (`P.mom`, builds over 1.2 s of running, up to +45% speed, lost on a hit, stop or
  turn), `vent` (launches 我 when stepped on, up to the vent roof's edge), `cable` zip lines (`P.zip`, grabbed in the air at hand
  height, ↑ hops off, ↓ lets go), `board` billboards (a fist or a dash drops one as a bridge, `fallBoard`, `propCode` 5), `sign`
  platforms. Four screen modules rotate by `(n - 1) % 4`.
- Space finale: TOWER LIFT, SPACE ELEVATOR, then LANDING DECK x6 (`pod` cover, `panel` plats), ASTEROID FIELD x6 (`void`,
  `aster` platforms, half gravity), SPACEWALK x6 (`vac: 1` uses the water physics as a jetpack, drifting `ufo` plats), LASER
  DECK x8 (`laser` gates, `laserOn`: on 1.6 s of every 3 s, a touch costs a heart), MOTHERSHIP GATE and CORE (the core's
  door ends the journey). No boss or unique finale mechanic yet.
- Daniel (2026-11-15): "the art directions of prototypes look good"; he keeps refining art in the art thread, this thread moves on.
  In art rooms the way out is an orange signpost with a blinking arrow (in `artScene`), not `drawDoor`. Rooftops get an antenna or a
  neon sign on the wall face by a hash of the roof (decoration must not look like something to stand on or hide behind).
- Layout pass (Daniel, 2026-11-15, chose "Rework layouts per level": Claude redesigns where platforms, cover and gaps go from the
  reference folders, bamboo first, each tested with two players; every layout is Claude's proposal). Bamboo is done: `genBamboo`
  rotates three screens by `modOf`: stone terraces (`rock` blocks 112 / 224 / 112 high, one jump each, with a `leaf` roof), a low
  stone wall plus a canopy walk, and thickets plus canopy. `chunkList` skips bamboo, so it uses these and not the LDtk blocks.
  `tileBlock` uses a `wall` tile frame for a block's body when the set has one (asked the art thread for bamboo masonry).
  The climb wall mixes `wall_bay`, `wall_bay_b`, `wall_bay_c`. The house `rug` sprite is not placed yet.
  The bamboo set has that `wall` frame now. A room's `deco: [sprite, x, base height]` is decor only, drawn in `artScene` behind the
  props (bamboo: `torii` before a terrace, `stone_lantern` on its top, `statue` on the low wall).
  Dojo: `genDojo` has a fourth screen, STAGE (a raised wooden stage 96 high as a wide `crate` block, two beams over it, a dummy
  after it); `chunkList` skips dojo too. `mixOf(n, m, salt)` picks the screen kind for dojo and bamboo, because `modOf` picks
  repeat in runs (neighbouring `rngOf` seeds give alike first draws); other sections still use `modOf`.
  Lake: `genLake` rotates rock pillars with turtles, a sunken ruin (a stepped broken wall, then an arch of two columns under a
  turtle) and a row of columns; the dive and lake screens skip the chunks too.
  House (Daniel asked the art thread for more household objects): `genHouse` fills three spots per room from `HOUSE_SETS[name]`
  with furniture groups (`G`: dining set, desk, reading corner, sofa, bed, crates, plant, stove, fridge, tv, shelf, wardrobe,
  grandfather clock `gclock`). Wardrobe and clock are 160 high and get a crate as a step. Solid kinds are sized by `FIT.house`;
  `lamp`, `vase`, `candle_table` and `rug` are `deco` (the lamp only behind an armchair, vases and candles on furniture), because
  anything that stands free on the floor has to be solid. The house skips the chunks, so rooms keep their names.
  Two floors (Daniel, 2026-11-15: the house backdrop is a three-storey cross-section at human scale, a storey is 320 px; "the two
  layers design need ladders or stairs to guide players to go up and down"): every other generated room (`two`) has `stairs` up,
  five `floor` planks at height 320 (the painted floor line; `plat`, 2 hp, a dead plank is drawn as a dark hole) and `stairs` down.
  `stairs` are one-way ramps: a `plat` prop with `rise` (+1 up to the right, -1 to the left), height from `stairH` in `surfAt`;
  我 walks up from the foot or passes underneath. The attic (640) is not reachable and the art thread's `ladder` sprites are not used.
  Volcano: third screen, pillar hop (`box` pillars 64 to 112 high, 208 apart, a `sign` shelf). Snow: third screen, a gully under `leaf`
  ledges. Space deck: cargo stacks. `OWN_` in `chunkList` lists the sections that skip the LDtk blocks: only the rooftop run takes them.
  Lake (Daniel: no city above the water, 90% under water, no boats): layers `bg_sky_b` / `bg_far_b` with the waterline 22 art px from
  the top, `water.top = FLOOR - 88`, taller ruins. The dive screen still shows the city behind its pond.
  Bamboo backdrop: `bg_*_long` layers, 1200 art px wide (`artBack` wraps a layer at its own width); `leaf` planks use `roof_*` tiles.
  Tower scale (Daniel, 2026-11-15: "change the skyscraper floor height to match the player's height"): `FH = 320` (80 art px, the
  same storey as the house; it was 200) and the tower has 18 floors (`buildClimb(18)`, was 28) so the climb is about as long as
  before. Stairs are 640 wide and zigzag on the right (`a` = 600/680 going right, 200/280 going left), the left stays free for the
  other ways up. Ledges come in two steps (`off` 110 and 215), wall kicks allow 3. Only stairs, ladders and hooks are bot-tested at
  this height; ropes, pipes, the lift and the elevator are not re-tested. Older notes that say `FH` apart = 200 or 28 floors are stale.
  Dojo at human scale (art thread, after Daniel signed off the house art): a two-level hall, gallery beam at 320. `genDojo` has a
  fifth screen, GALLERY (`stairs` up, five `floor` planks at 320, `stairs` down, dummies and a `drum` underneath). The dummy is drawn
  184 tall but blocks only up to 150 (`FIT.dojo`), so one jump clears it. Not placed: `rack`, `bag`, `cushion`, ladders.
  Dojo again (art thread, 2026-11-15, later the same day): ONE tall hall, no gallery and no stairs sprite. The GALLERY screen is
  switched off (`mixOf(n, 4, 211)`; its code stays). The DRILL screen starts with a `drum`. The set paints a roof ridge to stand on
  at art y 48, but Daniel had the stairs and ladders removed for now, so the roof is not reachable.
  No crates in the dojo (Daniel questioned the crate in the art mock, 2026-11-15): `FIT.dojo` turns every dojo `box` into a `drum`.
  Dojo roof (Daniel, 2026-11-15: "when character goes up to the roof, the camera will go up with him. the sky background will need
  to extend"): `fitProps` marks every dojo room `tall` and adds a `ridge` (one-way roof line at 640, `thru`: `surfAt` ignores it for
  fists unless 我 stands on it) and a `stalk` at x 170 with `boost: 1900` that flings 我 onto the roof (the way up is Claude's proposal;
  Daniel removed stairs and ladders). ↓ drops back through. In `tall` rooms `camFollow` raises the view with 我 (up to 896), and
  `artBack` draws a set's `T` layers from `<name>_tall.png` (448 high, bottom-aligned, moving with the camera). Dojo `bg_far` scrolls at 0.06.
  Tower climb stairs stay the original `stair_step` (Daniel rejected the station-style stairs; never wired).
- No wall holes (Daniel, 2026-11-15): the holes a landed fist used to leave on the back wall (`addHole`, `FX.holes`, `wallHole`)
  looked out of place on the new art; `addHole` now does nothing. It was only a visual.
- Art in the prototype: Endesga 64 and the Hoodie Guy sprite (PR #22's commit is cherry-picked onto this branch). The other
  characters, animation frames and the pixelfx effects are not in. Daniel chose no new screen effects on hits.
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
- Test hook: `?dbg=1` exposes `window.__pyf = { S, P, R, ROOMS, loadRoom, VIEW, surfAt, seed, mode, chunks }`.
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
