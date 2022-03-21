import random
from .constants import *


def new_game():
    ai = new_field()
    human = new_field()
    place_ships(ai)
    return ai, human


def new_field():
    return [[EMPTY] * 10 for _ in range(10)]


def place_ships(field):
    # 1 battleship - 4 cells
    # 2 cruisers - 3 cells
    # 3 destroyers - 2 cells
    # 4 torpedo boats - 1 cell
    for z in range(4, 0, -1):  # size of the ships
        for _ in range(5 - z):  # count of the ships
            while not place_one_ship(field, z):
                pass


def fill_surroundings(field, row, col, *, condition=EMPTY, fill_with):
    for drow, dcol in SURROUNDINGS:
        if (
            0 <= row + drow <= 9
            and 0 <= col + dcol <= 9
            and field[row + drow][col + dcol] == condition
        ):
            field[row + drow][col + dcol] = fill_with


def place_one_ship(field, size):
    dx, dy = random.choice(DIRECTIONS)
    ix = x = random.randint(0, 9 - dx * (size - 1))
    iy = y = random.randint(0, 9 - dy * (size - 1))

    # check place
    for i in range(size):
        if field[x][y] != EMPTY:
            return False
        x += dx
        y += dy

    # place new ship
    x, y = ix, iy
    for i in range(size):
        field[x][y] = SHIP
        x += dx
        y += dy

    # draw halo
    x, y = ix, iy
    for i in range(size):
        fill_surroundings(field, x, y, condition=EMPTY, fill_with=HALO)
        x += dx
        y += dy

    return True


def torpedo_ai(field, row, col):
    cell = field[row][col]
    if cell == MISS or cell == HIT or cell == SINK:
        return WRONG
    if field[row][col] != SHIP:
        field[row][col] = MISS
        return MISS

    def still_alive(x, y, dx, dy):
        if 0 <= x + dx <= 9 and 0 <= y + dy <= 9:
            c = field[x + dx][y + dy]
            if c == SHIP:
                return True
            if c == HIT:
                return still_alive(x + dx, y + dy, dx, dy)

    def sink(x, y, dx, dy):
        if 0 <= x + dx <= 9 and 0 <= y + dy <= 9:
            if field[x + dx][y + dy] == HIT:
                field[x + dx][y + dy] = SINK
                fill_surroundings(
                    field, x + dx, y + dy, condition=HALO, fill_with=VISIBLE_HALO
                )
                sink(x + dx, y + dy, dx, dy)

    field[row][col] = HIT
    if not any(
        [
            still_alive(row, col, -1, 0),
            still_alive(row, col, +1, 0),
            still_alive(row, col, 0, -1),
            still_alive(row, col, 0, +1),
        ]
    ):
        field[row][col] = SINK
        fill_surroundings(field, row, col, condition=HALO, fill_with=VISIBLE_HALO)
        sink(row, col, -1, 0)
        sink(row, col, +1, 0)
        sink(row, col, 0, -1)
        sink(row, col, 0, +1)
        return SINK

    return HIT


def torpedo_human(field, row, col, result):
    field[row][col] = result

    def sink(x, y, dx, dy):
        if 0 <= x + dx <= 9 and 0 <= y + dy <= 9:
            if field[x + dx][y + dy] == HIT:
                field[x + dx][y + dy] = SINK
                fill_surroundings(
                    field, x + dx, y + dy, condition=EMPTY, fill_with=HALO
                )
                sink(x + dx, y + dy, dx, dy)

    if result == SINK:
        fill_surroundings(field, row, col, condition=EMPTY, fill_with=HALO)
        sink(row, col, -1, 0)
        sink(row, col, +1, 0)
        sink(row, col, 0, -1)
        sink(row, col, 0, +1)


def check_end_game(field):
    yet_to_sink = 20  # 1 * 4 + 2 * 3 + 3 * 2 + 4 * 1
    for row in range(10):
        for col in range(10):
            cell = field[row][col]
            if cell == SHIP:
                return False
            if cell == SINK:
                yet_to_sink -= 1
    return yet_to_sink == 0
