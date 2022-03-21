from ..redis import Redis
from ..request import Request
from ..response import Response
from .help import handler as handle_help
from .name import handler as handle_name
from .session import handler as handle_session
from .game import handler as handle_game


def handle_dialog(redis: Redis, req: Request, res: Response):
    # required commands for moderation
    # https://yandex.ru/dev/dialogs/alice/doc/publish.html#moderation-checks
    handle_help(redis, req, res)

    # handle user name
    handle_name(redis, req, res)

    # game itself
    handle_session(redis, req, res)
    handle_game(redis, req, res)
