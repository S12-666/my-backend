from flask_restful import Resource, reqparse
import json
from ..utils import getArgsFromParser, response_wrapper
from ..methods.define import specifications
from ..controller.DiagnosesByUpids import DiagnosesDataByUpidsController
from . import api

parser = reqparse.RequestParser(trim=True, bundle_errors=True)
class GetDiagnosesDataByUpidsApi(Resource):
    def post(self, fault_type):

        try:
            args = getArgsFromParser(parser, specifications + ['upids'])

            para = {}
            for key in args:
                para[key] = json.loads(args[key])
            para['fault_type'] = fault_type
        except:
            return response_wrapper({}, 2)

        try:
            diag = DiagnosesDataByUpidsController(para)
            diag_res, platetype_range = diag.run()

            if type(diag_res) != list:
                return response_wrapper({}, 4, 'no train data')

            res = {
                'diagnosis': diag_res,
                'platetype_range': platetype_range
            }
            return response_wrapper(res)
        except Exception as e:
            print(e)
            return response_wrapper({}, 5)

api.add_resource(GetDiagnosesDataByUpidsApi, '/v1.0/visualization/getDiagnosesDataByUpids/<fault_type>')