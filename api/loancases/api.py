from flask import Blueprint, jsonify, g, request, current_app, make_response
from dataAccess.loancaseAccess import loancaseAccess
import json, os


apiLoancases = Blueprint('apiLoancases', __name__)

@apiLoancases.before_request
def before_request():
    apiLoancases.dataAccess = loancaseAccess()

@apiLoancases.route('/list', methods=['GET'])
def get_all_loancases():
    current_app.logger.info('get_all_loancases')
    
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
    
    for loancase in loancases: 
        results["data"].append({
            "_id":str(loancase["_id"]),
            "idNumber":loancase["idNumber"],
            "name":loancase["name"],
            "status":loancase["status"],
            "applyDate":loancase["applyDate"],
            "contactor":loancase["contactor"],
            "sales":loancase["sales"],
            "ticketCredit":loancase["ticketCredit"],
            "salesVisitDate":loancase["salesVisitDate"],
            "lastReplyDate":loancase["lastReplyDate"],
            "createDate":loancase["createDate"],
            "createUser":loancase["createUser"],
            "modifyDate":loancase["modifyDate"],
            "modifyUser":loancase["modifyUser"]
        })

    return jsonify(results)

@apiLoancases.route('/log/<id>', methods=['GET'])
def get_logs(id):
    current_app.logger.info('get_logs')
    
    result = apiLoancases.dataAccess.get_logs(id)

    ret =list( map(lambda x : {
            "action" : x["action"],
            "idNumber":x["loancase"]["idNumber"],
            "name":x["loancase"]["name"],
            "status":x["loancase"]["status"],
            "applyDate":x["loancase"]["applyDate"],
            "contactor":x["loancase"]["contactor"],
            "sales":x["loancase"]["sales"],
            "ticketCredit":x["loancase"]["ticketCredit"],
            "salesVisitDate":x["loancase"]["salesVisitDate"],
            "lastReplyDate":x["loancase"]["lastReplyDate"],
            "modifyDate":x["loancase"]["modifyDate"],
            "modifyUser":x["loancase"]["modifyUser"]
     } ,list(result)))
    
    print(ret)

    return jsonify(ret)

@apiLoancases.route('/add', methods=['POST'])
def add_loancase():
    print('add_loancases')
    data=json.loads(request.data)
    print(data)
    current_app.logger.info('add_loancases:'+ str(data))
    
    try:
        apiLoancases.dataAccess.insert_loancase(data)
    except:
        current_app.logger.error('error add_loancases')
        return make_response(jsonify("error"), 500) 

    return jsonify("recevied")

@apiLoancases.route('/update', methods=['PUT'])
def update_loancase():
    data=json.loads(request.data)
    print(data)
    current_app.logger.info('update_loancase:'+data['_id'])
    ip =  request.remote_addr

    try:
        apiLoancases.dataAccess.update_loancase(data, ip)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(str(e)), 500) 

    return jsonify("updated")

@apiLoancases.route('/key/<queryType>/<key>', methods=['GET'])
def get_loancase_keyList(queryType,key):
    print(queryType,key)
    results = apiLoancases.dataAccess.get_loancases_keyList(queryType,key)

    return jsonify(list(map(lambda x : x['_id'] ,list(results))))

@apiLoancases.route('/check/<queryType>/<key>', methods=['GET'])
def check_duplicate(queryType,key):
    print(queryType,key)
    results = apiLoancases.dataAccess.check_duplicate(queryType,key)

    return jsonify(results)

@apiLoancases.route('/delete', methods=['PUT'])
def delete_loancase():
    data=json.loads(request.data)
    current_app.logger.info('delete_loancase:'+ data['_id'])

    ip =  request.remote_addr
    try:
         apiLoancases.dataAccess.delete_loancase(data, ip)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(str(e)), 500) 

    return jsonify("deleted")

@apiLoancases.route('/<queryType>/<key>', methods=['GET'])
def get_loancases(queryType,key):
    current_app.logger.info('get_loancases')
    
    pageSize = request.args.get('pageSize', default =10, type = int)
    pageNumber = request.args.get('pageNumber', default = 1, type = int)

    try:
        result = apiLoancases.dataAccess.get_loancases(queryType,key,pageSize,pageNumber)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(str(e)), 500) 

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
    
    for loancase in loancases: 
        results["data"].append({
            "_id":str(loancase["_id"]),
            "idNumber":loancase["idNumber"],
            "name":loancase["name"],
            "status":loancase["status"],
            "applyDate":loancase["applyDate"],
            "contactor":loancase["contactor"],
            "sales":loancase["sales"],
            "ticketCredit":loancase["ticketCredit"],
            "salesVisitDate":loancase["salesVisitDate"],
            "lastReplyDate":loancase["lastReplyDate"],
            "createDate":loancase["createDate"],
            "createUser":loancase["createUser"],
            "modifyDate":loancase["modifyDate"],
            "modifyUser":loancase["modifyUser"]
        })
        
    return jsonify(results)