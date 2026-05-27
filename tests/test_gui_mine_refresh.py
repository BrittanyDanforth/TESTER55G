"""Mine count changes alone must not refresh the grid — only Detect does."""

import os
import unittest

os.environ.setdefault("DISPLAY", ":1")

import tkinter as tk

from mines_predictor.gui import MinesPredictorApp


class MineCountRefreshTests(unittest.TestCase):
    def test_mine_count_only_updates_after_detect(self) -> None:
        try:
            app = MinesPredictorApp()
        except tk.TclError as exc:
            if "no display" in str(exc).lower():
                self.skipTest("No display")
            raise

        try:
            app.demo_mode.set(True)
            app._apply_demo_mode()
            app.root.update()

            self.assertEqual(self._grid_mine_tiles(app), [])

            app._on_detect_click()
            app.root.update()
            self.assertEqual(len(self._grid_mine_tiles(app)), 3)

            app.mine_count_var.set("1")
            app.root.update_idletasks()
            self.assertEqual(len(self._grid_mine_tiles(app)), 3)

            app._on_detect_click()
            app.root.update()
            self.assertEqual(len(self._grid_mine_tiles(app)), 1)
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
