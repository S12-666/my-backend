import pandas as pd
import numpy as np
import time
from scipy.stats import norm, f
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
            contj_list = pca_res[i].get('CONTJ', [])
            contq_list = pca_res[i].get('contq', [])
            for j, name in enumerate(self.data_names):
                # single_res[i] 是一条钢板的所有测点列表，j 是对应的测点索引
                # pca_res[i] 是一条钢板的全局指标字典
                plate_res.append({
                    'name': name,
                    'T2': float(format(pca_res[i].get('T2', 0), '.4f')),
                    'Q': float(format(pca_res[i].get('Q', 0), '.4f')),
                    'T2_cont': float(format(contj_list[j], '.4f')) if j < len(contj_list) else 0.0,
                    'Q_cont': float(format(contq_list[j], '.4f')) if j < len(contq_list) else 0.0,
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
        # 统一转为 numpy 数组，方便矩阵运算
        self.train = np.array(train)
        self.test = np.array(test)
        self.data_names = data_names

        # 预留存储训练好的模型参数
        self.pca_model = None
        self.single_dim_model = None

    def run(self, method):
        diag_res = []

        # 1. 训练阶段：在循环外预先计算基准模型参数（仅执行一次）
        if method == 'PCA':
            self._fit_pca()
        elif method == 'single_demension':
            self._fit_single_demension(0.75, 0.95, 0.99)

        # 2. 预测阶段：只进行纯数学代入计算，速度极快
        for plate in self.test:
            if method == 'PCA':
                datum = self._predict_pca(plate)
            elif method == 'single_demension':
                datum = self._predict_single_demension(plate)
            diag_res.append(datum)

        return diag_res

    # ==================== PCA 算法模块 ====================
    def _fit_pca(self):
        """仅对 train 数据执行一次：计算均值、方差、特征向量及控制限"""
        if self.pca_model is not None:
            return

        Xtrain = self.train
        if Xtrain.ndim == 1 or Xtrain.size == 0 or Xtrain.shape[0] < 2:
            self.pca_model = {'valid': False}
            return

        X_row, X_col = Xtrain.shape
        X_mean = np.mean(Xtrain, axis=0)
        X_std = np.std(Xtrain, axis=0)
        X_std[X_std == 0] = 1e-8

        Xtrain_norm = (Xtrain - X_mean) / X_std

        # 协方差与特征值分解
        sigmaXtrain = np.cov(Xtrain_norm.T)
        lamda, T = np.linalg.eigh(sigmaXtrain)

        # 选取主成分
        D = -np.sort(-lamda, axis=0)
        D[D < 1e-8] = 1e-8
        num_pc = 1
        # D = -np.sort(-lamda, axis=0)
        while D[0:num_pc].sum() / D.sum() < 0.9:
            num_pc += 1

        P = T[:, np.arange(X_col - num_pc, X_col)]
        P_mat = np.matrix(P)

        # 计算控制限 (UCL)
        T2UCL1 = num_pc * (X_row - 1) * (X_row + 1) * f.ppf(0.99, num_pc, X_row - num_pc) / (X_row * (X_row - num_pc))
        T2UCL2 = num_pc * (X_row - 1) * (X_row + 1) * f.ppf(0.95, num_pc, X_row - num_pc) / (X_row * (X_row - num_pc))

        theta = [np.sum((D[num_pc:X_col]) ** (i + 1)) for i in range(3)]
        h0 = 1 - 2 * theta[0] * theta[2] / (3 * theta[1] ** 2) if theta[1] != 0 else 1
        ca = norm.ppf(0.99, 0, 1)

        QUCL = 0.0
        if theta[0] != 0:
            inner_val = h0 * ca * np.sqrt(np.abs(2. * theta[1])) / theta[0] + 1 + theta[1] * h0 * (h0 - 1.) / (
                        theta[0] ** 2.)
            inner_val = max(inner_val, 1e-8)
            QUCL = theta[0] * (inner_val) ** (1. / h0)

        # 取出被选中的主成分特征值
        selected_lamda = lamda[np.arange(X_col - num_pc, X_col)]

        # 【核心修复】：防止除以0或极小数导致无穷大
        # 将所有小于 1e-6 的特征值强制拉平到 1e-6
        selected_lamda = np.where(selected_lamda < 1e-6, 1e-6, selected_lamda)

        # 然后再求逆
        lamda_inv = np.matrix(np.diag(1.0 / selected_lamda))
        I_minus_PPT = np.eye(X_col) - P_mat * P_mat.T

        # 保存模型
        self.pca_model = {
            'valid': True, 'mean': X_mean, 'std': X_std, 'P': P_mat,
            'lamda_inv': lamda_inv, 'I_minus_PPT': I_minus_PPT,
            'num_pc': num_pc, 'D': D, 'T2UCL1': T2UCL1, 'T2UCL2': T2UCL2, 'QUCL': QUCL
        }

    def _predict_pca(self, plate):
        """对单块钢板进行高速向量运算"""
        mod = self.pca_model
        m = len(plate)
        if not mod.get('valid', False):
            return {
                'T2UCL1': 0.0, 'T2UCL2': 0.0, 'QUCL': 0.0,
                'T2': 0.0, 'Q': 0.0, 'CONTJ': [0.0] * m, 'contq': [0.0] * m
            }

        Xtest_norm = (np.array(plate) - mod['mean']) / mod['std']
        Xtest_mat = np.matrix(Xtest_norm)

        # 计算得分
        T2 = Xtest_mat * mod['P'] * mod['lamda_inv'] * mod['P'].T * Xtest_mat.T
        Q = Xtest_mat * mod['I_minus_PPT'] * Xtest_mat.T

        # 计算贡献度 (Contribution)
        S = np.array(Xtest_mat * mod['P'])[0]
        cont_t2 = np.zeros(m)
        D_sub = mod['D'][m - mod['num_pc']:]

        for i in range(mod['num_pc']):
            if (S[i] ** 2 / D_sub[i]) > (mod['T2UCL1'] / mod['num_pc']):
                for j in range(m):
                    cont_t2[j] += np.fabs(S[i] / D_sub[i] * mod['P'][j, i] * Xtest_norm[j])

        e = np.array(Xtest_mat * mod['I_minus_PPT'])[0]
        contq = e ** 2

        return {
            'T2UCL1': float(mod['T2UCL1']), 'T2UCL2': float(mod['T2UCL2']), 'QUCL': float(mod['QUCL']),
            'T2': float(T2[0, 0]), 'Q': float(Q[0, 0]),
            'CONTJ': cont_t2.tolist(), 'contq': contq.tolist()
        }

    # ==================== 单变量分位数模块 ====================
    def _fit_single_demension(self, q1, q2, q3):
        """仅对 train 数据执行一次：计算最大最小边界和各个分位数"""
        meas_range = meas_index()
        train_meas = self.train[:, meas_range[0]:meas_range[1] + 1]
        train_without_meas = np.concatenate((self.train[:, 0:meas_range[0]], self.train[:, meas_range[1] + 1:]), axis=1)

        meas_diff = train_meas.max(axis=0) - train_meas.min(axis=0)
        meas_diff[meas_diff == 0] = 1
        without_meas_diff = train_without_meas.max(axis=0) - train_without_meas.min(axis=0)
        without_meas_diff[without_meas_diff == 0] = 1

        norm_train_meas = ((train_meas - train_meas.min(axis=0)) / meas_diff)
        norm_train_without_meas = ((train_without_meas - train_without_meas.min(axis=0)) / without_meas_diff)

        # 缓存计算结果
        self.single_dim_model = {
            'meas_range': meas_range,
            'train_meas_min': train_meas.min(axis=0),
            'meas_diff': meas_diff,
            'train_without_meas_min': train_without_meas.min(axis=0),
            'without_meas_diff': without_meas_diff,

            # 分别缓存测量变量和过程变量的多级预警线（原始值和归一化值）
            'limits_without_meas': self.myQuantile(train_without_meas, q1, q2, q3),
            'limits_meas': self.myQuantile(train_meas, q1, q2, q3),
            'norm_limits_without_meas': self.myQuantile(norm_train_without_meas, q1, q2, q3),
            'norm_limits_meas': self.myQuantile(norm_train_meas, q1, q2, q3)
        }

    def _predict_single_demension(self, plate):
        """利用缓存好的分位线快速装配单条钢板的数据"""
        mod = self.single_dim_model
        meas_range = mod['meas_range']

        plate = np.array(plate)
        test_meas = plate[meas_range[0]:meas_range[1] + 1]
        test_without_meas = np.concatenate((plate[0:meas_range[0]], plate[meas_range[1] + 1:]))

        norm_test_meas = (test_meas - mod['train_meas_min']) / mod['meas_diff']
        norm_test_without_meas = (test_without_meas - mod['train_without_meas_min']) / mod['without_meas_diff']

        norm_test_meas[np.isnan(norm_test_meas)] = 0
        norm_test_without_meas[np.isnan(norm_test_without_meas)] = 0

        # 解构基准线数据
        l_wm, u_wm, el_wm, eu_wm, sel_wm, seu_wm = mod['limits_without_meas']
        nl_wm, nu_wm, nel_wm, neu_wm, nsel_wm, nseu_wm = mod['norm_limits_without_meas']

        l_m, u_m, el_m, eu_m, sel_m, seu_m = mod['limits_meas']
        nl_m, nu_m, nel_m, neu_m, nsel_m, nseu_m = mod['norm_limits_meas']

        result = []
        meas_i, proc_i = 0, 0

        for idx, col_name in enumerate(self.data_names):
            if meas_range[0] <= idx <= meas_range[1]:
                result.append({
                    'name': col_name,
                    'original_value': test_meas[meas_i],
                    'original_l': l_m[meas_i], 'original_u': u_m[meas_i],
                    'extremum_original_l': el_m[meas_i], 'extremum_original_u': eu_m[meas_i],
                    's_extremum_original_l': sel_m[meas_i], 's_extremum_original_u': seu_m[meas_i],
                    'value': norm_test_meas[meas_i],
                    'l': nl_m[meas_i], 'u': nu_m[meas_i],
                    'extremum_l': nel_m[meas_i], 'extremum_u': neu_m[meas_i],
                    's_extremum_l': nsel_m[meas_i], 's_extremum_u': nseu_m[meas_i]
                })
                meas_i += 1
            else:
                result.append({
                    'name': col_name,
                    'original_value': test_without_meas[proc_i],
                    'original_l': l_wm[proc_i], 'original_u': u_wm[proc_i],
                    'extremum_original_l': el_wm[proc_i], 'extremum_original_u': eu_wm[proc_i],
                    's_extremum_original_l': sel_wm[proc_i], 's_extremum_original_u': seu_wm[proc_i],
                    'value': norm_test_without_meas[proc_i],
                    'l': nl_wm[proc_i], 'u': nu_wm[proc_i],
                    'extremum_l': nel_wm[proc_i], 'extremum_u': neu_wm[proc_i],
                    's_extremum_l': nsel_wm[proc_i], 's_extremum_u': nseu_wm[proc_i]
                })
                proc_i += 1
        return result

    def myQuantile(self, data, q1, q2, q3):
        # 逻辑保持不变
        q1_lower = np.quantile(data, 1 - q1, axis=0)
        q1_upper = np.quantile(data, q1, axis=0)
        q2_lower = np.quantile(data, 1 - q2, axis=0)
        q2_upper = np.quantile(data, q2, axis=0)
        q3_lower = np.quantile(data, 1 - q3, axis=0)
        q3_upper = np.quantile(data, q3, axis=0)
        return q1_lower, q1_upper, q2_lower, q2_upper, q3_lower, q3_upper