from ..utils import response_wrapper
from ..controller.GetPredictionUpidController import GetPredictionUpidController
from . import api
import traceback
from flask_restful import Resource, reqparse

class GetPredictionUpidApi(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            # parser.add_argument('upid', type=str, location='args', required=True)
            parser.add_argument('upid', type=str, location='args', required=True, help="UPID cannot be empty")
            args = parser.parse_args()
            upid = args['upid']
        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")

        try:
            basic_data = GetPredictionUpidController(upid)
            res = basic_data.run()
            return response_wrapper(res)

        except Exception as e:
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")

api.add_resource(GetPredictionUpidApi, '/v1.0/prediction/getPredictionUpid')