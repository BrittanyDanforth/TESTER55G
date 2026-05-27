"""
Stake.com / Stake.us Mines — provably fair mine detection.

Verified against lucasholder/fair (Stake in-game verifier):
  - HMAC-SHA256 key=server_seed, message="{client_seed}:{bet_number}:{round}"
  - Bytes → floats (4 bytes each, Stake byte formula)
  - Fisher–Yates pick-and-remove: floor(float × remaining)
  - Mines = first `mine_count` picks (tiles 0–24, left→right, top→bottom)
"""

from __future__ import annotations

import hashlib
import hmac
import math
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class PredictionResult:
    """Mine detection output for one bet."""

    mine_tiles: tuple[int, ...]
    """Mine tile indices in placement order (Stake order)."""

    safe_tiles: tuple[int, ...]
    shuffle_order: tuple[int, ...]
    """Full pick sequence when all 25 tiles are resolved."""

    mine_count: int
    bet_number: int

    @property
    def mine_tiles_sorted(self) -> tuple[int, ...]:
        return tuple(sorted(self.mine_tiles))


class StakeRNG:
    """Provably fair random stream (Stake Originals)."""

    def __init__(
        self,
        server_seed: str,
        client_seed: str,
        bet_number: int,
        *,
        cursor: int = 0,
    ) -> None:
        self._server_seed = server_seed
        self._client_seed = client_seed
        self._bet_number = int(bet_number)
        self._round = cursor // 32
        self._round_byte = cursor % 32
        self._round_digest: bytes | None = None

    def _refresh_round(self) -> None:
        message = f"{self._client_seed}:{self._bet_number}:{self._round}"
        self._round_digest = hmac.new(
            self._server_seed.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        self._round_byte = 0

    def next_byte(self) -> int:
        if self._round_digest is None:
            self._refresh_round()
        assert self._round_digest is not None
        value = self._round_digest[self._round_byte]
        if self._round_byte >= 31:
            self._round_byte = 0
            self._round += 1
            self._round_digest = None
        else:
            self._round_byte += 1
        return value

    def next_float(self) -> float:
        chunk = bytes(self.next_byte() for _ in range(4))
        return bytes_to_float(chunk)

    def next_floats(self, count: int) -> list[float]:
        return [self.next_float() for _ in range(count)]


def bytes_to_float(chunk: bytes) -> float:
    total = 0.0
    for index, byte in enumerate(chunk):
        total += byte / (256 ** (index + 1))
    return total


def byte_generator(
    server_seed: str,
    client_seed: str,
    bet_number: int,
    cursor: int = 0,
) -> Iterator[int]:
    """Yield raw bytes from the Stake PF stream."""
    rng = StakeRNG(server_seed, client_seed, bet_number, cursor=cursor)
    while True:
        yield rng.next_byte()


def generate_floats(
    server_seed: str,
    client_seed: str,
    bet_number: int,
    count: int,
    *,
    cursor: int = 0,
) -> list[float]:
    rng = StakeRNG(server_seed, client_seed, bet_number, cursor=cursor)
    return rng.next_floats(count)


def pick_mine_tiles(
    server_seed: str,
    client_seed: str,
    bet_number: int,
    mine_count: int,
    *,
    grid_size: int = 25,
) -> list[int]:
    """Return mine tile indices in Stake placement order."""
    if mine_count < 1 or mine_count > grid_size - 1:
        raise ValueError(f"Mine count must be between 1 and {grid_size - 1}")

    remaining = list(range(grid_size))
    mines: list[int] = []
    rng = StakeRNG(server_seed, client_seed, bet_number)

    for _ in range(mine_count):
        floating = rng.next_float()
        index = math.floor(floating * len(remaining))
        mines.append(remaining.pop(index))

    return mines


def _full_shuffle_order(
    server_seed: str,
    client_seed: str,
    bet_number: int,
    *,
    grid_size: int = 25,
) -> list[int]:
    remaining = list(range(grid_size))
    order: list[int] = []
    rng = StakeRNG(server_seed, client_seed, bet_number)
    for _ in range(grid_size - 1):
        index = math.floor(rng.next_float() * len(remaining))
        order.append(remaining.pop(index))
    order.append(remaining[0])
    return order


def hash_server_seed(server_seed: str) -> str:
    return hashlib.sha256(server_seed.encode("utf-8")).hexdigest()


def verify_server_seed_hash(server_seed: str, expected_hash: str) -> bool:
    return hash_server_seed(server_seed).lower() == expected_hash.strip().lower()


def _normalize_seed(value: str, *, name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{name} is required")
    return cleaned


def predict_mines(
    server_seed: str,
    client_seed: str,
    bet_number: int,
    mine_count: int,
    *,
    grid_size: int = 25,
) -> PredictionResult:
    """
    Detect mine positions for a Stake-style Mines bet.

    Args:
        server_seed: Unhashed server seed (after rotation on live Stake).
        client_seed: Your client seed from fairness settings.
        bet_number: Bet counter for this seed pair (0, 1, 2, …).
        mine_count: Bombs on the board (1–24).
    """
    server = _normalize_seed(server_seed, name="Server seed")
    client = _normalize_seed(client_seed, name="Client seed")
    bet = int(bet_number)
    if bet < 0:
        raise ValueError("Bet number must be zero or positive")

    mines = pick_mine_tiles(server, client, bet, mine_count, grid_size=grid_size)
    shuffle = _full_shuffle_order(server, client, bet, grid_size=grid_size)
    mine_set = set(mines)
    safe = tuple(tile for tile in range(grid_size) if tile not in mine_set)

    return PredictionResult(
        mine_tiles=tuple(mines),
        safe_tiles=safe,
        shuffle_order=tuple(shuffle),
        mine_count=mine_count,
        bet_number=bet,
    )


# Backward-compatible alias
predict_mines_from_nonce = predict_mines


def tile_to_row_col(tile: int, cols: int = 5) -> tuple[int, int]:
    return divmod(tile, cols)


def format_tile_list(tiles: tuple[int, ...], cols: int = 5) -> str:
    return ", ".join(
        f"({tile_to_row_col(tile, cols)[0] + 1},{tile_to_row_col(tile, cols)[1] + 1})"
        for tile in tiles
    )
