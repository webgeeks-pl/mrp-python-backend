def format_row(label: str, values: list[str], cell_width: int, label_width: int) -> str:
    cells = " | ".join(f"{value:>{cell_width}}" for value in values)
    return f"| {label:<{label_width}} | {cells} |"
