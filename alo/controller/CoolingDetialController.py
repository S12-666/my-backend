import pandas as pd
from ..models.KeyIndicatorsData import getHeatingDetialSQL
import datetime as dt

class CoolingDetialController:
    def __init__(self, para):
        self.para = para
        self.upid = para['upid']
        self.slabid = para['slabid']

    def run(self):

        if self.upid:
            conditions = f"dd.upid = '{self.upid}'"
        else:
            conditions = f"lff.slab_no = '{self.slabid}'"

        row_data, col = getHeatingDetialSQL(conditions)
        data_sr = pd.Series(data=row_data[0], index=col)
        data_sr.fillna(0, inplace=True)

        discharge_time = data_sr.discharge_time
        enter_fce_time = discharge_time - dt.timedelta(minutes=data_sr.in_fce_time)
        section_info = {
            'discharging': {
                'surface': data_sr.sur_temp_dis,
                'center': data_sr.center_temp_dis,
                'seat': data_sr.skid_temp_dis,
                'average': data_sr.ave_temp_dis,
            },
            'preheating': {
                'entry': data_sr.ave_temp_entry_pre,
                'surface': data_sr.sur_temp_entry_pre,
                'center': data_sr.center_temp_entry_pre,
                'seat': data_sr.skid_temp_entry_pre,
                'average': data_sr.ave_temp_pre,
                'duration': data_sr.staying_time_pre,
            },
            'heating1': {
                'entry': data_sr.ave_temp_entry_1,
                'surface': data_sr.sur_temp_entry_1,
                'center': data_sr.center_temp_entry_1,
                'seat': data_sr.skid_temp_entry_1,
                'average': data_sr.ave_temp_1,
                'duration': data_sr.staying_time_1,
            },
            'heating2': {
                'entry': data_sr.ave_temp_entry_2,
                'surface': data_sr.sur_temp_entry_2,
                'center': data_sr.center_temp_entry_2,
                'seat': data_sr.skid_temp_entry_2,
                'average': data_sr.ave_temp_2,
                'duration': data_sr.staying_time_2,
            },
            'soaking': {
                'entry': data_sr.ave_temp_entry_soak,
                'surface': data_sr.sur_temp_entry_soak,
                'center': data_sr.center_temp_entry_soak,
                'seat': data_sr.skid_temp_entry_soak,
                'average': data_sr.ave_temp_soak,
                'duration': data_sr.staying_time_soak,
            },
        }


        return {
            'upid': data_sr.upid,
            'slabid': data_sr.slab_no,
            'thick': data_sr.slab_thickness,
            'HeatMode': data_sr.heating_pattern_code,
            'furnaceNo': data_sr.fce_no,
            'duration': data_sr.in_fce_time,
            'durationRange': [str(enter_fce_time), str(discharge_time)],
            'section': section_info,
            'furnace': data_sr.furnace
        }