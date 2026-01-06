import pandas as pd
from ..models.queryCoolingProcessData import get_cooling_pdi_data, get_cooling_flow_data, get_cooling_specific_data
from ..models.queryCoolingProcessData import get_cooling_scanner_data
from ..utils import concat_dict, format_value
import datetime as dt

class CoolingDetialController:
    def __init__(self, para):
        self.para = para
        self.upid = para['upid']
        self.slabid = para['slabid']

    def run(self):

        if not self.upid and not self.slabid:
            return {}

        if self.upid:
            conditions = f"lmpd.upid = '{self.upid}'"
        else:
            conditions = f"lmpd.slabid = '{self.slabid}'"

        res = {}
        table_data = self.process_table(conditions)
        scanner_data = self.process_scanner_map(conditions)

        res['table_data'] = table_data
        res['scanner_data'] = scanner_data

        return res

    def process_table(self, conditions):
        pdi_dict = self.pdi_data(conditions)
        flow_dict = self.flow_data(conditions)
        specific_dict = self.specific_data(conditions)
        res = {}
        concat_dict(res, pdi_dict)
        concat_dict(res, flow_dict)
        concat_dict(res, specific_dict)
        return res
    def process_scanner_map(self, conditions):
        scan_raw, scan_col = get_cooling_scanner_data(conditions)
        scan_series = pd.Series(data=scan_raw[0], index=scan_col)
        if scan_series.status_cooling == 1:
            return {}
        return scan_series.cooling
    def pdi_data(self, conditions):
        try:
            pdi_raw, pdi_cols = get_cooling_pdi_data(conditions)
            pdi_series = pd.Series(data=pdi_raw[0], index=pdi_cols)
            pdi_dict = pdi_series.fillna(0).to_dict()
        except:
            pdi_dict = {}
        return pdi_dict
    def flow_data(self, conditions):
        try:
            flow_raw, flow_cols = get_cooling_flow_data(conditions)
            flow_series = pd.Series(data=flow_raw[0], index=flow_cols)
            flow_dict = flow_series.fillna(0).to_dict()
        except:
            flow_dict = {}
        return flow_dict
    def specific_data(self, conditions):
        try:
            specific_raw, specific_cols = get_cooling_specific_data(conditions)
            specific_series = pd.Series(data=specific_raw[0], index=specific_cols)
            specific_dict = specific_series.fillna(0).to_dict()
        except:
            specific_dict = {}
        return specific_dict