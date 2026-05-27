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
    bet_number: int
    mine_count: int
    server_hash: str = ""


@dataclass(frozen=True)
class ScanResult:
    bet_number: int
    mines: tuple[int, ...]


class MinesDetector:
    """Facade for seed validation, detection, and multi-bet scans."""

    def detect(self, bundle: SeedBundle) -> PredictionResult:
        if bundle.server_hash:
            if not verify_server_seed_hash(bundle.server_seed, bundle.server_hash):
                raise ValueError(
                    "Server seed does not match the hash from fairness settings"
                )
        return predict_mines(
            bundle.server_seed,
            bundle.client_seed,
            bundle.bet_number,
            bundle.mine_count,
        )

    def scan_next_bets(
        self,
        bundle: SeedBundle,
        *,
        count: int = 5,
    ) -> list[ScanResult]:
        results: list[ScanResult] = []
        for offset in range(count):
            bet = bundle.bet_number + offset
            prediction = predict_mines(
                bundle.server_seed,
                bundle.client_seed,
                bet,
                bundle.mine_count,
            )
            results.append(
                ScanResult(bet_number=bet, mines=prediction.mine_tiles)
            )
        return results

    @staticmethod
    def compute_server_hash(server_seed: str) -> str:
        return hash_server_seed(server_seed)

    @staticmethod
    def format_mines(tiles: tuple[int, ...]) -> str:
        return format_tile_list(tiles)
