import pandas as pd
from ..models.diagnosesData import diagnosesTrainDataByArgs, diagnosesTestDataByUpid
from ..methods.dataProcessing import plateHasDefect, plateDetailedDefect, rawDataToModelData
from ..methods.define import data_names, flag_names, specifications
from ..methods.DiagnosesAlgorithm import DiagnosesAlgorithm
import time
class DiagnosesDataByUpidsController:
    def __init__(self, args):
        self.upids = args['upids']
        self.args = {
            'tgtwidth': args['tgtwidth'],
            'tgtplatelength2': args['tgtplatelength2'],
            'tgtthickness': args['tgtthickness'],
            'tgtdischargetemp': args['tgtdischargetemp'],
            'tgttmplatetemp': args['tgttmplatetemp']
        }
        self.train = None
        self.test = None
    def run(self):
        start_time = time.perf_counter()
        train_raw, train_col = diagnosesTrainDataByArgs(self.args)
        train_df = pd.DataFrame(data=train_raw, columns=train_col)
        test_raw, test_col = diagnosesTestDataByUpid(self.upids)
        test_df = pd.DataFrame(data=test_raw, columns=test_col)
        test_df.toc = test_df.apply(lambda x: x.toc.strftime("%Y-%m-%d %H:%M:%S"), axis=1)
        print(f'查询: {time.perf_counter() - start_time:.8f} s')
        if len(train_raw) == 0:
            return 'no train data', {}
        self.train = []
        train_df['label'] = train_df[['status_fqc', 'fqc_label']].apply(lambda x: plateHasDefect(x['status_fqc'], x['fqc_label']), axis=1)
        feature_df = train_df[train_df['label'] == 1][['platetype'] + specifications]
        grouped_feature_df = feature_df.groupby(['platetype'])
        quatile_df_1 = grouped_feature_df[specifications].quantile(0.25)
        quatile_df_2 = grouped_feature_df[specifications].quantile(0.75)
        grouped_test = test_df.groupby(['platetype'])
        platetype_range = {}
        for key, _ in grouped_test:
            temp = {}
            for name in specifications:
                try:
                    v1 = quatile_df_1[name][key]
                    v2 = quatile_df_2[name][key]
                    temp[name] = [v1, v2]
                except:
                    temp[name] = [0, 0]
            platetype_range[key] = temp
        for idx, flag in enumerate(flag_names):
            train_df[flag] = train_df[['status_fqc', 'fqc_label']].apply(lambda x: plateDetailedDefect(x['status_fqc'], x['fqc_label'], idx), axis=1)
            good_train_df = train_df[train_df[flag] == 1]
            data_matrix, _ = rawDataToModelData(good_train_df)
            self.train.append(data_matrix)
        self.test, test_labels_matrix = rawDataToModelData(test_df)
        print(f'数据转换: {time.perf_counter() - start_time:.8f} s')
        diag_inst = DiagnosesAlgorithm(self.train, self.test)
        pca_res = diag_inst.run('PCA')
        single_res = diag_inst.run('single_demension')
        print(f'诊断: {time.perf_counter() - start_time:.8f} s')
        diag_res = []
        upids = test_df.upid.values
        for i, upid in enumerate(upids):
            plate_res = []
            for j, name in enumerate(data_names):
                plate_res.append({
                    'name': name,
                    'T2': self.concatPcaList(pca_res[i], j, 'T2'),
                    'Q': self.concatPcaList(pca_res[i], j, 'Q'),
                    'orig_v': self.concatSingleList(single_res[i], j, 'original_value'),
                    'orig_l': self.concatSingleList(single_res[i], j, 'original_l'),
                    'orig_u': self.concatSingleList(single_res[i], j, 'original_u'),
                    'ext_orig_l': self.concatSingleList(single_res[i], j, 'extremum_original_l'),
                    'ext_orig_u': self.concatSingleList(single_res[i], j, 'extremum_original_u'),
                    's_ext_orig_l': self.concatSingleList(single_res[i], j, 's_extremum_original_l'),
                    's_ext_orig_u': self.concatSingleList(single_res[i], j, 's_extremum_original_u'),
                    'v': self.concatSingleList(single_res[i], j, 'value'),
                    'l': self.concatSingleList(single_res[i], j, 'l'),
                    'u': self.concatSingleList(single_res[i], j, 'u'),
                    'ext_l': self.concatSingleList(single_res[i], j, 'extremum_l'),
                    'ext_u': self.concatSingleList(single_res[i], j, 'extremum_u'),
                    's_ext_l': self.concatSingleList(single_res[i], j, 's_extremum_l'),
                    's_ext_u': self.concatSingleList(single_res[i], j, 's_extremum_u')
                })
            diag_res.append({
                'upid': upid,
                'labels': test_labels_matrix[i],
                'diagnosis': plate_res
            })
        print(f'生成结果: {time.perf_counter() - start_time:.8f} s')
        return diag_res, platetype_range
    def rawDataToModelData_2(self, data_df):
        data_matrix = data_df[data_names]
        return data_matrix.values.tolist()
    def getStatsByKey(self, stats, key):
        try:
            return stats[key]
        except:
            return 0
    def concatPcaList(self, datum, col_idx, type):
        con_list = []
        if type == 'T2':
            t = 'CONTJ'
        elif type == 'Q':
            t = 'contq'
        else:
            return con_list
        for i in range(5):
            val = datum[i][t][col_idx]
            con_list.append(float(format(val, '.4f')))
        return con_list
    def concatSingleList(self, datum, col_idx, key):
        single_list = []
        for i in range(5):
            val = datum[i][col_idx][key]
            single_list.append(float(format(val, '.4f')))
        return single_list
