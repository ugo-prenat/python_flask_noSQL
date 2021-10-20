from pymongo import MongoClient
from flask import request
from flask import Flask
import numpy as np
import os
import json

app = Flask(__name__)

username = 'ugo'
password = 'XMGYXZTCk4HnhhEj'

mongo_uri = f'mongodb+srv://{username}:{password}@cluster0.aiyk2.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)
db = client.g4g
users = db.users

def get_users():
    users_list = users.find()
    print(users_list)
    """ for x in users_list:
        print(x) """
    return users_list

@app.route("/users", methods=["GET"])
def users_list():
    """
        Apply all request args on the users list and return it
    """

    users = get_users()
    return 'a'

                    

if __name__ == '__main__':
    app.run(
        host = "127.0.0.1",
        port = 3000,
        debug = True
    )