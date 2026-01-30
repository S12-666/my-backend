import pandas as pd
import numpy as np
from ..models.queryVisualData import getScatterData
from ..api import singelSteel
from ..methods.dataProcessing import getpfList, getFqcList, slabel
from ..utils import label_judge
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
class GetScatterDataController:
    def __init__(self, para):
        self.para = para
        self.thick_range = para.get('tgtthick')
        self.width_range = para.get('tgtwidth')
        self.length_range = para.get('tgtlength')
        self.disTemp_range = para.get('dis_temp')
        self.fmTemp_range = para.get('fm_temp')
        self.date_range = para.get('date_range')
        self.method = para.get('method')

    def run(self):
        data, col = getScatterData(self)
        if len(data) == 0:
            return None
        X = []

        for item in data:
            process_data = []
            if item[5] == 0:
                for data_name in singelSteel.data_names:
                    try:
                        process_data.append(item[3][data_name])
                    except:
                        process_data.append(0)
                X.append(process_data)
            elif item[5] == 1:
                for data_name in singelSteel.without_cooling_data_names:
                    try:
                        process_data.append(item[3][data_name])
                    except:
                        process_data.append(0)
                X.append(process_data)

        X = pd.DataFrame(X).fillna(0).values.tolist()
        if self.method == 'tsne':
            X_embedded = TSNE(n_components=2).fit_transform(X)
        else:
            X_embedded = PCA(n_components=2).fit_transform(X)

        index = 0
        upload_json = {}
        for item in data:
            flag_list = getpfList(item[6])
            label = label_judge(flag_list)
            single = {}
            single["x"] = X_embedded[index][0].item()
            single["y"] = X_embedded[index][1].item()
            single["toc"] = str(item[1])
            single["steelspec"] = item[2]
            single["upid"] = item[0]
            single["label"] = str(label)
            upload_json[str(index)] = single
            index += 1
        return upload_json