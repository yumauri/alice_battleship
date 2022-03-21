import json
from flask import render_template, jsonify, abort
from alice_battleship.skill import app, redis_client
from alice_battleship.skill.game.constants import *
from .alice.states import *


@app.route("/games.json")
def games_json():
    return jsonify(get_games_data())


@app.route("/games/")
def games():
    return render_template("games.html", data=json.dumps(get_games_data()))


@app.route("/games/<session_id>.json")
def game_json(session_id):
    data = get_one_game_data(session_id)
    if data is None:
        abort(404)
    return jsonify(data)


@app.route("/games/<session_id>")
def game(session_id):
    data = get_one_game_data(session_id)
    if data is None:
        abort(404)
    return render_template("game.html", data=json.dumps(data))


def get_games_data():
    redis_keys = redis_client.keys("alice:*:*:state")
    keys = [key.decode("utf-8").split(":") for key in redis_keys]
    names = {}
    in_progress_games = {}
    finished_games = {}
    for key in keys:
        _, application_id, session_id, __ = key
        name = redis_client.get(f"alice:{application_id}")
        state = redis_client.get(f"alice:{application_id}:{session_id}:state")
        update = redis_client.get(f"alice:{application_id}:{session_id}:update")
        if name and state and update:
            name = name.decode("utf-8")
            state = int(state)
            update = int(update)
            if application_id not in names:
                names[application_id] = name
            if state in [AI_WIN, HUMAN_WIN, ABORTED, CHEATING]:
                if application_id not in finished_games:
                    finished_games[application_id] = []
                finished_games[application_id].append([session_id, f"{state}", update])
            else:
                if application_id not in in_progress_games:
                    in_progress_games[application_id] = []
                in_progress_games[application_id].append(
                    [session_id, f"{state}", update]
                )

    return {
        "names": names,
        "in_progress": in_progress_games,
        "finished": finished_games,
        "states": {
            f"{NEW}": "NEW",
            f"{ACQUAINTANCE}": "ACQUAINTANCE",
            f"{AWAIT_START}": "AWAIT_START",
            f"{START_GAME}": "START_GAME",
            f"{AI_TURN}": "AI_TURN",
            f"{HUMAN_TURN}": "HUMAN_TURN",
            f"{AI_WIN}": "AI_WIN",
            f"{HUMAN_WIN}": "HUMAN_WIN",
            f"{ABORTED}": "ABORTED",
            f"{CHEATING}": "CHEATING",
        },
    }


def get_one_game_data(session_id):
    redis_keys = redis_client.keys(f"alice:*:{session_id}:state")
    if not redis_keys or len(redis_keys) > 1:
        return None

    application_id = redis_keys[0].decode("utf-8").split(":")[1]

    name = redis_client.get(f"alice:{application_id}")
    ai = redis_client.get(f"alice:{application_id}:{session_id}:ai")
    human = redis_client.get(f"alice:{application_id}:{session_id}:human")
    state = redis_client.get(f"alice:{application_id}:{session_id}:state")
    update = redis_client.get(f"alice:{application_id}:{session_id}:update")

    name = name.decode("utf-8")
    if ai and human:
        ai = json.loads(ai.decode("utf-8"))
        human = json.loads(human.decode("utf-8"))
    else:
        ai = [[EMPTY] * 10 for _ in range(10)]
        human = [[EMPTY] * 10 for _ in range(10)]
    state = int(state)
    update = int(update)

    # hide ai field ships location
    for row in range(10):
        for col in range(10):
            if ai[row][col] == SHIP or ai[row][col] == HALO:
                ai[row][col] = EMPTY

    return {
        "name": name,
        "ai": ai,
        "human": human,
        "state": state,
        "update": update,
        "states": {
            f"{NEW}": "NEW",
            f"{ACQUAINTANCE}": "ACQUAINTANCE",
            f"{AWAIT_START}": "AWAIT_START",
            f"{START_GAME}": "START_GAME",
            f"{AI_TURN}": "AI_TURN",
            f"{HUMAN_TURN}": "HUMAN_TURN",
            f"{AI_WIN}": "AI_WIN",
            f"{HUMAN_WIN}": "HUMAN_WIN",
            f"{ABORTED}": "ABORTED",
            f"{CHEATING}": "CHEATING",
        },
        "values": {
            "SHIP": SHIP,
            "VISIBLE_HALO": VISIBLE_HALO,
            "HALO": HALO,
            "HIT": HIT,
            "SINK": SINK,
            "MISS": MISS,
            "TRY": TRY,
        },
    }
