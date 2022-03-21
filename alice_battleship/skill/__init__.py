import os
from flask import Flask
from flask_redis import FlaskRedis


# create Flask application
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
    BASE_URL=os.environ.get("BASE_URL", "http://localhost:5000"),
    REDIS_URL=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
)

# create redis client
redis_client = FlaskRedis(app)


# add all controllers
# here is the circular imports, because each controller imports `app`, to use decorators,
# and while in general this is a bad idea, Flask documentation recommends this way for small applications:
# https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
# and because of circular imports we have to import this line *after* creating `app`,
# even if it is against PEP8
import alice_battleship.skill.controllers  # noqa

# initialize scheduler after app creation as well,
# because of circular imports
import alice_battleship.skill.scheduler  # noqa


# run dev server, this is not used in production, just for development and testing
def run():
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host="0.0.0.0", port=1380, debug=True)
