import requests, sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from flask_cors import CORS
from models import setup_db, TopNews, OtherNews, db, init_db, sync_news
from flask_apscheduler import APScheduler

ITEMS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='sync_news', func=sync_news, trigger='interval', minutes=5)
    scheduler.add_job(id='init_db', func=init_db)
    scheduler.start()

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route('/items', methods=['GET'])
    def get_items():
        page = request.args.get('page', 1, type=int)
        typ = request.args.get('type')
        start = (page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        if typ is None:
            items = db.session.query(TopNews).order_by(desc(TopNews.time))
        else:
            items = db.session.query(OtherNews).filter(OtherNews.item_type == "typ").order_by(desc(OtherNews.time))
            
        formatted_items = [item.format() for item in items]

        if len(formatted_items[start:end]) == 0:
            abort(404)
        return jsonify({
            "sucess": True,
            "items": formatted_items[start:end],
            "total_items": len(formatted_items[start:end])
        })
    
    @app.route('/items', methods=['POST'])
    def create_item():
        try:
            body = request.get_json()
            type_of_item = body.get('type', None)
            item_time = body.get('time', None)
            item_url = body.get('url', None)
            item_title = body.get('title', None)

            item = TopNews(
                item_type=type_of_item,
                time=item_time,
                is_from_api=False,
                url=item_url,
                title=item_title)
            item.insert()

            return jsonify({
                'success': True,
            })
        except BaseException:
            abort(422)
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "Success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "Success": False,
            "error": 422,
            "message": "cannot process"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "Success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "Success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405
    

    return app
    