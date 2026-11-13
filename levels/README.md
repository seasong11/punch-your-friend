# Punch Your Friend: LDtk project of the journey prototype

Generated from branch `house-prototype` at commit `c1ad7b5` (2026-11-13 09:27 UTC, "Longer stages, rooftop features and a space finale").
That's the version with the longer stages (173 screens), the rooftop vents, zip cables and billboards, and the space finale. Later changes to the prototype aren't in here; the scripts in `tools/` can rebuild it.

## Opening it

1. Pull this branch (or unzip the downloaded copy) and keep the `levels/` folder together: the `.ldtk` file looks for `sprites.png` and `backgrounds/` next to it.
2. In LDtk (1.5.3 or newer): **Load project** and pick `punch-your-friend.ldtk`.
3. Press **W** (world view) to see the whole journey as one map, then double-click a room to edit it.

## Working on it together

- Pull before you start editing, and push when you're done. The project is one big file, so take turns rather than editing at the same time.
- Turning on *Project settings → Save levels to separate files* in LDtk splits each screen into its own file, which makes edits to different screens merge cleanly.

## What's in it

- **173 levels, one per screen**, in journey order: `R001_LivingRoom` style names up to `R173_MothershipCore`. Each section gets its own row in the world view (house, dojo, bamboo, the tall rooftop climb, rooftop run, lake, volcano, snow, space), and inside a row the screens sit side by side the way the follow camera joins them, so floors line up across the seams.
- **Background image per room**: the room drawn by the prototype itself, without the furniture, decor or climbing pieces, so those can move freely on top.
- **Entities layer**: every prop, wall decoration and climbing piece, each shown with its real sprite from the game. They're grouped by section in the entity panel (House, Dojo, Bamboo, Climb, RooftopRun, Lake, Volcano, Snow, Space, Decor), so you can also drop in new ones.
- **Terrain layer** (IntGrid, 10 px cells, see-through): `ground`, `water`, `lava`, `floor_slab` (the climb's one-way floors) and `glass_wall` (the climb's side glass). Ramps and hills are stepped in 10 px columns.
- **Level fields** (Level panel): section, scene, style, wall and floor colours, outdoor/void/slide, checkpoint, vacuum (spacewalk), speed and gravity scale, lift ride time, entry height.

Units are game world units: one room is 1600 x 640, the floor line is at y = 550 (5980 in the climb), one art pixel is 4 units and a climb floor is 200.

## How things map back to the game

Each entity's pivot point is the number the game uses:

- **Furniture and other props** (pivot top-centre): x = the prop's `x`, the top edge is its standing height `h` (550 minus y), width is `w`. `hp` empty means unbreakable. One-way platforms (cyan) are thin bars at their top height; non-solid things (green) are stalks and mushrooms.
- **Climb pieces** (pivot bottom-centre): the bottom edge sits on the floor `lv` they start from. Pipes, ropes, the window lift and the elevator span `n` floors (height = n x 200). Hooks sit 150 above their floor, ledges 100 above theirs. Windows have the open/shut `offset`.
- **Laser gates and zip cables** (pivot bottom-centre): the bottom edge is their base. Laser `off` is the timing offset; a cable's ends are its `cx0/cy0` and `cx1/cy1` fields (they don't follow the box when you drag it). Billboards keep their bridge in `bx/bw/bh`.
- **Wall decor** (pivot top-left): only x matters to the game; y is fixed for each kind. Game x = entity x minus this offset: Pic -2, Lamp -166, Win -56, Clock -4, Books 2, Rug -36, Tiles 20, Pots 0, Shelf 0, Tree -24, Scroll -24 to -26, Rack -2.
- **The rooftop climb** is generated from a seed in the prototype; here every floor's stairs, ladders and pillars are laid out as ordinary entities so you can rearrange them by hand.

Sprites stretch when you resize something. That only changes the preview; the game draws each prop at its real size.

## Not covered yet

- The game doesn't read this file yet. Making the prototype load it is a separate step; the mapping above is what that loader would follow.
- Doors are drawn into the backgrounds, not entities. Fists, music and section rules stay in code.
- `tools/` holds the scripts that made this (render the prototype in a headless browser, then build the `.ldtk`), so it can be regenerated after the prototype changes.
