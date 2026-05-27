"""Tests for Stake-compatible mine detection."""

import unittest

from mines_predictor.detector import MinesDetector, SeedBundle
from mines_predictor.provably_fair import (
    StakeRNG,
    generate_floats,
    hash_server_seed,
    pick_mine_tiles,
    predict_mines,
    verify_server_seed_hash,
)


class StakeOfficialVectors(unittest.TestCase):
    """Vectors from lucasholder/fair (verified on Stake.com)."""

    def test_one_mine(self) -> None:
        mines = pick_mine_tiles("server seed", "client seed", 1, 1)
        self.assertEqual(mines, [18])

    def test_three_mines(self) -> None:
        mines = pick_mine_tiles("server seed", "client seed", 1, 3)
        self.assertEqual(mines, [18, 15, 5])

    def test_server_seed_hash(self) -> None:
        digest = hash_server_seed("server seed")
        self.assertEqual(
            digest,
            "a4e53dc2f480b8fce6fe688b1317658b446299df23ad533394406427c8c19557",
        )
        self.assertTrue(verify_server_seed_hash("server seed", digest))

    def test_prediction_result(self) -> None:
        result = predict_mines("server seed", "client seed", 1, 3)
        self.assertEqual(result.mine_tiles, (18, 15, 5))
        self.assertEqual(result.mine_count, 3)
        self.assertEqual(len(result.safe_tiles), 22)


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

    def test_high_nonce_first_float(self) -> None:
        rng = StakeRNG(
            "e8df2cc3b9ccb583ce5ea92336842387",
            "83e27f682128eb1852b048203dfd6931",
            1942124,
        )
        self.assertAlmostEqual(
            rng.next_float(),
            0.00000025122426450252533,
            places=20,
        )

    def test_generate_floats_count(self) -> None:
        floats = generate_floats("s", "c", 0, 24)
        self.assertEqual(len(floats), 24)
        for value in floats:
            self.assertGreaterEqual(value, 0.0)
            self.assertLess(value, 1.0)


class DetectorFacadeTests(unittest.TestCase):
    def test_detect_with_valid_hash(self) -> None:
        server = "server seed"
        detector = MinesDetector()
        bundle = SeedBundle(
            server_seed=server,
            client_seed="client seed",
            bet_number=1,
            mine_count=3,
            server_hash=hash_server_seed(server),
        )
        result = detector.detect(bundle)
        self.assertEqual(result.mine_tiles, (18, 15, 5))

    def test_detect_rejects_bad_hash(self) -> None:
        detector = MinesDetector()
        bundle = SeedBundle(
            server_seed="server seed",
            client_seed="client seed",
            bet_number=1,
            mine_count=1,
            server_hash="0" * 64,
        )
        with self.assertRaises(ValueError):
            detector.detect(bundle)

    def test_scan_next_bets(self) -> None:
        detector = MinesDetector()
        bundle = SeedBundle(
            server_seed="server seed",
            client_seed="client seed",
            bet_number=1,
            mine_count=1,
        )
        scans = detector.scan_next_bets(bundle, count=3)
        self.assertEqual(len(scans), 3)
        self.assertEqual(scans[0].bet_number, 1)
        self.assertEqual(scans[0].mines, (18,))


class ValidationTests(unittest.TestCase):
    def test_invalid_mine_count(self) -> None:
        with self.assertRaises(ValueError):
            predict_mines("a", "b", 0, 0)
        with self.assertRaises(ValueError):
            predict_mines("a", "b", 0, 25)

    def test_empty_seeds(self) -> None:
        with self.assertRaises(ValueError):
            predict_mines("", "client", 0, 3)


if __name__ == "__main__":
    unittest.main()
