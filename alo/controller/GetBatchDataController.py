import pandas as pd
import numpy as np
from ..models.queryVisualData import getBatchData, getlabelFlag
from ..api import singelSteel
from ..methods.dataProcessing import getpfList, getFqcList, slabel
from ..utils import label_judge
from sklearn.manifold import TSNE

class GetBatchDataController:
    def __init__(self, para):
        self.para = para
        self.thick_range = para.get('tgtthick')
        self.width_range = para.get('tgtwidth')
        self.length_range = para.get('tgtlength')
        self.disTemp_range = para.get('dis_temp')
        self.fmTemp_range = para.get('fm_temp')
        self.date_range = para.get('date_range')

    def run(self):
        data, col = getBatchData(self)
        pd_data = pd.DataFrame(data=data, columns=col)

        pd_data['tgtwidth'] = pd.to_numeric(pd_data['tgtwidth'])
        pd_data['tgtthickness'] = pd.to_numeric(pd_data['tgtthickness'])
        pd_data['toc'] = pd.to_datetime(pd_data['toc'])

        pd_data['group_change'] = pd_data['platetype'] != pd_data['platetype'].shift()
        pd_data['temp_group_id'] = pd_data['group_change'].cumsum()

        final_res = {}  # 使用字典，满足你要求的 "0": {}, "1": {} 格式
        index_counter = 0
        for g_id, group in pd_data.groupby('temp_group_id'):
            current_platetype = group.iloc[0]['platetype']
            count_stats = {0: 0, 1: 0, 2: 0}
            upids_dict = {}
            for _, row in group.iterrows():
                current_label = label_judge(getpfList(row['p_f_label']))
                if current_label in count_stats:
                    count_stats[current_label] += 1
                upid_key = str(row['upid'])
                upids_dict[upid_key] = {
                    "tgtwidth": row['tgtwidth'],
                    "tgtthickness": row['tgtthickness'],
                    "tgtlength": row['tgtlength'],
                    "toc": str(row['toc']),
                    "label": current_label
                }
            total_nums = len(upids_dict)
            ab_rate = count_stats[0] / total_nums if total_nums > 0 else 0.0
            block_info = {
                "platetype": current_platetype,
                "thick_range": [float(group['tgtthickness'].min()), float(group['tgtthickness'].max())],
                "width_range": [float(group['tgtwidth'].min()), float(group['tgtwidth'].max())],
                "date_range": [str(group['toc'].min()), str(group['toc'].max())],
                "length_range": [float(group['tgtlength'].min()), float(group['tgtlength'].max())],
                "upids": upids_dict,
                "plate_nums": total_nums,
                "abnormal_count": count_stats[0],
                "normal_count": count_stats[1],
                "undetected_count": count_stats[2],
                "abnormal_rate": round(ab_rate, 4)
            }

            final_res[str(index_counter)] = block_info
            index_counter += 1

        return final_res