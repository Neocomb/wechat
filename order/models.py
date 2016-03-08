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


class Lesson(mongo.Document):

    num = mongo.StringField()
    subject = mongo.StringField()
    name = mongo.StringField()

    @classmethod
    def load_by_subject(cls, subject):
        return cls.query.filter({"subject": subject})

    @classmethod
    def load_all(cls):
        return cls.query.all()


class Token(mongo.Document)
    key = mongo.StringField()