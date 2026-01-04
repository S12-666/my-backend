import pandas as pd
import numpy as np
from ..utils import concat_dict, format_value
from ..models.queryRollingProcessData import get_pdi_data, get_controlled_rolling_data, get_roll_status_data
from ..models.queryRollingProcessData import get_thickness_data, get_force_torque_data, get_thick_width_data


class RollingDetialController:
    def __init__(self, para):
        self.para = para
        self.upid = para.get('upid')
        self.slabid = para.get('slabid')
        # 移除了 self.get_type

    def run(self):
        # 基础校验
        if not self.upid and not self.slabid:
            return {}

        # 确定查询条件
        if self.upid:
            conditions = f"lmpd.upid = '{self.upid}'"
        else:
            conditions = f"lmpd.slabid = '{self.slabid}'"

        # 初始化返回结果
        res = {}

        table_data = {}
        concat_dict(table_data, self.pdi_data(conditions))
        concat_dict(table_data, self.control_data())
        concat_dict(table_data, self.status_data())
        res['tabledata'] = table_data
        # 2. 整合 Curve 数据
        # 为了防止 key 冲突（如 Passes），将不同的曲线数据放入独立的字段中
        res['thickness_curve'] = self.thickness_data()
        res['force_torque_curve'] = self.force_torque_data()
        res['width_thick_curve'] = self.width_thick_data()

        return res

    # --- 以下数据获取方法保持逻辑不变 ---

    def pdi_data(self, conditions):
        try:
            pdi_raw, pdi_cols = get_pdi_data(conditions)
            if not pdi_raw: return {}
            pdi_series = pd.Series(data=pdi_raw[0], index=pdi_cols)
            pdi_dict = pdi_series.to_dict()
        except:
            pdi_dict = {}
        return pdi_dict

    def control_data(self):
        try:
            # 注意：如果 self.upid 为空，这里可能需要根据实际业务调整逻辑，目前保持原样
            control_raw, control_cols = get_controlled_rolling_data(self.upid)
            if not control_raw: return {}

            control_series = pd.Series(data=control_raw[0], index=control_cols)
            center_thick = control_series.centerthickness
            right_thick = control_series.rightthickness
            left_thick = control_series.leftthickness

            # 删除原始的大数组数据，只保留统计值
            control_series.drop(['centerthickness', 'rightthickness', 'leftthickness'], inplace=True)
            control_dict = control_series.to_dict()

            # 计算统计值
            control_dict['thick_std_ce'] = format_value(np.std(center_thick))
            control_dict['thick_max_ce'] = format_value(np.max(center_thick))
            control_dict['thick_min_ce'] = format_value(np.min(center_thick))
            control_dict['thick_ave_ce'] = format_value(np.mean(center_thick))
            control_dict['thick_ave_ds'] = format_value(np.max(right_thick))  # 保持原逻辑使用max
            control_dict['thick_ave_os'] = format_value(np.max(left_thick))  # 保持原逻辑使用max
        except:
            control_dict = {}
        return control_dict

    def status_data(self):
        try:
            status_raw, status_cols = get_roll_status_data(self.upid)
            if not status_raw: return {}
            status_series = pd.Series(data=status_raw[0], index=status_cols)
            status_dict = status_series.to_dict()
        except:
            status_dict = {}
        return status_dict

    def thickness_data(self):
        try:
            thick_raw, thick_cols = get_thickness_data(self.upid)
            if not thick_raw: return {}
            thick_series = pd.Series(data=thick_raw[0], index=thick_cols)
            thick_dict = thick_series.to_dict()

            def my_format(x):
                return float(format(x * 1000, '.4f'))

            for key in thick_dict:
                if isinstance(thick_dict[key], list):
                    thick_dict[key] = list(map(my_format, thick_dict[key]))
            return thick_dict
        except:
            return {}

    def force_torque_data(self):
        try:
            ft_raw, ft_cols = get_force_torque_data(self.upid)
            if not ft_raw: return {}
            ft_df = pd.DataFrame(data=ft_raw, columns=ft_cols)
            res = {
                'Passes': [],
                'Epsilon': [],
                'ForcePost': [],
                'ForceMeas': [],
                'TorquePost': [],
                'TorqueMeas': []
            }
            cur_run = 1
            for _, row in ft_df.iterrows():
                if cur_run != row.run:
                    zero_nums = int(row.run - cur_run)
                    for j in range(zero_nums):
                        res['Passes'].append(cur_run + j)
                        res['Epsilon'].append(0)
                        res['ForcePost'].append(0)
                        res['ForceMeas'].append(0)
                        res['TorquePost'].append(0)
                        res['TorqueMeas'].append(0)
                    cur_run += zero_nums

                entrythickness = np.mean(row.entrythickness)
                exitthickness = np.mean(row.exitthickness)

                res['Passes'].append(row.run)
                # 增加分母为0的保护（可选）
                if entrythickness != 0:
                    res['Epsilon'].append((entrythickness - exitthickness) / entrythickness * 100)
                else:
                    res['Epsilon'].append(0)

                res['ForcePost'].append(np.mean(row.rollforcepost))
                res['ForceMeas'].append(np.mean(row.rollforcemeas))
                res['TorquePost'].append(np.mean(row.torquepost))
                res['TorqueMeas'].append(np.mean(row.torquemeas))
                cur_run = row.run + 1

            for key in res:
                res[key] = list(map(format_value, res[key]))

            return res if len(res['Passes']) != 0 else {}
        except:
            return {}

    def width_thick_data(self):
        try:
            tw_raw, tw_cols = get_thick_width_data(self.upid)
            if not tw_raw: return {}
            tw_df = pd.DataFrame(data=tw_raw, columns=tw_cols)
            res = {
                'Passes': [],
                'Thickness': [],
                'Width': []
            }
            cur_run = 1
            for _, row in tw_df.iterrows():
                if cur_run != row.run:
                    zero_nums = int(row.run - cur_run)
                    for j in range(zero_nums):
                        res['Passes'].append(cur_run + j)
                        res['Thickness'].append(0)
                        res['Width'].append(0)
                    cur_run += zero_nums
                res['Passes'].append(row.run)
                res['Thickness'].append(np.mean(row.exitthickness))
                res['Width'].append(np.mean(row.exitwidth))
                cur_run = row.run + 1

            for key in res:
                res[key] = list(map(format_value, res[key]))

            return res if len(res['Passes']) != 0 else {}
        except:
            return {}