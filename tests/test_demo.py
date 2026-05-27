"""Tests for offline demo preset."""

import unittest

from mines_predictor.demo import OFFLINE_DEMO, run_demo_detection
from mines_predictor.provably_fair import hash_server_seed, predict_mines


class DemoTests(unittest.TestCase):
    def test_demo_expected_mines(self) -> None:
        result = predict_mines(
            OFFLINE_DEMO.server_seed,
            OFFLINE_DEMO.client_seed,
            OFFLINE_DEMO.game_round,
            OFFLINE_DEMO.mine_count,
        )
        self.assertEqual(result.mine_tiles, OFFLINE_DEMO.expected_mines)

    def test_demo_hash(self) -> None:
        self.assertEqual(hash_server_seed(OFFLINE_DEMO.server_seed), OFFLINE_DEMO.server_hash)

    def test_run_demo_detection(self) -> None:
        ok, msg = run_demo_detection()
        self.assertTrue(ok, msg)


if __name__ == "__main__":
    unittest.main()
