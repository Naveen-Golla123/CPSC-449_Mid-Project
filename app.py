from flask import Flask, request, jsonify, make_response, render_template, redirect,url_for,abort,send_from_directory
import pymysql
from datetime import datetime, timedelta,date
import re
import jwt
from functools import wraps
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)


# Application configuration
app.config['SECRET_KEY']='key'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'


# MySql Connection
conn= pymysql.connect(
    host='localhost',
    user='root', 
    password = "Manasa@071200",
    db='cpsc_449_recipe',
    cursorclass=pymysql.cursors.DictCursor
)
cur= conn.cursor()


# Decorator for token verification which acts as an gaurd to required resource.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # The request header contains the string jwt.
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        # output 401 if no token is supplied
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
        try:
            print(token)
            # decoding the payload to retrieve the stored information
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
            cur.execute('SELECT * FROM users WHERE userName = % s', (data['userName']),)
            users = cur.fetchone()
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the context of the currently logged in user to the routes
        return  f(*args, **kwargs)
    return decorated

'''
Error handling for 401 -- UnAuthenticated User.
                   403 -- unAuthorized Request
                   500 -- Internal server error.
'''
@app.errorhandler(401)
def unAuthorized(msg):
    return msg, 401

@app.errorhandler(403)
def forbidden(msg):
    return msg, 403

@app.errorhandler(500)
def internalCodeError(msg):
    return msg, 500

@app.errorhandler(409)
def conflictError(msg):
    return msg, 409

# routes that logins the user with valid details.
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
        # prepare jwt token using encode method in pyJWT.
        return jwt.encode({
            'userName': userName,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, app.config['SECRET_KEY'])
    else:
        abort(401,"Invalid credentials")

 
# Route that returns all uploaded recipes.
@app.route('/allRecipes', methods =['GET'])
def allRecipes():
    cur.execute('SELECT * From recipes')
    recipes=cur.fetchall()
    return recipes

# Route that returns upload recipe file by its Name.
@app.route('/uploads/getFileById/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

# Route that returns specific recipe by given Id.
@app.route('/recipe/<id>')
def getRecipeById(id):
    cur.execute('SELECT * From recipes WHERE recipeId = % s', (id),)
    recipe=cur.fetchone()
    if recipe:
        return recipe
    else:
        abort(404, "Recipe with given Id doesnt exists")

# Route that allows user to upload details and Create a recipe. Note: this route is private which require valid token.
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

'''
 Route that helps user to register using userName, firstname , lastname , password and mobileNumer
 Duplicate usernames are not allowed
'''
@app.route('/register', methods =['POST'])
def register():
    data = request.form
    userName, firstName, lastName, password, location, mobileNumber = data.get('userName'), data.get('firstName'),data.get('lastName'),data.get('password'),data.get('location'),data.get('mobileNumber')
    print(userName, firstName,lastName,password,location,mobileNumber)
    cur.execute('SELECT * FROM users WHERE userName = % s', (userName),)
    users = cur.fetchone()
    if users:
        abort(409,'User already exists !')
    elif not re.match(r'[A-Za-z0-9]+', userName):
        abort(500,'name must contain only characters and numbers !')
    else:
        cur.execute('INSERT INTO users (userName, firstName,lastName,password,location,mobileNumber) VALUES ( % s, % s, % s, % s, % s, % s)', (userName, firstName,lastName,password,location,mobileNumber ),)
        conn.commit()
        return "Successfully Registered"

if __name__ == '__main__':
    app.run(debug=True)