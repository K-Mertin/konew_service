# mongo.py
from flask import Flask, jsonify, request, g
from DataAccess import DataAccess
from flask_cors import CORS
from Logger import Logger
import json
import configparser
import logging
import os
import datetime

app = Flask('Flask-Service')
CORS(app)

@app.before_request
def before_request():
    g.dataAccess = DataAccess()

@app.route('/api/requests', methods=['GET'])
def get_all_requests():
    # app.logger.info('get_all_requests')
    pageSize = request.args.get('pageSize', default =10, type = int)
    pageNumber = request.args.get('pageNumber', default = 1, type = int)
    
    result = g.dataAccess.get_allPaged_requests(pageSize,pageNumber)
    requests =  result['data']
    totalCount = result["totalCount"]
    totalPages = int( totalCount/ pageSize) + 1

    results = {
        "pagination" : {
            "pageSize":pageSize,
            "pageNumber":pageNumber,
            "totalCount":totalCount,
            "totalPages":totalPages
        },
        "data" : []
    }
    
    # sortBy = request.args.get('sortBy', default = 'keys', type= str)
    # totalCount = g.dataAccess.get_documents_count(requestId)

    for r in requests:
        # print(g.dataAccess.get_searchKey_progress(r["requestId"],x['key']))
        results["data"].append({
            "_id":str(r["_id"]),
            "requestId":r["requestId"],
            "status":r["status"],
            "searchKeys":list(map(lambda x : x['key']+'('+str(g.dataAccess.get_searchKey_progress(r["requestId"],x['key']))+'/'+str(x['count'])+')', r['searchKeys']))  ,
            "referenceKeys":r["referenceKeys"],
            "createDate":r["createDate"]
        })
    # print((requests))
    return jsonify(results)

@app.route('/api/documents/<requestId>', methods=['GET'])
def get_all_documents(requestId):
    # app.logger.info('get_all_documents:'+ requestId)
    pageSize = request.args.get('pageSize', default = 10, type = int)
    pageNumber = request.args.get('pageNumber', default = 1, type = int)
    sortBy = request.args.get('sortBy', default = 'keys', type= str)
    filters = request.args.getlist('filters')
    totalCount = g.dataAccess.get_documents_count(requestId, filters)
    print(len(filters))
    documents = g.dataAccess.get_allPaged_documents(requestId,pageSize,pageNumber,sortBy,filters)

    totalPages = int(totalCount / pageSize) + 1

    results = {
        "pagination" : {
            "pageSize":pageSize,
            "pageNumber":pageNumber,
            "totalCount":totalCount,
            "totalPages":totalPages
        },
        "data" : []
    }
    # print(results)

    for doc in documents:
        results["data"].append({
            "title": doc["_id"]["title"],
            "searchKeys":doc["_id"]["searchKeys"],
            "referenceKeys":doc["_id"]["referenceKeys"],
            "tags":doc["_id"]["tags"],
            "source":doc["source"]
        })
    # print(results)
    return jsonify(results)

@app.route('/api/requests', methods=['POST'])
def add_request():
    data=json.loads(request.data)
    app.logger.info('add_request:'+ str(data['searchKeys']))

    g.dataAccess.add_request({
        "searchKeys": data['searchKeys'],
        "referenceKeys": data['referenceKeys']
    })
    return jsonify("recevied")

@app.route('/api/requests', methods=['PUT'])
def change_request():
    data=json.loads(request.data)
    app.logger.info('change_request:'+data['_id'])
    print(data['referenceKeys'])
    # print()
    g.dataAccess.change_request_reference(data['_id'],data['referenceKeys'])
    
    return jsonify("updated")

@app.route('/api/requests/delete', methods=['PUT'])
def remove_request():
    data=json.loads(request.data)
    app.logger.info('remove_request:'+data['_id'])
    # print(data)
    g.dataAccess.remove_request(data['_id'])
    
    return jsonify("deleted")

@app.route('/api/relation/key/<queryType>/<key>', methods=['GET'])
def get_relation_keyList(queryType,key):
    print(queryType,key)
    results = g.dataAccess.get_relation_keyList(queryType,key)

    return jsonify(list(map(lambda x : x['_id'] ,list(results))))

@app.route('/api/relation/<queryType>/<key>', methods=['GET'])
def get_relations(queryType,key):
    results = g.dataAccess.get_relations(queryType,key)

    relations = [] 
    for r in results:
        relations.append({
            '_id':str(r['_id']),
            'reason':r['reason'],
            'subjects':r['subjects'],
            'objects':r['objects'],
            'createDate':r['createDate'],
            'createUser':r['createUser'],
            'modifyDate':r['modifyDate'],
            'modifyUser':r['modifyUser']
        })

    return jsonify(relations)

@app.route('/api/relation', methods=['POST'])
def add_relation():
    
    data=json.loads(request.data)
    print(data)
    app.logger.info('add_relation:'+ str(data))

    g.dataAccess.insert_relation(data)

    return jsonify("recevied")

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
