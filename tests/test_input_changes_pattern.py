"""Prove different inputs produce different mine patterns."""

import unittest

from mines_predictor.provably_fair import predict_mines


class PatternChangeTests(unittest.TestCase):
    def test_same_inputs_same_mines(self) -> None:
        args = ("server seed", "client seed", 1, 3)
        a = predict_mines(*args).mine_tiles
        b = predict_mines(*args).mine_tiles
        self.assertEqual(a, b)

    def test_different_client_different_mines(self) -> None:
        a = predict_mines("server seed", "client seed", 1, 3).mine_tiles
        b = predict_mines("server seed", "client seed!", 1, 3).mine_tiles
        self.assertNotEqual(a, b)

    def test_different_mine_count_different_set(self) -> None:
        a = set(predict_mines("server seed", "client seed", 1, 3).mine_tiles)
        b = set(predict_mines("server seed", "client seed", 1, 5).mine_tiles)
        self.assertNotEqual(a, b)
        self.assertLess(len(a), len(b))


if __name__ == "__main__":
    unittest.main()
