from ..redis import Redis
from ..request import Request
from ..response import Response
from ..handled_exception import HandledException
from ..states import *
from .help import WIKI_BUTTON


START_GAME_PHRASES = ["готов", "начина", "поехал", "старт", "давай", "ок", "го"]


def handler(redis: Redis, req: Request, res: Response):
    name = redis.name
    state = redis.state

    # there is no `name` and no `state` -> new gamer
    if not name and not state:
        redis.state = ACQUAINTANCE
        res << "Привет! Давай сыграем! Как тебя зовут?"
        raise HandledException()

    # there is no `name`, but state is ACQUAINTANCE -> awaits gamer name
    if not name and state == ACQUAINTANCE:
        first_name = req.name
        if not first_name:
            res << "Не расслышала имя. Повтори, пожалуйста!"
        else:
            redis.state = AWAIT_START
            first_name = first_name.title()
            redis.name = first_name
            # fmt: off
            res << f"Приятно познакомиться, {first_name}. Я — Алиса.\n"\
                   f"Возьми листик в клетку и расставь свои корабли, согласно правилам игры. "\
                   f"Мы начнём по твоей готовности!"
            res += {"title": "Я готов", "hide": True}
            res += WIKI_BUTTON
            # fmt: on
        raise HandledException()

    # there is `name`, but no `state` -> old gamer, new game
    if name and not state:
        redis.state = AWAIT_START
        # fmt: off
        res << f"С возвращением, {name}!\n" \
               f"Возьми листик в клетку и расставь свои корабли, согласно правилам игры. " \
               f"Мы начнём по твоей готовности!"
        res += {"title": "Я готов", "hide": True}
        res += WIKI_BUTTON
        # fmt: on
        raise HandledException()

    # if there is `name` and `state` is AWAIT_START -> wait for "start" phrase
    if name and state == AWAIT_START:
        if any(phrase in req.utterance for phrase in START_GAME_PHRASES):
            redis.state = START_GAME
        else:
            res << "Начинаем? Я не поняла."
            res += {"title": "Я готов", "hide": True}
            res += WIKI_BUTTON
            raise HandledException()
