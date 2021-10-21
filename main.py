from pymongo import MongoClient
from markupsafe import escape
from flask import request
from flask import Flask

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


def get_user_id():
    """
        Get the id of the last user in the database and return it plus 1
    """
    users_list = list(users.find())
    user_list_len = len(users_list)
    last_user = users_list[user_list_len - 1]
    last_id = last_user['_id']
    return last_id + 1

def get_tournament_id():
    """
        Get the id of the last tournament in the database and return it plus 1
    """
    tournaments_list = list(tournaments.find())
    tournament_list_len = len(tournaments_list)
    last_tournament = tournaments_list[tournament_list_len - 1]
    last_id = last_tournament['_id']
    return last_id + 1

def is_user_exists(wanted_id):
    """
        Loop on the list of all users to find the wanted user exists or not

        params:
            wanted_id: the id of the user we want to known if he exists or not
    """
    users_list = users.find({})

    for user in users_list:
        if user['_id'] == wanted_id:
            return True

    return False

def is_tournament_exists(wanted_id):
    """
        Loop on the list of all tournaments to find the wanted tournament exists or not

        params:
            wanted_id: the id of the tournament we want to known if he exists or not
    """
    tournament_list = tournaments.find({})

    for tournament in tournament_list:
        if tournament['_id'] == wanted_id:
            return True

    return False

def is_game_in_collection(game_name):
    """
        Search in the 'games' collection if the given game is in it

        params:
            game_name: the name of the game we want to known if it's in the 'games' collection or not
    """
    games_list = list(games.find())

    for game in games_list:
        if game['name'].lower() == game_name.lower():
            return True

    return False


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

def prevent_create_tournament_errors(args):
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

    title = args.get('title')
    game = args.get('game')
    participant_limit = args.get('participant_limit')

    # Check if required args are missing
    if title == None:
        error['found_error'] = True
        error['error_content'] = error_msg(400, 'L\'argument \'title\' est manquant')
        return error
    elif game == None:
        error['found_error'] = True
        error['error_content'] = error_msg(400, 'L\'argument \'game\' est manquant')
        return error
    elif participant_limit == None:
        error['found_error'] = True
        error['error_content'] = error_msg(400, 'L\'argument \'participant_limit\' est manquant')
        return error

    # Check if the game is in the games collection
    if is_game_in_collection(game) == False:
        error['found_error'] = True
        error['error_content'] = error_msg(400, f'Le jeu \'{game}\' n\'est pas présent dans la base de donnée')
        return error

    # Check if the 'participant_limit' variable is a number
    if participant_limit.isnumeric() == False:
        error['found_error'] = True
        error['error_content'] = error_msg(400, f'La valeur de l\'argument \'participant_limit\' est incorrecte, nombre requis')
        return error

    # if no error was found, return the 'error' object with the param 'found_error' set to false by default
    return error

def prevent_join_tournament_errors(args, user_id):
    """
        Prevent all possible errors

        params:
            args: array of all arguments passed in the request
            user_id: the id of the user who wants to join a tournament

        return the 'error' object
    """

    error = {
        'found_error': False,
        'error_content': {}
    }

    if len(args) == 0:
        error['found_error'] = True
        error['error_content'] = error_msg(400, f'L\'argument \'id\' est obligatoire')
        return error

    # Check for args errors
    for arg, value in args.items():
        if arg != 'id':
            error['found_error'] = True
            error['error_content'] = error_msg(400, f'L\'argument \'{arg}\' est inconnu')
            return error
        if arg == 'id' and value.isnumeric() == False:
            error['found_error'] = True
            error['error_content'] = error_msg(400, f'La valeur de l\'argument \'id\' est incorrecte, nombre requis')
            return error
        elif arg == 'id' and is_tournament_exists(int(value)) == False:
            error['found_error'] = True
            error['error_content'] = error_msg(400, f'Aucun tournoi n\'est rattaché à l\'id {value}')
            return error

    # Check if the user id is attached to an existing user
    if is_user_exists(int(user_id)) == False:
        error['found_error'] = True
        error['error_content'] = error_msg(400, f'Aucun utilisateur n\'est rattaché à l\'id {user_id}')
        return error

    # if no error was found, return the 'error' object with the param 'found_error' set to false by default
    return error

def create_user(args, user_id):
    """
        Create an object containing the values of the new user and insert it in the database

        params:
            args: array of all arguments passed in the request
            user_id: the id of the new user
    """

    new_user = {
        '_id': user_id,
        'username': args.get('username'),
        'mail': args.get('mail'),
        'password': args.get('password'),
        'is_admin': args.get('is_admin'),
        'tournaments_list': []
    }
    users.insert_one(new_user)

def create_tournament(args, tournament_id):
    """
        Create an object containing the values of the new tournament and insert it in the database

        params:
            args: array of all arguments passed in the request
            tournament_id: the id of the new tournament
    """

    new_tournament = {
        '_id': tournament_id,
        'title': args.get('title'),
        'game': args.get('game'),
        'participant_limit': args.get('participant_limit'),
        'total_participant': 0,
    }
    tournaments.insert_one(new_tournament)

def get_tournament_by_id(tournament_id):
    """
        Find a tournament in the tournaments list and return it

        params:
            tournament_id: the id of the tournament we want to find
    """
    tournaments_list = list(tournaments.find())

    for tournament in tournaments_list:
        if tournament['_id'] == tournament_id:
            return tournament

def get_user_by_id(user_id):
    """
        Find a user in the users list and return it

        params:
            user_id: the id of the user we want to find
    """
    users_list = list(users.find())

    for user in users_list:
        if user['_id'] == user_id:
            return user

def is_tournament_already_joined(user_tournament_list, tournament_id):
    """
        Loop in the user's joined tournaments to find if he already joined the tournament that he wants to join

        params: 
            user_tournament_list: list of all tournaments joined by the user
            tournament_id: the id of the tournament that we want to know if the user already joined it
    
        return: boolean
    """
    for tournament in user_tournament_list:
        if tournament['id'] == tournament_id:
            return True

    return False

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
        user_id = get_user_id()
        create_user(args, user_id)
        return success_msg(200, f'L\'utilisateur a été créé, id: {user_id}')

@app.route("/users/<id>", methods=["DELETE"])
def delete_user_route(id):
    """
        Delete the user attached to the 'id' variable in the request url

        param:
            id: the id of the user than we want to delete
    """
    user_id = escape(id)


    # Check if the given id isn't a number
    if id.isnumeric() == False:
        return error_msg(400, f'La valeur \'{user_id}\' est incorrecte, nombre requis')

    # Check if the given id is attached to a user in the DB
    if is_user_exists(int(user_id)):
        # Delete user
        users.delete_one({ '_id': int(user_id) })
        return success_msg(200, f'L\'utilisateur {user_id} a été supprimé')

    else:
        return error_msg(400, f'Aucun utilisateur n\'est rattaché à l\'id {user_id}')

@app.route("/users/<id>", methods=["PATCH"])
def modify_user(id):
    """
        Modify user's informations selected thanks to the ID
        Returns: The user with his new parameters
    """

    user_id = int(escape(id))
    args = request.args

    for key, values in args.items():
        new_values = {"$set": {key: values}}

    myquery = {"_id": user_id}
    users.update_one(myquery, new_values)
    return success_msg(200, "Utilisateur modifié")

@app.route("/tournaments", methods=["POST"])
def create_new_tournament():
    """
        Create a tournament with values passed in request args and insert it into the database
    """
    args = request.args

    error = prevent_create_tournament_errors(args)

    if error['found_error']:
        return error['error_content']
    else:
        tournament_id = get_tournament_id()
        create_tournament(args, tournament_id)
        return success_msg(200, f'Le tournoi a été créé, id: {tournament_id}')

@app.route("/users/<id>/tournaments", methods=["POST"])
def join_tournament(id):
    """
        Add a tournament to the selected user

        params:
            id: the id of the user
    """
    user_id = escape(id)

    # Check if args and user_id contain errors
    error = prevent_join_tournament_errors(request.args, user_id)
    tournaments_id = request.args.get('id')

    if error['found_error']:
        return error['error_content']
    else:
        tournament = get_tournament_by_id(int(tournaments_id))
        user = get_user_by_id(int(user_id))

        

        # Increment the number of participant of the tournament
        # If the participant limit has been reached, don't increment
        if tournament['participant_limit'] == tournament['total_participant']:
            return error_msg(400, 'Ce tournois est complet')
        # Check if the user already joined the tournament
        elif is_tournament_already_joined(user['tournaments_list'], tournaments_id):
            return error_msg(400, f'Ce tournoi a déjà été rejoint par l\'utilisateur {user_id}')
        else:
            # Increment the number of participant of the tournament
            tournaments.update_one(tournament, { '$inc': { 'total_participant': +1 }})

            # Add the tournament in the user profile
            new_tournament = {
                'id': tournaments_id,
                'title': tournament['title']
            }
            user['tournaments_list'].append(new_tournament)
            users.update_one({'_id': int(user_id)}, { '$set': { 'tournaments_list': user['tournaments_list'] }})
        
            return success_msg(200, f'Le tournoi {tournaments_id} a été rejoint')


if __name__ == '__main__':
    app.run(
        host = "127.0.0.1",
        port = 3000,
        debug = True
    )