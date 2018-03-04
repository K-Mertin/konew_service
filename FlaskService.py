# mongo.py
from flask import Flask, jsonify, request, g,  redirect, url_for
from DataAccess import DataAccess
from dataAccess.userAccess import userAccess
from flask_cors import CORS
from Logger import Logger


from api.test.view import blueprint
from api.relations.api import apiRelations
from api.requests.api import apiRequests
from api.loancases.api import apiLoancases
from api.user.api import apiUser
from api.setting.api import apiSetting

import json
import configparser
import logging
import os
import datetime

UPLOAD_FOLDER = os.curdir

app = Flask('Flask-Service')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secret'
app.register_blueprint(apiRelations, url_prefix='/api/relations')
app.register_blueprint(apiRequests, url_prefix='/api/requests')
app.register_blueprint(apiLoancases, url_prefix='/api/loancases')
app.register_blueprint(apiUser, url_prefix='/api/user')
app.register_blueprint(apiSetting, url_prefix='/api/setting')

CORS(app)

@app.before_request
def before_request():
    g.dataAccess = userAccess()

def Setting():
    config = configparser.ConfigParser()
    with open('Config.ini') as file:
        config.readfp(file)

    logPath = config.get('Options','Log_Path')
    

    formatter = logging.Formatter('[%(name)-12s %(levelname)-8s] %(asctime)s - %(message)s')
    # app.logger=logging.getLogger(__class__.__name__)
    app.logger.setLevel(logging.DEBUG)
    
    if not os.path.isdir(logPath):
        os.mkdir(logPath)

    fileHandler = logging.FileHandler(logPath+ datetime.datetime.now().strftime("%Y%m%d")+ '_' +app.name+'.log')
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)

    app.logger.addHandler(fileHandler)
    app.logger.addHandler(streamHandler)

    app.logger.info('Finish Setting')


if __name__ == '__main__':
    Setting()
    app.run(debug=True)
