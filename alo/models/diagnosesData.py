from ..utils import queryDataFromDatabase
selection_sql = """
    SELECT DD.UPID,
        DD.PLATETYPE,
        DD.TGTWIDTH as tgtwidth,
        DD.TGTLENGTH as tgtthickness,
        DD.TGTTHICKNESS as tgtplatelength2,
        LMPD.TGTDISCHARGETEMP as tgtdischargetemp,
        LMPD.TGTTMPLATETEMP as tgttmplatetemp,
        DD.STATS,
        DD.FQC_LABEL,
        DD.TOC,
        DD.STATUS_STATS,
        DD.STATUS_FQC,
        DD.STATUS_COOLING
    FROM APP.DEBA_DUMP_DATA DD
        LEFT JOIN DCENTER.L2_M_PLATE LMP ON DD.UPID = LMP.UPID
	    LEFT JOIN DCENTER.L2_M_PRIMARY_DATA LMPD ON LMPD.SLABID = LMP.SLABID
"""
def conditionRange(key, range):
    if len(range) == 0:
        return ''
    if key == 'tgtwidth':
        return '\nAND DD.TGTWIDTH BETWEEN {min} AND {max} '.format(min=range[0], max=range[1])
    elif key == 'tgtplatelength2':
        return '\nAND DD.TGTLENGTH BETWEEN {min} AND {max} '.format(min=range[0], max=range[1])
    elif key == 'tgtthickness':
        return '\nAND DD.TGTTHICKNESS BETWEEN {min} AND {max} '.format(min=range[0], max=range[1])
    elif key == 'tgtdischargetemp':
        return '\nAND LMPD.TGTDISCHARGETEMP BETWEEN {min} AND {max} '.format(min=range[0], max=range[1])
    elif key == 'tgttmplatetemp':
        return '\nAND LMPD.TGTTMPLATETEMP BETWEEN {min} AND {max} '.format(min=range[0], max=range[1])
    else:
        return ''
def diagnosesTrainDataByArgs(args):
    range_str = ''
    for key in args:
        range_str += conditionRange(key, args[key])
    condition_sql = """
        WHERE 1 = 1
            {range_str}
            AND DD.STATUS_STATS = 0
            AND DD.STATUS_FQC = 0
        ORDER BY DD.TOC DESC
        LIMIT {limit};
    """.format(range_str=range_str, limit=1000)
    data, columns = queryDataFromDatabase(selection_sql + condition_sql)
    return data, columns
def diagnosesTestDataByUpid(upids):
    upidsStr = ''
    for upid in upids:
        upidsStr += "'" + upid + "',"
    upidsStr = upidsStr[0: -1]
    condition_sql = """
        WHERE DD.UPID in ({upidsStr})
        ORDER BY DD.TOC;
    """.format(upidsStr=upidsStr)
    data, columns = queryDataFromDatabase(selection_sql + condition_sql)
    return data, columns
