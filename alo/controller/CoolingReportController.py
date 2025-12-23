import numpy as np
import pandas as pd
from ..methods.dataProcessing import getpfList
from ..models.KeyIndicatorsData import getCoolingReportSQL
from ..utils import label_judge
from datetime import datetime, timedelta

class CoolingReportController:
    def __init__(self, para):
        self.para = para
        self.upid = para['upid']
        self.slabid = para['slabid']
        self.daterange = para['daterange']

    def run(self):
        row_list = []
        if self.upid:
            conditions = f"dd.upid = '{self.upid}'"
        elif self.slabid:
            conditions = f"lmpd.slabid = '{self.slabid}'"
        else:
            start_time = self.daterange[0]
            end_time = self.daterange[1]
            end_exclusive = (datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            conditions = f"dd.toc >= '{start_time}' AND dd.toc < '{end_exclusive}'"

        row_data, col = getCoolingReportSQL(conditions)
        data_df = pd.DataFrame(columns=col, data=row_data)
        data_df.fillna(0, inplace=True)
        data_df['length'] = data_df['length'].round(2)
        data_df['width'] = data_df['width'].round(2)

        thick_range = [data_df['thick'].min(), data_df['thick'].max()]
        length_range = [data_df['length'].min(), data_df['length'].max()]
        width_range = [data_df['width'].min(), data_df['width'].max()]
        distemp_range = [data_df['ave_temp_dis'].min(), data_df['ave_temp_dis'].max()]
        tgtemp_range = [data_df['tgttmplatetemp'].min(), data_df['tgttmplatetemp'].max()]
        cr_range = [data_df['cooling_rate1'].min(), data_df['cooling_rate1'].max()]
        ranges = {
            'thick_range': thick_range,
            'length_range': length_range,
            'width_range': width_range,
            'distemp_range': distemp_range,
            'tgtemp_range': tgtemp_range,
            'cr_range': cr_range
        }

        raw_spec = data_df['steelspec'].unique()
        spec_list = sorted([x for x in raw_spec if x and x != 0])

        cool_temp1 = data_df['cooling_stop_temp1'].astype(float).astype(int).astype(str)
        cool_temp2 = data_df['cooling_stop_temp2'].astype(float).astype(int).astype(str)
        data_df['cooling_stop_temp'] = np.where(cool_temp2 == '0', cool_temp1, cool_temp1 + "/" + cool_temp2)

        cool_rate1 = data_df['cooling_rate1'].astype(float).astype(int).astype(str)
        cool_rate2 = data_df['cooling_rate2'].astype(float).astype(int).astype(str)
        data_df['cooling_rate'] = np.where(cool_temp2 == '0', cool_rate1, cool_rate1 + "/" + cool_rate2)


        for row in data_df.itertuples():
            row_list.append({
                'upid': row.upid,
                'slabid': row.slabid,
                'steelspec': row.steelspec,
                'thick': row.thick,
                'length': row.length,
                'width': row.width,
                'toc': str(row.toc),
                'adaptive_key': row.adaptive_key,
                'tapping_code': row.tapping_code,
                'ave_temp_dis': row.ave_temp_dis,
                'tg_temp': row.tgttmplatetemp,
                'cooling_start_temp': row.cooling_start_temp,
                'cooling_stop_temp': row.cooling_stop_temp,
                'operate_mode': row.operate_mode,
                'cooling_mode': row.cooling_mode,
                'cooling_rate': row.cooling_rate,
                'cooling_stop_temp1': row.cooling_stop_temp1,
                'cooling_stop_temp2': row.cooling_stop_temp2,
                'cooling_rate1': row.cooling_rate1,
                'cooling_rate2': row.cooling_rate2,
                'p1': row.avg_p1,
                'p2': row.avg_p2,
                'p5': row.avg_p5,
                'cr_act': row.avg_cr_act,
                'adap': row.speed_ratio,
                'p_f_label': getpfList(row.p_f_label),
                'label': label_judge(row.p_f_label)
            })
        result = {
            'tableData': row_list,
            'ranges': ranges,
            'specs': spec_list
        }
        return result