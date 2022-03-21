import random
from .constants import *
from .exceptions import *


def get_turn(field):
    # find first HIT cell and try to done the job
    for row in range(10):
        for col in range(10):
            if field[row][col] == HIT:
                return try_to_sink(field, row, col)

    # otherwise just hit random empty cell
    return try_random(field)


def try_random(field):
    empties = []
    for row in range(10):
        for col in range(10):
            if field[row][col] == EMPTY:
                empties.append((row, col))
    return random.choice(empties)


def try_to_sink(field, row, col):
    # helper to get field value with boundaries check
    def f(r, c):
        return field[r][c] if 0 <= r < 10 and 0 <= c < 10 else WRONG

    # helper to get first empty cell in direction
    def get_target_in_direction(r, c, dr, dc):
        while f(r, c) == HIT:
            r += dr
            c += dc
        return r, c

    location = UNKNOWN
    if f(row, col - 1) == HIT or f(row, col + 1) == HIT:
        location = HORIZONTAL
    elif f(row - 1, col) == HIT or f(row + 1, col) == HIT:
        location = VERTICAL

    targets = []
    if location == HORIZONTAL or location == UNKNOWN:
        dr, dc = DIRECTIONS[HORIZONTAL]
        targets.append(get_target_in_direction(row, col, dr, dc))
        targets.append(get_target_in_direction(row, col, -dr, -dc))
    if location == VERTICAL or location == UNKNOWN:
        dr, dc = DIRECTIONS[VERTICAL]
        targets.append(get_target_in_direction(row, col, dr, dc))
        targets.append(get_target_in_direction(row, col, -dr, -dc))
    targets = list(filter(lambda pos: f(*pos) == EMPTY, targets))

    return random.choice(targets) if targets else None


def check_cheating(field):
    #
    # check hit ships, which are impossible to sink
    #

    for row in range(10):
        for col in range(10):
            if field[row][col] == HIT:
                if try_to_sink(field, row, col) is None:
                    raise ImpossibleToSinkException()

    #
    # check sank ships
    #

    # helper to get ship (sank or hit) length
    def ship_length(f, r, c, v):
        if 0 <= r < 10 and 0 <= c < 10 and f[r][c] == v:
            f[r][c] = -v
            return (
                1
                + ship_length(f, r - 1, c, v)
                + ship_length(f, r + 1, c, v)
                + ship_length(f, r, c - 1, v)
                + ship_length(f, r, c + 1, v)
            )
        return 0

    sank = []
    f = [[cell for cell in row] for row in field]
    for row in range(10):
        for col in range(10):
            if f[row][col] == SINK:
                sank.append(ship_length(f, row, col, SINK))

    if sank.count(1) > 4:
        raise TooMany1CellShips()
    if sank.count(2) > 3:
        raise TooMany2CellShips()
    if sank.count(3) > 2:
        raise TooMany3CellShips()
    if sank.count(4) > 1:
        raise TooMany4CellShips()

    hit = []
    for row in range(10):
        for col in range(10):
            if f[row][col] == HIT:
                hit.append(ship_length(f, row, col, HIT))

    if (
        (hit.count(4) > 0)
        or (hit.count(3) > 0 and sank.count(4) == 1)
        or (hit.count(2) > 0 and sank.count(4) + sank.count(3) == 3)
        or (hit.count(1) > 0 and sank.count(4) + sank.count(3) + sank.count(2) == 6)
    ):
        raise TooLongHitShip()

    #
    # check left empty fields
    #

    left = sum([sum([cell == EMPTY for cell in row]) for row in field])
    if left == 0:
        raise NoMoreEmptyCells()

    if left < 20 - (sum(sank) + sum(hit)):
        raise TooLittleEmptyCellsLeft()
