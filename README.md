# Mines Detector (Python GUI)

Detect mine positions on a **Stake-style** 5×5 provably fair grid. Works for **your own site** (same math as Stake) — no need to have stake.com open.

## Run

```bash
python3 main.py
```

Linux: `sudo apt install python3-tk`

## Offline demo mode (top right)

Turn **Offline demo mode** on to try detection instantly with **real verified seeds** (from Stake’s published provably fair test vectors). You should see **3 mines** at tiles **18, 15, 5**.

Turn it **off** to paste seeds from **your site’s** fairness page.

## Your site (live mode)

1. Copy **unhashed server seed** + **client seed** from your game’s fairness settings  
2. Set **mines on board** to match the game  
3. Click **Detect mines**

Uses **game round 0** for your seeds (first round with that pair). Same algorithm as Stake Originals Mines.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Demo reference

| Server seed | Client seed | Round | Mines | Result tiles |
|-------------|-------------|-------|-------|----------------|
| `server seed` | `client seed` | 1 | 3 | 18, 15, 5 |
