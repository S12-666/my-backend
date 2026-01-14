import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np


class RealTimeTrainer:

    @staticmethod
    def train_xgboost(df, feature_cols, target_col):
        """
        :return: (model, explainer, metrics_dict)
        """
        if df.empty: return None, None, {}

        # 1. 准备数据
        X = df[feature_cols]
        y = df[target_col]

        try:
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        except ValueError:
            X_train, X_val, y_train, y_val = X, X, y, y

        # 3. 动态权重
        num_neg = (y_train == 0).sum()
        num_pos = (y_train == 1).sum()
        weight = num_pos / num_neg if num_neg > 0 else 1.0

        params = {
            'objective': 'binary:logistic',
            'tree_method': 'gpu_hist',
            'gpu_id': 0,
            'eval_metric': 'auc',
            'scale_pos_weight': weight,
            'max_depth': 5,
            'n_estimators': 150,
            'learning_rate': 0.05,
            'verbosity': 0
        }

        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

        y_pred = model.predict(X_val)
        y_prob = model.predict_proba(X_val)[:, 1]  # 正常概率

        try:
            auc = roc_auc_score(y_val, y_prob)
        except:
            auc = 0.5

        acc = accuracy_score(y_val, y_pred)

        bad_total = (y_val == 0).sum()
        bad_caught = ((y_val == 0) & (y_pred == 0)).sum()
        recall_abnormal = bad_caught / bad_total if bad_total > 0 else 0.0

        metrics = {
            "auc": round(float(auc), 3),
            "accuracy": round(float(acc), 3),
            "recall_abnormal": round(float(recall_abnormal), 3),  # 关键指标
            "train_size": len(X_train),
            "val_size": len(X_val)
        }

        explainer = shap.TreeExplainer(model)

        return model, explainer, metrics

    @staticmethod
    def train_isolation_forest(df, feature_cols):
        X = df[feature_cols].fillna(0)

        from sklearn.ensemble import IsolationForest
        model = IsolationForest(n_estimators=100, contamination=0.01, n_jobs=-1, random_state=42)
        model.fit(X)

        metrics = {
            "model_type": "Unsupervised",
            "contamination": 0.01,
            "train_size": len(X)
        }

        return model, metrics

    @staticmethod
    def train_pca_anomaly(df, feature_cols):
        """
        现场训练 PCA 异常检测模型
        :return: (pipeline, metadata)
        """
        X = df[feature_cols].fillna(0)

        if len(X) > 50000:
            X = X.sample(n=50000, random_state=42)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        pca = PCA(n_components=0.90)
        pca.fit(X_scaled)

        X_recon = pca.inverse_transform(pca.transform(X_scaled))
        recon_errors = np.sum(np.square(X_scaled - X_recon), axis=1)
        confidence_level = 99.0

        threshold = np.percentile(recon_errors, confidence_level)
        info_retention = np.sum(pca.explained_variance_ratio_)

        model_bundle = {
            "scaler": scaler,
            "pca": pca,
            "threshold": threshold,
            "feature_cols": feature_cols
        }

        metrics = {
            "model_type": "PCA_Reconstruction",
            "train_size": len(X),
            "accuracy": round(float(info_retention), 4),
            "recall_abnormal": round(float(confidence_level / 100), 4),
            "threshold": round(float(threshold), 2)
        }

        return model_bundle, metrics

    @staticmethod
    def predict_pca(model_bundle, X_input):
        """
        使用 PCA 模型预测并计算“类 SHAP”值
        """
        scaler = model_bundle['scaler']
        pca = model_bundle['pca']
        threshold = model_bundle['threshold']
        feature_cols = model_bundle['feature_cols']

        X_scaled = scaler.transform(X_input)

        X_pca = pca.transform(X_scaled)
        X_recon = pca.inverse_transform(X_pca)

        diff = np.abs(X_scaled - X_recon)[0]  # 取第一行

        total_error = np.sum(np.square(X_scaled - X_recon))
        pred_label = 0 if total_error > threshold else 1  # 0异常, 1正常

        abnormal_prob = 1 - np.exp(-total_error / threshold)

        feature_importance = []
        for name, contribution, actual in zip(feature_cols, diff, X_input.iloc[0]):
            feature_importance.append({
                "feature": name,
                "shap_value": float(contribution),
                "actual_value": float(actual)
            })

        # 排序
        feature_importance.sort(key=lambda x: x['shap_value'], reverse=True)

        return pred_label, abnormal_prob, feature_importance[:10], total_error