from flask import Blueprint, jsonify, g, request, current_app, make_response
from dataAccess.userAccess import userAccess
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json, os
import jwt

apiUser = Blueprint('user', __name__)

@apiUser.before_request
def before_request():
    apiUser.dataAccess = userAccess()


@apiUser.route('/register', methods=['POST'])
def create_user():
    data=json.loads(request.data)

    apiUser.dataAccess.create_user(data)
    

    return jsonify({'message' : 'New user created!'})

@apiUser.route('/', methods=['GET'])
def get_all_user():
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})
    # print(current_app.config['SECRET_KEY'])
    
    users = apiUser.dataAccess.get_all_user()
    output = []
    for user in users:
        user_data = {}
        user_data['_id'] = str(user['_id'])
        user_data['name'] = user['name']
        user_data['password'] = user['password']
        output.append(user_data)

    return jsonify(output)

@apiUser.route('/login', methods=['POST'])
def login():
    
    auth = request.authorization

    print(auth)
    
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify1', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = apiUser.dataAccess.find_user(auth.username)

    if not user:
        return make_response('Could not verify2', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user['password'], auth.password):
        token = jwt.encode({'name' : user['name'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8'), 'username':user['name'], 'role': user['role'] })
 
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})