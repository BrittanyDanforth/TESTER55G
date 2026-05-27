"""Mine count changes must refresh the grid (headless)."""

import os
import unittest

os.environ.setdefault("DISPLAY", ":1")

import tkinter as tk

from mines_predictor.gui import MinesPredictorApp


class MineCountRefreshTests(unittest.TestCase):
    def test_demo_mine_count_changes_grid(self) -> None:
        try:
            app = MinesPredictorApp()
        except tk.TclError as exc:
            if "no display" in str(exc).lower():
                self.skipTest("No display")
            raise

        try:
            if app._detect_after_id is not None:
                app.root.after_cancel(app._detect_after_id)

            app.demo_mode.set(True)
            app._apply_demo_mode()
            app.root.update()

            mines_three = self._grid_mine_tiles(app)
            self.assertEqual(len(mines_three), 3)

            app.mine_count_var.set("1")
            app.root.update_idletasks()
            app._run_detect(show_popup=False)
            app.root.update()

            mines_one = self._grid_mine_tiles(app)
            self.assertEqual(len(mines_one), 1)
        finally:
            if app._detect_after_id is not None:
                app.root.after_cancel(app._detect_after_id)
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
