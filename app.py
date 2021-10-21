from pymongo import MongoClient
from flask import request
from flask import Flask
import numpy as np
import os
import json
from markupsafe import escape

app = Flask(__name__)

# Connection to the data base
username = 'maxime_ugo'
password = 'dspDsTMgE5bu0J72'

mongo_uri = f'mongodb+srv://{username}:{password}@cluster0.aiyk2.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)
db = client.g4g

# Collections initiation
users = db.users
tournaments = db.tournaments
games = db.games


def error_msg(code, msg):
    """
        Return an error object

        params:
            code: the code of the error
            msg: the message of the error
    """

    error = {
        'code': code,
        'msg': msg
    }
    return error


def success_msg(code, msg):
    """
        Return an success object

        params:
            code: the code of the success
            msg: the message of the success
    """

    success = {
        'code': code,
        'msg': msg
    }
    return success


def prevent_create_user_errors(args):
    """
        Prevent all possible errors

        params:
            args: array of all arguments passed in the request

        return the 'error' object
    """

    error = {
        'found_error': False,
        'error_content': {}
    }

    username = args.get('username')
    mail = args.get('mail')
    password = args.get('password')
    is_admin = args.get('is_admin')

    # Check if required args are missing
    if username == None:
        error['found_error'] = True
        error['error_content'] = error_msg(400, 'L\'argument \'username\' est manquant')
        return error
    elif mail == None:
        error['found_error'] = True
        error['error_content'] = error_msg(400, 'L\'argument \'mail\' est manquant')
        return error
    elif password == None:
        error['found_error'] = True
        error['error_content'] = error_msg(400, 'L\'argument \'password\' est manquant')
        return error
    elif is_admin == None:
        error['found_error'] = True
        error['error_content'] = error_msg(400, 'L\'argument \'is_admin\' est manquant')
        return error

    # Check if the 'is_admin' value is a boolean
    if is_admin.lower() != 'false' and is_admin.lower() != 'true':
        error['found_error'] = True
        error['error_content'] = error_msg(400, 'La valeur de l\'argument \'is_admin\' est incorrecte, booléen requis')
        return error

    # Loop on all args to see if an arg is unknown
    for arg in args:
        if arg != 'username' and arg != 'mail' and arg != 'password' and arg != 'is_admin':
            error['found_error'] = True
            error['error_content'] = error_msg(400, f'L\'argument \'{arg}\' est inconnu')
            return error

    # if no error was found, return the 'error' object with the param 'found_error' set to false by default
    return error


def create_user(args):
    """
        Create an object containing the values of the new user and insert it in the database

        params:
            args: array of all arguments passed in the request
    """

    new_user = {
        'username': args.get('username'),
        'mail': args.get('mail'),
        'password': args.get('password'),
        'is_admin': args.get('is_admin'),
    }
    users.insert_one(new_user)


@app.route("/users", methods=["POST"])
def create_new_user():
    """
        Create a new user with values passed in request args

    """
    args = request.args

    error = prevent_create_user_errors(args)

    if error['found_error']:
        return error['error_content']

    else:
        create_user(args)
        return success_msg(200, 'L\'utilisateur a été créé')


@app.route("/users/<id>", methods=["PATCH"])
def modify_user(id):
    """
    Modify user's informations selected thanks to the ID
    Returns: The user with his new parameters

    """
    args = request.args

    user_list = users.find({})

    user_id = int(escape(id))

    for key, value in args.items():
        new_values = {"$set": {key: value}}

    myquery = {"_id": user_id}
    users.update_one(myquery, new_values)
    return success_msg(200, "Utilisateur modifié")


if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=3000,
        debug=True
    )
