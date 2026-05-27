"""Stake-style Mines detector / predictor."""

from mines_predictor.detector import MinesDetector, SeedBundle
from mines_predictor.provably_fair import predict_mines

__all__ = ["MinesDetector", "SeedBundle", "predict_mines"]
