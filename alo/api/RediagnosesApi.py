# RediagnosesApi
from flask_restful import Resource, reqparse
import json
from ..utils import getArgsFromParser
from ..controller.Rediagnoses import RediagnosesController
parser = reqparse.RequestParser(trim=True, bundle_errors=True)
from . import api
class RediagnosesApi(Resource):
    def post(self):
        args = getArgsFromParser(parser, ['condition', 'testData', 'selectedKey'])
        condition = json.loads(args['condition'])
        testData = json.loads(args['testData'])
        selectedKey = json.loads(args['selectedKey'])
        rediag = RediagnosesController(condition, testData, selectedKey)
        res = rediag.run()
        response = {
            'code': 0,
            'msg': 'ok',
            'data': res
        }
        return response, 200, {'Access-Control-Allow-Origin': '*'}

api.add_resource(RediagnosesApi, '/v1.0/visualization/rediagnoses')
