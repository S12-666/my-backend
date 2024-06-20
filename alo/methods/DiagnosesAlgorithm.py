import numpy as np
from scipy.stats import norm, f
from .define import meas_index, data_names
class DiagnosesAlgorithm:
    def __init__(self, train, test):
        self.train = train
        self.test = test
    def run(self, method):
        diag_res = []
        for plate in self.test:         
            plate_diag_res = []
            for train_data in self.train:     
                datum = []
                if method == 'PCA':
                    datum = self.PCA(train_data, [plate])
                elif method == 'single_demension':
                    datum = self.single_demension(train_data, [plate], 0.75, 0.95, 0.99)
                plate_diag_res.append(datum)
            diag_res.append(plate_diag_res)
        return diag_res
    def PCA(self, train, test):
        Xtrain = np.array(train)
        Xtest = np.array(test)
        X_row = Xtrain.shape[0]
        X_col = Xtrain.shape[1]
        X_mean = np.mean(Xtrain, axis=0)
        X_std = np.std(Xtrain, axis=0)
        Xtrain = (Xtrain - np.tile(X_mean, (X_row, 1))) / np.tile(X_std, (X_row, 1))
        sigmaXtrain = np.cov(Xtrain.T)
        [lamda, T] = np.linalg.eigh(sigmaXtrain)
        num_pc = 1
        D = -np.sort(-lamda, axis=0)
        lamda = np.diag(lamda)
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
        QUCL = theta[0] * (
                h0 * ca * np.sqrt(2. * theta[1]) / theta[0] + 1 + theta[1] * h0 * (h0 - 1.) / theta[0] ** 2.) ** (
                       1. / h0)
        n = Xtest.shape[0]
        m = Xtest.shape[1]
        Xtest = (Xtest - np.tile(X_mean, (n, 1))) / np.tile(X_std, (n, 1))
        P = np.matrix(P)
        [r, y] = (P * P.T).shape
        I = np.eye(r, y)
        T2 = np.zeros((n, 1))
        Q = np.zeros((n, 1))
        for i in range(n):
            T2[i] = np.matrix(Xtest[i, :]) * P * np.matrix(
                (lamda[np.ix_(np.arange(m - num_pc, m), np.arange(m - num_pc, m))])).I * P.T * np.matrix(Xtest[i, :]).T
            Q[i] = np.matrix(Xtest[i, :]) * (I - P * P.T) * np.matrix(Xtest[i, :]).T
        test_Num = 0
        S = np.array(np.matrix(Xtest[test_Num, :]) * P[:, np.arange(0, num_pc)])
        S = S[0]
        r = []
        for i in range(num_pc):
            if S[i] ** 2 / lamda[i, 0] > T2UCL1 / num_pc:
                r.append(i)
        cont = np.zeros((len(r), m))
        for i in [len(r) - 1]:
            for j in range(m):
                cont[i][j] = np.fabs(S[i] / D[i] * P[j, i] * Xtest[test_Num, j])
        CONTJ = []
        for j in range(m):
            CONTJ.append(np.sum(cont[:, j]))
        e = np.matrix(Xtest[test_Num, :]) * (I - P * P.T)
        e = np.array(e)[0]
        contq = e ** 2
        return {
            'T2UCL1': T2UCL1,
            'T2UCL2': T2UCL2,
            'QUCL': QUCL,
            'T2': T2,
            'Q': Q,
            'CONTJ': CONTJ,
            'contq': contq
        }
    def single_demension(self, train, test, quantile, extremum_quantile, super_extremum_quantile):
        meas_range = meas_index()
        train_np = np.array(train)
        test_np = np.array(test)
        row = train_np.shape[0]
        col = train_np.shape[1]
        train_meas = train_np[:, meas_range[0]:meas_range[1]+1]
        train_without_meas = np.concatenate((train_np[:, 0:meas_range[0]], train_np[:, meas_range[1]+1:]), axis=1)
        norm_train_meas = ((train_meas - train_meas.min(axis=0)) / (train_meas.max(axis=0) - train_meas.min(axis=0)))
        norm_train_without_meas = ((train_without_meas - train_without_meas.min(axis=0)) / (train_without_meas.max(axis=0) - train_without_meas.min(axis=0)))
        test_meas = test_np[:, meas_range[0]:meas_range[1]+1]
        test_without_meas = np.concatenate((test_np[:, 0:meas_range[0]], test_np[:, meas_range[1]+1:]), axis=1)
        norm_test_meas = ((test_meas - train_meas.min(axis=0)) / (train_meas.max(axis=0) - train_meas.min(axis=0)))
        norm_test_without_meas = ((test_without_meas - train_without_meas.min(axis=0)) / (train_without_meas.max(axis=0) - train_without_meas.min(axis=0)))
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
        for idx, col_name in enumerate(data_names):
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
