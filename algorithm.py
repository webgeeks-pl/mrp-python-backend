from __future__ import annotations


from ghp import calculate_ghp, print_ghp_as_table, validate_ghp_input
from input2 import (
    GHP_INPUT,
    MRP_LEVEL1_0_INPUT,
    MRP_LEVEL1_1_INPUT,
    MRP_LEVEL2_INPUT,
)
from mrp import calculate_mrp, print_mrp_as_table, validate_mrp_input


def aggregate_scheduled_receipts(weeks: int, scheduled_receipts: list[tuple[int, int]]) -> list[int]:
    receipts = [0] * weeks
    for week, amount in scheduled_receipts:
        receipts[week - 1] += amount
    return receipts


def run(validate: bool = False):
    print("=== Symulacja GHP + MRP ===")

    weeks = int(GHP_INPUT.weeks)
    ghp_lead_time = int(GHP_INPUT.lead_time)

    demand_per_week = [0] * weeks
    for week, amount in GHP_INPUT.batches:
        demand_per_week[week - 1] += amount

    if validate:
        validate_ghp_input(ghp_input=GHP_INPUT)
        validate_mrp_input(mrp_input=MRP_LEVEL1_0_INPUT, weeks=weeks)
        validate_mrp_input(mrp_input=MRP_LEVEL1_1_INPUT, weeks=weeks)
        validate_mrp_input(mrp_input=MRP_LEVEL2_INPUT, weeks=weeks)

    ghp_result = calculate_ghp(
        ghp_input=GHP_INPUT,
        demand_per_week=demand_per_week,
    )

    print_ghp_as_table(ghp_result=ghp_result, lead_time=ghp_lead_time)

    agregated_scheduled_receipts_for_level1_0 = aggregate_scheduled_receipts(
        weeks=weeks,
        scheduled_receipts=MRP_LEVEL1_0_INPUT.scheduled_receipts
    )

    mrp_result_level1_0 = calculate_mrp(
        mrp_input=MRP_LEVEL1_0_INPUT,
        parent_production=ghp_result.production,
        scheduled_receipts=agregated_scheduled_receipts_for_level1_0,
        ghp_lead_time=ghp_lead_time,
    )

    print_mrp_as_table(mrp_result=mrp_result_level1_0)

    agregated_scheduled_receipts_for_level1_1 = aggregate_scheduled_receipts(
        weeks=weeks,
        scheduled_receipts=MRP_LEVEL1_1_INPUT.scheduled_receipts,
    )

    mrp_result_level1_1 = calculate_mrp(
        mrp_input=MRP_LEVEL1_1_INPUT,
        parent_production=ghp_result.production,
        scheduled_receipts=agregated_scheduled_receipts_for_level1_1,
        ghp_lead_time=ghp_lead_time,
    )

    print_mrp_as_table(mrp_result=mrp_result_level1_1)

    agregated_scheduled_receipts_for_level2 = aggregate_scheduled_receipts(
        weeks=weeks,
        scheduled_receipts=MRP_LEVEL2_INPUT.scheduled_receipts,
    )

    mrp_result_level2 = calculate_mrp(
        mrp_input=MRP_LEVEL2_INPUT,
        parent_production=mrp_result_level1_1.planned_orders,
        scheduled_receipts=agregated_scheduled_receipts_for_level2,
        ghp_lead_time=0,
    )

    print_mrp_as_table(mrp_result=mrp_result_level2)


def main():
    run(validate=True)


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"Błąd danych wejściowych: {exc}")
