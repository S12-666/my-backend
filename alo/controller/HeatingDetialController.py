import pandas as pd
from ..methods.dataProcessing import getpfList
from ..models.KeyIndicatorsData import getHeatingReportSQL
from ..utils import label_judge
from datetime import datetime, timedelta

class HeatingDetialController:
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
            conditions = f"lff.slab_no = '{self.slabid}'"
        else:
            start_time = self.daterange[0]
            end_time = self.daterange[1]
            end_exclusive = (datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            conditions = f"lff.discharge_time >= '{start_time}' AND lff.discharge_time < '{end_exclusive}'"

        row_data, col = getHeatingReportSQL(conditions)
        data_df = pd.DataFrame(columns=col, data=row_data)
        data_df.fillna(0, inplace=True)

        thick_range = [data_df['slab_thickness'].min(), data_df['slab_thickness'].max()]
        length_range = [data_df['slab_length'].min(), data_df['slab_length'].max()]
        width_range = [data_df['slab_width'].min(), data_df['slab_width'].max()]
        distemp_range = [data_df['ave_temp_dis'].min(), data_df['ave_temp_dis'].max()]
        ranges = {
            'thick_range': thick_range,
            'length_range': length_range,
            'width_range': width_range,
            'distemp_range': distemp_range
        }

        raw_spec = data_df['steelspec'].unique()
        spec_list = sorted([x for x in raw_spec if x and x != 0])

        for row in data_df.itertuples():
            row_list.append({
                'upid': row.upid,
                'slabid': row.slab_no,
                'steelspec': row.steelspec,
                'thick': row.slab_thickness,
                'length': row.slab_length,
                'width': row.slab_width,
                'alltime': row.in_fce_time,
                'ave_temp_entry_pre': row.ave_temp_entry_pre,
                'ave_temp_pre': row.ave_temp_pre,
                'staying_time_pre': row.staying_time_pre,
                'ave_temp_entry_1': row.ave_temp_entry_1,
                'ave_temp_1': row.ave_temp_1,
                'staying_time_1': row.staying_time_1,
                'ave_temp_entry_2': row.ave_temp_entry_2,
                'ave_temp_2': row.ave_temp_2,
                'staying_time_2': row.staying_time_2,
                'ave_temp_entry_soak': row.ave_temp_entry_soak,
                'ave_temp_soak': row.ave_temp_soak,
                'staying_time_soak': row.staying_time_soak,
                'ave_temp_dis': row.ave_temp_dis,
                'discharge_time': str(row.discharge_time),
                'p_f_label': getpfList(row.p_f_label),
                'label': label_judge(row.p_f_label)
            })
        result = {
            'tableData': row_list,
            'ranges': ranges,
            'specs': spec_list
        }
        return result