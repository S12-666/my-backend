import pandas as pd
import numpy as np
from ..utils import concat_dict, format_value
from ..models.queryRollingProcessData import get_pdi_data, get_controlled_rolling_data, get_roll_status_data
from ..models.queryRollingProcessData import get_thickness_data, get_force_torque_data, get_thick_width_data

class RollingDetialController:
    def __init__(self, para):
        self.para = para
        self.upid = para['upid']
        self.slabid = para['slabid']
        # self.get_type = para.get('get_type', '')

    def run(self):
        if not self.upid and not self.slabid:
            return {}
        if self.upid:
            conditions = f"lmpd.upid = '{self.upid}'"
        else:
            conditions = f"lmpd.slabid = '{self.slabid}'"
        # if self.get_type:
        #     return self.process_curve()
        # else:
        #     return self.process_table(conditions)

        return self.process_table(conditions)

    def process_table(self, conditions):
        pdi_dict = self.pdi_data(conditions)
        control_dict = self.control_data()
        status_dict = self.status_data()
        res = {}
        concat_dict(res, pdi_dict)
        concat_dict(res, control_dict)
        concat_dict(res, status_dict)
        return res
    def process_curve(self):
        if self.get_type == 'thickness':
            return self.thickness_data()
        elif self.get_type == 'force_torque':
            return self.force_torque_data()
        elif self.get_type == 'width_thick':
            return self.width_thick_data()
        else:
            return {}
    def pdi_data(self, conditions):
        try:
            pdi_raw, pdi_cols = get_pdi_data(conditions)
            pdi_series = pd.Series(data=pdi_raw[0], index=pdi_cols)
            pdi_dict = pdi_series.to_dict()
        except:
            pdi_dict = {}
        return pdi_dict
    def control_data(self):
        try:
            control_raw, control_cols = get_controlled_rolling_data(self.upid)
            control_series = pd.Series(data=control_raw[0], index=control_cols)
            center_thick = control_series.centerthickness
            right_thick = control_series.rightthickness
            left_thick = control_series.leftthickness
            control_series.drop(['centerthickness', 'rightthickness', 'leftthickness'], inplace=True)
            control_dict = control_series.to_dict()
            control_dict['thick_std_ce'] = format_value(np.std(center_thick))
            control_dict['thick_max_ce'] = format_value(np.max(center_thick))
            control_dict['thick_min_ce'] = format_value(np.min(center_thick))
            control_dict['thick_ave_ce'] = format_value(np.mean(center_thick))
            control_dict['thick_ave_ds'] = format_value(np.max(right_thick))
            control_dict['thick_ave_os'] = format_value(np.max(left_thick))
        except:
            control_dict = {}
        return control_dict
    def status_data(self):
        try:
            status_raw, status_cols = get_roll_status_data(self.upid)
            status_series = pd.Series(data=status_raw[0], index=status_cols)
            status_dict = status_series.to_dict()
        except:
            status_dict = {}
        return status_dict
    def thickness_data(self):
        thick_raw, thick_cols = get_thickness_data(self.upid)
        thick_series = pd.Series(data=thick_raw[0], index=thick_cols)
        thick_dict = thick_series.to_dict()
        def my_format(x):
            return float(format(x * 1000, '.4f'))
        for key in thick_dict:
            if type(thick_dict[key]) == list:
                thick_dict[key] = list(map(my_format, thick_dict[key]))
        return thick_dict
    def force_torque_data(self):
        ft_raw, ft_cols = get_force_torque_data(self.upid)
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
                zero_nums = row.run - cur_run
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
            res['Epsilon'].append((entrythickness - exitthickness) / entrythickness * 100)
            res['ForcePost'].append(np.mean(row.rollforcepost))
            res['ForceMeas'].append(np.mean(row.rollforcemeas))
            res['TorquePost'].append(np.mean(row.torquepost))
            res['TorqueMeas'].append(np.mean(row.torquemeas))
            cur_run = row.run + 1
        for key in res:
            res[key] = list(map(format_value, res[key]))
        return res if len(res['Passes']) != 0 else {}
    def width_thick_data(self):
        tw_raw, tw_cols = get_thick_width_data(self.upid)
        tw_df = pd.DataFrame(data=tw_raw, columns=tw_cols)
        res = {
            'Passes': [],
            'Thickness': [],
            'Width': []
        }
        cur_run = 1
        for _, row in tw_df.iterrows():
            if cur_run != row.run:
                zero_nums = row.run - cur_run
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