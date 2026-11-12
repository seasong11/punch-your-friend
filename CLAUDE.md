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
- Rendering: world drawn to an offscreen 1600x640 canvas, downscaled 2x and upscaled with hard pixels;
  `fillText` calls are recorded and replayed crisp in pixel fonts (Press Start 2P / DotGothic16).
- Levels: `levelOf(score)` — LV2 at 25 points, LV3 at 75, then triangular growth. Speed curve caps around 4.2.
  A fairness check (`fairSpot`) stops the practice bot from throwing unescapable punches.
- Six stages by level (living room, dojo, rooftop, bamboo, volcano with fire dragon, space with ships),
  stage-themed punch skins (`PUNCH`), layered music intensity (`setLevel`).
- 我 (dodger): move, block/perfect block (↓/S/Space), dash (Shift), Golden Bell (E, Rage meter),
  perfect-block stun, on-fire streak buff (5/10/20 combo → +10/20/30% speed), taunts, six unlockable
  costumes (`COS`) each with its own move set (`MOVES`).
- 兄弟 (puncher): tap to chop, formations (1/2/3), feint (F), homing (H), 黄泉指 Underworld Finger (Y),
  如来神掌 Buddha Palm (charged super), Punch Rain ultimate (R).

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
- Test without the PeerJS cloud: open with `?mock=1` and inject a `window.MockPeer` (BroadcastChannel)
  before the page scripts run.

## Phones
- Landscape phones (`orientation: landscape` and `max-height: 540px`) switch `.wrap` to a grid: arena in the
  middle, ◀ ▶ on the left, block/chop and skills on the right, the rest of the page below. `.pads`,
  `#meSkills` and `#broMoves` become `display: contents` so their buttons are placed one by one.
  `body.is-bro` reserves room for the 兄弟 tool row under the arena.
- Portrait phones get a compact header and invite bar and a tip to turn the phone sideways.
- On touch devices (`pointer: coarse`) the world canvas is drawn directly at half size (`LOWRES`),
  skipping the shrink pass; recorded text is replayed with a 2x base transform (`TXT_BASE`).
- The invite button uses the system share sheet on phones; hits vibrate (Android); a screen wake lock
  is taken on the first tap.

## Working on it
- Edit `index.html` directly; there is no build step.
- To test multiplayer locally, serve the folder (`python3 -m http.server`) and open two browser windows:
  one at `/` (host) and one at the invite link it shows.
- Keep the game working inside a single file so it can be dropped onto any static host.
