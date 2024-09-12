from ..utils import queryDataFromDatabase

def sql_selection(type):
    label_selection = []
    table_selection = ''
    if type == 'performance':
        label_selection = ['ddp.p_f_label', 'dd.status_fqc']
        table_selection = ''' from   app.deba_dump_data dd
                            left join dcenter.l2_m_plate lmp on dd.upid = lmp.upid
                            left join dcenter.l2_m_primary_data lmpd on lmpd.slabid = lmp.slabid
                            right join app.deba_dump_properties ddp on ddp.upid = dd.upid '''
    elif type == 'thickness':
        label_selection = ['ddp.p_f_label', 'dd.status_fqc']
        table_selection = ''' from   app.deba_dump_data dd
                                    left join dcenter.l2_m_plate lmp on dd.upid = lmp.upid
                                    left join dcenter.l2_m_primary_data lmpd on lmpd.slabid = lmp.slabid
                                    right join app.deba_dump_properties ddp on ddp.upid = dd.upid '''
    label_selection = ','.join(label_selection)

    selection_sql = '''select  dd.upid,
                           dd.platetype,
                           dd.tgtwidth as tgtwidth,
                           dd.tgtlength as tgtthickness,
                           dd.tgtthickness as tgtplatelength2,
                           lmpd.tgtdischargetemp as tgtdischargetemp,
                           lmpd.tgttmplatetemp as tgttmplatetemp,
                           dd.stats,
                           --dd.fqc_label,
                           dd.toc,
                           dd.status_stats,
                           --dd.status_fqc,
                           dd.status_cooling,'''

    return selection_sql, label_selection, table_selection

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
        where 1 = 1
            {range_str}
            and dd.status_stats = 0
            and dd.status_fqc = 0
            and ddp.p_f_label != '[]'
         order by dd.toc desc
         limit {limit};
    """.format(range_str=range_str, limit=1000)

    type = args['fault_type']

    selection_sql, label_selection, table_selection = sql_selection(type)

    sql = selection_sql + label_selection + table_selection + condition_sql

    data, columns = queryDataFromDatabase(sql)
    return data, columns
def diagnosesTestDataByUpid(args):
    upids = args['upids']
    upidsStr = ''
    for upid in upids:
        upidsStr += "'" + upid + "',"
    upidsStr = upidsStr[0: -1]
    condition_sql = """
        where dd.upid in ({upidsStr})
        order by dd.toc
    """.format(upidsStr=upidsStr)

    type = args['fault_type']

    selection_sql, label_selection, table_selection = sql_selection(type)

    sql = selection_sql + label_selection + table_selection + condition_sql

    data, columns = queryDataFromDatabase(sql)
    return data, columns
