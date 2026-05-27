"""GUI demo toggle behavior (headless)."""

import os
import unittest

os.environ.setdefault("DISPLAY", ":1")

import tkinter as tk

from mines_predictor.gui import MinesPredictorApp


class DemoToggleTests(unittest.TestCase):
    def test_demo_off_keeps_seeds_no_crash(self) -> None:
        try:
            app = MinesPredictorApp()
        except tk.TclError as exc:
            if "no display" in str(exc).lower():
                self.skipTest("No display for GUI tests")
            raise

        try:
            app.demo_mode.set(True)
            app._apply_demo_mode()
            app.root.update()

            app.demo_mode.set(False)
            app._apply_demo_mode()
            app.root.update()

            self.assertTrue(app.server_seed_var.get().strip())
            self.assertTrue(app.client_seed_var.get().strip())
            self.assertEqual(self._grid_mine_tiles(app), [])
        finally:
            app.root.destroy()

    @staticmethod
    def _grid_mine_tiles(app: MinesPredictorApp) -> list[int]:
        tiles = []
        for row in range(5):
            for col in range(5):
                if app._cell_labels[row][col].cget("text") == "💣":
                    tiles.append(row * 5 + col)
        return tiles


if __name__ == "__main__":
    unittest.main()
