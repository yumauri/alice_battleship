from flask import request
from alice_battleship.skill import app, redis_client
from .redis import Redis
from .request import Request
from .response import Response
from .handled_exception import HandledException
from .handlers import handle_dialog


@app.route("/talk", methods=["POST"])
def alice():
    req = Request(request.json)
    res = Response(request.json)
    redis = Redis(req)
    app.logger.debug("Request: %r", req)

    try:
        handle_dialog(redis, req, res)
    except HandledException:
        pass  # normal situation
    except Exception as err:
        res << "Что-то я запуталась..."
        app.logger.critical("Error: %r", err)

    app.logger.debug("Response: %r", res)
    return +res
