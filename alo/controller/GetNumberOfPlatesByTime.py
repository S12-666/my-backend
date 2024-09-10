import pandas as pd
from ..methods.dataProcessing import plateHasDefect
from ..models.labelNumberOfPlates import getLabelData
class GetLabelNumberByTimeController:
    def __init__(self, start, end, type):
        self.startTime = start
        self.endTime = end
        self.type = type
    def transTime(self, time):
        return time.strftime('%Y-%m-%d')
    def countLabel(self, item):
        good = bad = noflag = total = 0
        for idx, row in item.iterrows():
            total += 1
            label = plateHasDefect(row.status_fqc, row.p_f_label)
            if label == 0:
                bad += 1
            elif label == 1:
                good += 1
            else:
                noflag += 1
        return {
            'good': good,
            'bad': bad,
            'noflag': noflag,
            'total': total
        }
    def run(self):
        raw_data, columns = getLabelData(self.startTime, self.endTime, self.type)
        df = pd.DataFrame(raw_data, columns=columns)
        df.toc = df.apply(lambda x: self.transTime(x.toc), axis=1)
        res = []
        groups = df.groupby(['toc']).groups
        for date in groups:
            idxArr = groups[date].values
            data = df.loc[idxArr]
            temp = self.countLabel(data)
            temp['date'] = date
            res.append(temp)
        return res
