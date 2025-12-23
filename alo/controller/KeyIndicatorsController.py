import pandas as pd
import numpy as np
import datetime as dt
import time
from ..models.KeyIndicatorsData import getKeyIndicatorsDataByTimeRang
from ..methods.dataProcessing import getFqcList, getpfList
class KeyIndicatorsController:
    def __init__(self, args, req_type):
        self.start = args['startTime']
        self.end = args['endTime']
        if req_type == 'range':
            self.page_num = args['pageNum']
            self.page_size = args['pageSize']
            self.range_flag = True
        else:
            self.range_flag = False
    def run(self):
        return self.processAllData()
    def processAllData(self):
        start_time = time.perf_counter()
        raw, col = getKeyIndicatorsDataByTimeRang(self.start, self.end)
        data_df = pd.DataFrame(data=raw, columns=col)
        # print(f'查询: {time.perf_counter() - start_time:.8f} s')
        all_data = []
        data_df[['rm', 'fm', 'acc', 'fqc_list', 'p_f_label']] = data_df[['stops', 'status_fqc', 'fqc_label', 'p_f_label']].apply(self.time_func, axis=1)
        data_df.fillna(0, inplace=True)
        data_df.sort_values(by=['toc'], ascending=False)
        for i, row in data_df.iterrows():
            all_data.append({
                'index': i + 1,
                'slabid': row.slabid,
                'upid': row.upid,
                'platetype': row.platetype,
                'steelspec': row.steelspec,
                'toc': row.toc.strftime('%Y-%m-%d %H:%M:%S'),
                'slabthick': row.slabthickness,
                'tgtthick': row.tgtthickness,
                'tgtlen': row.tgtlength,
                'tgtwidth': row.tgtwidth,
                'tgtdistemp': row.tgtdischargetemp,
                'tgttmptemp': row.tgttmplatetemp,
                'c_start_t': row.cooling_start_temp,
                'c_stop_t': row.cooling_stop_temp,
                'c_rate': row.cooling_rate1,
                'discharge': row.in_fce_time,
                'rm': row.rm,
                'fm': row.fm,
                'acc': row.acc,
                'fault': row.p_f_label
            })
        # print(f'数据处理: {time.perf_counter() - start_time:.8f} s')
        # print(f'数据量: {len(all_data)} 条')
        return all_data
    def time_func(self, row):
        stops = row.stops
        rm_time = self.processTime(stops, '2')
        fm_time = self.processTime(stops, '3')
        acc_time = self.processTime(stops, '4')
        fqc_list = getFqcList(row.fqc_label)
        p_f_label = getpfList(row.p_f_label)
        return pd.Series([rm_time, fm_time, acc_time, fqc_list, p_f_label], index=['rm', 'fm', 'acc', 'fqc_list', 'p_f_label'])
    def processTime(self, stops, zone):
        try:
            filter_list = []
            for item in stops:
                if item['station']['zone'] == zone:
                    filter_list.append({
                        'time': item['realTime'],
                        'key': item['station']['key']
                    })
            sort_list = sorted(filter_list, key=lambda x: x['key'])
            t1 = dt.datetime.strptime(sort_list[0]['time'], '%Y-%m-%d %H:%M:%S')
            t2 = dt.datetime.strptime(sort_list[-1]['time'], '%Y-%m-%d %H:%M:%S')
            time_spend = (t2 - t1).total_seconds()
        except:
            time_spend = 0
        return time_spend
