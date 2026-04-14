from typing import Union, Optional, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from ghp_level0 import oblicz_ghp_poziom0, GHPResult


# Input Request models (same as input.py format)
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


# Calculated Result models (for display)
class GHPResultRequest(BaseModel):
    type: Literal["GHP"] = "GHP"
    tygodnie: int
    popyt: list[int]
    produkcja: list[int]
    dostepne: list[int]
    stan_poczatkowy: int


class MRPResultRequest(BaseModel):
    type: Literal["MRP"] = "MRP"
    tygodnie: int
    calkowite_zapotrzebowanie: list[int]
    planowane_przyjecia: list[int]
    przewidywane_na_stanie: list[int]
    zapotrzebowanie_netto: list[int]
    planowane_zamowienia: list[int]
    planowane_przyjecie_zamowien: list[int]
    czas_realizacji: int
    wielkosc_partii: int
    poziom_bom: int
    stan_poczatkowy: int
    nazwa_elementu: str


# Response models
class TableResponse(BaseModel):
    type: str
    rows: list[dict]
    metadata: dict


class ProcessResultsResponse(BaseModel):
    results: list[TableResponse]


# Create FastAPI app
app = FastAPI(
    title="GHP/MRP API",
    description="API for processing Gross and Net Requirements Planning calculations",
    version="1.0.0"
)


def calculate_ghp_from_input(ghp_input: GHPInputRequest) -> GHPResultRequest:
    """Calculate GHP from input data"""
    # Build demand array from batches
    popyt = [0] * ghp_input.weeks
    for tydzien, ilosc in ghp_input.batches:
        popyt[tydzien - 1] += ilosc
    
    # Calculate GHP
    wynik = oblicz_ghp_poziom0(
        tygodnie=ghp_input.weeks,
        stan_poczatkowy=ghp_input.initial_stock,
        popyt_po_tygodniach=popyt,
    )
    
    return GHPResultRequest(
        type="GHP",
        tygodnie=wynik.tygodnie,
        popyt=wynik.popyt,
        produkcja=wynik.produkcja,
        dostepne=wynik.dostepne,
        stan_poczatkowy=wynik.stan_poczatkowy,
    )


def calculate_mrp_from_input(mrp_input: MRPInputRequest, parent_production: list[int]) -> MRPResultRequest:
    """Calculate MRP from input data and parent production"""
    tygodnie = len(parent_production)
    
    # Calculate total requirement
    calkowite_zapotrzebowanie = [p * mrp_input.usage_per_parent for p in parent_production]
    
    # Scheduled receipts array
    planowane_przyjecia = [0] * tygodnie
    for tydzien, ilosc in mrp_input.scheduled_receipts:
        if tydzien > 0 and tydzien <= tygodnie:
            planowane_przyjecia[tydzien - 1] = ilosc
    
    # Simple MRP calculation
    przewidywane_na_stanie = []
    zapotrzebowanie_netto = []
    planowane_zamowienia = []
    planowane_przyjecie_zamowien = [0] * tygodnie
    
    available = mrp_input.initial_stock
    
    for i in range(tygodnie):
        available = available + planowane_przyjecia[i] - calkowite_zapotrzebowanie[i]
        przewidywane_na_stanie.append(max(0, available))
        
        net_demand = max(0, calkowite_zapotrzebowanie[i] - (available + planowane_przyjecia[i]))
        zapotrzebowanie_netto.append(net_demand)
        
        # Order in multiples of lot size
        if net_demand > 0:
            order_qty = ((net_demand - 1) // mrp_input.lot_size + 1) * mrp_input.lot_size
        else:
            order_qty = 0
        planowane_zamowienia.append(order_qty)
    
    return MRPResultRequest(
        type="MRP",
        tygodnie=tygodnie,
        calkowite_zapotrzebowanie=calkowite_zapotrzebowanie,
        planowane_przyjecia=planowane_przyjecia,
        przewidywane_na_stanie=przewidywane_na_stanie,
        zapotrzebowanie_netto=zapotrzebowanie_netto,
        planowane_zamowienia=planowane_zamowienia,
        planowane_przyjecie_zamowien=planowane_przyjecie_zamowien,
        czas_realizacji=mrp_input.lead_time,
        wielkosc_partii=mrp_input.lot_size,
        poziom_bom=mrp_input.bom_level,
        stan_poczatkowy=mrp_input.initial_stock,
        nazwa_elementu=mrp_input.name,
    )


def convert_ghp_to_table(ghp: GHPResultRequest) -> TableResponse:
    """Convert GHP result to table format"""
    okresy = [str(i) for i in range(1, ghp.tygodnie + 1)]
    rows = [
        {
            "row_label": "tydzien",
            "values": okresy,
        },
        {
            "row_label": "przewidywany popyt",
            "values": ghp.popyt,
        },
        {
            "row_label": "produkcja",
            "values": ghp.produkcja,
        },
        {
            "row_label": "dostepne",
            "values": ghp.dostepne,
        },
    ]
    
    return TableResponse(
        type="GHP",
        rows=rows,
        metadata={
            "Stan Poczatkowy": ghp.stan_poczatkowy,
            "Liczba Tygodni": ghp.tygodnie,
        }
    )


def convert_mrp_to_table(mrp: MRPResultRequest) -> TableResponse:
    """Convert MRP result to table format"""
    okresy = [str(i) for i in range(1, mrp.tygodnie + 1)]
    rows = [
        {
            "row_label": "okres",
            "values": okresy,
        },
        {
            "row_label": "calk. zapotrz.",
            "values": mrp.calkowite_zapotrzebowanie,
        },
        {
            "row_label": "planowane przyjecia",
            "values": mrp.planowane_przyjecia,
        },
        {
            "row_label": "przewidywane na stanie",
            "values": mrp.przewidywane_na_stanie,
        },
        {
            "row_label": "zapotrzebowanie netto",
            "values": mrp.zapotrzebowanie_netto,
        },
        {
            "row_label": "planowane zamowienia",
            "values": mrp.planowane_zamowienia,
        },
        {
            "row_label": "plan. przyj. zamowien",
            "values": mrp.planowane_przyjecie_zamowien,
        },
    ]
    
    return TableResponse(
        type="MRP",
        rows=rows,
        metadata={
            "Nazwa Elementu": mrp.nazwa_elementu,
            "Poziom BOM": mrp.poziom_bom,
            "Stan Poczatkowy": mrp.stan_poczatkowy,
            "Czas Realizacji": mrp.czas_realizacji,
            "Wielkosc Partii": mrp.wielkosc_partii,
            "Liczba Tygodni": mrp.tygodnie,
        }
    )


@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint"""
    return {
        "message": "GHP/MRP API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process": "Process array of GHP/MRP results and return table-formatted data"
        }
    }


@app.post(
    "/process",
    response_model=ProcessResultsResponse,
    tags=["Processing"],
    summary="Process GHP and MRP inputs",
    description="Accepts an array of GHP or MRP input objects and returns them formatted as tables suitable for frontend display"
)
def process_results(
    inputs: list[Union[GHPInputRequest, MRPInputRequest]]
):
    """
    Process an array of GHP or MRP input objects.
    
    Each object in the array should be either:
    - A GHP input with type='GHP' and batches, weeks, etc.
    - An MRP input with type='MRP' and usage_per_parent, lot_size, etc.
    
    Returns table-formatted data with columns and rows ready for frontend display.
    """
    if not inputs:
        raise HTTPException(status_code=400, detail="Inputs array cannot be empty")
    
    processed = []
    
    # Store parent production demands by id
    # GHP -> produkcja
    # MRP -> planowane_zamowienia 
    parent_productions = {}
    
    # Sort inputs by bom_level to ensure parents are computed before children
    try:
        sorted_inputs = sorted(inputs, key=lambda x: x.bom_level)
    except Exception:
        sorted_inputs = inputs
        
    for input_item in sorted_inputs:
        if isinstance(input_item, GHPInputRequest):
            # Calculate GHP
            ghp_result = calculate_ghp_from_input(input_item)
            processed.append((input_item.id, convert_ghp_to_table(ghp_result)))
            
            # The production becomes the demand source for its children
            parent_productions[input_item.id] = ghp_result.produkcja
            
        elif isinstance(input_item, MRPInputRequest):
            if input_item.parent_id not in parent_productions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Parent item with id '{input_item.parent_id}' not found or processed after its child."
                )
            
            # Calculate MRP using the specific parent's production
            mrp_result = calculate_mrp_from_input(input_item, parent_productions[input_item.parent_id])
            processed.append((input_item.id, convert_mrp_to_table(mrp_result)))
            
            # This item's planned orders become the demand source for its children
            parent_productions[input_item.id] = mrp_result.planowane_zamowienia
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid input type. Must be GHP or MRP."
            )
            
    # Reorder processed results back to the original order submitted by the user
    original_order_map = {item_id: table for item_id, table in processed}
    final_processed = [original_order_map[item.id] for item in inputs if item.id in original_order_map]
    
    return ProcessResultsResponse(results=final_processed)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
