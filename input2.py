from __future__ import annotations

from dataclasses import dataclass, field

from ghp import GHPInput
from mrp import MRPInput


GHP_INPUT = GHPInput(
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

MRP_LEVEL1_0_INPUT = MRPInput(
    name="Nogi",
    bom_level=1,
    initial_stock=40,
    lead_time=2,
    usage_per_parent=4,
    lot_size=80,
    scheduled_receipts=[],
)

MRP_LEVEL1_1_INPUT = MRPInput(
    name="Blaty",
    bom_level=1,
    initial_stock=22,
    lead_time=3,
    usage_per_parent=1,
    lot_size=40,
    scheduled_receipts=[],
)

MRP_LEVEL2_INPUT = MRPInput(
    name="Deska",
    bom_level=2,
    initial_stock=10,
    lead_time=1,
    usage_per_parent=1,
    lot_size=50,
    scheduled_receipts=[],
)
