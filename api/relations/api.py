from flask import Blueprint, jsonify, g, request, current_app
from dataAccess.relationAccess import relationAccess
from werkzeug import secure_filename
import json
import os

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv'])


apiRelations = Blueprint('relations', __name__)


@apiRelations.before_request
def before_request():
    apiRelations.dataAccess = relationAccess()


@apiRelations.route('/key/<queryType>/<key>', methods=['GET'])
def get_relation_keyList(queryType, key):
    print(queryType, key)
    results = apiRelations.dataAccess.get_relation_keyList(queryType, key)

    return jsonify(list(map(lambda x: x['_id'], list(results))))


@apiRelations.route('/<queryType>/<key>', methods=['GET'])
def get_relations(queryType, key):
    relations = apiRelations.dataAccess.get_relations(queryType, key)

    result = []
    for r in relations:
        result.append({
            '_id': str(r['_id']),
            'reason': r['reason'],
            'subjects': r['subjects'],
            'objects': r['objects'],
            'status': r['status'],
            'createDate': r['createDate'],
            'createUser': r['createUser'],
            'modifyDate': r['modifyDate'],
            'modifyUser': r['modifyUser']
        })

    return jsonify(result)


@apiRelations.route('/add', methods=['POST'])
def add_relation():
    print('add_relation')
    data = json.loads(request.data)
    print(data)
    current_app.logger.info('add_relation:' + str(data))

    apiRelations.dataAccess.insert_relation(data)

    return jsonify("recevied")


@apiRelations.route('/<id>/<user>', methods=['DELETE'])
def delete_relation(id, user):
    current_app.logger.info('delete_relation:' + id)
    ip = request.remote_addr
    apiRelations.dataAccess.delete_relation(id, user, ip)

    return jsonify("deleted")


@apiRelations.route('/update', methods=['PUT'])
def update_relation():
    data = json.loads(request.data)
    print(data)
    current_app.logger.info('update_relation:'+data['_id'])
    ip = request.remote_addr

    apiRelations.dataAccess.update_relation(data, ip)

    return jsonify("updated")


@apiRelations.route('/download', methods=['GET'])
def download_relations():
    relations = apiRelations.dataAccess.download_relations()
    current_app.logger.info('get All')

    result = []
    for r in relations:

        result.append({
            '_id': str(r['_id']),
            'reason': r['reason'],
            'subjects': r['subjects'],
            'objects':  r['objects'],
            'status': r['status'],
            'createDate': r['createDate'],
            'createUser': r['createUser'],
            'modifyDate': r['modifyDate'],
            'modifyUser': r['modifyUser']
        })

    return jsonify(result)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@apiRelations.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['Document']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        file = open(filename, 'r')
        print(file.read())

        return jsonify('success')
    else:
        return jsonify('failed')


@apiRelations.route('/log/<id>', methods=['GET'])
def get_logs(id):
    current_app.logger.info('get_logs')

    result = apiRelations.dataAccess.get_logs(id)

    ret = list(map(lambda x: {
        "action": x["action"],
        'reason': x['relation']['reason'],
        'subjects': x['relation']['subjects'],
        'objects': x['relation']['objects'],
        'status': x['relation']['status'],
        'modifyDate': x['relation']['modifyDate'],
        'modifyUser': x['relation']['modifyUser']
    }, list(result)))

    print(ret)

    return jsonify(ret)
    
@apiRelations.route('/network/<idNumber>', methods=['GET'])
def get_network(idNumber):
    nodeList = [idNumber]
    edgeList = []
    result = apiRelations.dataAccess.get_connections(idNumber)
    
    ret = list(map(lambda x: {
        'subjects': x['subjects'],
        'objects': x['objects'],
        'reason' : x['reason']
    }, list(result)))

    print(idNumber)

    for link in ret:
        if link in edgeList:
            continue
        edgeList.append(link)

        if link['objects']['idNumber'] != idNumber and not link['objects']['idNumber'] in nodeList:
            get_connections(link['objects']['idNumber'], nodeList, edgeList)
        if link['subjects']['idNumber'] != idNumber and not link['subjects']['idNumber'] in nodeList:
            get_connections(link['subjects']['idNumber'], nodeList, edgeList)
            
            
    transformGraph(edgeList)
    return jsonify(list(ret))

def get_connections(idNumber, processList, edgeList):
    processList.append(idNumber)
    result = apiRelations.dataAccess.get_connections(idNumber)
    print(idNumber)

    ret = list(map(lambda x: {
        'subjects': x['subjects'],
        'objects': x['objects'],
        'reason' : x['reason']
    }, list(result)))
    
    for link in ret:
        if link in edgeList:
            continue
        edgeList.append(link)

        if link['objects']['idNumber'] != idNumber and not link['objects']['idNumber'] in processList:
            get_connections(link['objects']['idNumber'], processList, edgeList)
        if link['subjects']['idNumber'] != idNumber and not link['subjects']['idNumber'] in processList:
            get_connections(link['subjects']['idNumber'], processList, edgeList)

    return

def transformGraph(edgeList):
    nodes = []
    links = []
    nodeInfo = []
    for edge in edgeList:
        node = {'name': edge['subjects']['name'], 'idNumber': edge['subjects']['idNumber']}
        if node not in nodes:
            nodes.append(node)
            nodeInfo.append({'memo':[edge['subjects']['memo']]})

        source = nodes.index(node)
        # nodeInfo[nodes.index(node)]=nodeInfo[nodes.index(node)].append( edge['subjects']['memo'])

        node = {'name': edge['objects']['name'], 'idNumber': edge['objects']['idNumber']}
        if node not in nodes:
            nodes.append(node)
            nodeInfo.append({'memo':[edge['objects']['memo']],'relations':[edge['objects']['relationType']]})
        target = nodes.index(node)
        
        links.append({ 'source': source, 'target': target, 'value': 1 })
        
    print(links)
    print(nodes)
    print(nodeInfo)
       