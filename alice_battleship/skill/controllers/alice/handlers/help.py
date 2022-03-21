from flask import current_app
from ..redis import Redis
from ..request import Request
from ..response import Response
from ..handled_exception import HandledException


TRIGGER_PHRASES = ["помощь", "что ты умеешь", "правила"]
URL_PHRASES = ["игра", "игру", "посмотреть"]

# fmt: off
HELP_TEXT = \
    "Классическая игра в «Морской бой», русская версия.\n" \
    "Игра ведётся на поле 10×10 клеток, на котором размещаются 10 кораблей:\n" \
    " - 1 линкор длиной четыре клетки,\n" \
    " - 2 крейсера длиной по три клетки,\n" \
    " - 3 эсминца длиной по две клетки,\n" \
    " - и 4 торпедные катера по одной клетке каждый.\n" \
    "При размещении корабли не могут касаться друг друга сторонами и углами.\n" \
    "Цель игры: потопить все корабли противника."
URL_TEXT = "Нашу игру в реальном времени можно посмотреть по ссылке."
# fmt: on

URL = "https://ru.wikipedia.org/wiki/%D0%9C%D0%BE%D1%80%D1%81%D0%BA%D0%BE%D0%B9_%D0%B1%D0%BE%D0%B9_(%D0%B8%D0%B3%D1%80%D0%B0)"
WIKI_BUTTON = {"title": "Википедия", "url": URL, "hide": True}


def get_url_button(req: Request):
    return {
        "title": "Ссылка",
        "url": f"{current_app.config['BASE_URL']}/games/{req.session_id}",
        "hide": True,
    }


def handler(redis: Redis, req: Request, res: Response):
    if any(phrase in req.utterance for phrase in TRIGGER_PHRASES):
        res << HELP_TEXT
        res += WIKI_BUTTON
        raise HandledException()

    if "википедия" in req.utterance:
        res << "Я подожду"
        res += WIKI_BUTTON
        raise HandledException()

    if any(phrase in req.utterance for phrase in URL_PHRASES):
        res << URL_TEXT
        res += get_url_button(req)
        raise HandledException()

    if "ссылка" in req.utterance:
        res << "Я подожду"
        res += get_url_button(req)
        raise HandledException()
