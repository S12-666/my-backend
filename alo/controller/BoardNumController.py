import pandas as pd
import numpy as np
from ..api.singelSteel import filterSQL
from ..utils import getLabelData, label_flag_judge


class ComputeBoardNum:

    def __init__(self, upid):
        self.upid = upid
        self.paramsIllegal = False
        try:
            # 如果以后加入参数，在这里加入
            # print('createDiagResu方法暂时没有参数')
            pass
        except Exception:
            self.paramsIllegal = True

    def getData(self, parser, selection, limit):
        SQL, status_cooling = filterSQL(parser)
        select = ','.join(selection)
        ismissing = ['dd.status_stats']
        lefttable = ''' from  dcenter.l2_m_primary_data lmpd
                            left join dcenter.l2_m_plate lmp on lmpd.slabid = lmp.slabid
                            left join dcenter.l2_cc_pdi lcp  on lmpd.slabid = lcp.slab_no
                            right join app.deba_dump_data dd on dd.upid = lmp.upid 
                            right join app.deba_dump_properties ddp on ddp.upid = dd.upid '''
        if (SQL != ''):
            for i in ismissing:
                SQL += ' and ' + i + '= ' + '0'
        if (SQL == ''):
            SQL = "where " + SQL
            for i in ismissing:
                SQL += ' ' + i + '= ' + '0' + ' and '
            SQL = SQL[:-4]
        SQL = SQL + ' and dd.status_cooling = ' + str(status_cooling) + " "
        # 后期删掉
        selct_1 = " and ddp.p_f_label !='[]' "
        Limit = ' ORDER BY dd.toc  DESC Limit ' + str(limit)
        SQL = 'select ' + select + lefttable + SQL + selct_1 + Limit
        # print(SQL)
        data, col_names = getLabelData(SQL)

        return data, col_names


    def getGoodNum(self, data, col_names,fault_type):

        if len(data) == 0:
            return 204, {}


        bad_count = 0
        good_count = 0
        no_count = 0
        type_list = []
        p_type_name = ["gs", "pa", "pf", "pn", "ps"]
        t_type_name = []
        if fault_type == 'performance':
            type_name =  p_type_name
        elif fault_type == 'thickness':
            type_name =  p_type_name

        for item in data:
            item_df = pd.DataFrame(data = [item], columns = col_names)
            label = label_flag_judge(item_df, fault_type)

            if label == 404:
                no_count += 1
            elif label == 1:
                good_count += 1
            elif label == 0:
                bad_count += 1

            item_p = item[2]
            item_p = list(map(lambda x: 1 if x == 0 else 0, item_p))
            type_list.append(item_p)


            # if item[1] == 1:    # status_fqc
            #     no_p_count += 1
            # elif item[1] == 0:
            #     if (np.array(item[2]).sum() == 10) or (len(item[2]) == 0):     # fqc_label
            #         no_p_count += 1
            #     elif 0 in item[2]:
            #         bad_count += 1
            #     else:
            #         good_count += 1
            #         item_p = item[2]
            #         item_p = list(map(lambda x: 1 if x == 0 else 0, item_p))
            #         p_type_list.append(item_p)

        type_count = np.sum(np.array(type_list), axis=0).tolist()

        result = {}
        result["no_p_count"] = no_count
        result["good_count"] = good_count
        result["bad_count"] = bad_count
        result["total_count"] = len(data)
        fqc_type_len = len(type_list)

        for i, type in enumerate(type_name):
            if fqc_type_len == 0:
                result[type] = 0
            else:
                result[type] = type_count[i]

        return 200, result


