from flask import Blueprint, jsonify, g, request, current_app
# from DataAccess import DataAccess
from dataAccess.relationAccess import relationAccess
from werkzeug import secure_filename
import json, os

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv'])


apiRelations = Blueprint('relations', __name__)

@apiRelations.before_request
def before_request():
    apiRelations.dataAccess = relationAccess()

@apiRelations.route('/key/<queryType>/<key>', methods=['GET'])
def get_relation_keyList(queryType,key):
    print(queryType,key)
    results = apiRelations.dataAccess.get_relation_keyList(queryType,key)

    return jsonify(list(map(lambda x : x['_id'] ,list(results))))

@apiRelations.route('/<queryType>/<key>', methods=['GET'])
def get_relations(queryType,key):
    relations = apiRelations.dataAccess.get_relations(queryType,key)

    result = [] 
    for r in relations:
        result.append({
            '_id':str(r['_id']),
            'reason':r['reason'],
            'subjects':r['subjects'],
            'objects':r['objects'],
            'createDate':r['createDate'],
            'createUser':r['createUser'],
            'modifyDate':r['modifyDate'],
            'modifyUser':r['modifyUser']
        })

    return jsonify(result)

@apiRelations.route('/add', methods=['POST'])
def add_relation():
    print('add_relation')
    data=json.loads(request.data)
    print(data)
    current_app.logger.info('add_relation:'+ str(data))

    apiRelations.dataAccess.insert_relation(data)

    return jsonify("recevied")

@apiRelations.route('/<id>', methods=['DELETE'])
def delete_relation(id):
    current_app.logger.info('delete_relation:'+ id)
    ip =  request.remote_addr
    apiRelations.dataAccess.delete_relation(id, ip)

    return jsonify("deleted")

@apiRelations.route('/update', methods=['PUT'])
def update_relation():
    data=json.loads(request.data)
    print(data)
    current_app.logger.info('update_relation:'+data['_id'])
    ip =  request.remote_addr

    apiRelations.dataAccess.update_relation(data, ip)

    return jsonify("updated")


@apiRelations.route('/download', methods=['GET'])
def download_relations():
    relations = apiRelations.dataAccess.download_relations()
    current_app.logger.info('get All')

    result = [] 
    for r in relations:

        result.append({
            '_id':str(r['_id']),
            'reason':r['reason'],
            'subjects':r['subjects'],
            'objects':  r['objects'],
            'createDate':r['createDate'],
            'createUser':r['createUser'],
            'modifyDate':r['modifyDate'],
            'modifyUser':r['modifyUser']
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
        
        file = open(filename,'r') 
        print (file.read()) 

        return jsonify('success')
    else:
        return jsonify('failed')
