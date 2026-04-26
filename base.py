from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BaseInput:
    name: str
    bom_level: int
    initial_stock: int
    lead_time: int
