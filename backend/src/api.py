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


class InvalidInput(Exception):
    def __init__(self, input_errors):
        self.input_errors = input_errors


def validate_create_drink_input(data):
    attribute_required = 'The attribute \"{}\" is required.'
    expected_string = 'Expected \"{}\" to be a string.'
    expected_integer = 'Expected \"{}\" to be an integer.'
    expected_objects_array = 'Expected \"{}\" to be an array of objects.'

    input_errors = []
    if 'title' not in data:
        input_errors.append({
            'attribute': 'title',
            'type': 'attribute_required',
            'message': attribute_required.format('title')
        })
    elif type(data['title']) is not str:
        input_errors.append({
            'attribute': 'title',
            'type': 'invalid_type',
            'message': expected_string.format('title')
        })

    if 'recipe' not in data:
        input_errors.append({
            'attribute': 'recipe',
            'type': 'attribute_required',
            'message': attribute_required.format('recipe')
        })
    elif type(data['recipe']) is not list:
        input_errors.append({
            'attribute': 'recipe',
            'type': 'invalid_type',
            'message': expected_objects_array.format('recipe')
        })
    else:
        for index, item in enumerate(data['recipe']):
            if 'color' not in item:
                input_errors.append({
                    'attribute': f'recipe[{index}].color',
                    'type': 'attribute_required',
                    'message': attribute_required.format(
                        f'recipe[{index}].color')
                })
            elif type(item['color']) is not str:
                input_errors.append({
                    'attribute': f'recipe[{index}].color',
                    'type': 'invalid_type',
                    'message': expected_string.format(
                        f'recipe[{index}].color')
                })

            if 'name' not in item:
                input_errors.append({
                    'attribute': f'recipe[{index}].name',
                    'type': 'attribute_required',
                    'message': attribute_required(
                        f'recipe[{index}].name')
                })
            elif type(item['name']) is not str:
                input_errors.append({
                    'attribute': f'recipe[{index}].name',
                    'type': 'invalid_type',
                    'message': expected_string.format(
                        f'recipe[{index}].name')
                })

            if 'parts' not in item:
                input_errors.append({
                    'attribute': f'recipe[{index}].parts',
                    'type': 'attribute_required',
                    'message': attribute_required.format(
                        f'recipe[{index}].parts')
                })
            elif type(item['parts']) is not int:
                input_errors.append({
                    'attribute': f'recipe[{index}].parts',
                    'type': 'invalid_type',
                    'message': expected_integer.format(
                        f'recipe[{index}].parts')
                })

    return input_errors


def validate_update_drink_input(data):
    input_errors = []

    if 'title' in data and type(data['title']) is not str:
        input_errors.append({
            'attribute': 'title',
            'type': 'invalid_type',
            'message': expected_string.format('title')
        })

    if 'recipe' in data:
        if type(data['recipe']) is not list:
            input_errors.append({
                'attribute': 'recipe',
                'type': 'invalid_type',
                'message': expected_objects_array.format('recipe')
            })
        else:
            for index, item in enumerate(data['recipe']):
                if 'color' not in item:
                    input_errors.append({
                        'attribute': f'recipe[{index}].color',
                        'type': 'attribute_required',
                        'message': attribute_required.format(
                            f'recipe[{index}].color')
                    })
                elif type(item['color']) is not str:
                    input_errors.append({
                        'attribute': f'recipe[{index}].color',
                        'type': 'invalid_type',
                        'message': expected_string.format(
                            f'recipe[{index}].color')
                    })

                if 'name' not in item:
                    input_errors.append({
                        'attribute': f'recipe[{index}].name',
                        'type': 'attribute_required',
                        'message': attribute_required(
                            f'recipe[{index}].name')
                    })
                elif type(item['name']) is not str:
                    input_errors.append({
                        'attribute': f'recipe[{index}].name',
                        'type': 'invalid_type',
                        'message': expected_string.format(
                            f'recipe[{index}].name')
                    })

                if 'parts' not in item:
                    input_errors.append({
                        'attribute': f'recipe[{index}].parts',
                        'type': 'attribute_required',
                        'message': attribute_required.format(
                            f'recipe[{index}].parts')
                    })
                elif type(item['parts']) is not int:
                    input_errors.append({
                        'attribute': f'recipe[{index}].parts',
                        'type': 'invalid_type',
                        'message': expected_integer.format(
                            f'recipe[{index}].parts')
                    })

    return input_errors


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
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drink_details(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


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
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    data = request.get_json()
    if not data:
        abort(400)

    input_errors = validate_create_drink_input(data)
    if input_errors:
        raise InvalidInput(input_errors)

    try:
        drink = Drink(
            title=data['title'],
            recipe=json.dumps(data['recipe']))
        drink.insert()
    except exc.IntegrityError as exception:
        description = exception.args[0]
        unique_contraint_prefix = (
            '(sqlite3.IntegrityError) UNIQUE constraint failed: ')
        if description.find(unique_contraint_prefix) != -1:
            start_index = description.rfind('.') + 1
            attribute = description[start_index:]
            message = f'The value provided for attribute \"{attribute}\" ' + \
                'is already taken.'

            return jsonify({
                'success': False,
                'error': 400,
                'message': message
            })

        raise exception

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


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
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    data = request.get_json()
    if not data:
        abort(400)

    input_errors = validate_update_drink_input(data)
    if input_errors:
        raise InvalidInput(input_errors)

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    if 'title' in data:
        drink.title = data['title']
    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])

    drink.update()
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


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
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    drink.delete()
    return jsonify({
        'success': True,
        'delete': id
    })


# Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'The server could not understand the request.'
    }), 400


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


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': (
            'The request was well-formed but could not be'
            ' processed due to semantic errors.')
    }), 422


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code


@app.errorhandler(InvalidInput)
def invalid_input(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'The request could not be processed due to invalid data.',
        'input_errors': error.input_errors
    }), 400


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
