from flask import Flask
import pymysql

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World 1!</p>"

if __name__ == '__main__':
    app.run(debug=True)