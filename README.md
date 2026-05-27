# Stake Mines Detector / Predictor (Python GUI)

Offline **mines detector** for Stake-style provably fair Mines. Paste seeds from Fairness settings to **reveal every bomb** on the 5×5 grid.

Uses the **verified Stake algorithm** ([lucasholder/fair](https://github.com/lucasholder/fair)) — same math as Stake.com’s in-game verifier.

## Phase 1

- Python desktop GUI (`tkinter`)
- Stake-compatible HMAC-SHA256 mine detection
- 5×5 grid (mines vs safe)
- Server seed hash check
- Scan next 5 bets

## Requirements

- Python 3.10+
- Tkinter (`sudo apt install python3-tk` on Debian/Ubuntu)

## Run

```bash
python3 main.py
```

## How to use

1. Stake → **Settings → Fairness**
2. After **rotate seeds**, copy **unhashed server seed**, **client seed**, and **bet #** from bet history
3. Set **mines on board** (1–24)
4. Click **Detect mines**

Optional: paste **server seed hash** before rotating to confirm the seed later.

## Verify with known test seeds

| Server seed | Client seed | Bet # | Mines | Result tiles |
|-------------|-------------|-------|-------|----------------|
| `server seed` | `client seed` | `1` | `1` | `[18]` |
| `server seed` | `client seed` | `1` | `3` | `[18, 15, 5]` |

## Project layout

| Path | Role |
|------|------|
| `main.py` | Launch GUI |
| `mines_predictor/provably_fair.py` | Stake RNG + mine placement |
| `mines_predictor/detector.py` | Detection API (hash check, scans) |
| `mines_predictor/gui.py` | Desktop UI |
| `tests/test_provably_fair.py` | Official vectors + RNG tests |

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## CLI detection (no GUI)

```bash
python3 -c "
from mines_predictor import predict_mines
r = predict_mines('server seed', 'client seed', 1, 3)
print('Mines:', list(r.mine_tiles))
"
```
