from flask_restful import Resource, reqparse
from ..utils import response_wrapper
from ..controller.GetScatterDataController import GetScatterDataController
from . import api
from flask import request
import traceback
import ast

parser = reqparse.RequestParser(trim=True, bundle_errors=True)

class GetScatterDataApi(Resource):
    def post(self):
        try:
            json_data = request.get_json(force=True)

            list_keys = ['tgtthick', 'tgtwidth', 'tgtlength', 'dis_temp', 'fm_temp', 'date_range']
            string_keys = ['method']

            para = {}
            for key in list_keys:
                raw_val = json_data.get(key, "[]")
                try:
                    parsed_val = ast.literal_eval(raw_val)
                    para[key] = parsed_val if isinstance(parsed_val, list) else []
                except (ValueError, SyntaxError):
                    para[key] = []
            for key in string_keys:
                para[key] = json_data.get(key, "tsne")
        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")
        try:
            detial = GetScatterDataController(para)
            res = detial.run()
            return response_wrapper(res)
        except Exception as e:
            # print(f"业务逻辑执行错误: {e}")
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")
            # 服务器内部错误返回码

api.add_resource(GetScatterDataApi, '/v1.0/visual/getscatterdata')