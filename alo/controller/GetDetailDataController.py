import pandas as pd
import numpy as np
import time
from scipy.stats import norm, f

from ..models.diagnosesData import diagnosesTrainDataByArgs, diagnosesTestDataByUpid
from ..methods.dataProcessing import plateDetailedDefect, rawDataToModelData
from ..methods.define import data_names, flag_names, specifications, meas_index
from ..methods.DiagnosesAlgorithm import DiagnosesAlgorithm
from ..utils import plateHasDefect
from ..models.queryVisualData import getDetailDataByUpids, getTrainData


class GetDetailDataController:
    def __init__(self, para):
        self.para = para
        self.platetype = para.get('type', '')
        self.upids = para.get('upids', [])
        self.data_names = data_names

    def run(self):
        if not self.upids:
            return {}

        start_time = time.perf_counter()

        # 1. 获取测试集与训练集数据
        test_raw, test_col = getDetailDataByUpids(self.upids)
        test_df = pd.DataFrame(data=test_raw, columns=test_col)

        train_raw, train_col = getTrainData(self.platetype)
        train_df = pd.DataFrame(data=train_raw, columns=train_col)

        if train_df.empty:
            return 'no train data', {}

        # 格式化时间戳
        if 'toc' in test_df.columns:
            test_df['toc'] = test_df['toc'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else x)
        if 'toc' in train_df.columns:
            train_df['toc'] = train_df['toc'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else x)

        # 2. 计算基准统计范围 (用于前端规格上下限)
        train_df['label'] = train_df.apply(lambda x: plateHasDefect(x['p_f_label']), axis=1)

        # 3. 提取特征矩阵 (合并为单一基准模型)
        # 提取总体良品作为 PCA 的基准空间 (正常生产态)
        good_train_df = train_df[train_df['label'] == 1]

        # 极端情况兜底：如果这 2000 条里一条良品都没有，就退而求其次用全部数据
        if good_train_df.empty:
            good_train_df = train_df

        self.train, _ = rawDataToModelData(good_train_df)
        self.test, test_labels_matrix = rawDataToModelData(test_df)

        # 4. 执行核心诊断算法
        diag_inst = DiagnosesAlgorithm(self.train, self.test, self.data_names)
        pca_res = diag_inst.run('PCA')
        single_res = diag_inst.run('single_demension')

        # 5. 结果组装 (扁平化，不再是嵌套数组)
        diag_res = []
        upids = test_df['upid'].values

        for i, upid in enumerate(upids):
            current_row = test_df.iloc[i]
            plate_res = []
            for j, name in enumerate(self.data_names):
                # single_res[i] 是一条钢板的所有测点列表，j 是对应的测点索引
                # pca_res[i] 是一条钢板的全局指标字典
                plate_res.append({
                    'name': name,
                    'T2': float(format(pca_res[i].get('T2', 0), '.4f')),
                    'Q': float(format(pca_res[i].get('Q', 0), '.4f')),
                    'orig_v': float(format(single_res[i][j].get('original_value', 0), '.4f')),
                    'orig_l': float(format(single_res[i][j].get('original_l', 0), '.4f')),
                    'orig_u': float(format(single_res[i][j].get('original_u', 0), '.4f')),
                    'ext_orig_l': float(format(single_res[i][j].get('extremum_original_l', 0), '.4f')),
                    'ext_orig_u': float(format(single_res[i][j].get('extremum_original_u', 0), '.4f')),
                    's_ext_orig_l': float(format(single_res[i][j].get('s_extremum_original_l', 0), '.4f')),
                    's_ext_orig_u': float(format(single_res[i][j].get('s_extremum_original_u', 0), '.4f')),
                    'v': float(format(single_res[i][j].get('value', 0), '.4f')),
                    'l': float(format(single_res[i][j].get('l', 0), '.4f')),
                    'u': float(format(single_res[i][j].get('u', 0), '.4f')),
                    'ext_l': float(format(single_res[i][j].get('extremum_l', 0), '.4f')),
                    'ext_u': float(format(single_res[i][j].get('extremum_u', 0), '.4f')),
                    's_ext_l': float(format(single_res[i][j].get('s_extremum_l', 0), '.4f')),
                    's_ext_u': float(format(single_res[i][j].get('s_extremum_u', 0), '.4f'))
                })

            diag_res.append({
                'upid': upid,
                'labels': test_labels_matrix[i],
                'diagnosis': plate_res,
                'tgtthickness': float(current_row['tgtthickness']) if pd.notna(current_row.get('tgtthickness')) else 0.0,
                'tgtwidth': float(current_row['tgtwidth']) if pd.notna(current_row.get('tgtwidth')) else 0.0,
                'tgtlength': float(current_row['tgtlength']) if pd.notna(current_row.get('tgtlength')) else 0.0,
                'platetype': str(current_row['platetype']) if pd.notna(current_row.get('platetype')) else '',
                'toc': str(current_row['toc']) if pd.notna(current_row.get('toc')) else '',
                'status_cooling': str(current_row['status_cooling']) if pd.notna(current_row.get('status_cooling')) else '',
            })

        print(f'请求完成，耗时: {time.perf_counter() - start_time:.4f} s')
        return diag_res


class DiagnosesAlgorithm:
    def __init__(self, train, test, data_names):
        # 此时的 train 直接是一个 numpy 二维数组，不再是 list
        self.train = train
        self.test = test
        self.data_names = data_names

    def run(self, method):
        diag_res = []
        # 直接遍历测试集的每一块钢板
        for plate in self.test:
            # 不再需要内层循环遍历 5 个模型，直接拿 self.train 这一套基准去算
            if method == 'PCA':
                datum = self.PCA(self.train, [plate])
            elif method == 'single_demension':
                datum = self.single_demension(self.train, [plate], 0.75, 0.95, 0.99)

            diag_res.append(datum)
        return diag_res

    def PCA(self, train, test):
        Xtrain = np.array(train)
        Xtest = np.array(test)

        # 安全校验：维度检查与空数据拦截
        if Xtrain.ndim == 1:
            if Xtrain.size == 0:
                m = Xtest.shape[1] if Xtest.ndim == 2 else (len(Xtest) if Xtest.ndim == 1 else 0)
                return {
                    'T2UCL1': 0.0, 'T2UCL2': 0.0, 'QUCL': 0.0,
                    'T2': 0.0, 'Q': 0.0, 'CONTJ': [0.0] * m, 'contq': []
                }
            else:
                Xtrain = Xtrain.reshape(1, -1)

        X_row, X_col = Xtrain.shape
        if X_row < 2:
            m = Xtest.shape[1] if Xtest.ndim == 2 else X_col
            return {
                'T2UCL1': 0.0, 'T2UCL2': 0.0, 'QUCL': 0.0,
                'T2': 0.0, 'Q': 0.0, 'CONTJ': [0.0] * m, 'contq': []
            }

        if Xtest.ndim == 1:
            Xtest = Xtest.reshape(1, -1)

        X_mean = np.mean(Xtrain, axis=0)
        X_std = np.std(Xtrain, axis=0)
        X_std[X_std == 0] = 1e-8
        Xtrain = (Xtrain - np.tile(X_mean, (X_row, 1))) / np.tile(X_std, (X_row, 1))

        sigmaXtrain = np.cov(Xtrain.T)
        lamda, T = np.linalg.eigh(sigmaXtrain)

        num_pc = 1
        D = -np.sort(-lamda, axis=0)
        lamda_mat = np.diag(lamda)
        while D[0:num_pc].sum(axis=0) / D.sum(axis=0) < 0.9:
            num_pc = num_pc + 1

        P = T[:, np.arange(X_col - num_pc, X_col)]
        T2UCL1 = num_pc * (X_row - 1) * (X_row + 1) * f.ppf(0.99, num_pc, X_row - num_pc) / (X_row * (X_row - num_pc))
        T2UCL2 = num_pc * (X_row - 1) * (X_row + 1) * f.ppf(0.95, num_pc, X_row - num_pc) / (X_row * (X_row - num_pc))

        theta = np.zeros(3)
        for i in range(3):
            theta[i] = np.sum((D[np.arange(num_pc, X_col)]) ** (i + 1))
        h0 = 1 - 2 * theta[0] * theta[2] / (3 * theta[1] ** 2)
        ca = norm.ppf(0.99, 0, 1)

        inner_val = h0 * ca * np.sqrt(np.abs(2. * theta[1])) / theta[0] + 1 + theta[1] * h0 * (h0 - 1.) / (
                    theta[0] ** 2.)
        inner_val = max(inner_val, 1e-8)
        QUCL = theta[0] * (inner_val) ** (1. / h0)

        n, m = Xtest.shape
        Xtest = (Xtest - np.tile(X_mean, (n, 1))) / np.tile(X_std, (n, 1))
        P = np.matrix(P)
        r, y = (P * P.T).shape
        I = np.eye(r, y)

        T2 = np.zeros((n, 1))
        Q = np.zeros((n, 1))
        for i in range(n):
            T2[i] = np.matrix(Xtest[i, :]) * P * np.matrix(
                (lamda_mat[np.ix_(np.arange(m - num_pc, m), np.arange(m - num_pc, m))])).I * P.T * np.matrix(
                Xtest[i, :]).T
            Q[i] = np.matrix(Xtest[i, :]) * (I - P * P.T) * np.matrix(Xtest[i, :]).T

        test_Num = 0
        S = np.array(np.matrix(Xtest[test_Num, :]) * P[:, np.arange(0, num_pc)])
        S = S[0]

        r_list = []
        for i in range(num_pc):
            if S[i] ** 2 / lamda_mat[i, i] > T2UCL1 / num_pc:
                r_list.append(i)

        cont = np.zeros((len(r_list), m))
        if len(r_list) > 0:
            for i, pc_idx in enumerate(r_list):
                for j in range(m):
                    cont[i][j] = np.fabs(S[pc_idx] / D[pc_idx] * P[j, pc_idx] * Xtest[test_Num, j])

        CONTJ = []
        for j in range(m):
            CONTJ.append(np.sum(cont[:, j]))

        e = np.matrix(Xtest[test_Num, :]) * (I - P * P.T)
        e = np.array(e)[0]
        contq = e ** 2

        return {
            'T2UCL1': float(T2UCL1),
            'T2UCL2': float(T2UCL2),
            'QUCL': float(QUCL),
            'T2': float(T2[0, 0]) if T2.size > 0 else 0.0,
            'Q': float(Q[0, 0]) if Q.size > 0 else 0.0,
            'CONTJ': CONTJ,
            'contq': contq.tolist()
        }
    def single_demension(self, train, test, quantile, extremum_quantile, super_extremum_quantile):
        meas_range = meas_index()
        train_np = np.array(train)
        test_np = np.array(test)

        train_meas = train_np[:, meas_range[0]:meas_range[1] + 1]
        train_without_meas = np.concatenate((train_np[:, 0:meas_range[0]], train_np[:, meas_range[1] + 1:]), axis=1)

        # 防止除以0
        meas_diff = train_meas.max(axis=0) - train_meas.min(axis=0)
        meas_diff[meas_diff == 0] = 1
        without_meas_diff = train_without_meas.max(axis=0) - train_without_meas.min(axis=0)
        without_meas_diff[without_meas_diff == 0] = 1

        norm_train_meas = ((train_meas - train_meas.min(axis=0)) / meas_diff)
        norm_train_without_meas = ((train_without_meas - train_without_meas.min(axis=0)) / without_meas_diff)

        test_meas = test_np[:, meas_range[0]:meas_range[1] + 1]
        test_without_meas = np.concatenate((test_np[:, 0:meas_range[0]], test_np[:, meas_range[1] + 1:]), axis=1)
        norm_test_meas = ((test_meas - train_meas.min(axis=0)) / meas_diff)
        norm_test_without_meas = ((test_without_meas - train_without_meas.min(axis=0)) / without_meas_diff)

        norm_test_meas[np.isnan(norm_test_meas)] = 0
        norm_test_without_meas[np.isnan(norm_test_without_meas)] = 0

        lower_limit, upper_limit, \
            extremum_lower_limit, extremum_upper_limit, \
            s_extremum_lower_limit, s_extremum_upper_limit = \
            self.myQuantile(train_without_meas, quantile, extremum_quantile, super_extremum_quantile)

        meas_lower_limit, meas_upper_limit, \
            meas_extremum_lower_limit, meas_extremum_upper_limit, \
            meas_s_extremum_lower_limit, meas_s_extremum_upper_limit = \
            self.myQuantile(train_meas, quantile, extremum_quantile, super_extremum_quantile)

        norm_lower_limit, norm_upper_limit, \
            norm_extremum_lower_limit, norm_extremum_upper_limit, \
            norm_s_extremum_lower_limit, norm_s_extremum_upper_limit = \
            self.myQuantile(norm_train_without_meas, quantile, extremum_quantile, super_extremum_quantile)

        norm_meas_lower_limit, norm_meas_upper_limit, \
            norm_meas_extremum_lower_limit, norm_meas_extremum_upper_limit, \
            norm_meas_s_extremum_lower_limit, norm_meas_s_extremum_upper_limit = \
            self.myQuantile(norm_train_meas, quantile, extremum_quantile, super_extremum_quantile)

        result = []
        meas_i = 0
        proc_i = 0
        for idx, col_name in enumerate(self.data_names):
            if meas_range[0] <= idx and idx <= meas_range[1]:
                result.append({
                    'name': col_name,
                    'original_value': test_meas[0][meas_i],
                    'original_l': meas_lower_limit[meas_i],
                    'original_u': meas_upper_limit[meas_i],
                    'extremum_original_l': meas_extremum_lower_limit[meas_i],
                    'extremum_original_u': meas_extremum_upper_limit[meas_i],
                    's_extremum_original_l': meas_s_extremum_lower_limit[meas_i],
                    's_extremum_original_u': meas_s_extremum_upper_limit[meas_i],
                    'value': norm_test_meas[0][meas_i],
                    'l': norm_meas_lower_limit[meas_i],
                    'u': norm_meas_upper_limit[meas_i],
                    'extremum_l': norm_meas_extremum_lower_limit[meas_i],
                    'extremum_u': norm_meas_extremum_upper_limit[meas_i],
                    's_extremum_l': norm_meas_s_extremum_lower_limit[meas_i],
                    's_extremum_u': norm_meas_s_extremum_upper_limit[meas_i]
                })
                meas_i += 1
            else:
                result.append({
                    'name': col_name,
                    'original_value': test_without_meas[0][proc_i],
                    'original_l': lower_limit[proc_i],
                    'original_u': upper_limit[proc_i],
                    'extremum_original_l': extremum_lower_limit[proc_i],
                    'extremum_original_u': extremum_upper_limit[proc_i],
                    's_extremum_original_l': s_extremum_lower_limit[proc_i],
                    's_extremum_original_u': s_extremum_upper_limit[proc_i],
                    'value': norm_test_without_meas[0][proc_i],
                    'l': norm_lower_limit[proc_i],
                    'u': norm_upper_limit[proc_i],
                    'extremum_l': norm_extremum_lower_limit[proc_i],
                    'extremum_u': norm_extremum_upper_limit[proc_i],
                    's_extremum_l': norm_s_extremum_lower_limit[proc_i],
                    's_extremum_u': norm_s_extremum_upper_limit[proc_i]
                })
                proc_i += 1
        return result

    def myQuantile(self, data, q1, q2, q3):
        q1_lower = np.quantile(data, 1 - q1, axis=0)
        q1_upper = np.quantile(data, q1, axis=0)
        q2_lower = np.quantile(data, 1 - q2, axis=0)
        q2_upper = np.quantile(data, q2, axis=0)
        q3_lower = np.quantile(data, 1 - q3, axis=0)
        q3_upper = np.quantile(data, q3, axis=0)
        return q1_lower, q1_upper, q2_lower, q2_upper, q3_lower, q3_upper