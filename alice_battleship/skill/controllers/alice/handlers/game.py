from ..redis import Redis
from ..request import Request
from ..response import Response
from ..handled_exception import HandledException
from ..states import *

from alice_battleship.skill.game import (
    torpedo_ai,
    torpedo_human,
    check_cheating,
    parse_turn,
    get_turn,
    stringify_turn,
    parse_torpedo_result_response,
    check_end_game,
)
from alice_battleship.skill.game.constants import *
from alice_battleship.skill.game.exceptions import *


def check_win(redis: Redis, res: Response, ai, human):
    if check_end_game(ai):
        res <<= "Ты победил! Хочешь сыграть ещё?"
        res += {"title": "Хочу!", "hide": True}
        res += {"title": "Не хочу", "hide": True}
        redis.state = HUMAN_WIN
        raise HandledException()

    if check_end_game(human):
        res <<= "Я победила! Сыграем ещё?"
        res += {"title": "Давай!", "hide": True}
        res += {"title": "Хватит", "hide": True}
        redis.state = AI_WIN
        raise HandledException()


def check_for_cheater(redis: Redis, res: Response, human):
    cheater = False
    try:
        check_cheating(human)
    except ImpossibleToSinkException:
        res |= (
            "Я должна была попасть или потопить этот корабль!\n"
            + "Возвращайся, когда захочешь сыграть честно!"
        )
        cheater = True
    except TooMany1CellShips:
        res |= (
            "У тебя больше четырёх одно-палубных кораблей!\n"
            + "Возвращайся, когда захочешь сыграть честно!"
        )
        cheater = True
    except TooMany2CellShips:
        res |= (
            "У тебя больше трёх двух-палубных кораблей!\n"
            + "Возвращайся, когда захочешь сыграть честно!"
        )
        cheater = True
    except TooMany3CellShips:
        res |= (
            "У тебя больше двух трёх-палубных кораблей!\n"
            + "Возвращайся, когда захочешь сыграть честно!"
        )
        cheater = True
    except TooMany4CellShips:
        res |= (
            "У тебя больше одного четырёх-палубного корабля!\n"
            + "Возвращайся, когда захочешь сыграть честно!"
        )
        cheater = True
    except TooLongHitShip:
        res |= (
            "Я должна была потопить этот корабль!\n"
            + "Возвращайся, когда захочешь сыграть честно!"
        )
        cheater = True
    except NoMoreEmptyCells:
        res |= (
            "Мне уже некуда стрелять!\n" + "Возвращайся, когда захочешь сыграть честно!"
        )
        cheater = True
    except TooLittleEmptyCellsLeft:
        res |= (
            "Оставшиеся корабли не поместятся в оставшемся месте!\n"
            + "Возвращайся, когда захочешь сыграть честно!"
        )
        cheater = True

    if cheater:
        redis.state = CHEATING
        raise HandledException()


def handler(redis: Redis, req: Request, res: Response):
    state = redis.state
    ai, human = redis.ai, redis.human
    check_win(redis, res, ai, human)

    if state == AI_TURN:
        coords = redis.coords

        # my turn, calculate new coords and save them in session
        if not coords:
            row, col = get_turn(human)
            human_readable = stringify_turn(row, col)
            redis.coords = human_readable
            human[row][col] = TRY

            res <<= f"Мой ход: {human_readable}"
            res += {"title": "Мимо", "hide": True}
            res += {"title": "Ранила :(", "hide": True}
            res += {"title": "Потопила!", "hide": True}

            redis.human = human

        # my turn, get human response
        else:
            result = parse_torpedo_result_response(req.utterance)
            if result == WRONG:
                res << "Не могу разобрать, повтори, пожалуйста..."
                res += {"title": "Мимо", "hide": True}
                res += {"title": "Ранила :(", "hide": True}
                res += {"title": "Потопила!", "hide": True}
                return

            row, col = parse_turn(coords)
            human[row][col] = EMPTY
            del redis.coords
            torpedo_human(human, row, col, result)
            redis.human = human

            check_for_cheater(redis, res, human)
            check_win(redis, res, ai, human)

            if result == MISS:
                res << "Твой ход?"
                redis.state = HUMAN_TURN
            else:
                handler(redis, req, res)

    if state == HUMAN_TURN:
        row, col = parse_turn(req.utterance)

        if row is None or col is None:
            res << "Не понимаю, повтори, пожалуйста..."
            return

        result = torpedo_ai(ai, row, col)
        redis.ai = ai

        if result == WRONG:
            res << "Похоже, сюда уже стреляли, повтори, пожалуйста"

        elif result == HIT:
            res << "Попал! "
            check_win(redis, res, ai, human)

        elif result == SINK:
            res << "Потопил! "
            check_win(redis, res, ai, human)

        elif result == MISS:
            res << "Мимо!\n"
            redis.state = AI_TURN
            handler(redis, req, res)
