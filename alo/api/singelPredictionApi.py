from flask_restful import Resource
from ..utils import response_wrapper
from ..controller.SingelPredictionController import SingelPredictionController
from . import api
from flask import request
import traceback


class singelPredictionApi(Resource):
    def post(self):
        try:
            json_data = request.get_json(force=True)

            upid = json_data.get('upid')
            status_cooling = json_data.get('status_cooling')
            platetype = json_data.get('platetype')
            label = json_data.get('label')

            para = {
                'upid': upid,
                'status_cooling': status_cooling,
                'platetype': platetype,
                'label' : label
            }

        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")

        try:
            # 3. 调用控制器
            detial_ctrl = SingelPredictionController(para)
            res = detial_ctrl.run()
            return response_wrapper(res)

        except Exception as e:
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")


api.add_resource(singelPredictionApi, '/v1.0/prediction/singelplate')