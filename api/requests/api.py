from flask import Blueprint, jsonify, g, request, current_app
from dataAccess.requestAccess import requestAccess
import json, os
import decorators

apiRequests = Blueprint('requests', __name__)

@apiRequests.before_request
# @decorators.token_required
def before_request():
    apiRequests.dataAccess = requestAccess()
    # print(current_user)

@apiRequests.route('/list', methods=['GET'])
def get_all_requests():
    # current_app.logger.info('get_all_requests')
    pageSize = request.args.get('pageSize', default =10, type = int)
    pageNumber = request.args.get('pageNumber', default = 1, type = int)
    
    result = apiRequests.dataAccess.get_allPaged_requests(pageSize,pageNumber)
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
    # totalCount = apiRequests.dataAccess.get_documents_count(requestId)

    for r in requests:
        # print(apiRequests.dataAccess.get_searchKey_progress(r["requestId"],x['key']))
        results["data"].append({
            "_id":str(r["_id"]),
            "requestId":r["requestId"],
            "status":r["status"],
            "searchKeys":list(map(lambda x : x['key']+'('+str(apiRequests.dataAccess.get_searchKey_progress(r["requestId"],x['key']))+'/'+str(x['count'])+')', r['searchKeys']))  ,
            "referenceKeys":r["referenceKeys"],
            "createDate":r["createDate"]
        })
    # print((requests))
    return jsonify(results)

@apiRequests.route('/documents/<requestId>', methods=['GET'])
def get_all_documents(requestId):
    # current_app.logger.info('get_all_documents:'+ requestId)
    pageSize = request.args.get('pageSize', default = 10, type = int)
    pageNumber = request.args.get('pageNumber', default = 1, type = int)
    sortBy = request.args.get('sortBy', default = 'keys', type= str)
    filters = request.args.getlist('filters')
    totalCount = apiRequests.dataAccess.get_documents_count(requestId, filters)
    print(len(filters))
    documents = apiRequests.dataAccess.get_allPaged_documents(requestId,pageSize,pageNumber,sortBy,filters)

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

@apiRequests.route('/add', methods=['POST'])
def add_request():
    data=json.loads(request.data)
    current_app.logger.info('add_request:'+ str(data['searchKeys']))

    apiRequests.dataAccess.add_request({
        "searchKeys": data['searchKeys'],
        "referenceKeys": data['referenceKeys']
    })
    return jsonify("recevied")

@apiRequests.route('/update', methods=['PUT'])
def change_request():
    data=json.loads(request.data)
    current_app.logger.info('change_request:'+data['_id'])
    print(data['referenceKeys'])
    # print()
    apiRequests.dataAccess.change_request_reference(data['_id'],data['referenceKeys'])
    
    return jsonify("updated")

@apiRequests.route('/delete', methods=['PUT'])
def remove_request():
    data=json.loads(request.data)
    current_app.logger.info('remove_request:'+data['_id'])
    # print(data)
    apiRequests.dataAccess.remove_request(data['_id'])
    
    return jsonify("deleted")
