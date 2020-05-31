import os
import sqlalchemy
from flask import Flask, jsonify, request, abort, flash, make_response
from models import setup_db, Users, Books, Exchange, db
from auth.auth import requires_auth, AuthError


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    setup_db(app)

    @app.route("/users", methods=['GET'])
    def get_users():

        users = Users.query.all()

        if not users:
            abort(make_response(jsonify(
                'No users exist at the moment, please add a user'
            )))

        result = {
            "success": True,
            "message": list(map(Users.long, users))
        }
        return jsonify(result)

    @app.route("/user", methods=['POST'])
    def create_user():
        try:
            new_user = request.get_json()
        except Exception as e:
            abort(make_response(jsonify({
                'message': 'Incorrect data'
            })))

        if all(k in new_user for k in ('name', 'city', 'zip_code', 'country')):
            users = Users(
                name=new_user['name'],
                zip_code=new_user['zip_code'],
                city=new_user['city'],
                country=new_user['country']
            )
            try:
                users.insert()
            except Exception as e:
                db.session.rollback()
                abort(404, e)

            result = {
                "success": True,
                "message": 'User ' + new_user['name'] + ' has been added successfully'
            }
            return jsonify(result)

        else:
            abort(make_response(jsonify({
                'message': 'You seem to have missed some data, Provide name, zip_code, city and country'
            })))

    @app.route("/user/<int:user_id>", methods=['DELETE'])
    @requires_auth('delete:user')
    def delete_user(valid, user_id):
        if valid:
            data = Users.query.get(user_id)

            if data:
                name = data.name
                try:
                    Users.delete(data)
                except Exception as e:
                    abort(404, e)
            else:
                abort(make_response(jsonify({
                    'message': 'User does not exist'
                }), 404))

            result = {
                "success": True,
                "message": name + ' has been deleted'

            }
            return jsonify(result)
        else:
            abort(401)

    @app.route('/books', methods=['POST', 'GET'])
    @requires_auth('add:book')
    def create_book(valid):
        if valid:
            if request.method == 'GET':
                books = Books.query.all()

                if not books:
                    abort(make_response(jsonify(
                        'No books added yet'
                    )))

                return jsonify({
                    'success': True,
                    'books': [Books.details(book) for book in books]
                })

            else:
                try:
                    new_book = request.get_json()
                except Exception as e:
                    abort(make_response(jsonify({
                        'error message': 'Incorrect data'
                    })))

                if all(k in new_book for k in ('title', 'author', 'user_id')):
                    book = Books(
                        title=new_book['title'],
                        author=new_book['author'],
                        created_by=new_book['user_id']
                    )
                    try:
                        book.insert()
                    except sqlalchemy.exc.IntegrityError as e:
                        abort(make_response(jsonify({'message': 'provided user does not exist'})))
                    except Exception as e:
                        db.session.rollback()
                        abort(404, e)

                    result = {
                        "success": True,
                        "message": 'book ' + new_book['title'] + ' has been added successfully'
                    }
                    return jsonify(result)
                else:
                    abort(make_response(jsonify({
                        'message': 'You seem to have missed some data: Provide title of the book, its author '
                                   'and user_id who created the book'
                    })))

                # TODO user legitimacy to be implemented

    @app.route('/request/<int:user_id>', methods=['POST'])
    @requires_auth('request:book')
    def request_book(valid, user_id):
        if valid:
            try:
                new_request = request.get_json()
            except Exception as e:
                abort(400, str(e))

            if all(k in new_request for k in ('lender_id', 'book_id')):
                exchange = Exchange(
                    requester_id=user_id,
                    # TODO - requester_id later to be picked from db using session user name
                    lender_id=new_request['lender_id'],
                    book_id=new_request['book_id'],
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
            else:
                abort(make_response(jsonify({
                    'success': False,
                    'message': 'You seem to have missed some data: Provide '
                               'requester_id(user_id of the requester), lender_id(book owner:user_id), '
                })))

    @app.route('/requests/<int:user_id>', methods=['GET'])
    def check_for_requests(user_id):

        # count = Exchange.query.filter(Exchange.status != 'approved').filter(Exchange.lender_id == 1).count()
        try:
            Users.query.filter(Users.user_id == user_id).one()
        except:
            abort(make_response(jsonify({
                'message': 'User does not exist'
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
                "success": True,
                "requests": list(map(Exchange.requests, data))
            })

    @app.route('/requests/<int:user_id>', methods=['PATCH'])
    def handle_requests(user_id):
        requests = Exchange.query.filter(Exchange.status != 'approved'). \
            filter(Exchange.lender_id == user_id).all()

        if not requests:
            abort(make_response(jsonify({'message': 'No requests for this user OR user does not exist',
                                         'success': False})))

        for req in requests:
            req.status = 'approved'
            try:
                Exchange.update(req)
            except Exception as e:
                db.session.rollback()
                abort(404, e)
            finally:
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

    @app.errorhandler(400)
    def unprocessable(error):
        return jsonify({
            "error": 400,
            "success": False,
            "message": str(error)
        }), 400

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
