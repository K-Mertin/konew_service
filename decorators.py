from functools import wraps
from flask import request, jsonify
from flask import current_app
import jwt
from dataAccess.userAccess import userAccess

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user =userAccess().find_user(data['username'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
