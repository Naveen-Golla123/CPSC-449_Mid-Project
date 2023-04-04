from flask import Flask, request, jsonify, make_response, render_template, redirect,url_for,abort,send_from_directory
import pymysql
from datetime import datetime, timedelta,date
import re
import jwt
from functools import wraps
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SECRET_KEY']='key'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'

conn= pymysql.connect(
    host='localhost',
    user='root',
    password='Mynameissai@07',
    db='cpsc_449_recipe',
    cursorclass=pymysql.cursors.DictCursor
)
cur= conn.cursor()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
        try:
            print(token)
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
            cur.execute('SELECT * FROM users WHERE userName = % s', (data['userName']),)
            users = cur.fetchone()
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users context to the routes
        return  f(*args, **kwargs)
    return decorated


@app.errorhandler(401)
def unAuthorized(msg):
    return msg, 401

@app.errorhandler(403)
def forbidden(msg):
    return msg, 403

@app.errorhandler(500)
def internalCodeError(msg):
    return msg, 500



@app.route("/")
@app.route('/login', methods =['POST'])
def login():
    auth= request.form
    userName, password= auth.get('userName'),auth.get('password')
    cur.execute('SELECT * FROM users WHERE userName = % s', (userName,))
    users = cur.fetchone()
    token = ""
    print(users)
    if not users:
        abort(404,'User Does not Exist')
    elif users['password']==password:
        return jwt.encode({
            'userName': userName,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, app.config['SECRET_KEY'])
 

@app.route('/logout', methods =['GET', 'POST'])
def logout():
    return "<p>Hello, World 1!</p>"

@app.route('/allRecipes', methods =['GET', 'POST'])
def allRecipes():
    cur.execute('SELECT * From recipes')
    recipes=cur.fetchall()
    # for recipe in recipes:
    #     recipe["recipeImgName"] = send_from_directory(app.config['UPLOAD_PATH'],recipe["recipeImgName"])

    return recipes

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/recipe/<id>')
def getRecipeById(id):
    cur.execute('SELECT * From recipes WHERE recipeId = % s', (id),)
    recipe=cur.fetchone()
    if recipe:
        return recipe
    else:
        abort(404, "Recipe with given Id doesnt exists")

@app.route('/uploadRecipe', methods =['POST'])
@token_required
def uploadRecipe():
    uploadedFile= request.files['recipepost']
    data=request.form
    print(uploadedFile)
    print(data)
    filename = secure_filename(uploadedFile.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(500,"File type is not allowed")
    uploadedFile.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    cur.execute ('INSERT INTO recipes(recipeHeadline,recipeDes,recipeImgName,recipePostedBy,recipePostedTime) VALUES (% s, % s, % s, % s, % s)', (data.get("recipeHeadline"),data.get("recipeDes"),filename,2,datetime.now(),))
    conn.commit()
    return "Uploaded Successfully"

@app.route('/register', methods =['POST'])
def register():
    data = request.form
    userName, firstName, lastName, password, location, mobileNumber = data.get('userName'), data.get('firstName'),data.get('lastName'),data.get('password'),data.get('location'),data.get('mobileNumber')
    print(userName, firstName,lastName,password,location,mobileNumber)
    cur.execute('SELECT * FROM users WHERE userName = % s', (userName),)
    users = cur.fetchone()
    if users:
        abort(404,'User already exists !')
    elif not re.match(r'[A-Za-z0-9]+', userName):
        abort(500,'name must contain only characters and numbers !')
    else:
        cur.execute('INSERT INTO users (userName, firstName,lastName,password,location,mobileNumber) VALUES ( % s, % s, % s, % s, % s, % s)', (userName, firstName,lastName,password,location,mobileNumber ),)
        conn.commit()
        return "Successfully Registered"

if __name__ == '__main__':
    app.run(debug=True)