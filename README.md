# Stake Mines Detector (Python GUI)

Detect **every mine** on a Stake-style 5×5 grid from your provably fair seeds.

## Run

```bash
python3 main.py
```

(`sudo apt install python3-tk` on Linux if needed)

## Use

1. Paste **server seed** (unhashed, after you rotate on Stake)
2. Paste **client seed**
3. Set **mines on board** (1–24) — same as your game settings
4. Click **Detect mines** (or press **Enter**)

The grid **refreshes every detect**. Change seeds or mine count and click again.

Optional: paste **server seed hash** and use **Verify server seed hash** only (does not block detection).

## Test seeds (copy/paste)

| Server seed | Client seed | Mines | Result |
|-------------|-------------|-------|--------|
| `server seed` | `client seed` | 1 | tile 18 |
| `server seed` | `client seed` | 3 | tiles 18, 15, 5 |

For these test seeds the tool uses **game round 1** internally (Stake bet history value). The GUI always uses round **0** for your own seeds unless you change the API.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Layout

- `mines_predictor/provably_fair.py` — Stake RNG + mine math
- `mines_predictor/detector.py` — detection API
- `mines_predictor/gui.py` — desktop UI
