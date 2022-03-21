import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from . import app, redis_client
from .controllers.alice.states import *


def get_games():
    games = []
    redis_keys = redis_client.keys("alice:*:*:update")
    keys = [key.decode("utf-8").split(":") for key in redis_keys]
    for key in keys:
        _, application_id, session_id, __ = key
        state = redis_client.get(f"alice:{application_id}:{session_id}:state")
        update = redis_client.get(f"alice:{application_id}:{session_id}:update")
        if state and update:
            games.append((application_id, session_id, int(state), int(update)))
    return games


def abort_long_awaited_games():
    app.logger.debug("Abort long awaited games")

    now = int(time.time() * 1000)
    games = get_games()
    for application_id, session_id, state, update in games:
        if (
            state not in [AI_WIN, HUMAN_WIN, ABORTED, CHEATING]
            and now - update > 30 * 60 * 1000  # 30 minutes
        ):
            app.logger.debug(f"Abort {application_id}:{session_id}")
            redis_client.set(f"alice:{application_id}:{session_id}:state", ABORTED)


def clean_old_games():
    app.logger.debug("Clean old games")

    now = int(time.time() * 1000)
    games = get_games()
    for application_id, session_id, state, update in games:
        if (
            state in [AI_WIN, HUMAN_WIN, ABORTED, CHEATING]
            and now - update > 3 * 60 * 60 * 1000  # 3 hours
        ):
            app.logger.debug(f"Clean {application_id}:{session_id}")
            redis_client.delete(f"alice:{application_id}:{session_id}:ai")
            redis_client.delete(f"alice:{application_id}:{session_id}:human")
            redis_client.delete(f"alice:{application_id}:{session_id}:coords")
            redis_client.delete(f"alice:{application_id}:{session_id}:state")
            redis_client.delete(f"alice:{application_id}:{session_id}:update")


@app.before_first_request
def init_scheduler():
    # initial cleaning
    abort_long_awaited_games()
    clean_old_games()

    # setup scheduler and jobs
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=abort_long_awaited_games, trigger="interval", minutes=11)
    scheduler.add_job(func=clean_old_games, trigger="interval", minutes=31)

    # startup scheduler
    scheduler.start()

    # shutdown scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
