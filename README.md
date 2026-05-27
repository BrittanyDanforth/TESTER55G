# Stake Mines Detector / Predictor (Python GUI)

Offline **mines detector** for Stake-style provably fair Mines games. Enter your server seed, client seed, and nonce to **predict every mine position** on the 5×5 grid before you click tiles.

This is **not** classic Minesweeper. It matches games like **Stake Mines** where you pick gems and avoid bombs using provably fair seeds.

## Phase 1 (current)

- Python desktop GUI (`tkinter`)
- Stake-compatible HMAC-SHA256 + Fisher–Yates mine placement
- 5×5 grid highlighting predicted **mines** and **safe** tiles
- Server seed hash verification
- Scan next 5 nonces (preview upcoming rounds)

## Requirements

- Python 3.10+
- Tkinter (included with most Python installs; on Debian/Ubuntu: `sudo apt install python3-tk`)

No pip packages required.

## Run

```bash
python3 main.py
```

## How to use

1. Open **Settings → Fairness** on Stake (or your offline clone).
2. After you **rotate seeds**, copy the **unhashed server seed**, your **client seed**, and the bet **nonce**.
3. Set **mines on board** to match your game (1–24).
4. Click **Detect mines** — the grid shows predicted bomb and safe cells.

### Important

- You **cannot** predict live Stake rounds without the unhashed server seed (only the hash is shown until rotation). That is by design.
- For **offline** games using the same provably fair math, this tool detects mines as soon as you know the seeds.

## Project layout

| Path | Purpose |
|------|---------|
| `main.py` | Entry point |
| `mines_predictor/provably_fair.py` | Seed → mine position math |
| `mines_predictor/gui.py` | Detector UI |
| `tests/test_provably_fair.py` | Unit tests |

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Planned phases

| Phase | Focus |
|-------|--------|
| **1** | Core predictor GUI + Stake PF algorithm |
| 2 | Import bet JSON, multiplier / cash-out calculator |
| 3 | Session log, export grid images |
| 4 | Optional themes, hotkeys, second casino presets |
