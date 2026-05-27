#!/usr/bin/env python3
"""Capture desktop screenshot with offline demo mode enabled."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mines_predictor.gui import MinesPredictorApp

OUTPUT = "/opt/cursor/artifacts/screenshots/mines-predictor-desktop.png"


def main() -> None:
    app = MinesPredictorApp()
    app.demo_mode.set(True)

    def shot() -> None:
        app.root.update()
        os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
        subprocess.run(
            ["scrot", "-o", OUTPUT],
            check=True,
            env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":1")},
        )
        print(f"Saved {OUTPUT}")
        app.root.quit()

    app.root.after(600, shot)
    app.root.mainloop()


if __name__ == "__main__":
    main()
