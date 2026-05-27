"""GUI demo toggle behavior (headless)."""

import os
import unittest

os.environ.setdefault("DISPLAY", ":1")

import tkinter as tk

from mines_predictor.gui import MinesPredictorApp


class DemoToggleTests(unittest.TestCase):
    def test_demo_off_keeps_seeds_no_crash(self) -> None:
        root_started = False
        try:
            app = MinesPredictorApp()
            root_started = True
            app.demo_mode.set(True)
            app._apply_demo_mode()
            app.root.update()

            app.demo_mode.set(False)
            app._apply_demo_mode()
            app.root.update()

            self.assertTrue(app.server_seed_var.get().strip())
            self.assertTrue(app.client_seed_var.get().strip())
            app.root.destroy()
        except tk.TclError as exc:
            if "no display" in str(exc).lower():
                self.skipTest("No display for GUI tests")
            raise


if __name__ == "__main__":
    unittest.main()
