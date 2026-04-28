from typing import Literal, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from algorithm import aggregate_scheduled_receipts
from ghp import GHPInput, calculate_ghp, validate_ghp_input
from mrp import MRPInput, calculate_mrp, validate_mrp_input


app = FastAPI(
    title="GHP/MRP API",
    description="API for processing Gross and Net Requirements Planning calculations",
    version="1.0.0"
)


class GHPInputRequest(BaseModel):
    id: str
    type: Literal["GHP"] = "GHP"
    name: str
    bom_level: int
    initial_stock: int
    lead_time: int
    weeks: int
    total_order: int
    batches: list[tuple[int, int]]


class MRPInputRequest(BaseModel):
    id: str
    parent_id: str
    type: Literal["MRP"] = "MRP"
    name: str
    bom_level: int
    initial_stock: int
    lead_time: int
    usage_per_parent: int
    lot_size: int
    scheduled_receipts: list[tuple[int, int]] = Field(default_factory=list)


def convert_ghp_to_table(ghp_result, item_name: str, bom_level: int):
    weeks = [str(i) for i in range(1, ghp_result.weeks + 1)]
    return {
        "type": "GHP",
        "rows": [
            {"rowLabel": "tydzien", "values": weeks},
            {"rowLabel": "przewidywany popyt", "values": ghp_result.demand},
            {"rowLabel": "produkcja", "values": ghp_result.production},
            {"rowLabel": "dostepne", "values": ghp_result.available},
        ],
        "metadata": {
            "itemName": item_name,
            "bomLevel": bom_level,
            "initialStock": ghp_result.initial_stock,
            "weeks": ghp_result.weeks,
        },
    }


def convert_mrp_to_table(mrp_result):
    weeks = [str(i) for i in range(1, mrp_result.weeks + 1)]
    return {
        "type": "MRP",
        "rows": [
            {"rowLabel": "okres", "values": weeks},
            {"rowLabel": "całk. zapotrz.", "values": mrp_result.total_demand},
            {"rowLabel": "planowane przyjęcia",
                "values": mrp_result.scheduled_receipts},
            {"rowLabel": "przewidywane na stanie",
                "values": mrp_result.expected_stock},
            {"rowLabel": "zapotrzebowanie netto", "values": mrp_result.net_demand},
            {"rowLabel": "planowane zamówienia",
                "values": mrp_result.planned_orders},
            {"rowLabel": "plan. przyj. zamówień",
                "values": mrp_result.planned_order_acceptance},
        ],
        "metadata": {
            "itemName": mrp_result.item_name,
            "bomLevel": mrp_result.bom_level,
            "initialStock": mrp_result.initial_stock,
            "leadTime": mrp_result.lead_time,
            "lotSize": mrp_result.lot_size,
            "weeks": mrp_result.weeks,
        },
    }


@app.post("/process")
def process_results(inputs: list[Union[GHPInputRequest, MRPInputRequest]]):
    if not inputs:
        raise HTTPException(
            status_code=400, detail="Inputs array cannot be empty")

    processed: list[dict] = []
    parent_production_by_id: dict[str, list[int]] = {}
    ghp_lead_time_by_id: dict[str, int] = {}

    sorted_inputs = sorted(inputs, key=lambda item: item.bom_level)

    try:
        for input_item in sorted_inputs:
            if isinstance(input_item, GHPInputRequest):
                demand_per_week = [0] * input_item.weeks
                for week, amount in input_item.batches:
                    demand_per_week[week - 1] += amount

                ghp_input = GHPInput(
                    name=input_item.name,
                    bom_level=input_item.bom_level,
                    initial_stock=input_item.initial_stock,
                    lead_time=input_item.lead_time,
                    weeks=input_item.weeks,
                    total_order=input_item.total_order,
                    batches=input_item.batches,
                )

                validate_ghp_input(ghp_input)
                ghp_result = calculate_ghp(
                    ghp_input=ghp_input,
                    demand_per_week=demand_per_week,
                )

                processed.append({
                    "source": input_item,
                    "table": convert_ghp_to_table(
                        ghp_result=ghp_result,
                        item_name=input_item.name,
                        bom_level=input_item.bom_level,
                    ),
                })
                parent_production_by_id[input_item.id] = ghp_result.production
                ghp_lead_time_by_id[input_item.id] = ghp_input.lead_time

            elif isinstance(input_item, MRPInputRequest):
                if input_item.parent_id not in parent_production_by_id:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Parent item with id '{input_item.parent_id}' not found "
                            "or processed after its child."
                        ),
                    )

                parent_production = parent_production_by_id[input_item.parent_id]
                weeks = len(parent_production)
                scheduled_receipts = aggregate_scheduled_receipts(
                    weeks=weeks,
                    scheduled_receipts=input_item.scheduled_receipts,
                )
                current_ghp_lead_time = (
                    ghp_lead_time_by_id.get(input_item.parent_id, 0)
                    if input_item.bom_level == 1
                    else 0
                )

                mrp_input = MRPInput(
                    name=input_item.name,
                    bom_level=input_item.bom_level,
                    initial_stock=input_item.initial_stock,
                    lead_time=input_item.lead_time,
                    usage_per_parent=input_item.usage_per_parent,
                    lot_size=input_item.lot_size,
                    scheduled_receipts=input_item.scheduled_receipts,
                )

                validate_mrp_input(mrp_input, weeks=weeks)
                mrp_result = calculate_mrp(
                    mrp_input=mrp_input,
                    parent_production=parent_production,
                    scheduled_receipts=scheduled_receipts,
                    ghp_lead_time=current_ghp_lead_time,
                )

                processed.append(
                    {"source": input_item, "table": convert_mrp_to_table(mrp_result)})
                parent_production_by_id[input_item.id] = mrp_result.planned_orders

        input_position = {id(item): index for index, item in enumerate(inputs)}
        processed.sort(key=lambda item: input_position[id(item["source"])])
        return {"results": [item["table"] for item in processed]}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
