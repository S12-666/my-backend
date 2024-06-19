from datetime import datetime
from flask_restful import Resource, reqparse
from ..utils import getArgsFromParser
from ..controller.GetNumberOfPlatesByTime import GetLabelNumberByTimeController
from . import api

parser = reqparse.RequestParser(trim=True, bundle_errors=True)
class GetNumberOfPlatesByTimeApi(Resource):
    def get(self):
        args = getArgsFromParser(parser, ['date'])
        date1 = args['date']
        d1 = datetime.strptime(date1, '%Y-%m-%d')
        d2 = datetime(d1.year, d1.month + 1, d1.day)
        date2 = d2.strftime('%Y-%m-%d')

        labels = GetLabelNumberByTimeController(date1, date2)
        res = labels.run()

        response = {
            'code': 0,
            'msg': 'ok',
            'data': res
        }

        return response, 200, {'Access-Control-Allow-Origin': '*'}

api.add_resource(GetNumberOfPlatesByTimeApi, '/v1.0/visualization/getNumberOfPlatesByTime')
