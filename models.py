import requests
import sys
from sqlalchemy import Column, String, Integer, Boolean, ARRAY
from flask_sqlalchemy import SQLAlchemy
from settings import DB_NAME, DB_PASSWORD, DB_USER

database_path = "postgresql://{}:{}@{}/{}".format(
    DB_USER, DB_PASSWORD, "localhost:5432", DB_NAME
)

db = SQLAlchemy()

BASE_URL = 'https://hacker-news.firebaseio.com/v0'

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
        # get latest jobs and stories first since 
        # comments are infintely greater than stories instead of using maxItem endpoints
        url = f'{BASE_URL}/topstories.json'
        response = requests.get(url)
        body = response.json()
        ids = body
        for x in range(50):
            insert_item(ids[x])
        url = f"{BASE_URL}/maxitem.json"
        response = requests.get(url)
        item_id = response.text
        current_id = int(item_id)
        for x in range(50):
            try:
                insert_item(current_id)
                current_id = current_id - 1
                print(current_id)
            except BaseException:
                print(sys.exc_info())


def sync_news():
    print('scheduled database insert...')
    try:
        url = f'{BASE_URL}/topstories.json'
        response = requests.get(url)
        body = response.json()
        ids = body
        insert_item(ids[0])
        url = f"{BASE_URL}/maxitem.json"
        response = requests.get(url)
        item_id = response.text
        insert_item(item_id)
        print('Next scheduled database insert in 5 minutes')
    except BaseException:
        print(sys.exc_info())


def insert_item(item_id):
    try:
        url = f'{BASE_URL}/item/{item_id}.json'
        response = requests.get(url)
        body = response.json()
        news_type = body.get('type', None)
        news_time = body.get('time', None)
        news_url = body.get('url', None)
        news_title = body.get('title', None)
        parent = body.get('parent', None)
        news_text = body.get('text', None)
        news_kids_count = body.get('descendants', 0)
        news_kids = body.get('kids', None)
        
        if parent is None:
            present_item = db.session.query(TopNews).filter_by(item_id=parent).first()
            if present_item is None: 
                news = TopNews(item_id=int(item_id), item_type=news_type, time=news_time,
                            is_from_api=True, url=news_url, title=news_title, text=news_text, kids=news_kids, kids_count=news_kids_count)
                news.insert()
            else:
                present_item.kids_count = news_kids_count
                present_item.kids = news_kids
                present_item.insert()
        else:
            parent_item = db.session.query(TopNews).filter_by(item_id=parent).first()
            if parent_item is None:
                parent_item = db.session.query(
                    OtherNews).filter_by(item_id=parent).first()
            if parent_item is not None:
                if item_id not in parent_item.kids:
                # update kids and kids_count
                    parent_item.kids.append(item_id)
                    parent_item.kids_count = len(parent_item.kids)
                    parent_item.insert()

            news = OtherNews(item_id=int(item_id), parent_id=parent, item_type=news_type,
                             time=news_time, is_from_api=True, url=news_url, title=news_title, text=news_text, kids=news_kids, kids_count=news_kids_count)
            news.insert()
    except BaseException:
        print(sys.exc_info())

def get_api_item(item_id):
    url = f'{BASE_URL}/item/{item_id}.json'
    response = requests.get(url)
    body = response.json()
    news_type = body.get('type', None)
    news_time = body.get('time', None)
    news_url = body.get('url', None)
    news_title = body.get('title', '')
    parent = body.get('parent', None)
    news_text = body.get('text', None)
    news_kids_count = body.get('descendants', 0)
    news_kids = body.get('kids', None)

    return {
        'type': news_type,
        'news_time': news_time,
        'news_url': news_url,
        'news_title': news_title,
        'news_text': news_text
    }



"""
News

"""


class TopNews(db.Model):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, unique=True)
    item_type = Column(String)
    time = Column(Integer)
    is_from_api = Column(Boolean, default=True)
    url = Column(String)
    title = Column(String)
    text = Column(String)
    kids = Column(ARRAY(Integer))
    kids_count = Column(Integer)

    def __init__(self, item_id, item_type, time, is_from_api, url, title, text, kids, kids_count):
        self.item_id = item_id
        self.item_type = item_type
        self.time = time
        self.is_from_api = is_from_api
        self.url = url
        self.title = title
        self.text = text
        self.kids = kids
        self.kids_count = kids_count

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
            'kids': self.kids,
            'kids_count': self.kids_count
        }


class OtherNews(db.Model):
    __tablename__ = 'other_items'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, unique=True)
    parent_id = Column(Integer)
    item_type = Column(String)
    time = Column(Integer)
    is_from_api = Column(Boolean, default=True)
    url = Column(String)
    title = Column(String)
    text = Column(String)
    kids = Column(ARRAY(Integer))
    kids_count = Column(Integer)

    def __init__(self, item_id, parent_id, item_type, time, is_from_api, url, title, text, kids, kids_count):
        self.item_id = item_id
        self.parent_id = parent_id
        self.item_type = item_type
        self.time = time
        self.is_from_api = is_from_api
        self.url = url
        self.title = title
        self.text = text
        self.kids = kids
        self.kids_count = kids_count

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
            'kids': self.kids,
            'kids_count': self.kids_count
        }
