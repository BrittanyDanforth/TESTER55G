"""High-level detection API for the mines predictor."""

from __future__ import annotations

from dataclasses import dataclass

from mines_predictor.provably_fair import (
    PredictionResult,
    format_tile_list,
    hash_server_seed,
    predict_mines,
    verify_server_seed_hash,
)


@dataclass(frozen=True)
class SeedBundle:
    server_seed: str
    client_seed: str
    mine_count: int
    """Round index for provably fair math (0 = first game with this seed pair)."""
    game_round: int = 0


class MinesDetector:
    """Facade for seed validation and mine detection."""

    def detect(self, bundle: SeedBundle) -> PredictionResult:
        return predict_mines(
            bundle.server_seed,
            bundle.client_seed,
            bundle.game_round,
            bundle.mine_count,
        )

    @staticmethod
    def verify_hash(server_seed: str, expected_hash: str) -> bool:
        return verify_server_seed_hash(server_seed, expected_hash)

    @staticmethod
    def compute_server_hash(server_seed: str) -> str:
        return hash_server_seed(server_seed)

    @staticmethod
    def format_mines(tiles: tuple[int, ...]) -> str:
        return format_tile_list(tiles)
