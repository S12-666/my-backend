from ..utils import queryDataFromDatabase
def getOverviewData(start, end):
    sql = """
        SELECT DD.UPID,
            LMPD.STEELSPEC,
            DD.TOC,
            DD.TGTWIDTH,
            DD.TGTLENGTH,
            DD.TGTTHICKNESS * 1000 AS TGTTHICKNESS,
            DD.STATS,
            DD.FQC_LABEL,
            (CASE
                WHEN LMPD.SHAPECODE = '11' OR LMPD.SHAPECODE = '12' THEN LMPD.TGTPLATETHICKNESS5
                ELSE LMPD.TGTPLATETHICKNESS1
             END) * 1000,
            DD.STATUS_COOLING,
            DD.STATUS_FQC,
            LMPD.SLABTHICKNESS * 1000 AS SLABTHICKNESS,
            LMPD.TGTDISCHARGETEMP,
            LMPD.TGTTMPLATETEMP,
            LCP.COOLING_START_TEMP,
            LCP.COOLING_STOP_TEMP,
            LCP.COOLING_RATE1
        FROM DCENTER.L2_M_PRIMARY_DATA LMPD
        LEFT JOIN DCENTER.L2_FU_ACC_T LFAT ON LMPD.SLABID = LFAT.SLAB_NO
        LEFT JOIN DCENTER.L2_M_PLATE LMP ON LMPD.SLABID = LMP.SLABID
        LEFT JOIN DCENTER.L2_CC_PDI LCP ON LMPD.SLABID = LCP.SLAB_NO
        RIGHT JOIN APP.DEBA_DUMP_DATA DD ON DD.UPID = LMP.UPID
        WHERE DD.TOC between '{start}' AND '{end}';
    """.format(start=start, end=end)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
