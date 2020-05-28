import os
from flask import Flask, jsonify, request, abort, flash, make_response
from models import setup_db, Users, Books, Exchange, db
from auth.auth import requires_auth, AuthError


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    setup_db(app)

    @app.route("/users", methods=['GET'])
    def get_users():

        result = {
            "success": True,
            "message": list(map(Users.long, Users.query.all()))
        }
        return jsonify(result)

    @app.route("/user", methods=['POST'])
    def create_user():
        new_user = request.get_json()

        users = Users(
            name=new_user['name'],
            zip_code=new_user['zip_code'],
            city=new_user['city'],
            country=new_user['country']
        )

        users.insert()

        result = {
            "success": True,
            "message": 'User ' + new_user['name'] + ' has been added successfully'
        }
        return jsonify(result)

    @app.route("/user/<int:user_id>", methods=['DELETE'])
    def delete_user(user_id):
        data = Users.query.get(user_id)
        name = data.name
        if data:
            Users.delete(data)
        else:
            raise abort(404)

        result = {
            "success": True,
            "message": name + ' has been deleted'

        }
        return jsonify(result)

    @app.route('/books', methods=['POST', 'GET'])
    @requires_auth('add:book')
    def create_book(valid):
        if valid:
            if request.method == 'GET':
                return jsonify({
                    'books': [Books.details(book) for book in Books.query.all()]
                })

            else:
                new_book = request.get_json()

                # TODO user legitimacy to be implemented

                book = Books(
                    title=new_book['title'],
                    author=new_book['author'],
                    created_by=new_book['user_id']
                )
                try:
                    book.insert()
                except Exception as e:
                    db.session.rollback()
                    abort(404, e)

                result = {
                    "success": True,
                    "message": 'book ' + new_book['title'] + ' has been added successfully'
                }
                return jsonify(result)
        else:
            abort(404)

    @app.route('/request', methods=['POST'])
    @requires_auth('request-book')
    def request_book(valid):
        if valid:
            try:
                data = request.get_json()
            except Exception as e:
                abort(400, str(e))

            exchange = Exchange(
                requester_id=data['requester_id'],
                # TODO - requester_id later to be picked from db using session user name
                lender_id=data['lender_id'],
                book_id=data['book_id'],
                status='pending for approval'
            )

            try:
                exchange.insert()
            except Exception as e:
                abort(404, str(e))

            result = {
                "success": True,
                "message": 'request submitted successfully'
            }

            return jsonify(result)

    @app.route('/requests/<int:user_id>', methods=['GET'])
    def check_for_requests(user_id):

        # count = Exchange.query.filter(Exchange.status != 'approved').filter(Exchange.lender_id == 1).count()
        try:
            Users.query.filter(Users.user_id == user_id).one()
        except:
            abort(make_response(jsonify({
                'message': 'User does not exist',
                'advice': 'Know your user'
            }), 404))

        try:
            data = Exchange.query.filter(Exchange.status != 'approved'). \
                filter(Exchange.lender_id == user_id).all()
        except Exception as e:
            abort(404, e)
        if not data:
            return jsonify({
                'message': 'No pending requests found for user'
            })
        else:
            return jsonify({
                "requests": list(map(Exchange.requests, data))
            })

    @app.route('/requests/<int:user_id>', methods=['PATCH'])
    def handle_requests(user_id):
        requests = Exchange.query.filter(Exchange.status != 'approved'). \
            filter(Exchange.lender_id == user_id).one_or_none()

        requests.status = 'approved'

        Exchange.update(requests)

        return jsonify({
            "success": True,
            "message": "Your requests are approved"
        })

    @app.errorhandler(404)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": str(error)
        }), 404

    @app.errorhandler(401)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": str(error)
        }), 401

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
