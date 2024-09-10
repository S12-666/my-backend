from flask_restful import Resource, reqparse
from ..utils import getArgsFromParser
from ..controller.GetScatterDataByTime import GetScatterDataByTimeController
from . import api

parser = reqparse.RequestParser(trim=True, bundle_errors=True)
class GetScatterDataByTimeApi(Resource)     :
    def get(self, type, fault_type):
        args = getArgsFromParser(parser, ['startTime', 'endTime', 'fault_type'])
        startTime = args['startTime']
        endTime = args['endTime']

        scatter = GetScatterDataByTimeController(startTime, endTime, type, fault_type)
        res = scatter.run()

        response = {
            'code': 0,
            'msg': 'ok',
            'data': res
        }

        return response, 200, {'Access-Control-Allow-Origin': '*'}

api.add_resource(GetScatterDataByTimeApi, '/v1.0/visualization/getScatterDataByTime/<type>/<fault_type>')