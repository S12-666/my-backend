import pandas as pd
from ..models.queryFQCData import getFQCDetialSQL
from ..methods.dataProcessing import getpfList, getFqcList, slabel
from ..utils import label_judge

class FQCDetialController:
    def __init__(self, para):
        self.para = para
        self.upid = para['upid']
        self.slabid = para['slabid']

    def run(self):

        if self.upid:
            conditions = f"dd.upid = '{self.upid}'"
        else:
            conditions = f"lcp.slab_no = '{self.slabid}'"

        row_data, col = getFQCDetialSQL(conditions)
        data_sr = pd.Series(data=row_data[0], index=col)
        data_sr.fillna(0, inplace=True)

        slabel = {
            'bend': getFqcList(data_sr.fqc_label)[0],
            'abnormalThickness': getFqcList(data_sr.fqc_label)[1],
            'horizonWave': getFqcList(data_sr.fqc_label)[2],
            'leftWave': getFqcList(data_sr.fqc_label)[3],
            'rightWave': getFqcList(data_sr.fqc_label)[4],
        }

        plabel = {
            'pa': getpfList(data_sr.p_f_label)[0],
            'pf': getpfList(data_sr.p_f_label)[1],
            'pn': getpfList(data_sr.p_f_label)[2],
            'ps': getpfList(data_sr.p_f_label)[3],
            'gs': getpfList(data_sr.p_f_label)[4],
        }

        # p_data = data_sr.pa_data[]

        return {
            'upid': data_sr.upid,
            'slabid': data_sr.slabid,
            'toc': str(data_sr.toc),
            'thick': data_sr.thick,
            'width': data_sr.width,
            'length': data_sr.length,
            'tgtthick': data_sr.tgtthickness,
            'tgtwidth': data_sr.tgtwidth,
            'tgtlength': data_sr.tgtlength,
            'slabel': slabel,
            'plabel': plabel
        }