import pandas as pd
from ..methods.define import data_names, without_cooling_data_names
from ..methods.dataProcessing import plateHasDefect
from ..utils import getOverviewData, label_flag_judge
from sklearn.manifold import TSNE
def getValueByKey(item, key):
    return item[key] if item[key] is not None else 0
class GetScatterDataByTimeController:
    def __init__(self, start, end, type, fault_type):
        self.startTime = start
        self.endTime = end
        self.type = type
        self.fault_type = fault_type
        self.data = None
        self.x = None       
        self.pos = None     
    def run(self):
        rawData, columns = getOverviewData(self.startTime, self.endTime, self.fault_type)
        self.data = rawData
        self.dataProcess()
        if self.x is None:
            return []
        dra = DimensionReductionAlgorithm(self.x)
        if self.type == 't-sne':
            self.pos = dra.Tsne()
        res = self.dataToRes(columns)
        return res
    def dataProcess(self):
        x = []
        if self.data is None:
            self.x = x
        for item in self.data:
            process_data = []
            if item[8] == 0:
                for data_name in data_names:
                    try:
                        process_data.append(item[6][data_name])
                    except:
                        process_data.append(0)
                x.append(process_data)
            elif item[8] == 1:
                for data_name in without_cooling_data_names:
                    try:
                        process_data.append(item[6][data_name])
                    except:
                        process_data.append(0)
                x.append(process_data)
        self.x = pd.DataFrame(x).fillna(0).values.tolist()
    def dataToRes(self, columns):
        if self.x is None or self.data is None or self.pos is None:
            return []
        res = []
        for idx, item in enumerate(self.data):
            item_df = pd.DataFrame(data=[item], columns=columns)
            try:
                label = label_flag_judge(item_df, self.fault_type)
                # label = plateHasDefect(item[-1], item[-2])
            except:
                label = 404
                print('has error')
            plate = {
                'x': self.pos[idx][0].item(),
                'y': self.pos[idx][1].item(),
                'toc': str(item[2]),
                'upid': item[0],
                'label': label,
                'labels': item[-2],
                'status_cooling': item[8],
                'tgtthickness': item[5],
                'slab_thickness': item[9],
                'tgtdischargetemp': item[10],
                'tgttmplatetemp': item[11],
                'cooling_start_temp': item[12],
                'cooling_stop_temp': item[13],
                'cooling_rate1': item[14],
                'tgtwidth': getValueByKey(item[6], 'tgtwidth'),
                'steelspec': getValueByKey(item[6], 'steelspec'),
                'tgtplatelength2': getValueByKey(item[6], 'tgtplatelength2'),
                'productcategory': getValueByKey(item[6], 'productcategory')
            }
            res.append(plate)
        return res

class DimensionReductionAlgorithm:
    def __init__(self, data):
        self.data = data
    def run(self):
        return []
    def Tsne(self):
        x_embedded = TSNE(n_components=2).fit_transform(self.data)
        return x_embedded
