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
        self.logger.logger.info('add_user:' + str(user['name']))

        hashed_password = generate_password_hash(user['password'], method='sha256')
        
        user['createDate'] = datetime.datetime.utcnow()
        user['password'] = hashed_password

        return self.db['User'].insert(user)

    def get_all_user(self):
        self.logger.logger.info('get_all_user')

        return self.db['User'].find()

    def find_user(self, name):
        self.logger.logger.info('find_user1')

        return self.db['User'].find_one({'name':name})


if __name__ == "__main__":
    db = DataAccess()
