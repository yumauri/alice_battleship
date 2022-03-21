import random
from rich import print
from alice_battleship.skill.game import (
    new_game,
    torpedo_ai,
    torpedo_human,
    print_fields,
    parse_turn,
    get_turn,
    check_cheating,
    stringify_turn,
    parse_torpedo_result_response,
    check_end_game,
)
from alice_battleship.skill.game.constants import *
from alice_battleship.skill.game.exceptions import *


def next(turn):
    return AI if turn == HUMAN else HUMAN


def run():
    ai, human = new_game()
    turn = random.choice([AI, HUMAN])
    while True:
        print()

        if turn == HUMAN:
            print_fields(human, ai)

            print("\n[bold magenta]Ваш ход[/bold magenta]", end=": ")
            try:
                row, col = parse_turn(input())
            except KeyboardInterrupt:
                print("\n[bold magenta]Возвращайтесь![/bold magenta]")
                break

            if row is None or col is None:
                print("[red]Не могу разобрать ваш ход, повторите, пожалуйста[/red]")
                continue
            res = torpedo_ai(ai, row, col)
            if res == WRONG:
                print("[red]Похоже вы сюда уже стреляли, повторите, пожалуйста[/red]")
                continue
            if res == HIT:
                print("[blue]Попал![/blue]")
            elif res == SINK:
                print("[blue]Потопил :([/blue]")
            elif res == MISS:
                print("[blue]Мимо![/blue]")
                turn = next(turn)

        elif turn == AI:
            row, col = get_turn(human)
            cell = human[row][col]
            human[row][col] = TRY
            print_fields(human, ai)
            human[row][col] = cell

            print(
                "\n[bold blue]Мой ход[/bold blue]:", stringify_turn(row, col), end="  "
            )
            print("[bold magenta]???[/bold magenta]", end=": ")
            try:
                while (result := parse_torpedo_result_response(input())) == WRONG:
                    print("[red]Не могу разобрать, повторите, пожалуйста[/red]")
            except KeyboardInterrupt:
                print("\n[bold magenta]Возвращайтесь![/bold magenta]")
                break

            torpedo_human(human, row, col, result)
            try:
                check_cheating(human)
            except ImpossibleToSinkException:
                print(
                    "[bold red]Я должна была попасть или потопить этот корабль!\n"
                    "Возвращайтесь, когда захотите сыграть честно![/bold red]"
                )
                break
            except TooMany1CellShips:
                print(
                    "[bold red]У вас больше четырёх одно-палубных кораблей!\n"
                    "Возвращайтесь, когда захотите сыграть честно![/bold red]"
                )
                break
            except TooMany2CellShips:
                print(
                    "[bold red]У вас больше трёх двух-палубных кораблей!\n"
                    "Возвращайтесь, когда захотите сыграть честно![/bold red]"
                )
                break
            except TooMany3CellShips:
                print(
                    "[bold red]У вас больше двух трёх-палубных кораблей!\n"
                    "Возвращайтесь, когда захотите сыграть честно![/bold red]"
                )
                break
            except TooMany4CellShips:
                print(
                    "[bold red]У вас больше одного четырёх-палубного корабля!\n"
                    "Возвращайтесь, когда захотите сыграть честно![/bold red]"
                )
                break
            except TooLongHitShip:
                print(
                    "[bold red]Я должна была потопить этот корабль!\n"
                    "Возвращайтесь, когда захотите сыграть честно![/bold red]"
                )
                break
            except NoMoreEmptyCells:
                print(
                    "[bold red]Мне уже некуда стрелять!\n"
                    "Возвращайтесь, когда захотите сыграть честно![/bold red]"
                )
                break
            except TooLittleEmptyCellsLeft:
                print(
                    "[bold red]Оставшиеся корабли не поместятся в оставшемся месте!\n"
                    "Возвращайтесь, когда захотите сыграть честно![/bold red]"
                )
                break

            if result == MISS:
                turn = next(turn)

        if check_end_game(ai):
            print_fields(human, ai)
            print("[bold magenta]Вы победили![/bold magenta]")
            break

        if check_end_game(human):
            print_fields(human, ai)
            print("[bold magenta]Я победила![/bold magenta]")
            break
