from flask import Blueprint, jsonify, g, request, current_app
from loancaseAccess import loancaseAccess
import json, os

apiLoancases = Blueprint('apiLoancases', __name__)

@apiLoancases.before_request
def before_request():
    apiLoancases.dataAccess = loancaseAccess()

@apiLoancases.route('/list', methods=['GET'])
def get_all_requests():
    current_app.logger.info('get_all_requests')
    
    pageSize = request.args.get('pageSize', default =10, type = int)
    pageNumber = request.args.get('pageNumber', default = 1, type = int)
    
    result = apiLoancases.dataAccess.get_allPaged_loancases(pageSize,pageNumber)
    loancases =  result['data']
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

    for l in loancases:
        
        results["data"].append({
            "_id":str(l["_id"]),
            "idNumber":l["idNumber"],
            "status":l["name"],
            "status":l["status"],
        })

    return jsonify(results)
