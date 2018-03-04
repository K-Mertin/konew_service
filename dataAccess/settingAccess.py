from DataAccess import DataAccess
import pymongo
from bson.objectid import ObjectId

class settingAccess(DataAccess):

    def add_setting(self, setting):
        self.logger.logger.info('add_setting')
        return self.db['Setting'].insert(setting)

    def update_setting(self, name, attribute, value):
        return self.db['Setting'].update_one({'settingName': name}, {'$set': {attribute: value}})

    def get_setting(self, name):
        return self.db['Setting'].find_one({'settingName': name})

    def get_setting_list(self):
        return self.db['Setting'].find({},{'settingName':1})

if __name__ == "__main__":
    db = settingAccess()
