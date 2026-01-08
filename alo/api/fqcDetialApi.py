from flask_restful import Resource, reqparse
from ..utils import response_wrapper
from ..controller.FQCDetialController import FQCDetialController
from . import api
from flask import request
import traceback

parser = reqparse.RequestParser(trim=True, bundle_errors=True)

class GetFQCDetialApi(Resource):
    def post(self):
        try:
            json_data = request.get_json(force=True)
            upid = json_data.get('upid', '')
            slab_id = json_data.get('slabid', '')

            para = {
                'upid': upid,
                'slabid': slab_id
            }
        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")
        try:
            detial_ctrl = FQCDetialController(para)
            res = detial_ctrl.run()
            return response_wrapper(res)
        except Exception as e:
            # print(f"业务逻辑执行错误: {e}")
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")
            # 服务器内部错误返回码

api.add_resource(GetFQCDetialApi, '/v1.0/pidas/getFQCDetial')