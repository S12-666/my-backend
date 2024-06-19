import pandas as pd
from ..methods.define import data_names, without_cooling_data_names
from ..methods.dataProcessing import plateHasDefect
from ..models.overviewData import getOverviewData
from ..methods.DimensionReductionAlgorithm import DimensionReductionAlgorithm
def getValueByKey(item, key):
    return item[key] if item[key] is not None else 0
class GetScatterDataByTimeController:
    def __init__(self, start, end, type):
        self.startTime = start
        self.endTime = end
        self.type = type
        self.data = None
        self.x = None       
        self.pos = None     
    def run(self):
        rawData, columns = getOverviewData(self.startTime, self.endTime)
        self.data = rawData
        self.dataProcess()
        if self.x is None:
            return []
        dra = DimensionReductionAlgorithm(self.x)
        if self.type == 't-sne':
            self.pos = dra.Tsne()
        res = self.dataToRes()
        return res
    def dataProcess(self):
        x = []
        if self.data is None:
            self.x = x
        for item in self.data:
            process_data = []
            if item[9] == 0:
                for data_name in data_names:
                    try:
                        process_data.append(item[6][data_name])
                    except:
                        process_data.append(0)
                x.append(process_data)
            elif item[9] == 1:
                for data_name in without_cooling_data_names:
                    try:
                        process_data.append(item[6][data_name])
                    except:
                        process_data.append(0)
                x.append(process_data)
        self.x = pd.DataFrame(x).fillna(0).values.tolist()
    def dataToRes(self):
        if self.x is None or self.data is None or self.pos is None:
            return []
        res = []
        for idx, item in enumerate(self.data):
            try:
                label = plateHasDefect(item[10], item[7])
            except:
                label = 404
                print('has error')
            plate = {
                'x': self.pos[idx][0].item(),
                'y': self.pos[idx][1].item(),
                'toc': str(item[2]),
                'upid': item[0],
                'label': label,
                'labels': item[7]['method1']['data'] if label == 0 else [],  
                'status_cooling': item[9],
                'tgtthickness': item[5],
                'slab_thickness': item[11],
                'tgtdischargetemp': item[12],
                'tgttmplatetemp': item[13],
                'cooling_start_temp': item[14],
                'cooling_stop_temp': item[15],
                'cooling_rate1': item[16],
                'tgtwidth': getValueByKey(item[6], 'tgtwidth'),
                'steelspec': getValueByKey(item[6], 'steelspec'),
                'tgtplatelength2': getValueByKey(item[6], 'tgtplatelength2'),
                'productcategory': getValueByKey(item[6], 'productcategory')
            }
            res.append(plate)
        return res
