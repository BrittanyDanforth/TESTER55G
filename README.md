# Minesweeper

Browser-based Minesweeper with a classic detector-style UI.

## Phase 1 (current)

- Playable grid with left-click reveal and right-click flag
- Three difficulties: Beginner (9×9), Intermediate (16×16), Expert (16×30)
- Mine counter, timer, and reset face button
- First-click safe zone (mines never on first click or its neighbors)
- Flood-fill auto-reveal for empty regions
- Win/lose states with mine reveal on loss

## Run locally

Serve the project root with any static file server, then open `index.html`:

```bash
python3 -m http.server 8080
```

Visit http://localhost:8080

## Planned phases

| Phase | Focus |
|-------|--------|
| **1** | Core UI + gameplay (this release) |
| 2 | Chord click, keyboard navigation, mobile long-press |
| 3 | Best times, local storage, custom board sizes |
| 4 | Animations, sound, themes |
