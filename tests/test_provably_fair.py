"""Tests for provably fair mine prediction."""

import unittest

from mines_predictor.provably_fair import (
    fisher_yates_tile_order,
    generate_floats,
    predict_mines,
    verify_server_seed_hash,
)


class ProvablyFairTests(unittest.TestCase):
    def test_hash_verification_roundtrip(self) -> None:
        seed = "a" * 64
        digest = __import__("hashlib").sha256(seed.encode()).hexdigest()
        self.assertTrue(verify_server_seed_hash(seed, digest))

    def test_predict_returns_correct_counts(self) -> None:
        result = predict_mines("server" * 8, "client-seed", 0, 5)
        self.assertEqual(result.mine_count, 5)
        self.assertEqual(len(result.safe_tiles), 20)
        self.assertEqual(len(set(result.mine_tiles) & set(result.safe_tiles)), 0)

    def test_deterministic(self) -> None:
        args = ("abc123", "my_client", 7, 3)
        first = predict_mines(*args)
        second = predict_mines(*args)
        self.assertEqual(first.mine_tiles, second.mine_tiles)

    def test_floats_length(self) -> None:
        floats = generate_floats("s", "c", 0, count=24)
        self.assertEqual(len(floats), 24)
        for value in floats:
            self.assertGreaterEqual(value, 0.0)
            self.assertLess(value, 1.0)

    def test_shuffle_is_permutation(self) -> None:
        floats = generate_floats("seed", "client", 1)
        order = fisher_yates_tile_order(floats)
        self.assertEqual(len(order), 25)
        self.assertEqual(sorted(order), list(range(25)))

    def test_invalid_mine_count(self) -> None:
        with self.assertRaises(ValueError):
            predict_mines("a", "b", 0, 0)
        with self.assertRaises(ValueError):
            predict_mines("a", "b", 0, 25)


if __name__ == "__main__":
    unittest.main()
