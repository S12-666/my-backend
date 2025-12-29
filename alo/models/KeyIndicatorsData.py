from ..utils import queryDataFromDatabase
def getKeyIndicatorsDataByTimeRang(start_time, end_time):
    sql_str = '''
        SELECT DD.UPID,
            LMPD.SLABID,
            -- DD.PLATETYPE,
            LMPD.PRODUCTCATEGORY AS PLATETYPE,
            LMPD.STEELSPEC,
            DD.TOC,
            LMPD.SLABTHICKNESS * 1000 AS SLABTHICKNESS,
            DD.TGTTHICKNESS * 1000 AS TGTTHICKNESS,
            DD.TGTLENGTH,
            DD.TGTWIDTH,
            LMPD.TGTDISCHARGETEMP,
            LMPD.TGTTMPLATETEMP,
            LCP.COOLING_START_TEMP,
            LCP.COOLING_STOP_TEMP,
            LCP.COOLING_RATE1,
            DD.FQC_LABEL,
            DDP.P_F_LABEL,
            DD.STATUS_COOLING,
            DD.STATUS_FQC,
            DD.STOPS,
            L2FF60.IN_FCE_TIME
        FROM APP.DEBA_DUMP_DATA DD
        LEFT JOIN APP.deba_dump_properties DDP ON DD.UPID = DDP.UPID
        LEFT JOIN DCENTER.L2_M_PRIMARY_DATA LMPD ON DD.UPID = LMPD.UPID
        LEFT JOIN DCENTER.L2_FU_FLFTR60 L2FF60 ON DD.UPID = L2FF60.UPID
        LEFT JOIN DCENTER.L2_CC_PDI LCP ON LCP.SLAB_NO = LMPD.SLABID
        WHERE DD.TOC BETWEEN '{start_time}' AND '{end_time}'
        ORDER BY DD.TOC;
    '''.format(start_time=start_time, end_time=end_time)
    data, columns = queryDataFromDatabase(sql_str)
    return data, columns


def getSpecCountByTimeRang(start_time, end_time):
    sql_str = '''
        SELECT
        dd.upid,
        dd.toc,
        ddp.p_f_label
        FROM
        app.deba_dump_data dd
        LEFT JOIN app.deba_dump_properties ddp ON dd.upid = ddp.upid
        WHERE
        dd.toc >= '{start_time}' :: TIMESTAMP
        AND dd.toc <= '{end_time}' :: TIMESTAMP
        ORDER BY
        dd.toc
    '''.format(start_time=start_time, end_time=end_time)
    data, columns = queryDataFromDatabase(sql_str)
    return data, columns

def getHeatingReportSQL(conditions):
    sql = '''
    SELECT
    dd.upid,
    lff.slab_no,
    lmpd.steelspec,
    lfat.slab_thickness,
    lfat.slab_width / 1000 as slab_width,
	lfat.slab_length / 1000 as slab_length,
    lff.in_fce_time,
    lff.ave_temp_entry_pre,
    lff.ave_temp_pre,
    lff.staying_time_pre,
    lff.ave_temp_entry_1,
    lff.ave_temp_1,
    lff.staying_time_1,
    lff.ave_temp_entry_2,
    lff.ave_temp_2,
    lff.staying_time_2,
    lff.ave_temp_entry_soak,
    lff.ave_temp_soak,
    lff.staying_time_soak,
    lff.ave_temp_dis,
    lff.discharge_time,
    ddp.p_f_label
    FROM
    app.deba_dump_data dd
    LEFT JOIN dcenter.l2_fu_flftr60 lff ON lff.upid = dd.upid
    LEFT JOIN dcenter.l2_fu_acc_t lfat ON lfat.upid = dd.upid
    LEFT JOIN dcenter.l2_m_primary_data lmpd on lmpd.upid = dd.upid
    LEFT JOIN app.deba_dump_properties ddp ON ddp.upid = dd.upid
    WHERE
    {conditions}
    ORDER BY
    dd.toc
    '''.format(conditions = conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns

def getRollingReportSQL(conditions):
    sql = '''
        SELECT
	        dd.upid,
	        dd.toc,
	        lff.slab_no,
	        lmpd.steelspec,
	        lmpd.tgtplatethickness1 * 1000 AS tgtplatethickness,
	        lmpd.tgtwidth,
	        lmpd.tgtplatelength2 AS tgtplatelength,
	        lmpd.slabweight,
	        lmpd.tappingsteelgrade,
	        lmpd.productcategory,
	        lmp.timerollingstart,
	        lmp.timerollingfinish,
	        lmpd.crcode,
	        lmp.totalpassesrm,
	        lmp.totalpassesfm,
	        lff.ave_temp_dis,
	        lmpd.tgttmrestarttemp1,
	        lmpd.tgttmplatetemp,
	        ddp.p_f_label
        FROM
	        app.deba_dump_data dd
	        LEFT JOIN dcenter.l2_fu_flftr60 lff ON lff.upid = dd.upid
	        LEFT JOIN dcenter.l2_m_plate lmp ON lmp.upid = dd.upid
	        LEFT JOIN dcenter.l2_m_primary_data lmpd ON lmpd.upid = dd.upid 
	        LEFT JOIN app.deba_dump_properties ddp ON ddp.upid = dd.upid
        WHERE
            {conditions}
        ORDER BY
	        dd.toc
    '''.format(conditions = conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns

def getCoolingReportSQL(conditions):
    sql = '''
        SELECT
	        dd.upid,
	        lmpd.slabid,
	        lcp.thick,
	        lcp.width / 1000 AS width,
	        lcp.LENGTH / 1000 AS length,
	        dd.toc,
	        lmpd.steelspec,
	        lff.ave_temp_dis,
	        lmpd.tgttmplatetemp,
	        lcp.adaptive_key,
	        lcp.tapping_code,
	        lcp.cooling_start_temp,
	        lcp.start_time AT TIME ZONE 'Asia/Shanghai' AS start_time,
	        lcp.file_time AT TIME ZONE 'Asia/Shanghai' AS file_time,
	        lcp.cooling_stop_temp1,
	        lcp.cooling_stop_temp2,
	        lcp.cooling_mode,
	        lcp.operate_mode,
	        lcp.cooling_rate1,
	        lcp.cooling_rate2,
	        lcpc.avg_p1,
	        lcpc.avg_p2,
	        lcpc.avg_p5,
	        lcpc.avg_cr_act,
	        lcpc.speed_ratio,
	        ddp.p_f_label 
        FROM
	        app.deba_dump_data dd
	        LEFT JOIN dcenter.l2_fu_flftr60 lff ON lff.upid = dd.upid
	        LEFT JOIN dcenter.l2_m_primary_data lmpd ON lmpd.upid = dd.upid
	        LEFT JOIN dcenter.l2_cc_pdi lcp ON lcp.slab_no = lmpd.slabid
	        LEFT JOIN dcenter.l2_cc_postcalc lcpc ON lcpc.slab_no = lmpd.slabid
	        LEFT JOIN app.deba_dump_properties ddp ON ddp.upid = dd.upid 
        WHERE
	        dd.status_cooling = 0 AND 
            {conditions}
        ORDER BY
	        dd.toc
    '''.format(conditions = conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns


def getFQCReportSQL(conditions):
    sql = '''
        SELECT
	        dd.upid,
	        dd.toc,
	        lmpd.slabid,
	        dd.platetype,
	        dd.tgtthickness * 1000 as tgtthickness,
	        dd.tgtwidth,
	        dd.tgtlength,
	        lcp.thick,
	        lcp.width / 1000 AS width,
	        lcp.LENGTH / 1000 AS length,
	        dd.fqc_label,
	        ddp.p_f_label 
        FROM
	        app.deba_dump_data dd
	        LEFT JOIN dcenter.l2_m_primary_data lmpd ON lmpd.upid = dd.upid
	        LEFT JOIN dcenter.l2_cc_pdi lcp ON lcp.slab_no = lmpd.slabid
	        LEFT JOIN app.deba_dump_properties ddp ON ddp.upid = dd.upid 
        WHERE
            {conditions}
        ORDER BY
	        dd.toc
    '''.format(conditions = conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns

def getHeatingDetialSQL(conditions):
    sql = '''
        SELECT
	        dd.upid,
	        dd.furnace,
	        lff.slab_no,
	        lff.slab_thickness,
	        lff.heating_pattern_code,
	        lff.fce_no,
	        lff.in_fce_time,
	        lff.ave_temp_entry_pre,
	        lff.sur_temp_entry_pre,
	        lff.center_temp_entry_pre,
	        lff.skid_temp_entry_pre,
	        lff.ave_temp_pre,
	        lff.staying_time_pre,
	        lff.ave_temp_entry_1,
	        lff.sur_temp_entry_1,
	        lff.center_temp_entry_1,
	        lff.skid_temp_entry_1,
	        lff.ave_temp_1,
	        lff.staying_time_1,
	        lff.ave_temp_entry_2,
	        lff.sur_temp_entry_2,
	        lff.center_temp_entry_2,
	        lff.skid_temp_entry_2,
	        lff.ave_temp_2,
	        lff.staying_time_2,
	        lff.ave_temp_entry_soak,
	        lff.sur_temp_entry_soak,
	        lff.center_temp_entry_soak,
	        lff.skid_temp_entry_soak,
	        lff.ave_temp_soak,
	        lff.staying_time_soak,
	        lff.sur_temp_dis,
	        lff.center_temp_dis,
	        lff.skid_temp_dis,
	        lff.ave_temp_dis,
	        lff.discharge_time
        FROM
	        app.deba_dump_data dd
	        LEFT JOIN dcenter.l2_fu_flftr60 lff ON lff.upid = dd.upid 
        WHERE
	        {conditions}
        ORDER BY
	        dd.toc
    '''.format(conditions = conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns