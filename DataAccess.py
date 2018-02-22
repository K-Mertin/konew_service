import pymongo
import datetime
import time
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import configparser
import logging
import os
from Logger import Logger

class DataAccess:

    def __init__(self):
        self.Setting()
        self.logger = Logger('DataAccess-Flask')
        self.client = MongoClient(self.ipAddress, username=self.user , password=self.password, authSource=self.dbName )
        self.db = self.client['konew']
        # self.logger.info( 'Initialized')
       
    def Setting(self):
        self.config = configparser.ConfigParser()
        with open('Config.ini') as file:
            self.config.readfp(file)

        self.ipAddress = self.config.get('Mongo','ipAddress')
        self.dbName = self.config.get('Mongo','dbName')
        self.user = self.config.get('Mongo','user')
        self.password = self.config.get('Mongo','password')

    def add_request(self, request):
        self.logger.logger.info('add_request:' + str(request['searchKeys']) )
        request['status'] = 'created'
        request['createDate'] = datetime.datetime.utcnow()
        request['requestId'] = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))+'-'+request['searchKeys'][0]
        request['searchKeys'] = list(map(lambda x:{"key":x, "count":0}, request['searchKeys']))
        return self.db['Requests'].insert(request)

    def change_request_reference(self, id, refKey):
        self.logger.logger.info('change_request_reference:' + id + str(refKey))
        return self.db['Requests'].update_one({'_id': ObjectId(id)}, {'$set': {'referenceKeys': refKey, 'status': 'modified'}})
    
    def update_document_reference(self, collection, id, referenceKeys ):
        return self.db[collection].update_one({'_id': ObjectId(id)}, {'$set': {'referenceKeys': referenceKeys}})

    def get_allPaged_requests(self, pageSize=10, pageNum=1):
        skips = pageSize * (pageNum - 1)
        totalCount = self.db['Requests'].find({'status': {"$in": ['modified','created','processing','finished','failed']}}).count()

        result = {
            "totalCount":totalCount,
            "data": self.db['Requests'].find({'status': {"$in": ['modified','created','processing','finished','failed']}}).sort("createDate", pymongo.DESCENDING).skip(skips).limit(pageSize)
        }
        return result

    def get_created_requests(self):
        return self.db['Requests'].find({'status': {"$in": ['created']}})

    def get_modified_requests(self):
        return self.db['Requests'].find({'status': {"$in": ['modified']}})

    def get_processing_requests(self):
        return self.db['Requests'].find({'status': {"$in": ['processing']}})

    def get_removed_requests(self):
        return self.db['Requests'].find({'status': {"$in": ['removed']}})

    def processing_requests(self, id, searchKey, totalCount):
        return self.db['Requests'].update_one({'_id': ObjectId(id), 'searchKeys.key':searchKey}, {'$set': {'status': 'processing', 'searchKeys.$.count':totalCount}})

    def finish_requests(self, id):
        return self.db['Requests'].update_one({'_id': ObjectId(id)}, {'$set': {'status': 'finished'}})

    def remove_request(self, id):
        self.logger.logger.info('remove_request:' + id )
        return self.db['Requests'].update_one({'_id': ObjectId(id)}, {'$set': {'status': 'removed'}})

    def insert_documents(self, collection, documents):
        return self.db[collection].insert_many(documents)

    def get_allPaged_documents(self, collection='1514966746.2558856', pageSize=10, pageNum=1, sortBy="keys", filters=[]):
        skips = pageSize * (pageNum - 1)
        print(filters)
        filters = list(map(lambda x : [{"$or":[{'_id.searchKeys':x},{'_id.referenceKeys':x},{'_id.tags':x}]}],filters ))
        filters = sum(filters,[])

        aggregateList = []
        aggregateList.append(
            {
                        "$project":{
                            "searchKeys":1,
                            "referenceKeys":1,
                            "tags":1,
                            "title": 1,
                            "content":1,
                            "source":1,
                            "date":1,
                            "rkLength":{"$size":"$referenceKeys"},
                            "skLength":{"$size":"$searchKeys"},
                    }}
        )
        aggregateList.append(
            {
                            "$group": {"_id" : {
                                "searchKeys":"$searchKeys",
                                "referenceKeys":"$referenceKeys",
                                "tags":"$tags",
                                "title": "$title",
                                # "source":"$source",
                                "date":"$date",
                                "rkLength":"$rkLength",
                                "skLength":"$skLength",
                            },"source":{ "$first": "$source" }}}
        )
       
        if len(filters) >0:
            aggregateList.append( {  "$match":{"$and":filters}} )

        if sortBy == "keys":
            aggregateList.append( { "$sort": {"_id.skLength":-1,"_id.rkLength":-1, "_id.date": -1}})
        else:
            aggregateList.append( { "$sort": {"_id.skLength":-1,"_id.date": -1,"_id.rkLength":-1}})

        
        print(aggregateList)
        aggregateList.append( { "$skip": skips})

        aggregateList.append( { "$limit": pageSize })

        return self.db[collection].aggregate(aggregateList)
    
    def get_documents_count(self, collection, filters=[]):
        filters = list(map(lambda x : [{"$or":[{'_id.searchKeys':x},{'_id.referenceKeys':x},{'_id.tags':x}]}],filters ))
        filters = sum(filters,[])

        aggregateList = []

        aggregateList.append(
            {
                            "$group": {"_id" : {
                                "searchKeys":"$searchKeys",
                                "referenceKeys":"$referenceKeys",
                                "tags":"$tags",
                                "title": "$title",
                                # "source":"$source",
                                "date":"$date",
                                "skLength":"$skLength",
                            },"source":{ "$first": "$source" }}}
        )

        if len(filters) >0:
            aggregateList.append( {  "$match":{"$and":filters}} )

        return len(list(self.db[collection].aggregate(aggregateList)))
        # if len(filters) >0:
        #     filters = list(map(lambda x : [{"$or":[{'searchKeys':x},{'referenceKeys':x},{'tags':x}]}],filters ))
        #     filters = sum(filters,[])
        #     filters = {"$and":filters}
        #     return self.db[collection].find(filters).count()
        # else:
        #     return self.db[collection].find().count()

    def get_searchKey_progress(self, collection, searchKey):
        # print(collection+'_'+searchKey)
        documents = self.db[collection].aggregate(
                            [{
                                "$group": {
                                    "_id" : {
                                        "searchKeys":"$searchKeys",
                                        "title": "$title",
                                        "date":"$date",
                                        }
                                }
                            }, {
                                "$match":{
                                    '_id.searchKeys':searchKey
                                    }
                                }])
        return len(list(documents))

    def remove_all_documents(self, collection):
        return self.db[collection].drop() 

    def insert_relation(self, relation):
        relation['createDate'] = datetime.datetime.utcnow()
        relation['modifyDate'] = datetime.datetime.utcnow()
        relation['createUser'] = relation['user']
        relation['modifyUser'] = relation['user']
        relation.__delitem__('user')

        return self.db['Relations'].insert(relation)

    def delete_relation(self, id, ip):

        self.db['RelationLog'].insert({
            'action':'delete',
            'relation':self.db['Relations'].find_one({'_id': ObjectId(id)}),
            'date' : datetime.datetime.utcnow(),
            'ip' : ip
        })

        return self.db['Relations'].delete_one({'_id': ObjectId(id)})
    
    def get_relations(self, queryType, key):
        if queryType == 'reason':
            return self.db['Relations'].find({queryType:key})

        return self.db['Relations'].find({'$or':[{'objects.'+queryType:key},{'subjects.'+queryType :key}]})

    def get_relation_keyList(self, queryType, key):
        if queryType == 'reason':
            print('/^'+key+'/')
            return self.db['Relations'].aggregate([{'$project':{'reason':1}},{'$group':{'_id':'$reason'}},{'$match':{'_id':{'$regex':'^'+key}}}])

        return self.db['Relations'].aggregate([{'$project': {  "combined":  { '$setUnion': [ "$subjects."+queryType, "$objects."+queryType ]}}},{ "$unwind": "$combined" }, { "$group": {"_id": "$combined"}},{"$match":{"_id":{ '$regex': '^'+key} }} ])
    
    def update_relation(self, relation, ip):
        id = relation['_id']
        relation['modifyDate'] = datetime.datetime.utcnow()
        relation['modifyUser'] = relation['user']
        relation.__delitem__('user')
        relation.__delitem__('_id')

        self.db['RelationLog'].insert({
            'action':'update',
            'relation':self.db['Relations'].find_one({'_id': ObjectId(id)}),
            'date' : datetime.datetime.utcnow(),
            'user' :  relation['modifyUser'],
            'ip' : ip
        })

        return self.db['Relations'].update({'_id':ObjectId(id)},relation)
    
    def download_relations(self):
        return self.db['Relations'].aggregate([{ "$unwind": "$subjects" },{ "$unwind": "$objects" },{'$project':{
    "subjects":1,
    "reason":1,
    "objects.name": 1,
    "objects.idNumber": 1,
    "objects.memo": 1,
    "objects.relationType":{
                "$map": {
                    "input": "$objects.relationType",
                    "as": "el",
                    "in": "$$el.itemName"
                }
            },
    "createDate":1,
            "createUser":1,
            "modifyDate":1,
            "modifyUser":1,
    }}])

if __name__ == "__main__":
    db = DataAccess()

# db.Relations.aggregate([{'$project': {  "combined":  { '$setUnion': [ "$subjects.idNumber", "$objects.idNumber" ]}}},{ "$unwind": "$combined" }, { "$group": {"_id": "$combined"}},{"$match":{"_id":{ '$regex': /^/ } }} ])

    relations = [{
    "reason": '違約',
    "subjects": [{
        "name": 'A借款人A',
        "idNumber": 'A001',
        "memo": '主要'
    }, {
        "name": 'B借款人B',
        "idNumber": 'A002',
        "memo": '次要'
    }],
    "objects": [{
        "name": 'C關係人C',
        "idNumber": 'AC001',
        "memo": '同仁'
    }, {
        "name": 'D關係人D',
        "idNumber": 'D001',
        "memo": '親友'
    }],
    "user": 'test1',
}, {
    "reason": '高風險',
    "subjects": [{
        "name": 'E借款人E',
        "idNumber": 'AE001',
        "memo": '主要'
    }, {
        "name": 'F借款人F',
        "idNumber": 'F001',
        "memo": '次要'
    }],
    "objects": [{
        "name": 'G關係人G',
        "idNumber": 'AG001',
        "memo": '同仁'
    }, {
        "name": 'H關係人H',
        "idNumber": 'AH001',
        "memo": '親友'
    }],
   "user": 'test1',
}, {
    "reason": '高風險',
    "subjects": [{
        "name": 'E借款人E',
        "idNumber": 'AE001',
        "memo": '主要'
    }, {
        "name": 'F借款人F',
        "idNumber": 'F001',
        "memo": '次要'
    }],
    "objects": [{
        "name": 'G關係人G',
        "idNumber": 'AG001',
        "memo": '同仁'
    }, {
        "name": 'H關係人H',
        "idNumber": 'AH001',
        "memo": '親友'
    }],
     "user": 'test1',
}]

    # print(relations)
    for relation in relations:
        db.insert_relation(relation)
        # print(relation)
    # request = {
    #     "searchKeys": ["郭國勝"],
    #     "referenceKeys": ["臺中"]
    # }
    # documents = [
    #     {
    #         "searchKeys":["康業資本"],
    #         "referenceKeys":["RK1"],
    #         "tags":["tagA","tagB"],
    #         "title": "title A",
    #         "content":"content A"
    #     },
    #     {
    #          "searchKeys":["康業資本"],
    #         "referenceKeys":["RK2"],
    #         "tags":["tagA","tagC"],
    #         "title": "title B",
    #         "content":"content B"
    #     }
    # ]
    # # refKey = ['A']
    # refKey.append('B')

    # remove_request(db,id)
    # results=db.get_all_documents()
    # print(len(list(db.db['20180117141005057082-新華生科技'].aggregate([ {
    #                         "$group": {"_id" : {
    #                             "searchKeys":"$searchKeys",
    #                             "title": "$title",
    #                             "date":"$date",
    #                         }}},{"$match":{'_id.searchKeys':'玉珍'}}]))))
    # results = db.db.get
    # db.change_reference('5a4ca418f6fadc82283bba6a',['臺中','基隆'])
    # print(db.get_modified_requests().count())
    # print(db.db['Requests'].update_one({'_id': ObjectId("5a4ca418f6fadc82283bba6a")},{'$set': {'requestId':'1514966746.2558856'}}))
    # results = db.get_all_documents('1514966746.2558856',5,2),z


    # db.change_reference('5a4ca418f6fadc82283bba6a',['嚴永誠','基隆','魏樹達','台北','臺北'])
    # # print(db.get_documents_count('1514966746.2558856'))
    # for re in results:
    #     print(re['referenceKeys'])


    # for result in results :
    #     print(result['requestId'])
        # processing_requests(db,result['_id'])
        # insert_documents(db,str(result['requestId'])+result['searchKey'][0],documents)
    # result=add_request(db,request)
