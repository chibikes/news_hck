import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_cors import CORS
from models import setup_db, TopNews, OtherNews, db, init_db, sync_news, get_api_item, insert_item
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

        items = db.session.query(TopNews).filter(TopNews.item_type == typ).order_by(desc(TopNews.time)).all()
        if len(items) ==0:
            items = db.session.query(OtherNews).filter(OtherNews.item_type == typ).order_by(desc(OtherNews.time)).all()
            
        formatted_items = [item.format() for item in items]

        if len(formatted_items[start:end]) == 0:
            abort(404)
        return jsonify({
            "sucess": True,
            "items": formatted_items[start:end],
            "total_items": len(formatted_items)
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

    @app.route('/items/<int:item_id>', methods=['DELETE'])
    def delete_item(item_id):
        if request.args.get('type') is None:
            item = TopNews.query.get(item_id)
        else:
            item = OtherNews.query.get(item_id)
        if item is None:
            abort(404)
        else:
            item.delete()
            return jsonify({
                'success': True,
                'id': item_id
            })
        
    @app.route('/items/<int:item_id>', methods=['GET'])
    def get_item(item_id):
        item = db.session.query(TopNews).filter_by(item_id=item_id).first()
        if item is None:
            item = db.session.query(OtherNews).filter_by(item_id=item_id).first()
        if item is None:
            abort(404)
        else:
            kids = item.kids
            kids_items = []
            for k in kids:
                kid = db.session.query(OtherNews).filter_by(item_id=k).first()
                if kid is not None:
                    kids_items.append(kid.format())
                else:
                    # later items are not in database
                    kids_items.append(get_api_item(k))
            return jsonify({
                'success': True,
                'id': item_id,
                'item': item.format(),
                'kids_items': kids_items
            })
        
    @app.route('/search/items', methods=['POST'])
    def search_items():
        print('it is happening')
        try:
            search_term = request.get_json().get('searchTerm')

            query_string = 'SELECT * FROM items WHERE title ILIKE \'%'
            sql = query_string + search_term + '%\''
            result = db.engine.execute(db.text(sql))
            items = result.fetchall()

            formatted_items = [{'id': item.item_id,
                                    'title': item.title,
                                    'text': item.text,
                                    'kids_count': item.kids_count
                                    } for item in items]
            
            query_string = 'SELECT * FROM items WHERE title ILIKE \'%'
            sql = query_string + search_term + '%\''
            result = db.engine.execute(db.text(sql))
            items = result.fetchall()

            formatted_items = [{'id': item.item_id,
                                    'title': item.title,
                                    'text': item.text,
                                    'kids_count': item.kids_count
                                    } for item in items]
            return jsonify({
                'success': True,
                'items': formatted_items,
                'total_items': len(formatted_items)
            })
        except BaseException:
            print(sys.exc_info())
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
    