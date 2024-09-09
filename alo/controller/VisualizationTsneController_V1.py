'''
VisualizationTsneController
'''


import numpy as np
import pandas as pd
import datetime as dt
from sklearn.manifold import TSNE
class getVisualizationTsne_1:
    '''
    getVisualizationTsne
    '''

    def __init__(self):
        pass
        # print('生成实例')

    def run(self, data, data_names):
        # read data from database which has character:
        # toc，upid，productcategory，tgtplatelength2，tgtplatethickness2，tgtwidth，ave_temp_dis，
        # crowntotal，nmrPre_params，wedgetotal，finishtemptotal，avg_p5

        # N=1000 #样本数

        # M=300 #一维变量维度

        # X = np.random.random((N,M))

        # X_embedded = TSNE(n_components=2).fit_transform(X[0:50])
        # x, y, toc，upid，productcategory，tgtplatelength2，tgtplatethickness2，tgtwidth，ave_temp_dis，crowntotal，nmrPre_params，wedgetotal，finishtemptotal，avg_p5


        # path1 = os.path.abspath('.')+r'\alo\pca_data'

        # # fp = open(r"./tsne_data")
        # fp = open(path1)

        # allTsne = fp.readlines()
        # fp.close()

        # allTsne_df = pd.DataFrame(json.loads(allTsne[0])).T

        # allTsne_df['toc'] = pd.to_datetime(allTsne_df['toc'])

        # startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
        # endTime = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")

        # somePlate_df_tmp = allTsne_df[allTsne_df['toc'] >= startTime]
        # somePlate_df = somePlate_df_tmp[somePlate_df_tmp['toc'] <= endTime]

        # somePlate_json = somePlate_df.T.to_json(orient='columns', force_ascii=False)
        # somePlate_json = json.loads(somePlate_json)
        X=[]

        for item in data:
            process_data = []
            # print(item[0])
            for data_name in data_names:
                process_data.append(item[6][data_name])
            X.append(process_data)
        X = pd.DataFrame(X).fillna(0).values.tolist()
        X_embedded = TSNE(n_components=2).fit_transform(X)

        index=0
        upload_json={}
        for item in data:
            label = 0
            if item[9] == 0:
                flags = item[7]
                if 0 not in flags:
                    if np.array(flags).sum == 8:
                        label = 404
                    else:
                        label = 1
            elif item[9] == 1:
                label = 404
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