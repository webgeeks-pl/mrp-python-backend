from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from base import BaseInput

from format import format_row


@dataclass(frozen=True)
class GHPInput(BaseInput):
    weeks: int
    total_order: int
    batches: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class GHPResult:
    weeks: int
    demand: list[int]  # popyt
    production: list[int]  # produkcja
    available: list[int]  # dostepne
    initial_stock: int  # stan_poczatkowy


def validate_ghp_input(
    ghp_input: GHPInput
) -> None:
    if ghp_input.weeks <= 0:
        raise ValueError("Liczba tygodni planowania musi być > 0.")
    if ghp_input.total_order <= 0:
        raise ValueError("Wielkość zamówienia musi być > 0.")
    if ghp_input.initial_stock < 0:
        raise ValueError("Liczba wyrobów gotowych na stanie musi być >= 0.")
    if ghp_input.lead_time < 1:
        raise ValueError("Czas realizacji musi być >= 1.")
    if not ghp_input.batches:
        raise ValueError("Lista partii nie może być pusta.")

    for week, amount in ghp_input.batches:
        if week < 1 or week > ghp_input.weeks:
            raise ValueError(
                f"Tydzień partii {week} musi być z zakresu 1..{ghp_input.weeks}.")
        if amount <= 0:
            raise ValueError("Ilość partii musi być > 0.")

    total_amount_from_batches = sum(amount for _, amount in ghp_input.batches)
    if total_amount_from_batches != ghp_input.total_order:
        raise ValueError(
            "Suma partii musi być równa wielkości zamówienia. "
            f"Podano {total_amount_from_batches}, oczekiwano {ghp_input.total_order}."
        )


def calculate_ghp(
    ghp_input: GHPInput,
    demand_per_week: list[int],
) -> GHPResult:
    production = [0] * ghp_input.weeks
    available = [0] * ghp_input.weeks

    last_available = ghp_input.initial_stock
    for i in range(ghp_input.weeks):
        lacking = demand_per_week[i] - last_available
        planned_receipts = max(0, lacking)

        production[i] = planned_receipts

        ending_inventory = last_available + \
            planned_receipts - demand_per_week[i]

        available[i] = ending_inventory
        last_available = ending_inventory

    return GHPResult(
        weeks=ghp_input.weeks,
        demand=demand_per_week,
        production=production,
        available=available,
        initial_stock=ghp_input.initial_stock,
    )


def print_ghp_as_table(ghp_result: GHPResult, lead_time: int) -> None:
    labels = ["tydzień", "przewidywany popyt", "produkcja", "dostępne"]
    week_labels = [str(i) for i in range(1, ghp_result.weeks + 1)]
    demand_labels = [str(v) if v != 0 else "" for v in ghp_result.demand]
    production_labels = [
        str(v) if v != 0 else "" for v in ghp_result.production]
    available_labels = [str(v) for v in ghp_result.available]

    all_cells = week_labels + demand_labels + production_labels + available_labels
    cell_width = max(2, max(len(cell) for cell in all_cells))
    label_width = max(len(label) for label in labels)
    separator = " | ".join("-" * cell_width for _ in range(ghp_result.weeks))

    print("\nGHP dla poziomu 0 (wyrób finalny)")
    print(format_row("tydzień", week_labels, cell_width, label_width))
    print(f"| {'-' * label_width} | {separator} |")
    print(format_row("przewidywany popyt", demand_labels, cell_width, label_width))
    print(format_row("produkcja", production_labels, cell_width, label_width))
    print(format_row("dostepne", available_labels, cell_width, label_width))
    print(f"na stanie = {ghp_result.initial_stock}")
    print(f"czas realizacji = {lead_time}")
