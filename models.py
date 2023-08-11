import requests
import sys
from sqlalchemy import Column, String, Integer, Boolean
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
    item = db.session.query(TopNews).first()
    if item is None:
        print("initializing database...")
        url = "https://hacker-news.firebaseio.com/v0/maxitem.json"
        response = requests.get(url)
        item_id = response.text
        current_id = int(item_id)
        for x in range(99):
            try:
                url = f'https://hacker-news.firebaseio.com/v0/item/{current_id}.json'
                response = requests.get(url)
                body = response.json()
                news_type = body.get('type', None)
                news_time = body.get('time', None)
                news_url = body.get('url', None)
                news_title = body.get('title', None)
                parent = body.get('parent', None)
                news_text = body.get('text', None)
                news_id = body.get('id')
                news_kids = body.get('descendants', 0)

                if parent is None:
                    news = TopNews(item_id=news_id, item_type=news_type, time=news_time,
                                   is_from_api=True, url=news_url, title=news_title, text=news_text, kids=news_kids)
                else:
                    news = OtherNews(item_id=news_id, parent_id=parent, item_type=news_type, time=news_time,
                                     is_from_api=True, url=news_url, title=news_title, text=news_text, kids=news_kids)
                news.insert()
                current_id = int(news_id) - 1
            except BaseException:
                print(sys.exc_info())


def sync_news():
    print('scheduled database insert...')
    try:
        url = "https://hacker-news.firebaseio.com/v0/maxitem.json"
        response = requests.get(url)
        item_id = response.text
        url = f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json'
        response = requests.get(url)
        body = response.json()
        news_type = body.get('type', None)
        news_time = body.get('time', None)
        news_url = body.get('url', None)
        news_title = body.get('title', None)
        parent = body.get('parent', None)
        news_text = body.get('text', None)
        news_kids = body.get('descendants', 0)

        if parent is None:
            news = TopNews(item_id=int(item_id), item_type=news_type, time=news_time,
                           is_from_api=True, url=news_url, title=news_title, text=news_text, kids=news_kids)
        else:
            parent_item = db.session.query(TopNews).filter(parent_id="parent")
            if parent_item is None:
                parent_item = db.session.query(TopNews).filter(parent_id="parent")
            
            news = OtherNews(item_id=int(item_id), parent_id=parent, item_type=news_type,
                             time=news_time, is_from_api=True, url=news_url, title=news_title, text=news_text, kids=news_kids)
        news.insert()
        print('Next scheduled database insert in 5 minutes')
    except BaseException:
        print(sys.exc_info())


"""
News

"""


class TopNews(db.Model):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    item_type = Column(String)
    time = Column(Integer)
    is_from_api = Column(Boolean, default=True)
    url = Column(String)
    title = Column(String)
    text = Column(String)
    kids = Column(Integer)

    def __init__(self, item_id, item_type, time, is_from_api, url, title, text, kids):
        self.item_id = item_id
        self.item_type = item_type
        self.time = time
        self.is_from_api = is_from_api
        self.url = url
        self.title = title
        self.text = text
        self.kids = kids

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
            'item_id': self.item_id,
            'item_type': self.item_type,
            'time': self.time,
            'is_from_api': self.is_from_api,
            'url': self.url,
            'title': self.title,
            'text': self.text,
            'kids': self.kids
        }


class OtherNews(db.Model):
    __tablename__ = 'other_items'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    parent_id = Column(Integer)
    item_type = Column(String)
    time = Column(Integer)
    is_from_api = Column(Boolean, default=True)
    url = Column(String)
    title = Column(String)
    text = Column(String)
    kids = Column(Integer)

    def __init__(self, item_id, parent_id, item_type, time, is_from_api, url, title, text, kids):
        self.item_id = item_id
        self.parent_id = parent_id
        self.item_type = item_type
        self.time = time
        self.is_from_api = is_from_api
        self.url = url
        self.title = title
        self.text = text
        self.kids = kids

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
            'item_id': self.item_id,
            'parent_id': self.parent_id,
            'item_type': self.item_type,
            'time': self.time,
            'is_from_api': self.is_from_api,
            'url': self.url,
            'title': self.title,
            'text': self.text,
            'kids': self.kids
        }
