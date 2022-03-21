from rich import print
from .constants import *


def print_fields(left, right, open=False):
    letters = "[bold white]     А   Б   В   Г   Д   Е   Ж   З   И   К  [/bold white]"
    header = "   ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗"
    middle = "   ╟───┼───┼───┼───┼───┼───┼───┼───┼───┼───╢"
    bottom = "   ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝"
    spacing = " "

    print(letters + spacing + letters)
    print(header + spacing + header)
    for row in range(10):
        print(f"[bold white]{row + 1:>2}[/bold white] ║", end="")
        for col in range(10):
            cell = left[row][col]
            print(f" {print_cell(cell, True)} ", end="│" if col < 9 else "║")
        print(f" [bold white]{row + 1:>2}[/bold white]", end=spacing + "║")
        for col in range(10):
            cell = right[row][col]
            print(f" {print_cell(cell, open)} ", end="│" if col < 9 else "║")
        print(f" [bold white]{row + 1}[/bold white]")
        if row < 9:
            print(middle + spacing + middle)
    print(bottom + spacing + bottom)
    print(letters + spacing + letters)


def print_cell(cell, open=False):
    if cell == SHIP and open:
        return "█"
    if cell == VISIBLE_HALO or (cell == HALO and open):
        return "[black]·[/black]"
    if cell == HIT:
        return "[red]╳[/red]"
    if cell == SINK:
        return "[red]▒[/red]"
    if cell == MISS:
        return "⚬"
    if cell == TRY:
        return "[blue]?[/blue]"
    return " "
