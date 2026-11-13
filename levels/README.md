# Punch Your Friend: chunk library (LDtk)

Open `punch-your-friend.ldtk` in LDtk 1.5.3 or newer. Keep this folder together, because the file loads `sprites.png` and `reference/` from next to it.

## How levels are built

A run is put together from **chunks**. The game follows each section's **beat list** and, for each beat, picks a chunk that fits from a shared seed, so 我 and every 兄弟 get the same run. Then it rolls each chunk's **random parts**.

- **Chunks join seamlessly.** They aren't rooms: there are no doors and no visible edges, and the ground of one runs straight into the next. Two chunks fit together when the terrain heights match at the seam (the right edge of one, the left edge of the next). The game reads those heights from the Terrain layer, so there is nothing to fill in by hand.
- **Sizes.** Pixels are the game's own art pixels. The grid is 16 px. The screen is 400 x 160 (25 x 10 tiles), and Hoodie Guy is about 3 tiles tall. A chunk is 400 wide by default but can be any multiple of 16. The floor line is the top of the bottom tile row (y = 144).
- **Set pieces** (`setPiece` on) are never picked at random. The beat list places them on purpose: the rooftop climb, the tower lift and elevator, the mothership gate and core.

## Level fields (select a level, then the Level panel)

| field | meaning |
|---|---|
| `section` | House, Dojo, Bamboo, Climb, Rooftop, Lake, Volcano, Snow, Space |
| `beats` | which beat slots this chunk can fill: Warmup, Challenge, Rest, Checkpoint, SetPiece, Finale |
| `difficulty` | 1 easy to 5 hard |
| `weight` | how often it's picked compared with other chunks that fit (1 = normal) |
| `setPiece` | placed by the beat list on purpose, never at random |
| `void`, `slide`, `vacuum`, `gravityScale`, `speedScale` | physics for this chunk (falling out costs a heart, snow sliding, spacewalk, and so on) |
| `fromScreen` | the prototype screen it was made from |

## Layers

- **Spawns** (the random parts):
  - `ItemSpawn`: a spot where an item may appear. `chance` runs from 0 to 1. `pool` lists which of the 17 items can show up, with their icons; leave it empty to allow any item for the section. Spawns that share a `group` give at most one item between them.
  - `HazardSpawn`: a spot where a hazard or prop may appear. `kind` is the entity name, e.g. `LaserGate`.
  - `VariantZone`: a pick-one area. Draw two or more zones with the same `group` and different `variant` numbers. Each run keeps one variant, and the other zones disappear with everything inside them.
- **Entities**: fixed props and climbing pieces, with their prototype pictures. Mapping rules as before: props anchor at top-centre, the standing height is the top edge, and climb pieces sit on their floor.
- **Terrain** (IntGrid, 16 px): `ground`, `platform` (one-way), `water`, `lava`, `wall`. Tile auto-layers will read this layer once the art bundles are in, so painting Terrain will paint the art too.

The level backgrounds in `reference/` are the prototype's drawings, kept only as a guide. They still show the old doors and room edges. Tiles will replace them.

## Starter chunks

There are 49 chunks, made from the prototype's screens: House 8, Dojo 4, Bamboo 4, Climb 1 (set piece), Rooftop 8, Lake 4, Volcano 4, Snow 4, Space 12. Each has a couple of `ItemSpawn` examples on top of props. Their beats, difficulty and weights are placeholders for you to set.

The climb keeps the prototype's 50 px floors, which don't sit on the 16 px grid; it needs its own pass. Slopes and hills are stepped to 16 px.

## Beat lists (proposal, yours to change)

Each section is a list of beats, and the game fills each beat with a random chunk that has that beat:

- House: Warmup, Warmup, Challenge, Rest, Challenge, Challenge, Checkpoint, Challenge
- Climb: SetPiece (the glass tower)
- Rooftop: Warmup, Challenge x2, Rest, Challenge x2, Checkpoint, Challenge x3
- Space: SetPiece (lift), SetPiece (elevator), Warmup, Challenge x3, Checkpoint, Challenge x3, Finale (gate), Finale (core)

The other sections follow the House pattern, at the length the stage needs to last a few minutes.

## Rebuilding

`tools/` holds the scripts that made this library. `run.js` renders the prototype in a headless browser, `gen.py` builds the full-map export from those renders, and `gen_chunks.py` turns that export into this chunk library.
