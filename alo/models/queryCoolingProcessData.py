from ..utils import queryDataFromDatabase
def get_cooling_pdi_data(conditions):
    sql = """
        SELECT LMPD.UPID,
            LMPD.SLABID,
            TO_CHAR(LMPD.TOC, 'yyyy-mm-dd HH24:mi:ss') AS TOC,
            LCP.THICK / 1000 AS THICK,
            LCP.WIDTH / 1000 AS WIDTH,
            LCP.LENGTH / 1000 AS LENGTH,
            LCP.ROLLING_FINISH_TEMP,
            LCP.COOLING_START_TEMP,
            LCP.COOLING_STOP_TEMP,
            LCP.COOLING_STOP_TEMP1,
            LCP.COOLING_STOP_TEMP2,
            LCP.COOLING_RATE1,
            LCP.COOLING_RATE2,
            LCP.COOLING_MODE,
            LCP.OPERATE_MODE,
            LCP.MATERIAL,
            LCP.CHEMISTRY_B,
            LCP.CHEMISTRY_C,
            LCP.CHEMISTRY_CR,
            LCP.CHEMISTRY_CU,
            LCP.CHEMISTRY_MN,
            LCP.CHEMISTRY_MO,
            LCP.CHEMISTRY_NB,
            LCP.CHEMISTRY_NI,
            LCP.CHEMISTRY_SI,
            LCP.CHEMISTRY_TI,
            LCP.CHEMISTRY_V
        FROM DCENTER.L2_M_PRIMARY_DATA LMPD
        LEFT JOIN DCENTER.L2_CC_PDI LCP ON LMPD.SLABID = LCP.SLAB_NO
        WHERE {conditions};
    """.format(conditions=conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
def get_cooling_flow_data(conditions):
    sql = """
        SELECT
            LCPRE.VC_FLOW_TOP_01,
            LCPRE.VC_FLOW_TOP_02,
            LCPRE.VC_FLOW_TOP_03,
            LCPRE.VC_FLOW_TOP_04,
            LCPRE.VC_FLOW_TOP_05,
            LCPRE.VC_FLOW_TOP_06,
            LCPRE.VC_FLOW_TOP_07,
            LCPRE.VC_FLOW_TOP_08,
            LCPRE.VC_FLOW_TOP_09,
            LCPRE.VC_FLOW_TOP_10,
            LCPRE.VC_FLOW_TOP_11,
            LCPRE.VC_FLOW_TOP_12,
            LCPRE.VC_FLOW_TOP_13,
            LCPRE.VC_FLOW_TOP_14,
            LCPRE.VC_FLOW_TOP_15,
            LCPRE.VC_FLOW_TOP_16,
            LCPRE.VC_FLOW_TOP_17,
            LCPRE.VC_FLOW_TOP_18,
            LCPRE.VC_FLOW_TOP_19,
            LCPRE.VC_FLOW_BOT_01,
            LCPRE.VC_FLOW_BOT_02,
            LCPRE.VC_FLOW_BOT_03,
            LCPRE.VC_FLOW_BOT_04,
            LCPRE.VC_FLOW_BOT_05,
            LCPRE.VC_FLOW_BOT_06,
            LCPRE.VC_FLOW_BOT_07,
            LCPRE.VC_FLOW_BOT_08,
            LCPRE.VC_FLOW_BOT_09,
            LCPRE.VC_FLOW_BOT_10,
            LCPRE.VC_FLOW_BOT_11,
            LCPRE.VC_FLOW_BOT_12,
            LCPRE.VC_FLOW_BOT_13,
            LCPRE.VC_FLOW_BOT_14,
            LCPRE.VC_FLOW_BOT_15,
            LCPRE.VC_FLOW_BOT_16,
            LCPRE.VC_FLOW_BOT_17,
            LCPRE.VC_FLOW_BOT_18,
            LCPRE.VC_FLOW_BOT_19,
            LCPRE.EM_POS_ABS_1,
            LCPRE.EM_POS_ABS_2,
            LCPRE.EM_POS_ABS_3,
            LCPRE.EM_POS_ABS_4
        FROM DCENTER.L2_CC_PRESET LCPRE
        LEFT JOIN DCENTER.L2_M_PRIMARY_DATA LMPD ON LMPD.SLABID = LCPRE.SLAB_NO
        WHERE {conditions};
    """.format(conditions=conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
def get_cooling_specific_data(conditions):
    sql = """
        SELECT
            LCPC.AVG_P2,
            LCPC.MAX_P2,
            LCPC.MIN_P2,
            LCPC.STD_P2,
            LCPC.AVG_P5,
            LCPC.MAX_P5,
            LCPC.MIN_P5,
            LCPC.STD_P5,
            LCPRE.MK_FACTOR_HEAD_TOP,
            LCPRE.MK_LENGTH_HEAD_TOP,
            LCPRE.MK_FACTOR_HEAD_BTM,
            LCPRE.MK_LENGTH_HEAD_BTM,
            LCPRE.MK_FACTOR_TAIL_TOP,
            LCPRE.MK_LENGTH_TAIL_TOP,
            LCPRE.MK_FACTOR_TAIL_BTM,
            LCPRE.MK_LENGTH_TAIL_BTM,
            LCPRE.DQ_WATER_TEMP,
            LCPRE.ACC_WATER_TEMP,
            LCPRE.AIR_TEMP,
            LCPC.AVG_CR_CAL,
            LCPC.AVG_CR_ACT,
            LCPC.LAST_ROLLING_FINISH_TEMP,
            LCPC.SPEED_RATIO,
            LCPC.LAST_COOLING_STOP_TEMP,
            LCPC.LAST_PLATE_SPEED,
            LCPC.LAST_COOLING_ZONE_LENGTH,
            LCPC.LAST_WATER_TEMP,
            LCP.TAPPING_CODE,
            LCPC.PLATE_COUNT,
            LCPC.PLATE_BEFORE_1,
            LCPC.PLATE_BEFORE_2,
            LCPC.PLATE_BEFORE_3
        FROM DCENTER.L2_M_PRIMARY_DATA LMPD
        LEFT JOIN DCENTER.L2_CC_POSTCALC LCPC ON LMPD.SLABID = LCPC.SLAB_NO
        LEFT JOIN DCENTER.L2_CC_PRESET LCPRE ON LMPD.SLABID = LCPRE.SLAB_NO
        LEFT JOIN DCENTER.L2_CC_PDI LCP ON LMPD.SLABID = LCP.SLAB_NO
        WHERE {conditions};
    """.format(conditions=conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
def get_cooling_scanner_data(conditions):
    sql = """
        SELECT DD.UPID,
            DD.COOLING,
            DD.STATUS_COOLING
        FROM APP.DEBA_DUMP_DATA DD
        LEFT JOIN DCENTER.L2_M_PRIMARY_DATA LMPD ON LMPD.UPID = DD.UPID
        WHERE {conditions};
    """.format(conditions=conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
