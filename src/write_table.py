import csv
from dataclasses import dataclass


@dataclass
class Line:
    number: int
    symbol: str
    first_set: list[str]
    shift: bool
    error: bool
    pointer: int
    stack: bool
    end: bool


def write_table(table: list[Line]) -> None:
    with open("../table.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        for line in table:
            writer.writerow([
                line.number,
                line.symbol,
                " ".join(sorted(line.first_set)),
                "+" if line.shift else "-",
                "+" if line.error else "-",
                line.pointer,
                "+" if line.stack else "-",
                "+" if line.end else "-"
            ])
