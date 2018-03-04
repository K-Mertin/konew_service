from flask import Blueprint, jsonify, g, request, current_app, make_response
from dataAccess.userAccess import userAccess
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json, os
import jwt
import decorators

apiUser = Blueprint('user', __name__)

@apiUser.before_request
def before_request():
    apiUser.dataAccess = userAccess()

@apiUser.route('/pwd', methods=['PUT'])
@decorators.token_required
def update_password(currentUser):
    data=json.loads(request.data)
    print(currentUser)
    if check_password_hash(currentUser['password'],  data['oldPassword']):
        newPassword = generate_password_hash(data['newPassword'], method='sha256')

        apiUser.dataAccess.update_password(str(currentUser['_id']),newPassword)

        return make_response(jsonify({'message' :'success'}), 200)
 
    return make_response(jsonify({'message' :'invalid password'}), 401, {'WWW-Authenticate' : 'Basic realm="wrong password"'})


@apiUser.route('/register', methods=['POST'])
def create_user():
    data=json.loads(request.data)

    user = apiUser.dataAccess.find_user(data['username'])

    if user:
        return make_response(jsonify({'message' :'user exist'}), 500 )
    
    data['password'] = generate_password_hash(data['password'], method='sha256')
        
    apiUser.dataAccess.create_user(data)

    return jsonify({'message' : 'New user created!'})

@apiUser.route('/', methods=['GET'])
def get_all_user():
   
    users = apiUser.dataAccess.get_all_user()
    output = []
    for user in users:
        user_data = {}
        user_data['_id'] = str(user['_id'])
        user_data['username'] = user['username']
        user_data['password'] = user['password']
        user_data['role'] = user['role']
        output.append(user_data)
        

    return jsonify(output)

@apiUser.route('/login')
def login():
    
    auth = request.authorization

    print(auth)
    
    if not auth or not auth.username or not auth.password:
        return make_response(jsonify({'message' :'Could not verify1'}), 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = apiUser.dataAccess.find_user(auth.username)

    if not user:
        return make_response(jsonify({'message' :'user not exist'}), 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user['password'], auth.password):
        token = jwt.encode({'username' : user['username'], 'role':user['role'], 'id':str(user['_id']), 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8'), 'username':user['username'], 'role': user['role'] })
 
    return make_response(jsonify({'message' :'wrong username or invalid password'}), 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})