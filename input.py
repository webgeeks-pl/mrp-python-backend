from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StandaryzowaneWejscie:
    name: str
    bom_level: int
    initial_stock: int
    lead_time: int


@dataclass(frozen=True)
class WejscieGHP(StandaryzowaneWejscie):
    weeks: int
    total_order: int
    batches: list[tuple[int, int]] = field(default_factory=list)


@dataclass(frozen=True)
class WejscieMRP(StandaryzowaneWejscie):
    usage_per_parent: int
    lot_size: int
    scheduled_receipts: list[tuple[int, int]] = field(default_factory=list)


GHP_LEVEL0_INPUT = WejscieGHP(
    name="Stół",
    bom_level=0,
    initial_stock=2,
    lead_time=1,
    weeks=10,
    total_order=60,
    batches=[
        (5, 20),
        (7, 40),
    ],
)

MRP_LEVEL1_OSTRZE_INPUT = WejscieMRP(
    name="Nogi",
    bom_level=1,
    initial_stock=40,
    lead_time=2,
    usage_per_parent=4,
    lot_size=80,
    scheduled_receipts=[],
)

MRP_LEVEL1_KIJ_INPUT = WejscieMRP(
    name="Blaty",
    bom_level=1,
    initial_stock=22,
    lead_time=3,
    usage_per_parent=1,
    lot_size=40,
    scheduled_receipts=[],
)

MRP_LEVEL2_DESKA_INPUT = WejscieMRP(
    name="Deska",
    bom_level=2,
    initial_stock=10,
    lead_time=1,
    usage_per_parent=1,
    lot_size=50,
    scheduled_receipts=[],
)
