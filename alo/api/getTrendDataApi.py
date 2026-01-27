from ..utils import response_wrapper
from ..controller.GetTrendDataController import GetTrendDataController, GetSpecBoxController
from . import api
import traceback
import calendar
from datetime import datetime
from flask_restful import Resource, reqparse

class GetTrendDataApi(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('date', type=str, location='args', required=True, help="Date cannot be empty")
            args = parser.parse_args()
            target_month_str = args['date']  # "2021-06"
            start_date = f"{target_month_str}-01"  # "2021-06-01"
            dt_obj = datetime.strptime(target_month_str, "%Y-%m")
            year = dt_obj.year
            month = dt_obj.month
            _, last_day = calendar.monthrange(year, month)
            end_date = f"{target_month_str}-{last_day}"  # "2021-06-30"
        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")

        try:
            basic_data = GetTrendDataController(start_date, end_date)
            res = basic_data.run()
            return response_wrapper(res)

        except Exception as e:
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")


class GetSpecBoxApi(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('date', type=str, location='args', required=True, help="Date cannot be empty")
            args = parser.parse_args()
            target_month_str = args['date']  # "2021-06"
            start_date = f"{target_month_str}-01"  # "2021-06-01"
            dt_obj = datetime.strptime(target_month_str, "%Y-%m")
            year = dt_obj.year
            month = dt_obj.month
            _, last_day = calendar.monthrange(year, month)
            end_date = f"{target_month_str}-{last_day}"  # "2021-06-30"
        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")

        try:
            basic_data = GetSpecBoxController(start_date, end_date)
            res = basic_data.run()
            return response_wrapper(res)

        except Exception as e:
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")


api.add_resource(GetTrendDataApi, '/v1.0/visual/gettrendbardata')
api.add_resource(GetSpecBoxApi, '/v1.0/visual/getspecbox')