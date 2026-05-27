#!/usr/bin/env python3
"""Launch the predictor with demo seeds and capture a desktop screenshot."""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mines_predictor.gui import MinesPredictorApp

ARTIFACT_DIR = "/opt/cursor/artifacts/screenshots"
OUTPUT_PATH = os.path.join(ARTIFACT_DIR, "mines-predictor-desktop.png")

DEMO_SERVER = "a" * 64
DEMO_CLIENT = "offline-demo-client-seed"
DEMO_NONCE = "0"
DEMO_MINES = 5


def capture() -> None:
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    display = os.environ.get("DISPLAY", ":1")
    subprocess.run(
        ["scrot", "-o", OUTPUT_PATH],
        check=True,
        env={**os.environ, "DISPLAY": display},
    )
    print(f"Saved screenshot to {OUTPUT_PATH}")


def main() -> None:
    app = MinesPredictorApp()
    app.server_seed_var.set(DEMO_SERVER)
    app.client_seed_var.set(DEMO_CLIENT)
    app.bet_number_var.set(DEMO_NONCE)
    app.mine_count_var.set(DEMO_MINES)

    def setup_and_shot() -> None:
        app._on_predict()
        app.root.update_idletasks()
        app.root.after(400, lambda: (capture(), app.root.quit()))

    app.root.after(300, setup_and_shot)
    app.root.mainloop()


if __name__ == "__main__":
    main()
