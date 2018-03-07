from flask import Blueprint, jsonify, g, request, current_app
from dataAccess.relationAccess import relationAccess
from werkzeug import secure_filename
import json
import os
import xlrd

ALLOWED_EXTENSIONS = set(['xlsx'])


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
    # print(data)
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
    # print(data)
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
    user = request.form['user']

    file = request.files['Document']
    if file and allowed_file(file.filename):
        filename = 'uploadTemp.xlsx'
        #secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        processFile(filename, user)

        return jsonify('success')
    else:
        return jsonify('檔案格式不符')


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

    # print(ret)

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

    # print(idNumber)

    for link in ret:
        if link in edgeList:
            continue
        edgeList.append(link)

        if link['objects']['idNumber'] != idNumber and not link['objects']['idNumber'] in nodeList:
            get_connections(link['objects']['idNumber'], nodeList, edgeList)
        if link['subjects']['idNumber'] != idNumber and not link['subjects']['idNumber'] in nodeList:
            get_connections(link['subjects']['idNumber'], nodeList, edgeList)
            
            
    ret = transformGraph(edgeList)
    return jsonify(ret)

def get_connections(idNumber, processList, edgeList):
    processList.append(idNumber)
    result = apiRelations.dataAccess.get_connections(idNumber)
    # print(idNumber)

    ret = list(map(lambda x: {
        'subjects': x['subjects'],
        'objects': x['objects'],
        'reason' : x['reason']
    }, list(result)))
    
    for link in ret:
        if link in edgeList:
            continue
        edgeList.append(link)

        if link['objects']['idNumber'] and link['objects']['idNumber'] != idNumber and not link['objects']['idNumber'] in processList:
            get_connections(link['objects']['idNumber'], processList, edgeList)
        if link['subjects']['idNumber'] and link['subjects']['idNumber'] != idNumber and not link['subjects']['idNumber'] in processList:
            get_connections(link['subjects']['idNumber'], processList, edgeList)

    return

def transformGraph(edgeList):
    nodes = []
    links = []
    nodeInfo = []
    for edge in edgeList:
        node = {'name': edge['subjects']['name'], 'idNumber': edge['subjects']['idNumber'],'reason':'' ,'memo':[],'relations':[]}
        
        if node not in nodes:
            nodes.append(node)
            nodeInfo.append({'reason':edge['reason'], 'memo':[edge['subjects']['memo']],'relations':['']})

        source = nodes.index(node)

        node = {'name': edge['objects']['name'], 'idNumber': edge['objects']['idNumber'],'reason':'','memo':[],'relations':[]}
        
        if node not in nodes:
            nodes.append(node)
            nodeInfo.append({'reason':'', 'memo':[edge['objects']['memo']],'relations':['']})

        target = nodes.index(node)

        if nodeInfo[source]['reason'] == '':
            nodeInfo[source]['reason'] = edge['reason']

        if edge['subjects']['memo'] not in nodeInfo[source]['memo']:
            nodeInfo[source]['memo']=nodeInfo[source]['memo']+[edge['subjects']['memo']]        

        if edge['objects']['memo'] not in nodeInfo[target]['memo']:
            nodeInfo[target]['memo']=nodeInfo[target]['memo']+[edge['objects']['memo']]


        edge['objects']['relationType'] = [nodes[source]['name']+'->'+ nodes[target]['name'] +'=>'+val for val in  edge['objects']['relationType']]

        if edge['objects']['relationType'] not in nodeInfo[target]['relations']:
            nodeInfo[target]['relations']=nodeInfo[target]['relations']+[edge['objects']['relationType']]
        


        links.append({ 'source': source, 'target': target, 'value': 1 })
    
    for i in range(len(nodes)):
        nodes[i]['reason'] = nodeInfo[i]['reason']
        nodes[i]['memo'] = [val for sublist in nodeInfo[i]['memo'] for val in sublist]
        nodes[i]['relations'] = [val for sublist in nodeInfo[i]['relations'] for val in sublist]

    return {'nodes':nodes, 'links':links }

@apiRelations.route('/check/<target>/<id>', methods=['GET'])
def check_duplicate(target,id):
    results = apiRelations.dataAccess.check_duplicate(target,id)
    return jsonify(results)

def processFile(filename, user):
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheets()[0]
    
    for i in range(sheet.nrows):
        relation = {
            'reason':'',
            'subjects': [{}],
            'objects': [{}],
            'user': user
        }

        if i == 0:
            continue

        relation['reason'] = sheet.row_values(i)[1]

        subjects = []
        subject = {}

        subject['name'] = sheet.row_values(i)[2] if sheet.row_values(i)[2] != '' else None
        subject['idNumber'] = str(sheet.row_values(i)[3]).replace('.0','') if sheet.row_values(i)[3] != '' else None
        subject['memo'] = sheet.row_values(i)[4].split(';;') if sheet.row_values(i)[4] != '' else []

        if not subject['name'] and not subject['idNumber'] :
                continue


        subjects.append(subject)

        relation['subjects'] = subjects

        objects = []
        obj = {}
        obj['name'] = sheet.row_values(i)[5]  if sheet.row_values(i)[5] != '' else None
        obj['idNumber'] = sheet.row_values(i)[6]  if sheet.row_values(i)[6] != '' else None
        obj['relationType'] = sheet.row_values(i)[7].split(';;') if sheet.row_values(i)[7] != '' else  ['NA']
        obj['memo'] = []

        if not obj['name']  and not obj['idNumber'] :
            obj['name'] = 'NA'
        
        objects.append(obj)
        
        j = 8
        while j < sheet.ncols: 
            obj = {}
            obj['name'] = sheet.row_values(i)[j] if sheet.row_values(i)[j] != '' else None
            obj['idNumber'] = str(sheet.row_values(i)[j+1]).replace('.0','') if sheet.row_values(i)[j+1] != '' else None
            obj['relationType'] = sheet.row_values(i)[j+2].split(';;') if sheet.row_values(i)[j+2] != '' else ['NA']
            obj['memo'] = sheet.row_values(i)[j+3].split(';;') if sheet.row_values(i)[j+3] != '' else []

            if not obj['name']  and not  obj['idNumber'] :
                j+=4
                continue
                
            objects.append(obj)
            j+=4

        relation['objects'] = objects
        importRelation(relation)
        # print(relation)

def importRelation(relation):
    idNumber = relation['subjects'][0]['idNumber']

    ret = apiRelations.dataAccess.get_relation(idNumber)
    # print(ret)
    if ret:
        ret['reason'] = relation['reason']
        ret['subjects'][0]['name'] = relation['subjects'][0]['name']

        if len(ret['subjects'][0]['memo']) > 0:
           ret['subjects'][0]['memo']= ret['subjects'][0]['memo']+ relation['subjects'][0]['memo']
        else:
            ret['subjects'][0]['memo'] =  relation['subjects'][0]['memo']
        
        objIdList = list(map(lambda x:x['idNumber'], ret['objects']))
        # print (objIdList)

        for obj in relation['objects']:
            if obj['idNumber'] and obj['idNumber'] in objIdList:
                for ret_obj in ret['objects']:
                    if ret_obj['idNumber'] == obj['idNumber']:
                        
                        ret_obj['name'] = obj['name']

                        for memo in obj['memo']:
                            if memo not in ret_obj['memo']:
                                ret_obj['memo'].append(memo)

                        for relationType in obj['relationType']:
                            if relationType not in ret_obj['relationType']:
                                ret_obj['relationType'].append(relationType)
            else:
                ret['objects'].append(obj)

        
        # ret['objects'] = relation['objects']
        ret['_id'] = str(ret['_id'])
        ret['user'] = relation['user']
        
        ret = apiRelations.dataAccess.update_relation(ret, '')
    else:
        ret = apiRelations.dataAccess.insert_relation(relation)

