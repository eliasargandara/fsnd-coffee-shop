import os
import traceback
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization,true')
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET,PATCH,POST,DELETE,OPTIONS')
    return response


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks or appropriate status code
        indicating reason for failure
'''
@app.route('/drinks')
def retrieve_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks or appropriate status code
        indicating reason for failure
'''


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record or appropriate
        status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': (
            'The request was well-formed but could not be'
            ' processed due to semantic errors.')
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'The server does not recognize the url.'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'The HTTP method is not allowed for the requested url.'
    }), 405


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.error['code'],
        'message': error.error['description']
    }), error.status_code


@app.errorhandler(Exception)
def unexpected_error(error):
    print(traceback.format_exc())
    return jsonify({
        'success': False,
        'error': 500,
        'message': (
            'We apoligize. Our service seems to'
            ' have experienced an unexpected error.'
        )
    }), 500
