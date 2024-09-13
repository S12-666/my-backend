import pandas as pd
from ..utils import getLabelData_4
from ..utils import label_flag_judge
class GetLabelNumberByTimeController:
    def __init__(self, start, end, type):
        self.startTime = start
        self.endTime = end
        self.type = type
    def transTime(self, time):
        return time.strftime('%Y-%m-%d')
    def countLabel(self, item, type):
        good = bad = noflag = total = 0
        for i in range(len(item)):
            row_df = item.iloc[[i]]
            total += 1
            label = label_flag_judge(row_df, type)
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
        raw_data, columns = getLabelData_4(self.startTime, self.endTime, self.type)
        df = pd.DataFrame(raw_data, columns=columns)
        df.toc = df.apply(lambda x: self.transTime(x.toc), axis=1)
        res = []
        groups = df.groupby(['toc']).groups
        for date in groups:
            idxArr = groups[date].values
            data = df.loc[idxArr]
            temp = self.countLabel(data, self.type)
            temp['date'] = date
            res.append(temp)
        return res
