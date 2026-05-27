"""
Offline demo preset — real Stake-verified provably fair seeds.

Same math as Stake.com / Stake.us; use this to test detection without any site open.
Vectors from https://github.com/lucasholder/fair (checked against Stake verifier).
"""

from __future__ import annotations

from dataclasses import dataclass

from mines_predictor.provably_fair import hash_server_seed, predict_mines


@dataclass(frozen=True)
class DemoPreset:
    server_seed: str
    client_seed: str
    game_round: int
    mine_count: int
    server_hash: str
    expected_mines: tuple[int, ...]
    label: str


OFFLINE_DEMO = DemoPreset(
    server_seed="server seed",
    client_seed="client seed",
    game_round=1,
    mine_count=3,
    server_hash="a4e53dc2f480b8fce6fe688b1317658b446299df23ad533394406427c8c19557",
    expected_mines=(18, 15, 5),
    label="Stake-verified offline demo",
)


def run_demo_detection(mine_count: int | None = None) -> tuple[bool, str]:
    """
    Run detection with the demo preset. Returns (matches_expected, message).
    """
    count = mine_count if mine_count is not None else OFFLINE_DEMO.mine_count
    result = predict_mines(
        OFFLINE_DEMO.server_seed,
        OFFLINE_DEMO.client_seed,
        OFFLINE_DEMO.game_round,
        count,
    )
    if count == OFFLINE_DEMO.mine_count:
        ok = result.mine_tiles == OFFLINE_DEMO.expected_mines
        if not ok:
            return False, (
                f"Demo sanity check failed: got {list(result.mine_tiles)}, "
                f"expected {list(OFFLINE_DEMO.expected_mines)}"
            )
    hash_ok = hash_server_seed(OFFLINE_DEMO.server_seed) == OFFLINE_DEMO.server_hash
    if not hash_ok:
        return False, "Demo server seed hash mismatch"
    return True, "Demo detection OK (Stake-compatible math)"
