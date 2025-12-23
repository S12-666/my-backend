import pandas as pd
from ..methods.dataProcessing import getpfList
from ..models.KeyIndicatorsData import getRollingReportSQL
from ..utils import label_judge
from datetime import datetime, timedelta

class RollingReportController:
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
            conditions = f"dd.toc >= '{start_time}' AND dd.toc < '{end_exclusive}'"

        row_data, col = getRollingReportSQL(conditions)
        data_df = pd.DataFrame(columns=col, data=row_data)
        data_df.fillna(0, inplace=True)

        data_df['timerollingstart'] = data_df['timerollingstart'].astype(str).str[:14]
        data_df['timerollingfinish'] = data_df['timerollingfinish'].astype(str).str[:14]
        data_df['timerollingstart'] = pd.to_datetime(data_df['timerollingstart'], format='%Y%m%d%H%M%S', errors='coerce')
        data_df['timerollingfinish'] = pd.to_datetime(data_df['timerollingfinish'], format='%Y%m%d%H%M%S', errors='coerce')

        data_df['timerollingstart'] = data_df['timerollingstart'].fillna(0)
        data_df['timerollingfinish'] = data_df['timerollingfinish'].fillna(0)
        thick_range = [data_df['tgtplatethickness'].min(), data_df['tgtplatethickness'].max()]
        length_range = [data_df['tgtplatelength'].min(), data_df['tgtplatelength'].max()]
        width_range = [data_df['tgtwidth'].min(), data_df['tgtwidth'].max()]
        distemp_range = [data_df['ave_temp_dis'].min(), data_df['ave_temp_dis'].max()]
        tgtemp_range = [data_df['tgttmplatetemp'].min(), data_df['tgttmplatetemp'].max()]
        ranges = {
            'thick_range': thick_range,
            'length_range': length_range,
            'width_range': width_range,
            'distemp_range': distemp_range,
            'tgtemp_range': tgtemp_range
        }

        raw_spec = data_df['steelspec'].unique()
        spec_list = sorted([x for x in raw_spec if x and x != 0])

        for row in data_df.itertuples():
            row_list.append({
                'upid': row.upid,
                'slabid': row.slab_no,
                'steelspec': row.steelspec,
                'thick': row.tgtplatethickness,
                'length': row.tgtplatelength,
                'width': row.tgtwidth,
                'weight': row.slabweight,
                'dis_code': row.tappingsteelgrade,
                'cr_code': row.crcode,
                'r_start_time': str(row.timerollingstart),
                'r_end_time': str(row.timerollingfinish),
                'rm_passes': row.totalpassesrm,
                'fm_passes': row.totalpassesfm,
                'ave_temp_dis': row.ave_temp_dis,
                'fm_start_temp': row.tgttmrestarttemp1,
                'tg_temp': row.tgttmplatetemp,
                'p_f_label': getpfList(row.p_f_label),
                'label': label_judge(row.p_f_label)
            })
        result = {
            'tableData': row_list,
            'ranges': ranges,
            'specs': spec_list
        }
        return result