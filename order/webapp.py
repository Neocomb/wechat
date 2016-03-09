import os
from flask import Flask
from order.models import mongo

app = Flask(__name__, instance_relative_config=True,
            instance_path=os.path.dirname(__file__))

app.config.update({
    'SECRET_KEY': 'yaling-is-a-beautiful-girl',
})


def setup():
    app.config.from_pyfile("../debug.cfg")

    mongo.init_app(app)
    from . import handlers
