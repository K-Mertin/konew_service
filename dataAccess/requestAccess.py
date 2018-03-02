from DataAccess import DataAccess
import pymongo
import datetime
import time
from bson.objectid import ObjectId
import re
import logging
import os

class requestAccess(DataAccess):

    def add_request(self, request):
        self.logger.logger.info('add_request:' + str(request['searchKeys']))
        request['status'] = 'created'
        request['createDate'] = datetime.datetime.utcnow()
        request['requestId'] = str(datetime.datetime.now().strftime(
            '%Y%m%d%H%M%S%f'))+'-'+request['searchKeys'][0]
        request['searchKeys'] = list(
            map(lambda x: {"key": x, "count": 0}, request['searchKeys']))
        return self.db['Requests'].insert(request)

    def change_request_reference(self, id, refKey):
        self.logger.logger.info('change_request_reference:' + id + str(refKey))
        return self.db['Requests'].update_one({'_id': ObjectId(id)}, {'$set': {'referenceKeys': refKey, 'status': 'modified'}})

    def update_document_reference(self, collection, id, referenceKeys):
        return self.db[collection].update_one({'_id': ObjectId(id)}, {'$set': {'referenceKeys': referenceKeys}})

    def get_allPaged_requests(self, pageSize=10, pageNum=1):
        skips = pageSize * (pageNum - 1)
        totalCount = self.db['Requests'].find(
            {'status': {"$in": ['modified', 'created', 'processing', 'finished', 'failed']}}).count()

        result = {
            "totalCount": totalCount,
            "data": self.db['Requests'].find({'status': {"$in": ['modified', 'created', 'processing', 'finished', 'failed']}}).sort("createDate", pymongo.DESCENDING).skip(skips).limit(pageSize)
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
        return self.db['Requests'].update_one({'_id': ObjectId(id), 'searchKeys.key': searchKey}, {'$set': {'status': 'processing', 'searchKeys.$.count': totalCount}})

    def finish_requests(self, id):
        return self.db['Requests'].update_one({'_id': ObjectId(id)}, {'$set': {'status': 'finished'}})

    def remove_request(self, id):
        self.logger.logger.info('remove_request:' + id)
        return self.db['Requests'].update_one({'_id': ObjectId(id)}, {'$set': {'status': 'removed'}})

    def insert_documents(self, collection, documents):
        return self.db[collection].insert_many(documents)

    def get_allPaged_documents(self, collection='1514966746.2558856', pageSize=10, pageNum=1, sortBy="keys", filters=[]):
        skips = pageSize * (pageNum - 1)
        print(filters)
        filters = list(map(lambda x: [{"$or": [{'_id.searchKeys': x}, {
                       '_id.referenceKeys': x}, {'_id.tags': x}]}], filters))
        filters = sum(filters, [])

        aggregateList = []
        aggregateList.append(
            {
                "$project": {
                    "searchKeys": 1,
                    "referenceKeys": 1,
                    "tags": 1,
                    "title": 1,
                    "content": 1,
                    "source": 1,
                    "date": 1,
                    "rkLength": {"$size": "$referenceKeys"},
                    "skLength": {"$size": "$searchKeys"},
                }}
        )
        aggregateList.append(
            {
                "$group": {"_id": {
                    "searchKeys": "$searchKeys",
                    "referenceKeys": "$referenceKeys",
                    "tags": "$tags",
                    "title": "$title",
                    # "source":"$source",
                    "date": "$date",
                    "rkLength": "$rkLength",
                                "skLength": "$skLength",
                }, "source": {"$first": "$source"}}}
        )

        if len(filters) > 0:
            aggregateList.append({"$match": {"$and": filters}})

        if sortBy == "keys":
            aggregateList.append(
                {"$sort": {"_id.skLength": -1, "_id.rkLength": -1, "_id.date": -1}})
        else:
            aggregateList.append(
                {"$sort": {"_id.skLength": -1, "_id.date": -1, "_id.rkLength": -1}})

        print(aggregateList)
        aggregateList.append({"$skip": skips})

        aggregateList.append({"$limit": pageSize})

        return self.db[collection].aggregate(aggregateList)

    def get_documents_count(self, collection, filters=[]):
        filters = list(map(lambda x: [{"$or": [{'_id.searchKeys': x}, {
                       '_id.referenceKeys': x}, {'_id.tags': x}]}], filters))
        filters = sum(filters, [])

        aggregateList = []

        aggregateList.append(
            {
                "$group": {"_id": {
                    "searchKeys": "$searchKeys",
                    "referenceKeys": "$referenceKeys",
                    "tags": "$tags",
                    "title": "$title",
                    # "source":"$source",
                    "date": "$date",
                    "skLength": "$skLength",
                }, "source": {"$first": "$source"}}}
        )

        if len(filters) > 0:
            aggregateList.append({"$match": {"$and": filters}})

        return len(list(self.db[collection].aggregate(aggregateList)))

    def get_searchKey_progress(self, collection, searchKey):
        documents = self.db[collection].aggregate(
            [{
                "$group": {
                    "_id": {
                        "searchKeys": "$searchKeys",
                        "title": "$title",
                        "date": "$date",
                    }
                }
            }, {
                "$match": {
                    '_id.searchKeys': searchKey
                }
            }])
        return len(list(documents))

    def remove_all_documents(self, collection):
        return self.db[collection].drop()


if __name__ == "__main__":
    db = requestAccess()
