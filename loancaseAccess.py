from DataAccess import DataAccess
from bson.objectid import ObjectId
from operator import  attrgetter
import pymongo
import datetime

class loancaseAccess(DataAccess):
    def insert_loancase(self, loancase):
        self.logger.logger.info('add loancase')
        loancase['createDate'] = datetime.datetime.utcnow()
        loancase['modifyDate'] = datetime.datetime.utcnow()
        loancase['createUser'] = loancase['user']
        loancase['modifyUser'] = loancase['user']
        loancase.__delitem__('user')

        return self.db['Loancases'].insert(loancase)

    def get_allPaged_loancases(self, pageSize=10, pageNum=1):
       skips = pageSize * (pageNum - 1)
       
       totalCount = self.db['Loancases'].find().count()

       result = {
           "totalCount":totalCount,
           "data": self.db['Loancases'].find().sort("createDate", pymongo.DESCENDING).skip(skips).limit(pageSize)
       }
       return result

    def update_loancase(self, loancase, ip):
        print('update')

        id = loancase['_id']
        loancase['modifyDate'] = datetime.datetime.utcnow()
        loancase['modifyUser'] = loancase['user']
        loancase.__delitem__('user')
        loancase.__delitem__('_id')
    
        self.db['LoancaseLog'].insert({
            'action':'update',
            'loancase':self.db['Loancases'].find_one({'_id': ObjectId(id)}),
            'date' : datetime.datetime.utcnow(),
            'user' :  loancase['modifyUser'],
            'ip' : ip
        })

        return self.db['Loancases'].update({'_id':ObjectId(id)},loancase)

    def get_loancases(self, queryType, key, pageSize=10, pageNum=1):
        print('db get loancases')
        skips = pageSize * (pageNum - 1)

        print('123123')

        data= self.db['Loancases'].aggregate([{'$match': {queryType:{'$regex':'^'+key}}}])
        totalCount = len(list(data))

        result = {
            "totalCount":totalCount,
            "data": list(self.db['Loancases'].aggregate([{'$match': {queryType:{'$regex':'^'+key}}},{ "$sort": {"createDate":-1}}, { "$skip": skips},{ "$limit": pageSize }]))
        }

        return result

    def get_loancases_keyList(self, queryType, key):
        print('/^'+key+'/')

        return self.db['Loancases'].aggregate([{'$project':{queryType:1}},{'$group':{'_id':'$'+queryType}},{'$match':{'_id':{'$regex':'^'+key}}}])
    
    def check_duplicate(self, queryType, key):
        return self.db['Loancases'].find({queryType:key}).count()

if __name__ == "__main__":
    db = loancaseAccess()
    print(db.get_allPaged_loancases()['data'][0])
