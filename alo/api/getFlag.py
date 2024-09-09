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
            label = 0
            if item[2] == 0:
                flags = item[1]
                if 0 not in flags:
                    if (np.array(flags).sum == 10) or (len(flags) == 0):
                        label = 404
                    else:
                        label = 1
            elif item[2] == 1:
                label = 404
            result[item[0]] = label

        # print(json)

        return result, 200, {'Access-Control-Allow-Origin': '*'}


api.add_resource(getFlag, '/v1.0/getFlag/<startTime>/<endTime>/<fault_type>/')