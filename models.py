import requests, sys, json
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from settings import DB_NAME, DB_PASSWORD, DB_USER

database_path = "postgresql://{}:{}@{}/{}".format(
    DB_USER, DB_PASSWORD, "localhost:5432", DB_NAME
)

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

"""
initialize database with the 100 latest items

"""
def init_db():
    url = "https://hacker-news.firebaseio.com/v0/maxitem.json"
    response = requests.get(url)
    item_id = response.text
    print(item_id)
    for x in range(99):
        try:
            item_id = str(int(item_id) - x)
            url = f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json'
            response = requests.get(url)
            body = response.json()
            new_type = body.get('type', None)
            new_time = body.get('time', None)
            new_score = body.get('score', None)
            new_url = body.get('url', None)
            new_title = body.get('title', None)
            news = News(item_type=new_type, time=new_time, score=new_score, url=new_url, title=new_title)
            news.insert()
        except BaseException:
            print(sys.exc_info())

def sync_news():
    try:
        print("it works")
        url = "https://hacker-news.firebaseio.com/v0/maxitem.json"
        response = requests.get(url)
        item_id = response.text
        url = f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json'
        response = requests.get(url)
        body = response.json()
        new_type = body.get('type', None)
        new_time = body.get('time', None)
        new_score = body.get('score', None)
        new_url = body.get('url', None)
        new_title = body.get('title', None)
        news = News(item_type=new_type, time=new_time, score=new_score, url=new_url, title=new_title)
        news.insert()
    except BaseException:
        print(sys.exc_info())

"""
News

"""
class News(db.Model):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    item_type = Column(String)
    time = Column(Integer)
    score = Column(Integer)
    url = Column(String)
    title = Column(String)

    def __init__(self, item_type, time, score, url, title):
        self.item_type = item_type
        self.time = time
        self.score = score
        self.url = url
        self.title = title

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'item_type': self.item_type,
            'time': self.time,
            'score': self.score,
            'url': self.url,
            'title': self.title
            }