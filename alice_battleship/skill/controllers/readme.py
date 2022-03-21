from flask import render_template
from alice_battleship.skill import app


@app.route("/")
def readme():
    return render_template("readme.html")
