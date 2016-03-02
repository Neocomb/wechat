from datetime import datetime
from flask_mongoalchemy import MongoAlchemy
from mongoalchemy.document import Index

mongo = MongoAlchemy()

class User(mongo.Document):
    username = mongo.StringField()
    password = mongo.StringField()
    ctime = mongo.DateTimeField(default=datetime.now())

    primary_key = Index().ascending(username).unique(True)

    @classmethod
    def load_one(cls, username, password):
        return cls.query.filter({"username": username, "password": password}).first()
