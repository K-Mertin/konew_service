import pymongo
from DataAccess import DataAccess
import datetime
import time
from bson.objectid import ObjectId
import re
import logging
from werkzeug.security import generate_password_hash, check_password_hash


class userAccess(DataAccess):

    def create_user(self, user):
        self.logger.logger.info('add_user:' + str(user['username']))
        
        user['createDate'] = datetime.datetime.utcnow()

        return self.db['User'].insert(user)

    def get_all_user(self):
        self.logger.logger.info('get_all_user')

        return self.db['User'].find()

    def find_user(self, name):
        self.logger.logger.info('find_user')

        return self.db['User'].find_one({'username':name})

    def find_userByid(self, id):
        self.logger.logger.info('find_userByid')

        return self.db['User'].find_one({'_id':ObjectId(id)})

    def update_password(self, id, password):
        
        return self.db['User'].update_one({'_id':ObjectId(id)},{'$set': {'password': password, 'modifyDate':datetime.datetime.utcnow()}})

if __name__ == "__main__":
    db = DataAccess()
