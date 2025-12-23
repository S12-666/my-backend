import numpy as np
import pandas as pd
from ..methods.dataProcessing import getpfList, getFqcList, slabel
from ..models.KeyIndicatorsData import getFQCReportSQL
from ..utils import label_judge
from datetime import datetime, timedelta
import datetime as dt

class FQCReportController:
    def __init__(self, para):
        self.para = para
        self.upid = para['upid']
        self.slabid = para['slabid']
        self.daterange = para['daterange']

    def get_fqc_time_by_upid(self, upid):
        if not upid or len(upid) < 5:
            return {'startTime': '0', 'endTime': '0'}

        try:
            year = int('20' + upid[0:2])
            day = int(upid[3:5])
            m = upid[2]
            if m == 'A':
                mon = 10
            elif m == 'B':
                mon = 11
            elif m == 'C':
                mon = 12
            else:
                mon = int(m)

            # 基础时间逻辑保持不变
            d1 = dt.datetime(year, mon, day, 15, 22, 32)
            d2 = dt.datetime(year, mon, day, 15, 25, 45)
            return {
                'startTime': d1.strftime("%Y-%m-%d %H:%M:%S"),
                'endTime': d2.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception:
            return {'startTime': '0', 'endTime': '0'}

    def run(self):
        if self.upid:
            conditions = f"dd.upid = '{self.upid}'"
        elif self.slabid:
            conditions = f"lmpd.slabid = '{self.slabid}'"
        else:
            start_time = self.daterange[0]
            end_time = self.daterange[1]
            end_exclusive = (datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            conditions = f"dd.toc >= '{start_time}' AND dd.toc < '{end_exclusive}'"

        row_data, col = getFQCReportSQL(conditions)
        data_df = pd.DataFrame(columns=col, data=row_data)
        data_df.fillna(0, inplace=True)
        data_df['length'] = data_df['length'].round(2)
        data_df['width'] = data_df['width'].round(2)

        thick_range = [data_df['thick'].min(), data_df['thick'].max()]
        length_range = [data_df['length'].min(), data_df['length'].max()]
        width_range = [data_df['width'].min(), data_df['width'].max()]
        tgthick_range = [data_df['tgtthickness'].min(), data_df['tgtthickness'].max()]
        tglength_range = [data_df['tgtlength'].min(), data_df['tgtlength'].max()]
        tgwidth_range = [data_df['tgtwidth'].min(), data_df['width'].max()]

        ranges = {
            'thick_range': thick_range,
            'length_range': length_range,
            'width_range': width_range,
            'tgthick_range': tgthick_range,
            'tglength_range': tglength_range,
            'tgwidth_range': tgwidth_range
        }

        raw_spec = data_df['platetype'].unique()
        spec_list = sorted([x for x in raw_spec if x and x != 0])

        row_list = []
        for row in data_df.itertuples():
            current_fqc_time = self.get_fqc_time_by_upid(row.upid)
            row_list.append({
                'upid': row.upid,
                'slabid': row.slabid,
                'steelspec': row.platetype,
                'thick': row.thick,
                'length': row.length,
                'width': row.width,
                'tgthick': row.tgtthickness,
                'tglength': row.tgtlength,
                'tgwidth': row.tgtwidth,
                'toc': str(row.toc),
                'startTime': current_fqc_time['startTime'],
                'endTime': current_fqc_time['endTime'],
                'fqc_label': getFqcList(row.fqc_label),
                'slabel': slabel(getFqcList(row.fqc_label)),
                'p_f_label': getpfList(row.p_f_label),
                'plabel': label_judge(row.p_f_label)
            })
        result = {
            'tableData': row_list,
            'ranges': ranges,
            'specs': spec_list
        }
        return result