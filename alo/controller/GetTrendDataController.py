from ..utils import queryDataFromDatabase
from datetime import datetime, timedelta
import pandas as pd
from ..models import queryVisualData
import math
class GetTrendDataController:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.time_diff = 6

    def _determine_flag(self, label_list):
        if label_list is None or len(label_list) == 0:
            return 2
        if 0 in label_list:
            return 0  # Bad
        elif all(x == 2 for x in label_list):
            return 2  # Unknown
        elif 1 in label_list:
            return 1  # Good
        else:
            return 2

    def run(self):

        data, col = queryVisualData.getTrendBar(self)
        # # 1. 构造时间范围
        sql_start = f"{self.start_date} 00:00:00"
        sql_end = f"{self.end_date} 23:59:59"
        df = pd.DataFrame(data, columns=col)

        if df.empty:
            return {"good_flag": [], "bad_flag": [], "no_flag": [], "endTimeOutput": []}
        df['toc'] = pd.to_datetime(df['toc'])
        df['flag'] = df['p_f_label'].apply(self._determine_flag)
        freq_str = f'{self.time_diff}h'

        df.set_index('toc', inplace=True)
        trend_df = df.groupby([pd.Grouper(freq=freq_str), 'flag']).size().unstack(fill_value=0)

        full_idx = pd.date_range(start=sql_start, end=sql_end, freq=freq_str)
        trend_df = trend_df.reindex(full_idx, fill_value=0)
        for required_col in [0, 1, 2]:
            if required_col not in trend_df.columns:
                trend_df[required_col] = 0

        dates = trend_df.index.strftime('%Y-%m-%d %H:%M:%S').tolist()

        bad_counts = trend_df[0].tolist()
        good_counts = trend_df[1].tolist()
        unknown_counts = trend_df[2].tolist()

        return {
            "good_flag": good_counts,
            "bad_flag": bad_counts,
            "no_flag": unknown_counts,
            "endTimeOutput": dates
        }

class GetSpecBoxController:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def _determine_flag(self, label_list):
        if label_list is None or len(label_list) == 0:
            return 2
        if 0 in label_list:
            return 0  # Bad
        elif all(x == 2 for x in label_list):
            return 2  # Unknown
        elif 1 in label_list:
            return 1  # Good
        else:
            return 2

    def run(self):
        # 1. 构造时间范围


        data, col = queryVisualData.getBoxData(self)
        res = []

        for item in data:
            res.append({
                'upid': item[0],
                'toc': str(item[1]),
                'tgtthick': item[2],
                'tgtwidth': item[3],
                'tgtlength': item[4],
                'flag': self._determine_flag(item[5]),
                'dis_temp': item[6],
                'fm_temp': item[7]
            })


        return res

