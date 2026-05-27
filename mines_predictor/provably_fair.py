"""
Stake-style Mines provably fair mine placement.

Implements the published Stake algorithm:
  - HMAC-SHA256(server_seed, f"{client_seed}:{nonce}:{cursor}")
  - 4-byte chunks → floats in [0, 1)
  - 24 floats with cursor 0..2 (3 increments)
  - Fisher–Yates: j = int(float[i] * remaining_tiles)
  - First `mine_count` tiles in shuffle order are mines

Works for Stake / Stake.us and offline clones using the same math.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionResult:
    mine_tiles: tuple[int, ...]
    safe_tiles: tuple[int, ...]
    shuffle_order: tuple[int, ...]
    floats_used: tuple[float, ...]

    @property
    def mine_count(self) -> int:
        return len(self.mine_tiles)


def hash_server_seed(server_seed: str) -> str:
    return hashlib.sha256(server_seed.encode("utf-8")).hexdigest()


def verify_server_seed_hash(server_seed: str, expected_hash: str) -> bool:
    computed = hash_server_seed(server_seed)
    return computed.lower() == expected_hash.strip().lower()


def _hmac_block(server_seed: str, client_seed: str, nonce: int, cursor: int) -> bytes:
    message = f"{client_seed}:{nonce}:{cursor}"
    return hmac.new(
        server_seed.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()


def _bytes_to_float(chunk: bytes) -> float:
    value = 0.0
    for index, byte in enumerate(chunk):
        value += byte / (256 ** (index + 1))
    return value


def generate_floats(
    server_seed: str,
    client_seed: str,
    nonce: int,
    *,
    count: int = 24,
) -> list[float]:
    floats: list[float] = []
    cursor = 0
    while len(floats) < count:
        digest = _hmac_block(server_seed, client_seed, nonce, cursor)
        for offset in range(0, 32, 4):
            if len(floats) >= count:
                break
            floats.append(_bytes_to_float(digest[offset : offset + 4]))
        cursor += 1
    return floats


def fisher_yates_tile_order(floats: list[float], *, grid_size: int = 25) -> list[int]:
    """Return full tile order after 24 selection steps (Stake Mines)."""
    cells = list(range(grid_size))
    order: list[int] = []
    for step in range(grid_size - 1):
        remaining = len(cells)
        index = int(floats[step] * remaining)
        if index >= remaining:
            index = remaining - 1
        order.append(cells.pop(index))
    order.append(cells[0])
    return order


def predict_mines(
    server_seed: str,
    client_seed: str,
    nonce: int,
    mine_count: int,
    *,
    grid_size: int = 25,
) -> PredictionResult:
    if not server_seed.strip():
        raise ValueError("Server seed is required")
    if not client_seed.strip():
        raise ValueError("Client seed is required")
    if nonce < 0:
        raise ValueError("Nonce must be zero or positive")
    if mine_count < 1 or mine_count > grid_size - 1:
        raise ValueError(f"Mine count must be between 1 and {grid_size - 1}")

    floats = generate_floats(server_seed.strip(), client_seed.strip(), int(nonce))
    shuffle_order = fisher_yates_tile_order(floats, grid_size=grid_size)
    mine_tiles = tuple(sorted(shuffle_order[:mine_count]))
    safe_tiles = tuple(sorted(set(range(grid_size)) - set(mine_tiles)))

    return PredictionResult(
        mine_tiles=mine_tiles,
        safe_tiles=safe_tiles,
        shuffle_order=tuple(shuffle_order),
        floats_used=tuple(floats),
    )


def tile_to_row_col(tile: int, cols: int = 5) -> tuple[int, int]:
    return divmod(tile, cols)


def format_tile_list(tiles: tuple[int, ...], cols: int = 5) -> str:
    parts = []
    for tile in tiles:
        row, col = tile_to_row_col(tile, cols)
        parts.append(f"({row + 1},{col + 1})")
    return ", ".join(parts)
