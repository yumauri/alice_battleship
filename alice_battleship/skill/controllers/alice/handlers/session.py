import random
from ..redis import Redis
from ..request import Request
from ..response import Response
from ..handled_exception import HandledException
from ..states import *
from .help import URL_TEXT, get_url_button
from alice_battleship.skill.game import new_game


NEW_GAME_PHRASES = ["да", "хочу", "новую", "новая", "начина"]
END_GAME_PHRASES = ["не", "надоел", "конец", "заканчи", "хватит", "всё", "гг"]


def handler(redis: Redis, req: Request, res: Response):
    state = redis.state

    # if game already finished
    if state == AI_WIN or state == HUMAN_WIN:
        if any(phrase in req.utterance for phrase in END_GAME_PHRASES):
            res |= "Спасибо за игру, надеюсь тебе понравилось!"
            raise HandledException()

        elif any(phrase in req.utterance for phrase in NEW_GAME_PHRASES):
            redis.state = state = START_GAME

        else:
            res << "Игра уже закончана, хочешь сыграть ещё?"
            res += {"title": "Да", "hide": True}
            res += {"title": "Нет", "hide": True}
            raise HandledException()

    # start new game
    if state == START_GAME:
        redis.ai, redis.human = new_game()
        redis.state = state = random.choice([AI_TURN, HUMAN_TURN])

        res << f"Отлично!\n{URL_TEXT}\n"
        res += get_url_button(req)
        if state == HUMAN_TURN:
            res <<= "Жребий выбрал, что тебе ходить! Твой ход?"
            raise HandledException()
        else:
            res <<= "Жребий выбрал, что ходить первой буду я!\n"

    # continue game
    else:
        res << ""
