import numpy as np
from ..models.KeyIndicatorsData import getSpecCountByTimeRang
import pandas as pd
class GetSpecCountController:
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
        raw, col = getSpecCountByTimeRang(self.start, self.end)
        df = pd.DataFrame(data=raw, columns=col)
        bad_count = 0
        good_count = 0
        total = 0
        no_p_count = 0
        p_type_list = []
        p_type_name = ["pa", "pf", "pn", "ps", "gs"]

        for item in raw:
            total += 1

            if item[2] == [] or np.sum(item[2]) == 10:
                no_p_count += 1
            elif 0 in item[2]:
                bad_count += 1
            else:
                good_count += 1

            item_p = item[2] if len(item[2]) != 0 else [2,2,2,2,2]
            item_p = list(map(lambda x: 1 if x == 0 else 0, item_p))
            p_type_list.append(item_p)

        p_type_count = np.sum(np.array(p_type_list), axis=0).tolist()

        result = {}
        result["no_p_count"] = no_p_count
        result["good_count"] = good_count
        result["bad_count"] = bad_count
        result["total_count"] = total
        fqc_type_len = len(p_type_list)
        for i, type in enumerate(p_type_name):
            if fqc_type_len == 0:
                result[type] = 0
            else:
                result[type] = p_type_count[i]

        return result