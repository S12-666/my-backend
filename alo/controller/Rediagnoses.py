import pandas as pd
from ..utils import format_value
from ..models.diagnosesData import diagnosesTrainDataByArgs
from ..methods.dataProcessing import rawDataToModelData, plateHasDefect, plateDetailedDefect
from ..methods.define import data_names, flag_names, name_index
from ..methods.DiagnosesAlgorithm import DiagnosesAlgorithm
class RediagnosesController:
    def __init__(self, args, test, selectedKey):
        self.args = args
        self.selectedKey = selectedKey
        test_list = []
        for name in data_names:
            try:
                val = test[name]
                test_list.append(val)
            except:
                test_list.append(0)
        self.test = [test_list]
    def run(self):
        train_raw, train_col = diagnosesTrainDataByArgs(self.args)
        train_df = pd.DataFrame(data=train_raw, columns=train_col)
        test_matrix = self.test
        train_matrix = []
        train_df['label'] = train_df[['status_fqc', 'fqc_label']].apply(lambda x: plateHasDefect(x['status_fqc'], x['fqc_label']), axis=1)
        for idx, flag in enumerate(flag_names):
            train_df[flag] = train_df[['status_fqc', 'fqc_label']].apply(lambda x: plateDetailedDefect(x['status_fqc'], x['fqc_label'], idx), axis=1)
            good_train_df = train_df[train_df[flag] == 1]
            data_matrix, _ = rawDataToModelData(good_train_df)
            train_matrix.append(data_matrix)
        diag_inst = DiagnosesAlgorithm(train_matrix, test_matrix)
        pca_res = diag_inst.run('PCA')
        t2 = {}
        q = {}
        for n_idx, name in enumerate(data_names):
            t2_list = []
            q_list = []
            for f_idx, flag in enumerate(flag_names):
                item = pca_res[0][f_idx]
                t2_val = item['CONTJ'][n_idx]
                t2_list.append(format_value(t2_val))
                q_val = item['contq'][n_idx]
                q_list.append(format_value(q_val))
            t2[name] = t2_list
            q[name] = q_list
        return {
            'T2': t2,
            'Q': q
        }
