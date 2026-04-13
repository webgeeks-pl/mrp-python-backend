from __future__ import annotations

from dataclasses import dataclass

from input import GHP_LEVEL0_INPUT, MRP_LEVEL1_OSTRZE_INPUT




@dataclass
class GHPResult:
    weeks: int
    demand: list[int]
    production: list[int]
    available: list[int]
    initial_stock: int


@dataclass
class MRPResult:
    weeks: int
    gross_requirements: list[int]
    scheduled_receipts: list[int]
    projected_available: list[int]
    net_requirements: list[int]
    planned_order_releases: list[int]
    planned_order_receipts: list[int]
    lead_time: int
    lot_size: int
    bom_level: int
    initial_stock: int
    item_name: str

def validate_inputs(
    weeks: int,
    total_order: int,
    batches: list[tuple[int, int]],
    initial_stock: int,
    lead_time: int,
) -> None:
    if weeks <= 0:
        raise ValueError("Liczba tygodni planowania musi byc > 0.")
    if total_order <= 0:
        raise ValueError("Wielkosc zamowienia musi byc > 0.")
    if initial_stock < 0:
        raise ValueError("Liczba wyrobow gotowych na stanie musi byc >= 0.")
    if lead_time < 1:
        raise ValueError("Czas realizacji musi byc >= 1.")
    if not batches:
        raise ValueError("Lista partii nie moze byc pusta.")

    for week, qty in batches:
        if week < 1 or week > weeks:
            raise ValueError(f"Tydzien partii {week} musi byc z zakresu 1..{weeks}.")
        if qty <= 0:
            raise ValueError("Ilosc partii musi byc > 0.")

    total_batches = sum(qty for _, qty in batches)
    if total_batches != total_order:
        raise ValueError(
            "Suma partii musi byc rowna wielkosci zamowienia. "
            f"Podano {total_batches}, oczekiwano {total_order}."
        )


def calculate_ghp_level0(
    weeks: int,
    initial_stock: int,
    demand_by_week: list[int],
) -> GHPResult:
    demand = list(demand_by_week)
    production = [0] * weeks
    available = [0] * weeks

    prev_available = initial_stock
    for i in range(weeks):
        # Planowane przyjecie w tygodniu i pokrywa niedobor po uwzglednieniu zapasu.
        shortage = demand[i] - prev_available
        planned_receipt = shortage if shortage > 0 else 0

        production[i] = planned_receipt

        end_available = prev_available + planned_receipt - demand[i]

        available[i] = end_available
        prev_available = end_available

    return GHPResult(
        weeks=weeks,
        demand=demand,
        production=production,
        available=available,
        initial_stock=initial_stock,
    )


def format_row(label: str, values: list[str], cell_width: int, label_width: int) -> str:
    cells = " | ".join(f"{value:>{cell_width}}" for value in values)
    return f"| {label:<{label_width}} | {cells} |"


def print_ghp_table(result: GHPResult, lead_time: int) -> None:
    labels = ["tydzien", "przewidywany popyt", "produkcja", "dostepne"]
    weeks_labels = [str(i) for i in range(1, result.weeks + 1)]
    demand_labels = [str(v) if v != 0 else "" for v in result.demand]
    production_labels = [str(v) if v != 0 else "" for v in result.production]
    available_labels = [str(v) for v in result.available]

    all_cells = weeks_labels + demand_labels + production_labels + available_labels
    cell_width = max(2, max(len(cell) for cell in all_cells))
    label_width = max(len(label) for label in labels)
    separator = " | ".join("-" * cell_width for _ in range(result.weeks))

    print("\nGHP dla poziomu 0 (wyrob finalny)")
    print(format_row("tydzien", weeks_labels, cell_width=cell_width, label_width=label_width))
    print(f"| {'-' * label_width} | {separator} |")
    print(format_row("przewidywany popyt", demand_labels, cell_width=cell_width, label_width=label_width))
    print(format_row("produkcja", production_labels, cell_width=cell_width, label_width=label_width))
    print(format_row("dostepne", available_labels, cell_width=cell_width, label_width=label_width))
    print(f"na stanie = {result.initial_stock}")
    print(f"czas realizacji = {lead_time}")


def validate_mrp_inputs(
    weeks: int,
    usage_per_parent: int,
    initial_stock: int,
    lead_time: int,
    lot_size: int,
    scheduled_receipts_raw: list[tuple[int, int]],
) -> None:
    if usage_per_parent <= 0:
        raise ValueError("Zuzycie komponentu na wyrob nadrzedny musi byc > 0.")
    if initial_stock < 0:
        raise ValueError("Stan poczatkowy komponentu musi byc >= 0.")
    if lead_time < 1:
        raise ValueError("Czas realizacji komponentu musi byc >= 1.")
    if lot_size <= 0:
        raise ValueError("Wielkosc partii komponentu musi byc > 0.")

    for week, qty in scheduled_receipts_raw:
        if week < 1 or week > weeks:
            raise ValueError(f"Tydzien planowanego przyjecia {week} musi byc z zakresu 1..{weeks}.")
        if qty < 0:
            raise ValueError("Planowane przyjecia nie moga miec ujemnej ilosci.")


def aggregate_scheduled_receipts(weeks: int, receipts_raw: list[tuple[int, int]]) -> list[int]:
    receipts = [0] * weeks
    for week, qty in receipts_raw:
        receipts[week - 1] += qty
    return receipts


def calculate_mrp_level1(
    parent_production: list[int],
    usage_per_parent: int,
    initial_stock: int,
    lead_time: int,
    lot_size: int,
    scheduled_receipts: list[int],
    item_name: str,
    bom_level: int,
    ghp_lead_time: int = 1,
) -> MRPResult:
    weeks = len(parent_production)
    print(parent_production)
    # Shift parent production left by only GHP lead_time to get gross requirements
    shifted_production = [0] * weeks
    for idx in range(weeks):
        source_idx = idx + ghp_lead_time
        if source_idx < weeks:
            shifted_production[idx] = parent_production[source_idx]
    
    gross_requirements = [qty * usage_per_parent for qty in shifted_production]
    projected_available = [0] * weeks
    net_requirements = [0] * weeks
    planned_order_releases = [0] * weeks
    planned_order_receipts = [0] * weeks

    prev_available = initial_stock
    for i in range(weeks):
        available_before_demand = prev_available + scheduled_receipts[i] + planned_order_receipts[i]

        if gross_requirements[i] == 0:
            net_req = 0
            receipt = 0
        elif available_before_demand >= gross_requirements[i]:
            net_req = 0
            receipt = 0
        else:
            net_req = gross_requirements[i] - available_before_demand
            # Stala wielkosc partii: przy niedoborze uruchamiamy jedna partie.
            receipt = lot_size

            release_week = i - lead_time
            if release_week < 0:
                raise ValueError(
                    f"MRP dla {item_name}: brak czasu na realizacje zamowienia dla tygodnia {i + 1}."
                )
            planned_order_releases[release_week] += receipt
            planned_order_receipts[i] += receipt

        end_available = available_before_demand + receipt - gross_requirements[i]

        net_requirements[i] = net_req
        projected_available[i] = end_available
        prev_available = end_available

    return MRPResult(
        weeks=weeks,
        gross_requirements=gross_requirements,
        scheduled_receipts=scheduled_receipts,
        projected_available=projected_available,
        net_requirements=net_requirements,
        planned_order_releases=planned_order_releases,
        planned_order_receipts=planned_order_receipts,
        lead_time=lead_time,
        lot_size=lot_size,
        bom_level=bom_level,
        initial_stock=initial_stock,
        item_name=item_name,
    )


def print_mrp_table(result: MRPResult) -> None:
    labels = [
        "okres",
        "calk. zapotrz.",
        "planowane przyjecia",
        "przewidywane na stanie",
        "zapotrzebowanie netto",
        "planowane zamowienia",
        "plan. przyj. zamowien",
    ]
    weeks_labels = [str(i) for i in range(1, result.weeks + 1)]
    gross_labels = [str(v) if v != 0 else "" for v in result.gross_requirements]
    sched_labels = [str(v) if v != 0 else "" for v in result.scheduled_receipts]
    avail_labels = [str(v) for v in result.projected_available]
    net_labels = [str(v) if v != 0 else "" for v in result.net_requirements]
    release_labels = [str(v) if v != 0 else "" for v in result.planned_order_releases]
    receipt_labels = [str(v) if v != 0 else "" for v in result.planned_order_receipts]

    all_cells = (
        weeks_labels
        + gross_labels
        + sched_labels
        + avail_labels
        + net_labels
        + release_labels
        + receipt_labels
    )
    cell_width = max(2, max(len(cell) for cell in all_cells))
    label_width = max(len(label) for label in labels)
    separator = " | ".join("-" * cell_width for _ in range(result.weeks))

    print(f"\nMRP poziom 1: {result.item_name}")
    print(format_row("okres", weeks_labels, cell_width=cell_width, label_width=label_width))
    print(f"| {'-' * label_width} | {separator} |")
    print(format_row("calk. zapotrz.", gross_labels, cell_width=cell_width, label_width=label_width))
    print(format_row("planowane przyjecia", sched_labels, cell_width=cell_width, label_width=label_width))
    print(format_row("przewidywane na stanie", avail_labels, cell_width=cell_width, label_width=label_width))
    print(format_row("zapotrzebowanie netto", net_labels, cell_width=cell_width, label_width=label_width))
    print(format_row("planowane zamowienia", release_labels, cell_width=cell_width, label_width=label_width))
    print(format_row("plan. przyj. zamowien", receipt_labels, cell_width=cell_width, label_width=label_width))
    print(f"czas realizacji = {result.lead_time}")
    print(f"wielkosc partii = {result.lot_size}")
    print(f"poziom BOM = {result.bom_level}")
    print(f"na stanie = {result.initial_stock}")


def run() -> None:
    print("=== Symulacja GHP + MRP (poziom 1 Ostrze) ===")

    weeks = int(GHP_LEVEL0_INPUT["weeks"])
    total_order = int(GHP_LEVEL0_INPUT["total_order"])
    initial_stock = int(GHP_LEVEL0_INPUT["initial_stock"])
    lead_time = int(GHP_LEVEL0_INPUT["lead_time"])
    batches = [(int(week), int(qty)) for week, qty in GHP_LEVEL0_INPUT["batches"]]

    validate_inputs(
        weeks=weeks,
        total_order=total_order,
        batches=batches,
        initial_stock=initial_stock,
        lead_time=lead_time,
    )

    demand_by_week = [0] * weeks
    for week, qty in batches:
        demand_by_week[week - 1] += qty

    result = calculate_ghp_level0(
        weeks=weeks,
        initial_stock=initial_stock,
        demand_by_week=demand_by_week,
    )

    print_ghp_table(result, lead_time=lead_time)

    item_name = str(MRP_LEVEL1_OSTRZE_INPUT["name"])
    bom_level = int(MRP_LEVEL1_OSTRZE_INPUT["bom_level"])
    usage_per_parent = int(MRP_LEVEL1_OSTRZE_INPUT["usage_per_parent"])
    ostrze_initial_stock = int(MRP_LEVEL1_OSTRZE_INPUT["initial_stock"])
    ostrze_lead_time = int(MRP_LEVEL1_OSTRZE_INPUT["lead_time"])
    ostrze_lot_size = int(MRP_LEVEL1_OSTRZE_INPUT["lot_size"])
    scheduled_receipts_raw = [
        (int(week), int(qty)) for week, qty in MRP_LEVEL1_OSTRZE_INPUT["scheduled_receipts"]
    ]

    validate_mrp_inputs(
        weeks=weeks,
        usage_per_parent=usage_per_parent,
        initial_stock=ostrze_initial_stock,
        lead_time=ostrze_lead_time,
        lot_size=ostrze_lot_size,
        scheduled_receipts_raw=scheduled_receipts_raw,
    )

    scheduled_receipts = aggregate_scheduled_receipts(weeks=weeks, receipts_raw=scheduled_receipts_raw)

    mrp_result = calculate_mrp_level1(
        parent_production=result.production,
        usage_per_parent=usage_per_parent,
        initial_stock=ostrze_initial_stock,
        lead_time=ostrze_lead_time,
        lot_size=ostrze_lot_size,
        scheduled_receipts=scheduled_receipts,
        item_name=item_name,
        bom_level=bom_level,
        ghp_lead_time=lead_time,
    )

    print_mrp_table(mrp_result)


if __name__ == "__main__":
    try:
        run()
    except ValueError as exc:
        print(f"Blad danych wejsciowych: {exc}")
