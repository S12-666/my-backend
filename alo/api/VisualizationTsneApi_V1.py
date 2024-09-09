'''
VisualizationTsneApi
'''
import pandas as pd
from flask_restful import Resource, reqparse
from . import api
from ..controller.VisualizationTsneController_V1 import getVisualizationTsne_1
from .singelSteel import modeldata_1,mareymodeldata,thicklabel,p_data_names
from ..api import singelSteel

parser = reqparse.RequestParser(trim=True, bundle_errors=True)

# # 根目录
# @app.route('/')


class VisualizationTsne_1(Resource):
    '''
    SixDpictureUpDownQuantile
    '''
    def post(self, current_time, limit, fault_type):
        """
        get
        ---
        tags:
          - 可视化马雷图部分TSNE
        parameters:
            - in: path
              name: startTime
              required: true
              description: 开始钢板upid
              type: string
            - in: path
              name: endTime
              required: true
              description: 结束钢板upid
              type: string
        responses:
            200:
                description: 执行成功
        """
        selection = []
        if (fault_type == 'performance'):
            selection = ['ddp.p_f_label', thicklabel, 'dd.status_fqc']
        elif (fault_type == 'thickness'):
            selection = ['ddp.p_f_label', thicklabel, 'dd.status_fqc']
        select = ','.join(selection)

        # data, status_cooling = modeldata(parser,['dd.upid', 'lmpd.steelspec','dd.toc', 'dd.tgtwidth','dd.tgtlength','dd.tgtthickness','dd.stats','dd.fqc_label',thicklabel,'dd.status_fqc'], limit)
        data, status_cooling = modeldata_1(parser,
                                        ['dd.upid', 'lmpd.steelspec', 'dd.toc', 'dd.tgtwidth', 'dd.tgtlength', 'dd.tgtthickness',
                                        'dd.stats', select],
                                        current_time,
                                        limit)

        if len(data) <= 1:
            return {}, 204, {'Access-Control-Allow-Origin': '*'}

        VisualizationTsne = getVisualizationTsne_1()

        data_names = []
        if status_cooling == 0:
            data_names = singelSteel.data_names
        elif status_cooling == 1:
            data_names = singelSteel.without_cooling_data_names
        json = VisualizationTsne.run(data, data_names)

        if len(json) < 5:
            return json, 202, {'Access-Control-Allow-Origin': '*'}
        return json, 200, {'Access-Control-Allow-Origin': '*'}


api.add_resource(VisualizationTsne_1, '/v1.0/model/VisualizationTsne_1/<current_time>/<limit>/<fault_type>')