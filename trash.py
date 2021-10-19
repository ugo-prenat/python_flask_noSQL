from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return \
        {
            "msg": 'success'
        }

def main():
    display_hello('On fait comment le sout en Python svp ?')

def display_hello(msg):
    """
        Display a simple message

        Args: 
            msg: the message to display
    """
    print(msg)

if __name__ == '__main__':
    app.run(
        host = "127.0.0.1",
        port = 3000,
        debug = True
    )