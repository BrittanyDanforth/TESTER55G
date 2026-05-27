"""Tests for Stake-compatible mine detection."""

import unittest

from mines_predictor.detector import MinesDetector, SeedBundle
from mines_predictor.provably_fair import (
    format_squares,
    StakeRNG,
    generate_floats,
    hash_server_seed,
    pick_mine_tiles,
    predict_mines,
    verify_server_seed_hash,
)


class StakeOfficialVectors(unittest.TestCase):
    def test_one_mine(self) -> None:
        self.assertEqual(pick_mine_tiles("server seed", "client seed", 1, 1), [18])

    def test_three_mines(self) -> None:
        self.assertEqual(pick_mine_tiles("server seed", "client seed", 1, 3), [18, 15, 5])

    def test_server_seed_hash(self) -> None:
        digest = hash_server_seed("server seed")
        self.assertEqual(
            digest,
            "a4e53dc2f480b8fce6fe688b1317658b446299df23ad533394406427c8c19557",
        )
        self.assertTrue(verify_server_seed_hash("server seed", digest))

    def test_format_squares_matches_fair_cli(self) -> None:
        result = predict_mines("server seed", "client seed", 1, 3)
        self.assertEqual(format_squares(result.mine_tiles), "Squares: [18, 15, 5]")

    def test_prediction_result(self) -> None:
        result = predict_mines("server seed", "client seed", 1, 3)
        self.assertEqual(result.mine_tiles, (18, 15, 5))


class StakeRNGTests(unittest.TestCase):
    def test_first_ten_floats(self) -> None:
        rng = StakeRNG("some server seed", "some client seed", 1)
        expected = [
            0.5919261889066547,
            0.81884371698834,
            0.17176169087179005,
            0.277875404804945,
            0.5454130100551993,
            0.913538561668247,
            0.732050604885444,
            0.34164569014683366,
            0.7736547295935452,
            0.5108428790699691,
        ]
        for target in expected:
            self.assertAlmostEqual(rng.next_float(), target, places=14)

    def test_generate_floats_count(self) -> None:
        floats = generate_floats("s", "c", 0, 24)
        self.assertEqual(len(floats), 24)


class DetectorFacadeTests(unittest.TestCase):
    def test_detect(self) -> None:
        detector = MinesDetector()
        bundle = SeedBundle(
            server_seed="server seed",
            client_seed="client seed",
            mine_count=3,
            game_round=1,
        )
        self.assertEqual(detector.detect(bundle).mine_tiles, (18, 15, 5))

    def test_detect_default_round_zero(self) -> None:
        detector = MinesDetector()
        bundle = SeedBundle(
            server_seed="server seed",
            client_seed="client seed",
            mine_count=1,
        )
        mines_at_zero = detector.detect(bundle).mine_tiles
        mines_at_one = detector.detect(
            SeedBundle("server seed", "client seed", 1, game_round=1)
        ).mine_tiles
        self.assertNotEqual(mines_at_zero, mines_at_one)

    def test_verify_hash(self) -> None:
        self.assertTrue(
            MinesDetector.verify_hash(
                "server seed",
                hash_server_seed("server seed"),
            )
        )


class ValidationTests(unittest.TestCase):
    def test_invalid_mine_count(self) -> None:
        with self.assertRaises(ValueError):
            predict_mines("a", "b", 0, 0)

    def test_empty_seeds(self) -> None:
        with self.assertRaises(ValueError):
            predict_mines("", "client", 0, 3)


if __name__ == "__main__":
    unittest.main()
