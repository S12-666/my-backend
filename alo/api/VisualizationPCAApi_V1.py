'''
VisualizationPCAApi
'''
from flask_restful import Resource, reqparse
from . import api
import pandas as pd
from ..controller.VisualizationPCAController_V1 import getVisualizationPCA_1
from .singelSteel import modeldata_1,mareymodeldata,thicklabel
from ..api import singelSteel

parser = reqparse.RequestParser(trim=True, bundle_errors=True)

# # 根目录
# @app.route('/')


class VisualizationPCA_1(Resource):
    '''
    SixDpictureUpDownQuantile
    '''
    def post(self, current_time, limit):
        """
        get
        ---
        tags:
          - 可视化马雷图部分PCA
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
        data, status_cooling = modeldata_1(parser,
                                         ['dd.upid', 'lmpd.steelspec', 'dd.toc', 'dd.tgtwidth', 'dd.tgtlength', 'dd.tgtthickness',
                                          'dd.stats', 'dd.fqc_label', thicklabel, 'dd.status_fqc'],
                                         current_time,
                                         limit)
        # marey_data, col_names = mareymodeldata(start_time, end_time, parser,
        #                                        ['dd.upid', 'lmpd.steelspec', 'dd.toc', 'dd.tgtwidth', 'dd.tgtlength', 'dd.tgtthickness', 'dd.stats', 'dd.fqc_label', thicklabel,
        #                                         'dd.status_fqc'],
        #                                        status_cooling)
        # data_df = pd.DataFrame(data=data, columns=col_names).dropna(axis=0, how='any').reset_index(drop=True)
        # marey_data_df = pd.DataFrame(data=marey_data, columns=col_names).dropna(axis=0, how='any').reset_index(drop=True)
        # data = data_df.append(marey_data_df).drop_duplicates(['upid']).reset_index(drop=True).values.tolist()

        if (len(data) == 0):
            return {}, 204, {'Access-Control-Allow-Origin': '*'}

        data_names = []
        if status_cooling == 0:
            data_names = singelSteel.data_names
        elif status_cooling == 1:
            data_names = singelSteel.without_cooling_data_names
        VisualizationPCAdata = getVisualizationPCA_1()
        jsondata = VisualizationPCAdata.run(data, data_names)

        if len(jsondata) < 5:
            return jsondata, 202, {'Access-Control-Allow-Origin': '*'}
        return jsondata, 200, {'Access-Control-Allow-Origin': '*'}


api.add_resource(VisualizationPCA_1, '/v1.0/model/VisualizationPCA_1/<current_time>/<limit>')