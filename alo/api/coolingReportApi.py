from flask_restful import Resource, reqparse
from ..utils import response_wrapper
from ..controller.CoolingReportController import CoolingReportController
from . import api
from flask import request
import traceback

parser = reqparse.RequestParser(trim=True, bundle_errors=True)

class GetCoolingReportApi(Resource):
    def post(self):
        try:
            json_data = request.get_json(force=True)
            daterange = json_data.get('daterange', [])
            upid = json_data.get('upid', '')
            slab_id = json_data.get('slabid', '')

            para = {
                'daterange': daterange,
                'upid': upid,
                'slabid': slab_id
            }
        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")
        try:
            report_ctrl = CoolingReportController(para)
            res = report_ctrl.run()
            return response_wrapper(res)
        except Exception as e:
            # print(f"业务逻辑执行错误: {e}")
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")
            # 服务器内部错误返回码

api.add_resource(GetCoolingReportApi, '/v1.0/pidas/getCoolingReport')