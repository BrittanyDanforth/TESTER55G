# Mines Verifier (Python GUI)

Reproduce mine positions on a **Stake-style** 5×5 provably fair grid — the same way legitimate verifiers do ([lucasholder/fair](https://github.com/lucasholder/fair), Stake’s in-game verify modal). Built for **your own offline / Stake-compatible site**, not random guessing.

> **Note:** GitHub repos titled “stake mines predictor” with ML or “pattern recognition” are scams. Real tools only **verify** outcomes from **server seed + client seed + bet #** after you have the unhashed server seed.

## Run

```bash
python3 main.py
```

Linux: `sudo apt install python3-tk`

## Cross-check with fair CLI

Official Stake test vector (3 mines, bet **1**):

```bash
fair mines "client seed" "server seed" 1
# Squares: [18, 15, 5]
```

Turn **Offline demo** on in the app, set mines to **3**, bet **#1**, then **Verify mines** — you should see the same squares and grid.

## Live mode

1. Copy **unhashed server seed** + **client seed** from your fairness page  
2. Set **mines on board** and **bet # (nonce)** to match the round you are checking  
3. Click **Verify mines** (only the button updates the board)

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Reference

| Server seed | Client seed | Bet # | Mines | Result tiles |
|-------------|-------------|-------|-------|----------------|
| `server seed` | `client seed` | 1 | 3 | 18, 15, 5 |

Algorithm: HMAC-SHA256, Fisher–Yates pick-and-remove — documented in `mines_predictor/provably_fair.py` and [lucasholder/fair `mines.rs`](https://github.com/lucasholder/fair/blob/master/src/games/mines.rs).
