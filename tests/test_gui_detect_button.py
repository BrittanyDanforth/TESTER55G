"""Detect button must always refresh, even when inputs unchanged."""

import os
import unittest

os.environ.setdefault("DISPLAY", ":1")

import tkinter as tk

from mines_predictor.gui import MinesPredictorApp


class DetectButtonTests(unittest.TestCase):
    def test_detect_click_forces_refresh(self) -> None:
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

            app._on_detect_click()
            app.root.update()
            first = app._last_bundle_key

            app._on_detect_click()
            app.root.update()
            self.assertIsNotNone(first)
            self.assertEqual(app._last_bundle_key, first)
            self.assertEqual(len(self._grid_mine_tiles(app)), 3)
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
