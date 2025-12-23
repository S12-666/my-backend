from flask_restful import Resource, reqparse
from ..utils import getArgsFromParser
from ..controller.getSpecCountController import GetSpecCountController
from . import api

parser = reqparse.RequestParser(trim=True, bundle_errors=True)

class GetSpecCountByTimeApi(Resource):
    def get(self, req_type):
        arg_list = ['startTime', 'endTime']
        if req_type == 'range':
            arg_list = arg_list + ['pageNum', 'pageSize']

        args = getArgsFromParser(parser, arg_list)

        key_ins = GetSpecCountController(args, req_type)
        res = key_ins.run()

        response = {
            'code': 200,
            'msg': 'ok',
            'data': res
        }

        return response, 200, {'Access-Control-Allow-Origin': '*'}

api.add_resource(GetSpecCountByTimeApi, '/v1.0/pidas/getSpecCountByTime/<req_type>')
