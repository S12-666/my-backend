from flask_restful import Resource
from ..utils import response_wrapper
from ..controller.SendPredictionController import SendPredictionController
from . import api
from flask import request
import traceback


class sendPredictionApi(Resource):
    def post(self):
        try:
            json_data = request.get_json(force=True)

            upid = json_data.get('upid')
            msg = json_data.get('msg')
            label = json_data.get('pred_label')

            para = {
                'upid': upid,
                'msg': msg,
                'label': label
            }

        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")

        try:
            # 3. 调用控制器
            detial_ctrl = SendPredictionController(para)
            res = detial_ctrl.run()
            return response_wrapper(res)

        except Exception as e:
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")


api.add_resource(sendPredictionApi, '/v1.0/prediction/sendPredLabel')