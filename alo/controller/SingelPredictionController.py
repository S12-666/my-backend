import pandas as pd
import numpy as np
from flask import current_app
from ..models import queryPredictionData
from ..api import singelSteel
from ..methods.RealTimeTrainer import RealTimeTrainer
import json


class SingelPredictionController:
    def __init__(self, para):
        self.para = para
        self.upid = para.get('upid')
        # status_cooling: 0=过冷却, 1=未过冷却
        self.status_cooling = para.get('status_cooling')
        self.platetype = para.get('platetype')
        self.label = para.get('label')

    def run(self):
        row, col_names = queryPredictionData.get_singel(self.upid)
        feature_cols = singelSteel.data_names if self.status_cooling == 0 else singelSteel.without_cooling_data_names

        data_df = pd.DataFrame(data=row, columns=col_names)
        stats_raw = data_df.loc[0, 'stats']

        stats_dict = {}
        for name in feature_cols:
            stats_dict[name] = stats_raw.get(name, 0) if stats_raw else 0

        expanded_stats_df = pd.DataFrame([stats_dict])
        X_input = expanded_stats_df[feature_cols]

        labels_map = {
            'pa': self.label[0],
            'pf': self.label[1],
            'pn': self.label[2],
            'ps': self.label[3],
            'gs': self.label[4]
        }

        diagnosis_result = {
            "upid": self.upid,
            "cooling_status": self.status_cooling,
            "predictions": {}
        }

        if self.status_cooling == 0:
            strategies = {
                'pa': 'supervised',
                'pf': 'supervised',
                'pn': 'supervised',
                'ps': 'unsupervised',
                'gs': 'unsupervised'
            }
        else:
            strategies = {
                'pa': 'supervised',
                'pf': 'supervised',
                'pn': 'unsupervised',  # 未过冷却落锤改为无监督
                'ps': 'unsupervised',
                'gs': 'unsupervised'
            }

        # 遍历每个指标
        for target, method in strategies.items():
            current_status = labels_map.get(target, 2)

            # --- A. 如果标签已知 (非2)，直接返回事实 ---
            if current_status != 2:
                diagnosis_result['predictions'][target] = {
                    "status": "known",
                    "pred_label": current_status,
                    "msg": "已检测数据，无需预测",
                    "abnormal_prob": 0.0 if current_status == 1 else 1.0
                }
                continue

            if method == 'supervised':
                self._train_predict_supervised(
                    X_input, feature_cols, target, diagnosis_result
                )
            else:
                self._train_predict_unsupervised(
                    X_input, feature_cols, target, diagnosis_result
                )

        return diagnosis_result

    def _train_predict_supervised(self, X_input, feature_cols, target_name, result_dict):
        """现场训练 XGBoost 并预测"""
        try:
            data, columns = queryPredictionData.get_specific_train_data(self.status_cooling, self.platetype, target_name)
            train_data = self._data_process(data, target_name)
            if train_data.empty or len(train_data) < 50:
                result_dict['predictions'][target_name] = {"status": "error", "msg": "训练样本不足"}
                return

            model, explainer, metrics = RealTimeTrainer.train_xgboost(train_data, feature_cols, target_name)
            if not model:
                result_dict['predictions'][target_name] = {"status": "error", "msg": "训练失败"}
                return

            prob_abnormal = model.predict_proba(X_input)[:, 0][0]
            pred_label = model.predict(X_input)[0]

            shap_values_obj = explainer(X_input)
            feature_importance = self._extract_shap_features(X_input, shap_values_obj)

            result_dict['predictions'][target_name] = {
                "status": "success",
                "pred_label": int(pred_label),
                "abnormal_prob": round(float(prob_abnormal), 4),
                "shap_base_value": float(shap_values_obj.base_values[0]),
                "top_features": feature_importance,
                "model_metrics": metrics
            }


        except Exception as e:
            current_app.logger.error(f"监督任务 {target_name} 失败: {e}")
            result_dict['predictions'][target_name] = {"status": "error", "msg": str(e)}

    def _train_predict_unsupervised(self, X_input, feature_cols, target_name, result_dict):
        """处理无监督预测 (PCA版 - 统一样式)"""
        try:
            data, columns = queryPredictionData.get_unsupervised_train_data(self.status_cooling, self.platetype, target_name)
            # 1. 调用实时训练器
            DF = pd.DataFrame(data=data, columns=columns)
            train_data = self._data_process(data, target_name)
            model_bundle, metrics = RealTimeTrainer.train_pca_anomaly(train_data, feature_cols)

            # 2. 预测
            pred_label, prob, top_features, current_error = RealTimeTrainer.predict_pca(model_bundle, X_input)

            result_dict['predictions'][target_name] = {
                "status": "success",
                "pred_label": int(pred_label),
                "abnormal_prob": round(float(prob), 4),
                "shap_base_value": 0.0,
                "top_features": top_features,
                "msg": "基于工艺一致性的重构检测",
                "model_metrics": metrics,
                "instance_metrics": {
                    "current_score": round(float(current_error), 2),
                    "threshold_score": metrics['threshold'],
                    "is_safe": bool(current_error <= metrics['threshold'])
                }
            }
        except Exception as e:
            result_dict['predictions'][target_name] = {"status": "error", "msg": str(e)}

    def _extract_shap_features(self, X, shap_values_obj):
        """辅助函数：提取 SHAP"""
        shap_vals = shap_values_obj.values[0]
        feature_importance = []
        for name, val, actual in zip(X.columns, shap_vals, X.iloc[0]):
            feature_importance.append({
                "feature": name,
                "shap_value": float(val),
                "actual_value": float(actual)
            })
        feature_importance.sort(key=lambda x: abs(x['shap_value']), reverse=True)
        return feature_importance[:10]

    def _data_process(self, data, target_name):
        labels_map = {
            'pa': 0,
            'pf': 1,
            'pn': 2,
            'ps': 3,
            'gs': 4
        }
        process_data = []
        index = labels_map.get(target_name)
        data_names = singelSteel.data_names if self.status_cooling == 0 else singelSteel.without_cooling_data_names
        for item in data:
            if item[2] is None:
                continue
            row = []
            for data_name in data_names:
                row.append(item[1].get(data_name))
            label_array = json.loads(item[2].replace('{', '[').replace('}', ']'))
            label = label_array[index]
            row.append(label)
            process_data.append(row)

        columns = data_names + [target_name]
        train_df = pd.DataFrame(process_data, columns=columns)
        return train_df
