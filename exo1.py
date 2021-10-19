from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/users", methods=["GET"])
def return_users():
    return {
        'users': [
            {
                'id': '0',
                'firstname': 'Thierry',
                'lastname': 'Decker',
                'age': '57'
            },
            {
                'id': '0',
                'firstname': 'Mya',
                'lastname': 'Decker',
                'age': '5'
            },
            {
                'id': '0',
                'firstname': 'Nelson',
                'lastname': 'Decker',
                'age': '4'
            },
        ]
    }


if __name__ == '__main__':
    app.run(
        host = "127.0.0.1",
        port = 3000,
        debug = True
    )