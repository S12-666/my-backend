from ..utils import queryDataFromDatabase
def get_pdi_data(conditions):
    sql = """
        SELECT LMPD.UPID,
            LMPD.SLABID,
            TO_CHAR(LMPD.TOC, 'yyyy-mm-dd HH24:mi:ss') AS TOC,
            LMPD.SLABTHICKNESS,
            LMPD.SLABWIDTH,
            LMPD.SLABLENGTH,
            LMPD.STEELSPEC,
            LMPD.STEELSPEC,
            LCP.TAPPING_CODE,
            LMPD.PRODUCTCATEGORY,
            LMPD.TGTPLATETHICKNESS2,
            LMPD.TGTWIDTH,
            LMPD.TGTPLATELENGTH2,
            LMPD.CRCODE,
            LMPD.ADCONTROLCODE,
            LFF60.HEATING_PATTERN_CODE,
            LFF60.AVE_TEMP_DIS,
            LMPD.TGTTMRESTARTTEMP1,
            LMPD.TGTTMPLATETEMP
        FROM DCENTER.L2_M_PRIMARY_DATA LMPD
        LEFT JOIN DCENTER.L2_FU_FLFTR60 LFF60 ON LMPD.UPID = LFF60.UPID
        LEFT JOIN DCENTER.L2_CC_PDI LCP ON LMPD.SLABID = LCP.SLAB_NO
        WHERE {conditions};
    """.format(conditions = conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
def get_controlled_rolling_data(conditions):
    sql = """
        SELECT LMPD.UPID,
            LMPD.SLABID,
            TO_CHAR(LMPD.TOC, 'yyyy-mm-dd HH24:mi:ss') AS TOC,
            LFF60.FCE_NO,
            LFF60.FCE_ROW,
            LFF60.IN_FCE_TIME,
            LFF60.STAYING_TIME_2,
            LFF60.STAYING_TIME_SOAK,
            TO_CHAR(LFF60.DISCHARGE_TIME, 'yyyy-mm-dd HH24:mi:ss') AS DISCHARGE_TIME,
            LFF60.SUR_TEMP_ENTRY_SOAK,
            LFF60.AVE_TEMP_DIS,
            LMPD.TGTTMRESTARTTEMP1,
            LMPD.TGTTMPLATETEMP,
            LMPD.SLABWEIGHT,
            LMPG.CENTERTHICKNESS,
            LMPG.RIGHTTHICKNESS,
            LMPG.LEFTTHICKNESS
        FROM DCENTER.L2_M_PRIMARY_DATA LMPD
        LEFT JOIN DCENTER.L2_FU_FLFTR60 LFF60 ON LMPD.UPID = LFF60.UPID
        LEFT JOIN DCENTER.L2_M_MV_THICKNESS_PG LMPG ON LMPD.UPID = LMPG.UPID
        WHERE {conditions};
    """.format(conditions=conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
def get_roll_status_data(conditions):
    sql = """
        SELECT LMPD.UPID,
            LMPD.SLABID,
            TO_CHAR(LMPD.TOC, 'yyyy-mm-dd HH24:mi:ss') AS TOC,
            LMP.TOPWRIDRM,
            LMP.TOPWRPLATECOUNTRM,
            LMP.BOTWRIDRM,
            LMP.BOTWRPLATECOUNTRM,
            LMP.TOPWRIDFM,
            LMP.TOPWRPLATECOUNTFM,
            LMP.BOTWRIDFM,
            LMP.BOTWRPLATECOUNTFM
        FROM DCENTER.L2_M_PLATE LMP
        LEFT JOIN DCENTER.L2_M_PRIMARY_DATA LMPD ON LMPD.UPID = LMP.UPID
        WHERE {conditions};
    """.format(conditions = conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
def get_thickness_data(conditions):
    sql = """
        SELECT LMPG.UPID,
            LMPG.POSITION,
            LMPG.CENTERTHICKNESS,
            LMPG.LEFTTHICKNESS,
            LMPG.RIGHTTHICKNESS,
            LMPD.TGTPLATETHICKNESS2,
            LMPD.MAXPLATETHICKNESS2,
            LMPD.MINPLATETHICKNESS2
        FROM DCENTER.L2_M_MV_THICKNESS_PG LMPG
        LEFT JOIN DCENTER.L2_M_PRIMARY_DATA LMPD ON LMPD.UPID = LMPG.UPID
        WHERE {conditions};
    """.format(conditions=conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
def get_force_torque_data(conditions):
    sql = """
        SELECT
            LMPD.UPID,
            LMPHP.RUN,
            LMPHPRE.ENTRYTHICKNESS,
            LMPHP.EXITTHICKNESS,
            LMPHP.ROLLFORCE AS ROLLFORCEPOST,
            LMPHP.TORQUE AS TORQUEPOST,
            LMPHM.ROLLFORCE AS ROLLFORCEMEAS,
            LMPHM.TORQUE AS TORQUEMEAS
        FROM DCENTER.L2_M_PSC_HPASS_POST LMPHP
        LEFT JOIN DCENTER.L2_M_PSC_HPASS_PRE LMPHPRE ON LMPHP.UPID = LMPHPRE.UPID AND LMPHPRE.RUN = LMPHP.RUN
        LEFT JOIN DCENTER.L2_M_PSC_HPASS_MEAS LMPHM ON LMPHP.UPID = LMPHM.UPID AND LMPHM.RUN = LMPHP.RUN
        RIGHT JOIN DCENTER.L2_M_PRIMARY_DATA LMPD ON LMPHP.UPID = LMPD.UPID
            WHERE {conditions}
            ORDER BY LMPHP.RUN;
    """.format(conditions=conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
def get_thick_width_data(conditions):
    sql = """
        SELECT LMPD.UPID,
            LMPD.SLABID,
            TO_CHAR(LMPD.TOC, 'yyyy-mm-dd HH24:mi:ss') AS TOC,
            LMPHP.RUN,
            LMPHP.POSITION,
            LMPHP.EXITTHICKNESS,
            LMPHP.EXITWIDTH
        FROM DCENTER.L2_M_PRIMARY_DATA LMPD
        LEFT JOIN DCENTER.L2_M_PSC_HPASS_POST LMPHP ON LMPD.UPID = LMPHP.UPID
        WHERE {conditions}
        ORDER BY LMPHP.RUN;
    """.format(conditions=conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
