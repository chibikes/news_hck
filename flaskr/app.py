import requests, sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, News, db, init_db, sync_news
from flask_apscheduler import APScheduler

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='sync_news', func=sync_news, trigger='interval', minutes=5)
    setup_db(app)
    init_db()
    scheduler.start()
    
    return app
    