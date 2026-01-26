from ..utils import queryDataFromDatabase
from datetime import datetime, timedelta
import pandas as pd
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
        # 1. 构造时间范围
        sql_start = f"{self.start_date} 00:00:00"
        sql_end = f"{self.end_date} 23:59:59"

        # 2. SQL 查询 (查询逻辑不变，依旧拉取全量数据，在内存中分桶)
        sql = '''
                select 
                        dd.toc,
                        dd.upid,
                        ddp.p_f_label
                        from app.deba_dump_data dd
                        left join dcenter.l2_m_mv_thickness_pg dt on dt.upid = dd.upid
                        LEFT JOIN app.deba_dump_properties ddp ON ddp.upid = dd.upid
                        where dd.toc >= to_timestamp('{start}', 'yyyy-mm-dd hh24:mi:ss')
                        and dd.toc <= to_timestamp('{end}', 'yyyy-mm-dd hh24:mi:ss')
                        order by dd.toc asc
                '''.format(start=sql_start, end=sql_end)
        data, col = queryDataFromDatabase(sql)
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
