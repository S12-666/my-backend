'''
VisualizationPCAController
'''

import numpy as np
import pandas as pd
import datetime as dt
from sklearn.decomposition import PCA
from ..api import singelSteel
from ..utils import label_flag_judge


class getVisualizationPCA_1:
    '''
    getVisualizationPCA
    '''

    def __init__(self):
        pass
        # print('生成实例')

    def run(self, data, data_names, col_names, fault_type):
# used to fix remote data
        # read data from database which has character:
        # toc，upid，productcategory，tgtplatelength2，tgtplatethickness2，
        # tgtwidth，ave_temp_dis，crowntotal，nmrPre_params，wedgetotal，finishtemptotal，avg_p5
        # N=1000 #样本数

        # M=300 #一维变量维度

        # X = np.random.random((N,M))

        # pca = PCA(n_components=2)

        # pca.fit(X)

        # X_transformed = pca.transform(X)
        # print(X_transformed)
        # selectSql = "select * from dcenter.dump_data where upid='" + '18901034000' + "'"
        # selectSql = "select upid, toc, fqc_label from dcenter.dump_data where fqc_ismissing = 0 and toc>='2018-09-01 00:00:00' and toc<='2018-09-02 00:00:00' "
        # data = getDataBySql(selectSql)


        # path1 = os.path.abspath('.')+'/alo/PCA_data.data'

        # # fp = open(r"./PCA_data")
        # fp = open(path1)

        # allPCA = fp.readlines()
        # fp.close()

        # allPCA_df = pd.DataFrame(json.loads(allPCA[0])).T

        # allPCA_df['toc'] = pd.to_datetime(allPCA_df['toc'])

        # startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
        # endTime = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")

        # somePlate_df_tmp = allPCA_df[allPCA_df['toc'] >= startTime]
        # somePlate_df = somePlate_df_tmp[somePlate_df_tmp['toc'] <= endTime]

        # somePlate_json = somePlate_df.T.to_json(orient='columns', force_ascii=False)
        # somePlate_json = json.loads(somePlate_json)

        # return somePlate_json
        # print(data)


        X=[]
        for item in data:
            process_data = []
            for data_name in data_names:
                process_data.append(item[6][data_name])
            X.append(process_data)
        X = pd.DataFrame(X).fillna(0).values.tolist()
        pca = PCA(n_components=2)
        pca.fit(X)
        X_embedded = pca.transform(X)

        index=0
        upload_json={}
        for item in data:
            item_df = pd.DataFrame(data=[item], columns=col_names)
            label = label_flag_judge(item_df, fault_type)
            upload_json[str(index)] = {"x":X_embedded[index][0].item(),
            "y":X_embedded[index][1].item(),
            "toc":str(item[2]),
            "upid":item[0],
            "productcategory":item[1],
            "tgtplatelength2":item[4],
            "tgtplatethickness":item[5],
            "tgtwidth":item[3],
            'label':str(label)}
            index+=1
        return upload_json