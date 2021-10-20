from pymongo import MongoClient
from markupsafe import escape
from flask import request
from flask import Flask
import numpy as np
import os
import json

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

    succes = {
        'code': code,
        'msg': msg
    }
    return succes

def get_user_id():
    """
        Get the id of the last user in the database and return it plus 1
    """
    users_list = list(users.find())
    user_list_len = len(users_list)
    last_user = users_list[user_list_len - 1]
    last_id = last_user['_id']
    return last_id + 1


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
        if arg != 'username' and arg != 'mail' and arg != 'password' and arg != 'is_admin' :
            error['found_error'] = True
            error['error_content'] = error_msg(400, f'L\'argument \'{arg}\' est inconnu')
            return error

    # if no error was found, return the 'error' object with the param 'found_error' set to false by default
    return error

def create_user(args, user_id):
    """
        Create an object containing the values of the new user and insert it in the database

        params:
            args: array of all arguments passed in the request
    """

    new_user = {
        '_id': user_id,
        'username': args.get('username'),
        'mail': args.get('mail'),
        'password': args.get('password'),
        'is_admin': args.get('is_admin'),
    }
    users.insert_one(new_user)

def is_user_exists(wanted_id):
    """
        Loop on the list of all users to find a wanted user

        params:
            wanted_id: the id of the user we want to known if he exists or not
    """
    users_list = users.find({})
    
    for user in users_list:
        if user['_id'] == wanted_id:
            return True

    return False

@app.route("/users", methods=["POST"])
def create_new_user():
    """
        Create a new user with values passed in request args and insert it into the database
    """
    args = request.args

    error = prevent_create_user_errors(args)

    if error['found_error']:
        return error['error_content']

    else:
        user_id = get_user_id()
        create_user(args, user_id)
        return success_msg(200, f'L\'utilisateur a été créé, id: {user_id}')

@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    """
        Delete the user attached to the 'id' variable in the request url
    """
    user_id = escape(id)

    # Check if the given id isn't a number
    if user_id.isnumeric() == False:
        return error_msg(400, f'La valeur \'{id}\' est incorrecte, nombre requis')
        
    # Check if the given id is attached to a user in the DB
    if is_user_exists(int(user_id)):
        # Delete user
        users.delete_one({ '_id': int(user_id) })
        return success_msg(200, f'L\'utilisateur {user_id} a été supprimé')
    
    else:
        return error_msg(400, f'Aucun utilisateur n\'est rattaché à l\'id {user_id}')

     

if __name__ == '__main__':
    app.run(
        host = "127.0.0.1",
        port = 3000,
        debug = True
    )