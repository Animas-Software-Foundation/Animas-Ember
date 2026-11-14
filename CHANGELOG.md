# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [0.0.1] - 2026-11-13

First tagged release: the overworld foundation.

### Changed
- Project renamed to **Animas: Ember**

### Added
- Project website in `docs/` (landing page, playable browser demo using the game's own font, live download links) deployed to GitHub Pages by `pages.yml`
- `tools/render_screenshot.py`, which renders the README and social-card screenshot from the game's own assets
- *Animas Pixel*, a custom bitmap font drawn from scratch (`tools/generate_font.py`), used for all in-game text
- On-screen touch controls for phones and tablets, and a project icon
- Export presets for Windows (x86_64, x86_32, arm64), Linux (x86_64, x86_32, arm64, arm32), macOS (universal), Android (arm64, arm32, x86_64, x86, universal), and iOS
- GitHub Actions workflow (`build.yml`) that tests, builds every platform, and publishes releases on version tags
- Grid-based player movement (tap to turn, hold to walk) with tile collision via `RayCast2D`
- `Warp` markers and a fade `SceneTransition` for moving between maps
- Talkable `NPC` nodes and a typewriter `Dialogue` box (including sign triggers)
- `GameState` autoload with input locking, spawn points, and story flags
- Original 16x16 tileset (`tiles.png` / `tiles.tres`) with collision and a `tall_grass` custom data flag
- Playable starter town and house, built at runtime from ASCII layouts (`AsciiMap`)
- Placeholder character art so the game runs before real sprites exist
- Placeholder tall-grass encounter message
- Headless smoke test (`tools/smoke_test.gd`) and tileset generator (`tools/generate_tiles.py`)
- Browser demo (`docs/index.html`) for GitHub Pages
- Developer documentation in `docs/DEVELOPING.md`

[0.0.1]: https://github.com/pixel-pulse-games/Animas-Ember/releases/tag/v0.0.1
