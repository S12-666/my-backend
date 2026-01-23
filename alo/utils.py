import re

import numpy as np
import psycopg2
import pandas as pd
# from .api.singelSteel import data_names,without_cooling_data_names,data_names_meas

def readConfig():
    # f = open('usr/src/config/config.txt')
    # f = open('usr/src/app/config.txt')
    f = open('config.txt')
    for line in f:
        configArr = line.split(' ')
        break
    return configArr

def SQLselect(selection,ismissing,tgtwidthSelect,tgtlengthSelect,tgtthicknessSelect,tocSelect,UpidSelect,Platetypes,AscOption,Limition):
    index=0;
    Process=['status_stats','status_cooling','status_furnace','status_rolling','status_fqc']
    miss=['0','0','0','0','0','0']
    missselect='';
    for i in ismissing:
        if(ismissing[i]):
            # selection.append(Process[index])
            missselect+= ' and '+i+'= '+miss[index];
        index+=1;
#         print(missselect)

    if(len(selection)==0): #select
        select='*'
        # print('fjdksjfskdjl')
    else:
        select = ','.join(selection)
#             print(select)
    if(len(tgtwidthSelect)==0):   #tgtwidth
        tgtwidth='';
    else: 
        tgtwidth=' and tgtwidth between '+tgtwidthSelect[0]+' and '+tgtwidthSelect[1]+' '
    if(len(tgtlengthSelect)==0):   #tgtlength
        tgtlength='';
    else: 
        tgtlength=' and tgtlength between '+tgtlengthSelect[0]+' and '+tgtlengthSelect[1]+' '
    if(len(tgtthicknessSelect)==0):  #tgtthickness
        tgtthickness='';
    else: 
        tgtthickness=' and tgtthickness between '+tgtthicknessSelect[0]+' and '+tgtthicknessSelect[1]+' '
    if(len(tocSelect)==0):   #toc
        toc='';
    else: 
        toc=' and toc between '+repr(tocSelect[0])+' and '+repr(tocSelect[1])+' '

    if(len(UpidSelect)==0): #upid
        upid='';
    else: 
        upid=' and (';
        for i in UpidSelect:
            upid+="upid="+repr(i)+' or '
        upid=upid[:-3]
        upid+=')';      
    if(len(Platetypes)==0):  #platetype
        platetype='';
    else: 
        platetype='and (';
        for i in Platetypes:
            platetype+='platetype='+repr(i)+' or '
        platetype=platetype[:-3]
        platetype+=')';
    if(AscOption==''):  #ASC
        ASC='';
    else:
        ASC=' ORDER BY '+AscOption+' DESC';
    if(Limition==''):  #Limit
        Limit='';
    else:
        Limit=' LIMIT '+Limition;
    Query=[tgtwidth,tgtlength,tgtthickness,toc,upid,platetype,missselect]

    for i in range(len(Query)):
        if(len(Query[i])!=0):
            Query[i]=Query[i][4:]
            # print(Query[i])
            SQL="select "+select+" from dcenter.dump_data " +"where"
            for j in Query:
                SQL+=j;
            SQL+=ASC+Limit;
            # print(SQL)
            return SQL
    return "select "+select+" from dcenter.dump_data "+ASC+Limit;

def getData(selection,ismissing,tgtwidthSelect,tgtlengthSelect,tgtthicknessSelect,tocSelect,UpidSelect,Platetypes,AscOption,Limition): 

    #  for docker outside config

    configArr = readConfig() 
    conn = psycopg2.connect(database=configArr[0], user=configArr[1], password=configArr[2], host=configArr[3],port=configArr[4])

    SQL=SQLselect(selection,ismissing,tgtwidthSelect,tgtlengthSelect,tgtthicknessSelect,tocSelect,UpidSelect,Platetypes,AscOption,Limition)

    # conn = psycopg2.connect(database='BSData20190713', user='postgres', password='616616', host='219.216.80.18',port='5432')
    # conn = psycopg2.connect(database='bg', user='postgres', password='woshimima', host='202.118.21.236',port='5432')

    cursor = conn.cursor()
    cursor.execute(SQL)
    rows = cursor.fetchall()
    
    conn.close()
    return rows
def SQLplateselect(selection,ismissing,tgtwidthSelect,tgtlengthSelect,tgtthicknessSelect,tocSelect,UpidSelect,Platetypes,AscOption,Limition):
    index=0;
    Process=['d.all_processes_statistics','d.v1','d.v2','d.v3','d.fqc_label']
    miss=['0','0','0','0','0','0']
    missselect='';
    for i in ismissing:
        if(ismissing[i]):
            # selection.append(Process[index])
            missselect+= ' and '+i+'= '+miss[index];
        index+=1;
#         print(missselect)

    if(len(selection)==0): #select
        select='*'
        # print('fjdksjfskdjl')
    else:
        select = ','.join(selection)
#             print(select)
    if(len(tgtwidthSelect)==0):   #tgtwidth
        tgtwidth='';
    else: 
        tgtwidth=' and d.tgtwidth between '+tgtwidthSelect[0]+' and '+tgtwidthSelect[1]+' '
    if(len(tgtlengthSelect)==0):   #tgtlength
        tgtlength='';
    else: 
        tgtlength=' and d.tgtlength between '+tgtlengthSelect[0]+' and '+tgtlengthSelect[1]+' '
    if(len(tgtthicknessSelect)==0):  #tgtthickness
        tgtthickness='';
    else: 
        tgtthickness=' and d.tgtthickness between '+tgtthicknessSelect[0]+' and '+tgtthicknessSelect[1]+' '
    if(len(tocSelect)==0):   #toc
        toc='';
    else: 
        toc=' and d.toc between '+repr(tocSelect[0])+' and '+repr(tocSelect[1])+' '

    if(len(UpidSelect)==0): #upid
        upid='';
    else: 
        upid=' and (';
        for i in UpidSelect:
            upid+="d.upid="+repr(i)+' or '
        upid=upid[:-3]
        upid+=')';      
    if(len(Platetypes)==0):  #platetype
        platetype='';
    else: 
        platetype='and (';
        for i in Platetypes:
            platetype+='m.productcategory='+repr(i)+' or '
        platetype=platetype[:-3]
        platetype+=')';
    if(AscOption==''):  #ASC
        ASC='';
    else:
        ASC=' ORDER BY d.'+AscOption+' DESC';
    if(Limition==''):  #Limit
        Limit='';
    else:
        Limit=' LIMIT '+Limition;
    Query=[tgtwidth,tgtlength,tgtthickness,toc,upid,platetype,missselect]
    index;
    for i in range(len(Query)):
        if(len(Query[i])!=0):
            Query[i]=Query[i][4:]
            # print(Query[i])
            SQL="select "+select+" from dcenter.dump_data d inner  join dcenter.l2_m_primary_data m ON d.upid=m.upid " +"where"
            for j in Query:
                SQL+=j;
            SQL+=ASC+Limit;
            # print(SQL)
            return getSQLData(SQL)
    return "select "+select+" from dcenter.dump_data "+ASC+Limit;
def getSQLData(SQLquery): 

    #  for docker outside config

    configArr = readConfig() 
    conn = psycopg2.connect(database=configArr[0], user=configArr[1], password=configArr[2], host=configArr[3],port=configArr[4])

    # conn = psycopg2.connect(database='BSData20190713', user='postgres', password='616616', host='219.216.80.18',port='5432')
    # conn = psycopg2.connect(database='bg', user='postgres', password='woshimima', host='202.118.21.236',port='5432')

    cursor = conn.cursor()
    cursor.execute(SQLquery)
    rows = cursor.fetchall()
    
    conn.close()
    return rows
def getFlagArr(str):
    arr = []
    midStr = re.findall('\[[0, 1].*[0,1]\]', str)
    m = re.search('([01]).*([01]).*([01]).*([01]).*([01])', midStr[0])
    for i in range(5):
        arr.append(int(m.group(i+1)))
    # print(arr)
    return arr
def getLabelData(SQLquery): 

    # conn = psycopg2.connect(database='BSData20190713', user='postgres', password='616616', host='219.216.80.18',port='5432')
    # conn = psycopg2.connect(database='bg', user='postgres', password='woshimima', host='202.118.21.236',port='5432')
    configArr = readConfig()
    conn = psycopg2.connect(database=configArr[0], user=configArr[1], password=configArr[2], host=configArr[3],port=configArr[4])

    cursor = conn.cursor()
    cursor.execute(SQLquery)
    rows = cursor.fetchall()

    # Extract the column names
    col_names = []
    for elt in cursor.description:
        col_names.append(elt[0])

    conn.close()
    return rows,col_names

def getLabel(data):
    label = ["头尾翘曲","中部厚度异常","中浪","左边浪","右边浪"]
    fault=getFlagArr(data['method1'])
    return dict(zip(label,fault))
ref = 5


def new_getData(selection, ismissing, tgtwidthSelect, tgtlengthSelect, tgtthicknessSelect, tocSelect, UpidSelect, Platetypes, AscOption, Limition):
    #  for docker outside config

    configArr = readConfig()
    conn = psycopg2.connect(database=configArr[0], user=configArr[1], password=configArr[2], host=configArr[3], port=configArr[4])

    SQL = sqlselect_bytime(selection, ismissing, tgtwidthSelect, tgtlengthSelect, tgtthicknessSelect, tocSelect, UpidSelect, Platetypes, AscOption, Limition)
    # print(SQL)
    # conn = psycopg2.connect(database='BSData20190713', user='postgres', password='616616', host='219.216.80.18',port='5432')
    # conn = psycopg2.connect(database='bg', user='postgres', password='woshimima', host='202.118.21.236',port='5432')

    cursor = conn.cursor()
    cursor.execute(SQL)
    rows = cursor.fetchall()
    col_names = []
    for elt in cursor.description:
        col_names.append(elt[0])
    conn.close()

    return rows, col_names

def new_SQLselect(selection,ismissing,tgtwidthSelect,tgtlengthSelect,tgtthicknessSelect,tocSelect,UpidSelect,Platetypes,AscOption,Limition):
    index=0
    miss=['0','0','0','0','0','0']
    missselect=''
    for i in ismissing:
        if(ismissing[i]):
            # selection.append(Process[index])
            missselect+= ' and '+i+'= '+miss[index]
        index+=1
#         print(missselect)

    if(len(selection)==0): #select
        select='*'
        # print('fjdksjfskdjl')
    else:
        select = ','.join(selection)
#             print(select)
    if(len(tgtwidthSelect)==0):   #tgtwidth
        tgtwidth=''
    else:
        tgtwidth=' and tgtwidth between '+tgtwidthSelect[0]+' and '+tgtwidthSelect[1]+' '
    if(len(tgtlengthSelect)==0):   #tgtlength
        tgtlength=''
    else:
        tgtlength=' and tgtlength between '+tgtlengthSelect[0]+' and '+tgtlengthSelect[1]+' '
    if(len(tgtthicknessSelect)==0):  #tgtthickness
        tgtthickness=''
    else:
        tgtthickness=' and tgtthickness between '+tgtthicknessSelect[0]+' and '+tgtthicknessSelect[1]+' '
    if(len(tocSelect)==0):   #toc
        toc=''
    else:
        toc=' and toc between '+repr(tocSelect[0])+' and '+repr(tocSelect[1])+' '

    if(len(UpidSelect)==0): #upid
        upid=''
    else:
        upid=' and ('
        for i in UpidSelect:
            upid+="upid="+repr(i)+' or '
        upid=upid[:-3]
        upid+=')'
    if(len(Platetypes)==0):  #platetype
        platetype=''
    else:
        platetype='and ('
        for i in Platetypes:
            platetype+='platetype='+repr(i)+' or '
        platetype=platetype[:-3]
        platetype+=')'
    if(AscOption==''):  #ASC
        ASC=''
    else:
        ASC=' ORDER BY '+AscOption+' DESC'
    if(Limition==''):  #Limit
        Limit=''
    else:
        Limit=' LIMIT '+Limition
    Query=[tgtwidth,tgtlength,tgtthickness,toc,upid,platetype,missselect]

    for i in range(len(Query)):
        if(len(Query[i])!=0):
            Query[i]=Query[i][4:]
            # print(Query[i])
            SQL="select "+select+" from app.deba_dump_data " +"where"
            for j in Query:
                SQL+=j
            SQL+=ASC+Limit
            # print(SQL)
            return SQL
    return "select "+select+" from app.deba_dump_data "+ASC+Limit


def sqlselect_bytime(selection, ismissing, tgtwidthSelect, tgtlengthSelect, tgtthicknessSelect, tocSelect, UpidSelect, Platetypes, AscOption, Limition):
    index=0
    miss=['0','0','0','0','0','0']
    missselect=''
    left_join_label = ''' from app.deba_dump_data dd 
                          right join app.deba_dump_properties ddp on ddp.upid = dd.upid '''
    for i in ismissing:
        if(ismissing[i]):
            # selection.append(Process[index])
            missselect+= ' and '+i+'= '+miss[index]
        index+=1
#         print(missselect)

    if(len(selection)==0): #select
        select='*'
        # print('fjdksjfskdjl')
    else:
        select = ','.join(selection)
#             print(select)
    if(len(tgtwidthSelect)==0):   #tgtwidth
        tgtwidth=''
    else:
        tgtwidth=' and tgtwidth between '+tgtwidthSelect[0]+' and '+tgtwidthSelect[1]+' '
    if(len(tgtlengthSelect)==0):   #tgtlength
        tgtlength=''
    else:
        tgtlength=' and tgtlength between '+tgtlengthSelect[0]+' and '+tgtlengthSelect[1]+' '
    if(len(tgtthicknessSelect)==0):  #tgtthickness
        tgtthickness=''
    else:
        tgtthickness=' and tgtthickness between '+tgtthicknessSelect[0]+' and '+tgtthicknessSelect[1]+' '
    if(len(tocSelect)==0):   #toc
        toc=''
    else:
        toc=' and dd.toc between '+repr(tocSelect[0])+' and '+repr(tocSelect[1])+' '

    if(len(UpidSelect)==0): #upid
        upid=''
    else:
        upid=' and ('
        for i in UpidSelect:
            upid+="dd.upid="+repr(i)+' or '
        upid=upid[:-3]
        upid+=')'
    if(len(Platetypes)==0):  #platetype
        platetype=''
    else:
        platetype='and ('
        for i in Platetypes:
            platetype+='platetype='+repr(i)+' or '
        platetype=platetype[:-3]
        platetype+=')'
    if(AscOption==''):  #ASC
        ASC=''
    else:
        ASC=' ORDER BY '+AscOption+' DESC'
    if(Limition==''):  #Limit
        Limit=''
    else:
        Limit=' LIMIT '+Limition
    Query=[tgtwidth,tgtlength,tgtthickness,toc,upid,platetype,missselect]

    for i in range(len(Query)):
        if(len(Query[i])!=0):
            Query[i]=Query[i][4:]
            # print(Query[i])
            SQL="select "+select+ left_join_label +"where"
            for j in Query:
                SQL+=j
            SQL+=ASC+Limit
            # print(SQL)
            return SQL + " order by dd.toc"
    return "select "+select+" from app.deba_dump_data "+ASC+Limit + " order by toc"


def new_getData(selection, ismissing, tgtwidthSelect, tgtlengthSelect, tgtthicknessSelect, tocSelect, UpidSelect, Platetypes, AscOption, Limition):
    #  for docker outside config

    configArr = readConfig()
    conn = psycopg2.connect(database=configArr[0], user=configArr[1], password=configArr[2], host=configArr[3], port=configArr[4])

    SQL = sqlselect_bytime(selection, ismissing, tgtwidthSelect, tgtlengthSelect, tgtthicknessSelect, tocSelect, UpidSelect, Platetypes, AscOption, Limition)
    # print("new_getData")
    # print(SQL)

    # conn = psycopg2.connect(database='BSData20190713', user='postgres', password='616616', host='219.216.80.18',port='5432')
    # conn = psycopg2.connect(database='bg', user='postgres', password='woshimima', host='202.118.21.236',port='5432')

    cursor = conn.cursor()
    cursor.execute(SQL)
    rows = cursor.fetchall()

    col_names = []
    for elt in cursor.description:
        col_names.append(elt[0])

    conn.close()
    return rows,col_names


def getData_bytime(selection, ismissing, tgtwidthSelect, tgtlengthSelect, tgtthicknessSelect, tocSelect, UpidSelect, Platetypes, AscOption, Limition):
    #  for docker outside config

    configArr = readConfig()
    conn = psycopg2.connect(database=configArr[0], user=configArr[1], password=configArr[2], host=configArr[3], port=configArr[4])

    SQL = sqlselect_bytime(selection, ismissing, tgtwidthSelect, tgtlengthSelect, tgtthicknessSelect, tocSelect, UpidSelect, Platetypes, AscOption, Limition)
    # print("new_getData")
    # print(SQL)

    # conn = psycopg2.connect(database='BSData20190713', user='postgres', password='616616', host='219.216.80.18',port='5432')
    # conn = psycopg2.connect(database='bg', user='postgres', password='woshimima', host='202.118.21.236',port='5432')

    cursor = conn.cursor()
    cursor.execute(SQL)
    rows = cursor.fetchall()

    col_names = []
    for elt in cursor.description:
        col_names.append(elt[0])

    conn.close()
    return rows,col_names

def getArgsFromParser(parser, keys):
    for key in keys:
        parser.add_argument(key, type=str, required=True)
    args = parser.parse_args(strict=True)
    return args

def queryDataFromDatabase(sql: str):
    configArr = readConfig()
    conn = psycopg2.connect(database=configArr[0], user=configArr[1], password=configArr[2], host=configArr[3], port=configArr[4])
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    col_names = []
    for elt in cursor.description:
        col_names.append(elt[0])
    conn.close()
    return rows, col_names

def response_wrapper(res, code=0, msg=''):
    """
        code:
            0 => success
            1 => response warning
            2 => request parameter error
            4 => no response content
            5 => data calculation error
    """
    if code == 1:
        msg = 'something warning' if len(msg) == 0 else msg
    elif code == 2:
        msg = 'request parameter error' if len(msg) == 0 else msg
    elif code == 5:
        msg = 'data calculation error' if len(msg) == 0 else msg
    elif len(res) == 0:
        msg = 'no response data' if len(msg) == 0 else msg
        code = 4
    else:
        msg = 'ok' if len(msg) == 0 else msg
    return {'code': code, 'msg': msg, 'data': res}, 200, {'Access-Control-Allow-Origin': '*'}

def format_value(val: float, s: str = '.4f') -> float:
    return float(format(val, s))


def label_flag_judge(data, type):
    status = ''
    label_judge = []
    if type == 'performance':
        status = int(data['status_fqc'])
        label_judge = data['p_f_label'].iloc[0]
        label = 0
        if status == 1:
            label = 404
        elif status == 0:
            if 0 not in label_judge:
                if (np.array(label_judge).sum() == 10) or (len(label_judge) == 0):
                    label = 404
                else:
                    label = 1
    elif type == 'thickness':
        status = int(data['t_flag'])
        label_judge = data['t_label'].iloc[0]
        label = 0
        if status == 1:
            label = 404
        elif status == 0:
            if 0 not in label_judge:
                if (np.array(label_judge).sum() == 6) or (len(label_judge) == 0):
                    label = 404
                else:
                    label = 1
    return label

def getLabelData_4(start, end, type):

    label = ''
    status = ''
    right_tabel = ''

    if (type == 'performance'):
        label = 'ddp.p_f_label'
        status = 'dd.status_fqc'
        right_tabel = ''' app.deba_dump_data dd
                          right join app.deba_dump_properties ddp ON ddp.upid = dd.upid '''
    elif (type == 'thickness'):
        label = 't_label'
        status = 'status_fqc'

    select = 'select dd.toc,' + label + ',' + status
    tabel = '\nfrom ' + right_tabel
    sql = select + tabel + "\nwhere dd.toc between '" + start + "' and '" + end + "' " + 'order by dd.toc '
    data, columns = queryDataFromDatabase(sql)
    return data, columns

def getpfList(p_f_label):
    return p_f_label if p_f_label else []
def plateHasDefect(status: int, p_f_label: dict) -> int:
    if status == 1:
        return 404
    label = getpfList(p_f_label)
    if 0 not in label:
        if (np.array(label).sum() == 10) or (len(label) == 0):
            return 404
        else:
            return 1
    else:
        return 0
def plateDetailedDefect(status: int, p_f_label: list, idx: int) -> int:
    if status == 1:
        return 404
    else:
        if 0 not in p_f_label:
            if (np.array(p_f_label).sum() == 10) or (len(p_f_label) == 0):
                return 404
        return p_f_label[idx]
def fillListTail(data: list, length: int, fill=0) -> list:
    if len(data) >= length:
        return data
    return data + (length - len(data)) * [fill]

def getOverviewData(start, end, fault_type):

    right_tabel = ''' from dcenter.l2_m_primary_data lmpd
         left join dcenter.l2_fu_acc_t lfat on lmpd.slabid = lfat.slab_no
         left join dcenter.l2_m_plate lmp on lmpd.slabid = lmp.slabid
         left join dcenter.l2_cc_pdi lcp on lmpd.slabid = lcp.slab_no
         right join app.deba_dump_data dd on dd.upid = lmp.upid
         right join app.deba_dump_properties ddp on ddp.upid = dd.upid'''

    select = []
    if fault_type == 'performance':
        select = ['ddp.p_f_label', 'dd.status_fqc']
    elif fault_type == 'thickness':
        select = []
    select = ','.join(select)

    sql = '''select     dd.upid, 
                        lmpd.steelspec,
                        dd.toc,
                        dd.tgtwidth,
                        dd.tgtlength,
                        dd.tgtthickness *1000 as tgtthickness,
                        dd.stats,
                        (case when lmpd.shapecode = '11' or lmpd.shapecode = '12' then lmpd.tgtplatethickness5 else lmpd.tgtplatethickness1 end) * 1000,
                        dd.status_cooling,
                        lmpd.slabthickness * 1000 as slabthickness,
                        lmpd.tgtdischargetemp,
                        lmpd.tgttmplatetemp,
                        lcp.cooling_start_temp,
                        lcp.cooling_stop_temp,
                        lcp.cooling_rate1,
                        ''' + select + right_tabel + " where dd.toc between '" + start + " ' and ' " + end + " ' "

    data, columns = queryDataFromDatabase(sql)
    return data, columns
# def rawDataToModelData(data_df):
#     data_matrix = []
#     labels_matrix = []
#     feature_length = max(len(data_names), len(without_cooling_data_names))
#     for idx, row in data_df.iterrows():
#         status_cooling = row['status_cooling']
#         if status_cooling == 0:
#             iter_names = data_names
#             labels = getpfList(row['p_f_label'])
#         else:
#             iter_names = without_cooling_data_names
#             labels = getpfList(row['p_f_label'])
#         item_data = []
#         for name in iter_names:
#             try:
#                 item_data.append(row['stats'][name])
#             except:
#                 item_data.append(0)
#         item_data = list(map(lambda x: 0.0 if x is None else x, item_data))
#         item_data = fillListTail(item_data, feature_length, 0)
#         data_matrix.append(item_data)
#         labels_matrix.append(labels)
#     return data_matrix, labels_matrix

def response_wrapper(res: object = None, code: int = 200, msg: str = '') -> object:
    """
        code:
            0 => success
            1 => response warning
            2 => request parameter error
            4 => no response content
            5 => data calculation error
    """
    if res is None:
        res = {}

    if code == 200:
        if not msg:
            msg = 'success'
            if hasattr(res, '__len__') and len(res) == 0:
                msg = 'success(no data)'
    elif code == 400:
        msg = 'request parameter error' if not msg else msg
    elif code == 500:
        msg = 'internal server error' if not msg else msg
    return {'code': code, 'msg': msg, 'data': res}, 200, {'Access-Control-Allow-Origin': '*'}

def format_value(val: float, s: str = '.4f') -> float:
    return float(format(val, s))

def concat_dict(dict_1: dict, dict_2: dict) -> dict:
    for key in dict_2:
        dict_1[key] = dict_2[key]
    return dict_1

def label_judge(arr):
    if 0 in arr:
        return 0
    if 1 in arr:
        return 1
    return 2

def executeSql(sql: str):
    """
    专门用于执行 INSERT / UPDATE / DELETE 语句
    """
    configArr = readConfig()
    conn = None
    try:
        conn = psycopg2.connect(
            database=configArr[0],
            user=configArr[1],
            password=configArr[2],
            host=configArr[3],
            port=configArr[4]
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit() # 关键：提交事务
        affected_rows = cursor.rowcount # 获取受影响行数
        cursor.close()
        return True, f"Success, affected rows: {affected_rows}"
    except Exception as e:
        if conn:
            conn.rollback() # 出错回滚
        print(f"Database Execution Error: {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()