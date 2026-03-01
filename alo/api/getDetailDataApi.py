from flask_restful import Resource
from flask import request
import traceback
from ..utils import response_wrapper

# 假设你需要一个专门处理 Detail 的 Controller，这里仿照你的代码结构导入
# 实际开发中请根据你的真实文件路径和类名修改
from ..controller.GetDetailDataController import GetDetailDataController
from . import api


class GetDetailDataApi(Resource):
    def post(self):
        try:
            # 1. 解析前端传来的标准 JSON
            json_data = request.get_json(force=True)

            # 2. 提取 type 和 upids
            # json_data 此时是一个字典: {"type": "X65MSO|L450MSO", "upids": ["21611015000", ...]}
            platetype = json_data.get('type', "")
            upids = json_data.get('upids', [])

            # 组装给 Controller 的参数
            para = {
                'type': platetype,
                'upids': upids if isinstance(upids, list) else []
            }

        except Exception as e:
            print(f"参数解析错误:{e}")
            return response_wrapper({}, 400, f"Parameter Error: {str(e)}")

        try:
            # 3. 实例化你的 Controller 并执行业务逻辑
            detail_controller = GetDetailDataController(para)
            res = detail_controller.run()

            # 返回成功响应
            return response_wrapper(res)

        except Exception as e:
            traceback.print_exc()
            return response_wrapper({}, 500, f"Server Error: {str(e)}")
api.add_resource(GetDetailDataApi, '/v1.0/visual/getdetaildata')