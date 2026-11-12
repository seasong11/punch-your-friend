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
- Palette: `palettize()` snaps every art pixel to Endesga 32 (`PAL`) through a 15-bit lookup table each frame,
  which also removes soft anti-aliasing. Canvas text colours go through `palCol()`. `glow()` is a no-op (soft
  glows only band into rings on a palette).
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
