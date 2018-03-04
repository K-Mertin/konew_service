from flask import Blueprint, jsonify, g, request, current_app, make_response
from dataAccess.settingAccess import settingAccess
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json, os
import jwt
import decorators

apiSetting = Blueprint('setting', __name__)

@apiSetting.before_request
def before_request():
    apiSetting.dataAccess = settingAccess()


@apiSetting.route('/update', methods=['PUT'])
@decorators.token_required
def update_setting(currentUser):
    print(currentUser)

    if currentUser['role'] != 'admin':
        return make_response(jsonify({'message' :'unauthorized'}), 401)

    data=json.loads(request.data)

    apiSetting.dataAccess.update_setting(data['settingName'], data['key'], data['value'])

    return make_response(jsonify({'message' :'success'}), 200)

@apiSetting.route('/add', methods=['POST'])
@decorators.token_required
def create_setting(currentUser):
    print(currentUser)
    if currentUser['role'] != 'admin':
        return make_response(jsonify({'message' :'unauthorized'}), 401)


    data=json.loads(request.data)
        
    apiSetting.dataAccess.add_setting(data)

    return jsonify({'message' : 'New setting created!'})

@apiSetting.route('/<settingName>', methods=['GET'])
def get_setting(settingName):
   
    setting = apiSetting.dataAccess.get_setting(settingName)  

    setting['_id'] = str(setting['_id'])

    return jsonify(setting)

@apiSetting.route('/list', methods=['GET'])
def get_setting_list():
    setting = apiSetting.dataAccess.get_setting_list()  
    return jsonify(list(map(lambda x : x['settingName'], setting)))