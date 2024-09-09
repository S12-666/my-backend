'''
singelSteel
'''
from flask_restful import Resource, reqparse
from flask import json
from . import api
import pandas as pd
import numpy as np
from ..utils import getSQLData,getFlagArr,getLabelData,getLabel,ref
import json
import re

parser = reqparse.RequestParser(trim=True, bundle_errors=True)
thicklabel="(case when lmpd.shapecode ='11' or lmpd.shapecode='12' then lmpd.tgtplatethickness5 else lmpd.tgtplatethickness1 end)* 1000"
data_names = ["charging_temp_act", "tgtplatelength2", "tgtplatethickness2", "tgtwidth", "slab_length", "slab_thickness", "slab_weight_act", "slab_width",
            "ave_temp_1", "ave_temp_2", "ave_temp_dis", "ave_temp_pre", "ave_temp_soak", "ave_temp_entry_1", "ave_temp_entry_2", "ave_temp_entry_pre",
            "ave_temp_entry_soak", "center_temp_dis", "center_temp_entry_1", "center_temp_entry_2", "center_temp_entry_pre", "center_temp_entry_soak",
            "temp_uniformity_dis", "temp_uniformity_entry_1", "temp_uniformity_entry_2", "temp_uniformity_entry_pre", "temp_uniformity_entry_soak",
            "skid_temp_dis", "skid_temp_entry_1", "skid_temp_entry_2", "skid_temp_entry_pre", "skid_temp_entry_soak", "staying_time_1", "staying_time_2",
            "staying_time_pre", "staying_time_soak", "sur_temp_dis", "sur_temp_entry_1", "sur_temp_entry_2", "sur_temp_entry_pre", "sur_temp_entry_soak",
            "meas_temp_0", "meas_temp_1", "meas_temp_10", "meas_temp_11", "meas_temp_12", "meas_temp_13", "meas_temp_14", "meas_temp_15", "meas_temp_16",
            "meas_temp_17", "meas_temp_18", "meas_temp_19", "meas_temp_2", "meas_temp_3", "meas_temp_4", "meas_temp_5", "meas_temp_6", "meas_temp_7",
            "meas_temp_8", "meas_temp_9", "t_0", "t_1", "t_2", "t_3", "t_4", "t_5", "t_6", "pass",
            # "botbrplatecountfm", "botbrplatecountrm", "botwrplatecountfm", "botwrplatecountrm",
            "crownbody", "crownhead", "crowntail", "crowntotal", "devcrownbody", "devcrownhead", "devcrowntail",
            "devcrowntotal", "devfinishtempbody", "devfinishtemphead", "devfinishtemptail", "devfinishtemptotal", "wedgebody", "wedgehead",
            # "wedgetail",
            "wedgetotal", "devwedgebody", "devwedgehead", "devwedgetail", "devwedgetotal", "finishtempbody", "finishtemphead", "finishtemptail",
            "finishtemptotal", "avg_fct", "avg_p1",
            # "avg_p2",
            "avg_p5", "avg_sct", "max_fct", "max_p1", "max_p2", "max_p5", "max_sct",
            "min_fct", "min_p1", "min_p2", "min_p5", "min_sct", "std_fct", "std_p1", "std_p2", "std_p5", "std_sct"]

p_data_names = [# gs
                "aus_grain_lvl_b", "aus_grain_lvl_t", "ferr_grain_lvl_b", "ferr_grain_lvl_t",
                # pa
                "ts_1_b", "ts_1_t", "ts_2_b", "ts_2_t", "reh_1_b", "reh_1_t", "reh_2_b", "reh_2_t", "rel_1_b", "rel_1_t", "rel_2_b", "rel_2_t", "redu_1_b",
                "redu_1_t", "redu_2_b", "redu_2_t", "rp02_1_b", "rp02_1_t", "rp02_2_b", "rp02_2_t", "rt05_1_b", "rt05_1_t", "rt05_2_b", "rt05_2_t", "homoel_1_b",
                "homoel_1_t", "homoel_2_b", "homoel_2_t", "breakel_1_b", "breakel_1_t", "breakel_2_b", "breakel_2_t", "eldrate_1_b", "yieldrate_1_t", "yieldrate_2_b", "yieldrate_2_t",
                # pf
                "impact_cut_11_b", "impact_cut_11_t", "impact_cut_12_b", "impact_cut_12_t", "impact_cut_21_b", "impact_cut_21_t", "impact_cut_22_b", "impact_cut_22_t",
                "impact_temp_1_b", "impact_temp_1_t","impact_temp_2_b","impact_temp_2_t","impact_cut_avg1_b","impact_cut_avg1_t","impact_cut_avg2_b","impact_cut_avg2_t",
                "impact_energy_11_b","impact_energy_11_t","impact_energy_12_b","impact_energy_12_t","impact_energy_21_b","impact_energy_21_t","impact_energy_22_b","impact_energy_22_t",
                "impact_energy_avg1_b","impact_energy_avg1_t","impact_energy_avg2_b","impact_energy_avg2_t",
                # pn
                "dwtt_1_b", "dwtt_1_t", "dwtt_2_b", "dwtt_2_t", "dwtt_avg_b", "dwtt_avg_t", "dwtt_temp_b", "dwtt_temp_t",
                # ps
                "hardness_1_b", "hardness_1_t","hardness_2_b","hardness_2_t","hardness_3_b","hardness_3_t","hardness_avg_b","hardness_avg_t" ]

without_cooling_data_names = ["charging_temp_act", "tgtplatelength2", "tgtplatethickness2", "tgtwidth", "slab_length", "slab_thickness", "slab_weight_act", "slab_width",
            "ave_temp_1", "ave_temp_2", "ave_temp_dis", "ave_temp_pre", "ave_temp_soak", "ave_temp_entry_1", "ave_temp_entry_2", "ave_temp_entry_pre",
            "ave_temp_entry_soak", "center_temp_dis", "center_temp_entry_1", "center_temp_entry_2", "center_temp_entry_pre", "center_temp_entry_soak",
            "temp_uniformity_dis", "temp_uniformity_entry_1", "temp_uniformity_entry_2", "temp_uniformity_entry_pre", "temp_uniformity_entry_soak",
            "skid_temp_dis", "skid_temp_entry_1", "skid_temp_entry_2", "skid_temp_entry_pre", "skid_temp_entry_soak", "staying_time_1", "staying_time_2",
            "staying_time_pre", "staying_time_soak", "sur_temp_dis", "sur_temp_entry_1", "sur_temp_entry_2", "sur_temp_entry_pre", "sur_temp_entry_soak",
            "meas_temp_0", "meas_temp_1", "meas_temp_10", "meas_temp_11", "meas_temp_12", "meas_temp_13", "meas_temp_14", "meas_temp_15", "meas_temp_16",
            "meas_temp_17", "meas_temp_18", "meas_temp_19", "meas_temp_2", "meas_temp_3", "meas_temp_4", "meas_temp_5", "meas_temp_6",
            "meas_temp_7", "meas_temp_8", "meas_temp_9", "t_0", "t_1", "t_2", "t_3", "t_4", "t_5", "t_6", "pass",
            # "botbrplatecountfm", "botbrplatecountrm", "botwrplatecountfm", "botwrplatecountrm",
            "crownbody", "crownhead", "crowntail", "crowntotal", "devcrownbody", "devcrownhead", "devcrowntail",
            "devcrowntotal", "devfinishtempbody", "devfinishtemphead", "devfinishtemptail", "devfinishtemptotal", "wedgebody", "wedgehead",
            # "wedgetail",
            "wedgetotal", "devwedgebody", "devwedgehead", "devwedgetail", "devwedgetotal", "finishtempbody", "finishtemphead", "finishtemptail",
            "finishtemptotal"]
no_category_data_names = ["charging_temp_act", "slab_length", "slab_weight_act", "slab_width",
            "ave_temp_1", "ave_temp_2", "ave_temp_dis", "ave_temp_pre", "ave_temp_soak", "ave_temp_entry_1", "ave_temp_entry_2", "ave_temp_entry_pre",
            "ave_temp_entry_soak", "center_temp_dis", "center_temp_entry_1", "center_temp_entry_2", "center_temp_entry_pre", "center_temp_entry_soak",
            "temp_uniformity_dis", "temp_uniformity_entry_1", "temp_uniformity_entry_2", "temp_uniformity_entry_pre", "temp_uniformity_entry_soak",
            "skid_temp_dis", "skid_temp_entry_1", "skid_temp_entry_2", "skid_temp_entry_pre", "skid_temp_entry_soak", "staying_time_1", "staying_time_2",
            "staying_time_pre", "staying_time_soak", "sur_temp_dis", "sur_temp_entry_1", "sur_temp_entry_2", "sur_temp_entry_pre", "sur_temp_entry_soak",
            "meas_temp_0", "meas_temp_1", "meas_temp_10", "meas_temp_11", "meas_temp_12", "meas_temp_13", "meas_temp_14", "meas_temp_15", "meas_temp_16",
            "meas_temp_17", "meas_temp_18", "meas_temp_19", "meas_temp_2", "meas_temp_3", "meas_temp_4", "meas_temp_5", "meas_temp_6", "meas_temp_7",
            "meas_temp_8", "meas_temp_9", "t_0", "t_1", "t_2", "t_3", "t_4", "t_5", "t_6", "pass",
            # "botbrplatecountfm", "botbrplatecountrm", "botwrplatecountfm", "botwrplatecountrm",
            "crownbody", "crownhead", "crowntail", "crowntotal", "devcrownbody", "devcrownhead", "devcrowntail",
            "devcrowntotal", "devfinishtempbody", "devfinishtemphead", "devfinishtemptail", "devfinishtemptotal", "wedgebody", "wedgehead",
            # "wedgetail",
            "wedgetotal", "devwedgebody", "devwedgehead", "devwedgetail", "devwedgetotal", "finishtempbody", "finishtemphead", "finishtemptail",
            "finishtemptotal", "avg_fct", "avg_p1",
            # "avg_p2",
            "avg_p5", "avg_sct", "max_fct", "max_p1", "max_p2", "max_p5", "max_sct",
            "min_fct", "min_p1", "min_p2", "min_p5", "min_sct", "std_fct", "std_p1", "std_p2", "std_p5", "std_sct"]
no_category_data_names_without_cooling = ["charging_temp_act", "slab_length", "slab_weight_act", "slab_width",
            "ave_temp_1", "ave_temp_2", "ave_temp_dis", "ave_temp_pre", "ave_temp_soak", "ave_temp_entry_1", "ave_temp_entry_2", "ave_temp_entry_pre",
            "ave_temp_entry_soak", "center_temp_dis", "center_temp_entry_1", "center_temp_entry_2", "center_temp_entry_pre", "center_temp_entry_soak",
            "temp_uniformity_dis", "temp_uniformity_entry_1", "temp_uniformity_entry_2", "temp_uniformity_entry_pre", "temp_uniformity_entry_soak",
            "skid_temp_dis", "skid_temp_entry_1", "skid_temp_entry_2", "skid_temp_entry_pre", "skid_temp_entry_soak", "staying_time_1", "staying_time_2",
            "staying_time_pre", "staying_time_soak", "sur_temp_dis", "sur_temp_entry_1", "sur_temp_entry_2", "sur_temp_entry_pre", "sur_temp_entry_soak",
            "meas_temp_0", "meas_temp_1", "meas_temp_10", "meas_temp_11", "meas_temp_12", "meas_temp_13", "meas_temp_14", "meas_temp_15", "meas_temp_16",
            "meas_temp_17", "meas_temp_18", "meas_temp_19", "meas_temp_2", "meas_temp_3", "meas_temp_4", "meas_temp_5", "meas_temp_6",
            "meas_temp_7", "meas_temp_8", "meas_temp_9", "t_0", "t_1", "t_2", "t_3", "t_4", "t_5", "t_6", "pass",
            # "botbrplatecountfm", "botbrplatecountrm", "botwrplatecountfm", "botwrplatecountrm",
            "crownbody", "crownhead", "crowntail", "crowntotal", "devcrownbody", "devcrownhead", "devcrowntail",
            "devcrowntotal", "devfinishtempbody", "devfinishtemphead", "devfinishtemptail", "devfinishtemptotal", "wedgebody", "wedgehead",
            # "wedgetail",
            "wedgetotal", "devwedgebody", "devwedgehead", "devwedgetail", "devwedgetotal", "finishtempbody", "finishtemphead", "finishtemptail",
            "finishtemptotal"]
data_names_meas = ["meas_temp_0", "meas_temp_1", "meas_temp_10", "meas_temp_11", "meas_temp_12", "meas_temp_13", "meas_temp_14", "meas_temp_15", "meas_temp_16",
            "meas_temp_17", "meas_temp_18", "meas_temp_19", "meas_temp_2", "meas_temp_3", "meas_temp_4", "meas_temp_5", "meas_temp_6",
            "meas_temp_7", "meas_temp_8", "meas_temp_9"]
specifications = ["tgtwidth", "tgtplatelength2", "productcategory", "steelspec"]
# 没有的："slab_thickness", "tgtplatethickness2", "tgtdischargetemp", "tgttmplatetemp", "cooling_start_temp", "cooling_stop_temp", "cooling_rate1",



def filterSQL(parser):
    Query = {}
    label = [ "slabthickness", "tgtdischargetemp", "tgtplatethickness","tgtwidth", "tgtplatelength2", "tgttmplatetemp", "cooling_start_temp", "cooling_stop_temp", "cooling_rate1"]
    table = ["lmpd" , "lmpd","lmpd","lmpd","lmpd","lmpd","lcp","lcp","lcp"]
    tablename = dict(zip(label,table))
    for index in label:
        parser.add_argument(index, type=str, required=True)
    parser.add_argument("productcategory", type=str, required=True)
    parser.add_argument("steelspec", type=str, required=True)
    parser.add_argument("status_cooling", type=str, required=True)
    parser.add_argument("fqcflag", type=str, required=False)  # 如果是可选的参数
    args = parser.parse_args(strict=True)

    status_cooling = args["status_cooling"]

    for index in label:
        Query[index] = json.loads(args[index])
    SQL=''
    for index in Query:
        if(len(Query[index]) != 0):
            if index=="slabthickness" or index=="tgtwidth":
                Query[index][0]/=1000
                Query[index][1]/=1000
            if index=="tgtplatethickness":
                SQL =SQL+ thicklabel+ ' > ' + str(Query[index][0]) +' and ' + thicklabel + ' < ' + str(Query[index][1]) +' and '
            else:
                SQL =SQL+tablename[index]+'.' + index + ' > ' + str(Query[index][0]) +' and ' + tablename[index] +'.' + index + ' < ' + str(Query[index][1]) +' and '
    Query = {}
    label = ["productcategory", "steelspec"]
    table = ["lmpd","lmpd"]
    operation = dict(zip(label,[' = ', ' like ']))
    tablename = dict(zip(label,table))
    for index in label:
        Query[index] = json.loads(args[index])
    for index in Query:
        if(len(Query[index]) != 0):
            SQL=SQL+'('
            # 
            for item in Query[index]:
                opera = ' = '
                if not re.search('%', item) is None:
                    opera = ' like '
                    # item = re.sub('%', "", item)
                SQL =SQL+tablename[index]+'.' + index + opera + repr(item) +' or '
            SQL=SQL[:-4]
            SQL=SQL+' ) and '
    SQL=SQL[:-5]
    if (SQL!=''):
        SQL="where " + SQL
    return SQL, int(status_cooling)

def new_filterSQL(parser):
    Query = {}
    label = [ "slabthickness", "tgtdischargetemp", "tgtplatethickness","tgtwidth", "tgtplatelength2", "tgttmplatetemp", "cooling_start_temp", "cooling_stop_temp", "cooling_rate1"]
    table = ["lmpd" , "lmpd","lmpd","lmpd","lmpd","lmpd","lcp","lcp","lcp"]
    tablename = dict(zip(label,table))
    for index in label:
        parser.add_argument(index, type=str, required=True)
    parser.add_argument("productcategory", type=str, required=True)
    parser.add_argument("steelspec", type=str, required=True)
    parser.add_argument("status_cooling", type=str, required=True)
    parser.add_argument("fqcflag", type=str, required=True)
    args = parser.parse_args(strict=True)

    status_cooling = args["status_cooling"]
    fqcflag = args["fqcflag"]


    for index in label:
        Query[index] = json.loads(args[index])
    SQL=''
    for index in Query:
        if(len(Query[index]) != 0):
            if index=="slabthickness" or index=="tgtwidth":
                Query[index][0]/=1000
                Query[index][1]/=1000
            if index=="tgtplatethickness":
                SQL =SQL+ thicklabel+ ' > ' + str(Query[index][0]) +' and ' + thicklabel + ' < ' + str(Query[index][1]) +' and '
            else:
                SQL =SQL+tablename[index]+'.' + index + ' > ' + str(Query[index][0]) +' and ' + tablename[index] +'.' + index + ' < ' + str(Query[index][1]) +' and '
    Query = {}
    label = ["productcategory", "steelspec"]
    table = ["lmpd","lmpd"]
    operation = dict(zip(label,[' = ', ' like ']))
    tablename = dict(zip(label,table))
    for index in label:
        Query[index] = json.loads(args[index])
    for index in Query:
        if(len(Query[index]) != 0):
            SQL=SQL+'('
            #
            for item in Query[index]:
                opera = ' = '
                if not re.search('%', item) is None:
                    opera = ' like '
                    # item = re.sub('%', "", item)
                SQL =SQL+tablename[index]+'.' + index + opera + repr(item) +' or '
            SQL=SQL[:-4]
            SQL=SQL+' ) and '
    SQL=SQL[:-5]
    if (SQL!=''):
        SQL="where " + SQL
    # print(SQL)
    return SQL, int(status_cooling), int(fqcflag)

def filterSteelSpec(parser):
    Query = {}
    label = ["tgtplatethickness","tgtwidth", "tgtplatelength2"]
    table = ["lmpd","lmpd","lmpd"]
    tablename = dict(zip(label,table))
    for index in label:
        parser.add_argument(index, type=str, required=True)
    # parser.add_argument("productcategory", type=str, required=True)
    # parser.add_argument("steelspec", type=str, required=True)
    args = parser.parse_args(strict=True)

    for index in label:
        Query[index] = json.loads(args[index])
    SQL=''
    for index in Query:
        if(len(Query[index]) != 0):
            if index=="slabthickness" or index=="tgtwidth":
                Query[index][0]/=1000
                Query[index][1]/=1000
            if index=="tgtplatethickness":
                
                SQL =SQL+ thicklabel+ ' > ' + str(Query[index][0]) +' and ' + thicklabel + ' < ' + str(Query[index][1]) +' and '
            else:
                SQL =SQL+tablename[index]+'.' + index + ' > ' + str(Query[index][0]) +' and ' + tablename[index] +'.' + index + ' < ' + str(Query[index][1]) +' and '
    # Query = {}
    # label = ["productcategory", "steelspec"]
    # table = ["lmpd","lmpd"]
    # tablename = dict(zip(label,table))
    # for index in label:
    #     Query[index] = json.loads(args[index])
    # for index in Query:
    #     if(len(Query[index]) != 0):
    #         SQL=SQL+'('
    #         for item in Query[index]:
    #             SQL =SQL+tablename[index]+'.' + index + ' = ' + repr(item) +' or '
    #         SQL=SQL[:-4]
    #         SQL=SQL+' ) and '
    SQL=SQL[:-5]
    if (SQL!=''):
        SQL="where "+SQL
    return SQL


lefttable = ''' from  dcenter.l2_m_primary_data lmpd
            left join dcenter.l2_fu_acc_t lfat on lmpd.slabid = lfat.slab_no
            left join dcenter.l2_m_plate lmp   on lmpd.slabid = lmp.slabid
            left join dcenter.l2_cc_pdi lcp    on lmpd.slabid = lcp.slab_no
            left join dcenter.dump_data dd    on dd.upid = lmp.upid '''

new_lefttable = ''' from  dcenter.l2_m_primary_data lmpd
            left join dcenter.l2_fu_acc_t lfat on lmpd.slabid = lfat.slab_no
            left join dcenter.l2_m_plate lmp   on lmpd.slabid = lmp.slabid
            left join dcenter.l2_cc_pdi lcp    on lmpd.slabid = lcp.slab_no
            left join app.deba_dump_data dd    on dd.upid = lmp.upid '''

singleSQL_lefttable = ''' from  dcenter.l2_m_primary_data lmpd
            left join dcenter.l2_fu_acc_t lfat on lmpd.slabid = lfat.slab_no
            left join dcenter.l2_m_plate lmp   on lmpd.slabid = lmp.slabid
            left join dcenter.l2_cc_pdi lcp    on lmpd.slabid = lcp.slab_no
            right join app.deba_dump_data dd    on dd.upid = lmp.upid
            right join app.deba_dump_properties ddp on ddp.upid = dd.upid '''


def modeldata(parser, selection, startTime, endTime):
    SQL, status_cooling = filterSQL(parser)

    select = ','.join(selection)
    ismissing = ['dd.status_stats']
    if(SQL!=''):
        for i in ismissing:
            SQL+= ' and '+i+'= '+'0'
    if (SQL==''):
        SQL="where "+SQL
        for i in ismissing:
            SQL+= ' '+i+'= '+'0'+' and '
        SQL=SQL[:-4]

    # SQL = SQL + ' and dd.status_cooling = ' + str(status_cooling) + " "
    Limit = ''' and dd.toc >= '{startTime}'::timestamp
        and dd.toc <= '{endTime}'::timestamp; '''.format(startTime=startTime, endTime=endTime)

    SQL = 'select ' + select + singleSQL_lefttable + SQL + Limit
    # print(SQL)
    data, col_names = getLabelData(SQL)
    return data, status_cooling

def  modeldata_1(parser, selection, current_time, limit):
    SQL, status_cooling = filterSQL(parser)

    select = ','.join(selection)
    ismissing = ['dd.status_stats']
    if(SQL!=''):
        for i in ismissing:
            SQL+= ' and '+i+'= '+'0'
    if (SQL==''):
        SQL="where "+SQL
        for i in ismissing:
            SQL+= ' '+i+'= '+'0'+' and '
        SQL=SQL[:-4]

    SQL = SQL + ' and dd.status_cooling = ' + str(status_cooling) + " "
    # Limit = ' ORDER BY dd.toc  DESC Limit ' + str(limit)
    Limit = ''' and dd.toc >= '{current_time}'::timestamp
        order by abs(extract(epoch
        from dd.toc - '{current_time}'::timestamp))
        limit {limition}; '''.format(current_time=current_time, limition=limit)

    SQL = 'select ' + select + singleSQL_lefttable + SQL + Limit
    # print(SQL)
    data,col_names = getLabelData(SQL)
    return data, status_cooling

def cate_modeldata(parser, selection, Limit):
    SQL, status_cooling = filterSQL(parser)

    select = ','.join(selection)
    ismissing = ['dd.status_stats']
    if(SQL!=''):
        for i in ismissing:
            SQL+= ' and '+i+'= '+'0'
    if (SQL==''):
        SQL="where "+SQL
        for i in ismissing:
            SQL+= ' '+i+'= '+'0'+' and '
        SQL=SQL[:-4]

    # SQL = SQL + ' and dd.status_cooling = ' + str(status_cooling) + " "
    # Limit = ''' and dd.toc >= '{startTime}'::timestamp
    #     and dd.toc <= '{endTime}'::timestamp; '''.format(startTime=startTime, endTime=endTime)

    SQL = 'select ' + select + singleSQL_lefttable + SQL + Limit
    # print(SQL)
    data, col_names = getLabelData(SQL)
    return data, status_cooling


def modeldata_for_corr(parser, selection, startTime, endTime, limit_num):
    SQL, status_cooling = filterSQL(parser)

    select = ','.join(selection)
    ismissing = ['dd.status_stats']
    if(SQL!=''):
        for i in ismissing:
            SQL+= ' and '+i+'= '+'0'
    if (SQL==''):
        SQL="where "+SQL
        for i in ismissing:
            SQL+= ' '+i+'= '+'0'+' and '
        SQL=SQL[:-4]

    # SQL = SQL + ' and dd.status_cooling = ' + str(status_cooling) + " "
    Limit = ''' and dd.toc >= '{startTime}'::timestamp
        and dd.toc <= '{endTime}'::timestamp limit {limit}; '''.format(startTime=startTime, endTime=endTime, limit=limit_num)

    SQL = 'select ' + select + singleSQL_lefttable + SQL + Limit
    # print(SQL)
    data, col_names = getLabelData(SQL)
    return data, status_cooling


def new_modeldata(parser,selection, limit):
    SQL, status_cooling, fqcflag = new_filterSQL(parser)
    select = ','.join(selection)
    ismissing = ['dd.status_stats','dd.status_fqc']
    lefttable = ''' from  dcenter.l2_m_primary_data lmpd
                    left join dcenter.l2_m_plate lmp on lmpd.slabid = lmp.slabid
                    left join dcenter.l2_cc_pdi lcp  on lmpd.slabid = lcp.slab_no
                    right join app.deba_dump_data dd on dd.upid = lmp.upid
                    right join app.deba_dump_properties ddp on ddp.upid = dd.upid '''
    if(SQL!=''):
        if fqcflag == 0:
            for i in ismissing:
                SQL+= ' and '+i+'= '+'0'
        elif fqcflag == 1:
            for i in ismissing[:-1]:
                SQL+= ' and '+ i +'= '+'0'
    if (SQL==''):
        SQL="where "+SQL
        if fqcflag == 0:
            for i in ismissing:
                SQL+= ' '+i+'= '+'0'+' and '
        elif fqcflag == 1:
            for i in ismissing[:-1]:
                SQL += ' ' + i + '= ' + '0' + ' and '

        SQL=SQL[:-4]
    SQL = SQL + ' and dd.status_cooling = ' + str(status_cooling) + " "
    Limit = ' ORDER BY dd.toc  DESC Limit ' + str(limit)
    SQL = 'select ' + select + lefttable + SQL + Limit
    # print('Other Data: ', SQL)
    data, col_names = getLabelData(SQL)
    return data, col_names, status_cooling, fqcflag


def mareymodeldata(start_time, end_time, parser, selection, status_cooling):
    # SQL=filterSQL(parser)
    select = ','.join(selection)
    # ismissing = ['dd.status_stats']
    # if(SQL!=''):
    #     for i in ismissing:
    #         SQL+= ' and '+i+'= '+'0'
    # if (SQL==''):
    #     SQL="where " + SQL
    #     for i in ismissing:
    #         SQL+= ' '+i+'= '+'0'+' and '
    #     SQL=SQL[:-4]
    Limit = ' ORDER BY dd.toc DESC'
    SQL = 'select ' + select + singleSQL_lefttable +\
            " where dd.status_stats= 0 and dd.toc >= to_timestamp('" +start_time + "','yyyy-mm-dd hh24:mi:ss') " +\
            " and dd.status_cooling = " + str(status_cooling) +\
            " and dd.toc <= to_timestamp('" + end_time + "','yyyy-mm-dd hh24:mi:ss') "

    # print("------  mareymodeldata SQL ------")
    # print(SQL)
    # print("------  end ------")

    data,col_names = getLabelData(SQL)
    return data, col_names

def modelfilterdata(parser,selection):
    SQL= filterSteelSpec(parser)
    select = ','.join(selection)
    ismissing = ['dd.all_processes_statistics_ismissing','dd.cool_ismissing','dd.fu_temperature_ismissing','dd.m_ismissing','dd.fqc_ismissing']
    if(SQL!=''):
        for i in ismissing:
            SQL+= ' and '+i+'= '+'0'
    if (SQL==''):
        SQL="where "+SQL
        for i in ismissing:
            SQL+= ' '+i+'= '+'0'+' and '
        SQL=SQL[:-4]
    SQL = 'select ' + select + lefttable + SQL + ' ORDER BY dd.toc DESC'
    data,col_names=getLabelData(SQL)
    # if(len(data) == 0) modeldata(parser, selection)
    return data, col_names

class singelSteel(Resource):
    '''
    singelSteel
    '''
    def get(self, upid, fault_type):
        """
        get
        ---
        tags:
            - 钢板信息
        parameters:
            - in: path
            name: upid
            required: true
            description: 钢板upid
            type: string
        responses:
            200:
                description: 执行成功
        """
        selection = []
        if (fault_type == 'performance'):
            selection = ["dd.status_fqc", 'ddp.p_f_label']
        elif (fault_type == 'thickness'):
            selection = ["dd.status_fqc", 'dd.p_f_label']
        select = ','.join(selection)

        sql = '''select lmpd.slabid, 
                    lmpd.upid,
                    lmpd.productcategory, 
                    lmpd.steelspec,
                    lmpd.toc,
                    --出炉温度(目标值)
                    lmpd.slabthickness *1000 as slabthickness,
                    lmpd.tgtdischargetemp,
                    --钢板厚度
                    
                    (case when lmpd.shapecode ='11' or lmpd.shapecode='12' then lmpd.tgtplatethickness5 else lmpd.tgtplatethickness1 end) * 1000 as tgtplatethickness,
                    --钢板宽度
                    lmpd.tgtwidth *1000 as tgtwidth,
                    --钢板长度
                    lmpd.tgtplatelength2,
                    --板坯厚度

                    --终轧温度
                    lmpd.tgttmplatetemp,
                    --开冷温度
                    lcp.cooling_start_temp,
                    --终冷温度
                    lcp.cooling_stop_temp,
                    --冷却速率
                    lcp.cooling_rate1,

                    dd.status_cooling,
                    dd.status_furnace,
                    dd.status_rolling,
                    '''+ select + singleSQL_lefttable + ' where lmpd.upid='+repr(upid)+'order by lmpd.toc'
        jsondata, col_names = getLabelData(sql)
        if len(jsondata) == 0:
            return '', 204, {'Access-Control-Allow-Origin': '*'}

        label = 0
        if jsondata[0][-2] == 1:
            label = 404
            jsondata = list(jsondata[0])
        elif jsondata[0][-2] == 0: # 有性能检测标签
            jsondata = list(jsondata[0])
            if 0 not in jsondata[-1]: # 判断是否存在0
                label = 1
        jsondata[4] = str(jsondata[4])
        jsondata = dict(zip(col_names, jsondata))
        jsondata["label"] = label
        return jsondata, 200, {'Access-Control-Allow-Origin': '*'}

api.add_resource(singelSteel, '/v1.0/model/singelSteel/<upid>/<fault_type>/')