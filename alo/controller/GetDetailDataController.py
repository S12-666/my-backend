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
            current_t2_ucl = pca_res[i].get('T2UCL1', 0)
            current_q_ucl = pca_res[i].get('QUCL', 0)
            for j, name in enumerate(self.data_names):
                # single_res[i] 是一条钢板的所有测点列表，j 是对应的测点索引
                # pca_res[i] 是一条钢板的全局指标字典
                plate_res.append({
                    'name': name,
                    'T2': float(format(pca_res[i].get('T2', 0), '.4f')),
                    'Q': float(format(pca_res[i].get('Q', 0), '.4f')),
                    'T2_cont': float(format(contj_list[j], '.4f')) if j < len(contj_list) else 0.0,
                    'Q_cont': float(format(contq_list[j], '.4f')) if j < len(contq_list) else 0.0,
                    'T2UCL1': float(format(current_t2_ucl, '.4f')),
                    'QUCL': float(format(current_q_ucl, '.4f')),
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

        # 🚀 修复点 1：防止由于变量为常数导致的除法无限放大
        # 如果标准差接近 0，强制设为 1，这样归一化后保留原始偏离量
        X_std[X_std < 1e-6] = 1.0

        Xtrain_norm = (Xtrain - X_mean) / X_std

        # 计算协方差与特征值 (rowvar=False 代表列是变量)
        sigmaXtrain = np.cov(Xtrain_norm, rowvar=False)
        lamda, T = np.linalg.eigh(sigmaXtrain)

        # 🚀 修复点 2：主动将特征值和特征向量【降序排列】，彻底理清对应关系
        idx = np.argsort(lamda)[::-1]
        lamda_desc = lamda[idx]
        T_desc = T[:, idx]

        # 强行拉平由于浮点精度产生的极小值或负数特征值
        lamda_desc = np.maximum(lamda_desc, 1e-8)

        # 选取主成分 (根据累计方差贡献率 > 90%)
        total_var = np.sum(lamda_desc)
        cum_var = np.cumsum(lamda_desc) / total_var
        num_pc = np.searchsorted(cum_var, 0.9) + 1
        num_pc = min(num_pc, X_col)  # 兜底防止越界

        # 获取选定的载荷矩阵 P 和 对应的特征值
        P = T_desc[:, :num_pc]
        selected_lamda = lamda_desc[:num_pc]

        # 计算控制限 (UCL)
        F_99 = f.ppf(0.99, num_pc, X_row - num_pc)
        F_95 = f.ppf(0.95, num_pc, X_row - num_pc)
        T2UCL1 = num_pc * (X_row - 1) * (X_row + 1) * F_99 / (X_row * (X_row - num_pc))
        T2UCL2 = num_pc * (X_row - 1) * (X_row + 1) * F_95 / (X_row * (X_row - num_pc))

        # 计算 Q (SPE) 的控制限
        rem_lamda = lamda_desc[num_pc:]
        theta = [np.sum(rem_lamda ** (i + 1)) for i in range(3)]

        QUCL = 0.0
        if theta[0] > 1e-8:
            h0 = 1 - 2 * theta[0] * theta[2] / (3 * theta[1] ** 2) if theta[1] > 1e-8 else 1
            ca = norm.ppf(0.99)
            inner_val = h0 * ca * np.sqrt(2. * theta[1]) / theta[0] + 1 + theta[1] * h0 * (h0 - 1.) / (theta[0] ** 2.)
            inner_val = max(inner_val, 1e-8)
            QUCL = theta[0] * (inner_val) ** (1. / h0)

        self.pca_model = {
            'valid': True,
            'mean': X_mean,
            'std': X_std,
            'P': P,
            'selected_lamda': selected_lamda,
            'num_pc': num_pc,
            'T2UCL1': T2UCL1,
            'T2UCL2': T2UCL2,
            'QUCL': QUCL
        }

    def _predict_pca(self, plate):
        """对单块钢板进行极速数学评估"""
        mod = self.pca_model
        m = len(plate)
        if not mod.get('valid', False):
            return {
                'T2UCL1': 0.0, 'T2UCL2': 0.0, 'QUCL': 0.0,
                'T2': 0.0, 'Q': 0.0, 'CONTJ': [0.0] * m, 'contq': [0.0] * m
            }

        # 归一化测试数据
        Xtest_norm = (np.array(plate) - mod['mean']) / mod['std']

        P = mod['P']
        selected_lamda = mod['selected_lamda']

        # 1. 计算主成分得分 S = X * P
        S = np.dot(Xtest_norm, P)

        # 2. 计算 T2
        T2 = np.sum((S ** 2) / selected_lamda)

        # 3. 计算 Q (重构误差)
        X_reconstruct = np.dot(S, P.T)
        E = Xtest_norm - X_reconstruct
        Q = np.sum(E ** 2)

        # 🚀 修复点：移除原有的 if 拦截阈值，保证前端随时有数据可以画图
        # 并且将原来的双层 for 循环改写成了矩阵向量化运算，性能极大提升

        # T2 贡献度分解：c_j = sum( | (S_i / lamda_i) * P_ji * X_norm_j | )
        S_weighted = S / selected_lamda  # shape: (num_pc,)

        # 利用 numpy 广播机制直接生成 (m, num_pc) 的贡献矩阵，然后按行求和
        cont_matrix = np.abs(P * S_weighted * Xtest_norm[:, np.newaxis])
        cont_t2 = np.sum(cont_matrix, axis=1)

        # Q 贡献度就是误差的平方
        contq = E ** 2

        # 强制将结果截断，防范由于极个别恶劣工况产生的 inf 值引发 JSON 序列化崩溃
        return {
            'T2UCL1': float(mod['T2UCL1']), 'T2UCL2': float(mod['T2UCL2']), 'QUCL': float(mod['QUCL']),
            'T2': float(np.clip(T2, 0, 1e8)), 'Q': float(np.clip(Q, 0, 1e8)),
            'CONTJ': np.clip(cont_t2, 0, 1e6).tolist(), 'contq': np.clip(contq, 0, 1e6).tolist()
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