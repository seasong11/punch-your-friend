# Art bundles: how to hand them over

Drop each pack you find into `asset-bundles/incoming/` in the project files (a zip, as downloaded, is fine), and tell Claude in the LDtk thread. Claude will then:

1. Unpack it and read its licence.
2. Bring it onto the game's look: Endesga 64 palette and the 16 px grid. If a pack uses a different tile size, Claude will say so before rescaling anything.
3. Merge it into one tileset per section (house, dojo, bamboo, climb, rooftop, lake, volcano, snow, space) and add it to the LDtk project.
4. Write auto-layer rules on the Terrain layer, so that painting ground, platform, water, lava or wall lays the right tiles.
5. Record the pack's name, author, link and licence in `assets/CREDITS.md`.

## What to look for

- **Licence.** The game repo is public on GitHub, so the tile files will be publicly visible.
  - Safe: CC0, CC-BY (credit the author), or anything that says you may use it in games and redistribute it inside a game.
  - Ask first: packs that forbid redistributing the source images. Many paid itch.io packs do, and a public repo counts as redistribution. Claude will flag these instead of committing them.
- **Tile size.** Prefer 16 px. Hoodie Guy is 47 px tall, so 16 px tiles fit him.
- **Format.** PNG sheets. Keep the pack's own licence or readme file inside the zip.
- **Coverage per section.** The essentials are ground or floor with its edges and corners, one-way platforms, and walls. Nice to have: background pieces (back walls, windows, far city) and small decor. Breakable props, ladders, cables and so on stay as entities, so they don't need tiles.
- **Note in the message** which section each pack is meant for.
