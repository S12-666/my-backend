'''
VisualizationMDSApi
'''
from flask_restful import Resource, reqparse
from flask import json
from . import api
import numpy as np
import pandas as pd
from ..utils import getData,new_getData
from ..utils import getFlagArr
from ..utils import ref
from ..utils import label_flag_judge

parser = reqparse.RequestParser(trim=True, bundle_errors=True)

# # 根目录
# @app.route('/')


class getFlag(Resource):
    '''
    getFlag
    '''
    def get(self, startTime, endTime, fault_type):
        """
        get
        ---
        tags:
          - 获取钢板标签
        parameters:
            - in: path
              name: startTime
              required: true
              description: 开始时间
              type: string
            - in: path
              name: endTime
              required: true
              description: 结束时间
              type: string
        responses:
            200:
                description: 执行成功
        """
        selection = []
        if (fault_type == 'performance'):
            selection = 'ddp.p_f_label'
        elif (fault_type == 'thickness'):
            selection = 'ddp.p_f_label'

        # return {'hello': 'world'}
        tocSelect = [startTime, endTime]
        data, col_names = new_getData(['dd.upid', selection, 'dd.status_fqc'], {'status_stats':True}, [], [], [], tocSelect, [], [], '', '')

        result = {}
        # print(data)
        for item in data:
            item_df = pd.DataFrame(data=[item], columns=col_names)
            label = label_flag_judge(item_df, fault_type)
            result[item[0]] = label

        return result, 200, {'Access-Control-Allow-Origin': '*'}


api.add_resource(getFlag, '/v1.0/getFlag/<startTime>/<endTime>/<fault_type>/')