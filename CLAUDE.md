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
