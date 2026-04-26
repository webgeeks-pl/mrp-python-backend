from __future__ import annotations

from dataclasses import dataclass, field

from base import BaseInput

from format import format_row


@dataclass(frozen=True)
class MRPInput(BaseInput):
    usage_per_parent: int
    lot_size: int
    scheduled_receipts: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class MRPResult:
    weeks: int
    total_demand: list[int]  # calkowite_zapotrzebowanie
    scheduled_receipts: list[int]  # planowane_przyjecia
    expected_stock: list[int]  # przewidywane_na_stanie
    net_demand: list[int]  # zapotrzebowanie_netto
    planned_orders: list[int]  # planowane_zamowienia
    planned_order_acceptance: list[int]  # planowane_przyjecie_zamowien
    lead_time: int  # czas_realizacji
    lot_size: int  # wielkosc_partii
    bom_level: int  # poziom_bom
    initial_stock: int  # stan_poczatkowy
    item_name: str


def validate_mrp_input(mrp_input: MRPInput, weeks: int) -> None:
    if mrp_input.usage_per_parent <= 0:
        raise ValueError("Zużycie komponentu na wyrób nadrzędny musi być > 0.")
    if mrp_input.initial_stock < 0:
        raise ValueError("Stan początkowy komponentu musi być >= 0.")
    if mrp_input.lead_time < 1:
        raise ValueError("Czas realizacji komponentu musi być >= 1.")
    if mrp_input.lot_size <= 0:
        raise ValueError("Wielkość partii komponentu musi być > 0.")

    for week, amount in mrp_input.scheduled_receipts:
        if week < 1 or week > weeks:
            raise ValueError(
                f"Tydzień planowanego przyjęcia {week} musi być z zakresu 1..{weeks}.")
        if amount < 0:
            raise ValueError(
                "Planowane przyjęcia nie mogą mieć ujemnej ilości.")


def calculate_mrp(mrp_input: MRPInput, parent_production: list[int], scheduled_receipts: list[int], ghp_lead_time: int) -> MRPResult:
    weeks = len(parent_production)

    # Przesuniecie produkcji rodzica w lewo o tylko czas_realizacji_ghp aby uzyskac calkowite zapotrzebowanie
    offset_production = [0] * weeks
    for week in range(weeks):
        source_index = week + ghp_lead_time
        if source_index < weeks:
            offset_production[week] = parent_production[source_index]

    total_demand = [
        ilosc * mrp_input.usage_per_parent for ilosc in offset_production]
    expected_stock = [0] * weeks
    net_demand = [0] * weeks
    planned_orders = [0] * weeks
    planned_order_acceptance = [0] * weeks

    last_available = mrp_input.initial_stock
    for i in range(weeks):
        available_before_demand = last_available + \
            scheduled_receipts[i] + planned_order_acceptance[i]

        if total_demand[i] == 0:
            net_damand = 0
            order = 0
        elif available_before_demand >= total_demand[i]:
            net_damand = 0
            order = 0
        else:
            net_damand = total_demand[i] - available_before_demand
            # Stała wielkość partii: przy niedoborze uruchamiamy jedna partie.
            order = mrp_input.lot_size

            start_week = i - mrp_input.lead_time
            if start_week < 0:
                raise ValueError(
                    f"MRP dla {mrp_input.name}: brak czasu na realizacje zamówienia dla {i + 1} tygodnia."
                )
            planned_orders[start_week] += order
            planned_order_acceptance[i] += order

        ending_inventory = available_before_demand + order - total_demand[i]

        net_demand[i] = net_damand
        expected_stock[i] = ending_inventory
        last_available = ending_inventory

    return MRPResult(
        weeks=weeks,
        total_demand=total_demand,
        scheduled_receipts=scheduled_receipts,
        expected_stock=expected_stock,
        net_demand=net_demand,
        planned_orders=planned_orders,
        planned_order_acceptance=planned_order_acceptance,
        lead_time=mrp_input.lead_time,
        lot_size=mrp_input.lot_size,
        bom_level=mrp_input.bom_level,
        initial_stock=mrp_input.initial_stock,
        item_name=mrp_input.name,
    )


def print_mrp_as_table(mrp_result: MRPResult) -> None:
    labels = [
        "okres",
        "całk. zapotrz.",
        "planowane przyjęcia",
        "przewidywane na stanie",
        "zapotrzebowanie netto",
        "planowane zamówienia",
        "plan. przyj. zamówień",
    ]
    week_labels = [str(i) for i in range(1, mrp_result.weeks + 1)]
    demand_labels = [str(v) if v != 0 else "" for v in mrp_result.total_demand]
    scheduled_receipt_labels = [
        str(v) if v != 0 else "" for v in mrp_result.scheduled_receipts]
    expected_stock_labels = [str(v) for v in mrp_result.expected_stock]
    net_demand_labels = [
        str(v) if v != 0 else "" for v in mrp_result.net_demand]
    planned_orders_labels = [
        str(v) if v != 0 else "" for v in mrp_result.planned_orders]
    planned_order_acceptance_labels = [
        str(v) if v != 0 else "" for v in mrp_result.planned_order_acceptance]

    all_cells = (
        week_labels
        + demand_labels
        + scheduled_receipt_labels
        + expected_stock_labels
        + net_demand_labels
        + planned_orders_labels
        + planned_order_acceptance_labels
    )
    cell_width = max(2, max(len(cell) for cell in all_cells))
    label_width = max(len(label) for label in labels)
    separator = " | ".join("-" * cell_width for _ in range(mrp_result.weeks))

    print(f"\nMRP poziom {mrp_result.bom_level}: {mrp_result.item_name}")
    print(format_row(labels[0], week_labels, cell_width, label_width))
    print(f"| {'-' * label_width} | {separator} |")
    print(format_row(labels[1], demand_labels, cell_width, label_width))
    print(format_row(
        labels[2], scheduled_receipt_labels, cell_width, label_width))
    print(format_row(labels[3], expected_stock_labels,
          cell_width, label_width))
    print(format_row(labels[4], net_demand_labels, cell_width, label_width))
    print(format_row(labels[5], planned_orders_labels,
          cell_width, label_width))
    print(format_row(
        labels[6], planned_order_acceptance_labels, cell_width, label_width))
    print(f"czas realizacji = {mrp_result.lead_time}")
    print(f"wielkosc partii = {mrp_result.lot_size}")
    print(f"poziom BOM = {mrp_result.bom_level}")
    print(f"na stanie = {mrp_result.initial_stock}")
