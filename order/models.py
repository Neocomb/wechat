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

    @classmethod
    def load_subject(cls):
        return cls.query.distinct(cls.subject).all()


class Room(mongo.Document):
    building = mongo.StringField()
    room = mongo.StringField()

    @classmethod
    def load_by_building(cls, building):
        return cls.query.filter({"building": building})

    @classmethod
    def load_all(cls):
        return cls.query.all()


class Order(mongo.Document):
    week = mongo.StringField()
    day = mongo.StringField()
    time = mongo.StringField()
    classroom = mongo.StringField()
    subject = mongo.StringField()
    lesson = mongo.StringField()
    lesson_num = mongo.StringField()
    # order_create_time = mongo.DateTimeField()
    # order_book_time = mongo.DateTimeField()
    user = mongo.StringField()

    @classmethod
    def load_user(cls, username):
        return cls.query.filter(cls.user == username).all()
