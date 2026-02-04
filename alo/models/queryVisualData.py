from ..utils import queryDataFromDatabase
import datetime
def getConditionSQL(self):
    conditions = []

    if self.thick_range and len(self.thick_range) == 2:
        conditions.append(f"AND dd.tgtthickness * 1000 BETWEEN {self.thick_range[0]} AND {self.thick_range[1]}")
    if self.width_range and len(self.width_range) == 2:
        conditions.append(f"AND dd.tgtwidth BETWEEN {self.width_range[0]} AND {self.width_range[1]}")
    if self.length_range and len(self.length_range) == 2:
        conditions.append(f"AND dd.tgtlength BETWEEN {self.length_range[0]} AND {self.length_range[1]}")
    if self.date_range and len(self.date_range) == 2:
        conditions.append(f"AND dd.toc BETWEEN '{self.date_range[0]}' AND '{self.date_range[1]}'")
    if self.fmTemp_range and len(self.fmTemp_range) == 2:
        conditions.append(f"AND lmpd.tgttmrestarttemp1 BETWEEN {self.fmTemp_range[0]} AND {self.fmTemp_range[1]}")
    if self.disTemp_range and len(self.disTemp_range) == 2:
        conditions.append(f"AND lff.ave_temp_dis BETWEEN {self.disTemp_range[0]} AND {self.disTemp_range[1]}")

    return conditions

def parse_date_range(self):
    date_range = eval(self.date_range)
    start_date = datetime.datetime.strptime(date_range[0], "%Y-%m-%d %H:%M:%S")
    end_date = datetime.datetime.strptime(date_range[1], "%Y-%m-%d %H:%M:%S")
    start_year = str(start_date.year)[2:]  # 提取年份的后两位
    start_month = start_date.month
    start_day = str(start_date.day).zfill(2)
    start_hour = str(start_date.hour).zfill(2)
    # 替换月份为A, B, C, ... , J (10 -> A, 11 -> B, 12 -> C)
    if start_month == 10:
        start_month = 'A'
    elif start_month == 11:
        start_month = 'B'
    elif start_month == 12:
        start_month = 'C'
    else:
        start_month = str(start_month)
    start_date_str = f"{start_year}{start_month}{start_day}{start_hour}"
    # 处理结束日期
    end_year = str(end_date.year)[2:]
    end_month = end_date.month
    end_day = str(end_date.day).zfill(2)
    end_hour = str(end_date.hour).zfill(2)
    if end_month == 10:
        end_month = 'A'
    elif end_month == 11:
        end_month = 'B'
    elif end_month == 12:
        end_month = 'C'
    else:
        end_month = str(end_month)
    end_date_str = f"{end_year}{end_month}{end_day}{end_hour}"
    return start_date_str, end_date_str

def getTrendBar(self):
    sql_start = f"{self.start_date} 00:00:00"
    sql_end = f"{self.end_date} 23:59:59"
    # 2. SQL 查询 (查询逻辑不变，依旧拉取全量数据，在内存中分桶)
    sql = '''
                    select 
                            dd.toc,
                            dd.upid,
                            ddp.p_f_label
                            from app.deba_dump_data dd
                            left join dcenter.l2_m_mv_thickness_pg dt on dt.upid = dd.upid
                            LEFT JOIN app.deba_dump_properties ddp ON ddp.upid = dd.upid
                            where dd.toc >= to_timestamp('{start}', 'yyyy-mm-dd hh24:mi:ss')
                            and dd.toc <= to_timestamp('{end}', 'yyyy-mm-dd hh24:mi:ss')
                            order by dd.toc asc
                    '''.format(start=sql_start, end=sql_end)
    data, col = queryDataFromDatabase(sql)

    return data, col

def getBoxData(self):
    sql_start = f"{self.start_date} 00:00:00"
    sql_end = f"{self.end_date} 23:59:59"
    # 2. SQL 查询 (查询逻辑不变，依旧拉取全量数据，在内存中分桶)
    sql = '''
        SELECT
            dd.upid,
            dd.toc,
            dd.tgtthickness * 1000 as tgtthickness,
            dd.tgtwidth,
            dd.tgtlength,
            ddp.p_f_label,
            lff.ave_temp_dis,
            lmpd.tgttmrestarttemp1
        FROM
            app.deba_dump_data dd
            LEFT JOIN dcenter.l2_fu_flftr60 lff ON lff.upid = dd.upid
            LEFT JOIN dcenter.l2_m_primary_data lmpd ON lmpd.upid = dd.upid
            LEFT JOIN app.deba_dump_properties ddp ON dd.upid = ddp.upid
        WHERE
            dd.toc >= to_timestamp('{start}', 'yyyy-mm-dd hh24:mi:ss')
            AND dd.toc <= to_timestamp('{end}', 'yyyy-mm-dd hh24:mi:ss')
            AND lmpd.tgttmrestarttemp1 != 0
	        AND lff.ave_temp_dis != 0
	        AND dd.status_fqc = 0
        ORDER BY
            dd.toc
    '''.format(start=sql_start, end=sql_end)
    data, col = queryDataFromDatabase(sql)
    return data, col


def getScatterData(self):
    base_sql = '''
            SELECT
                dd.upid,
                dd.toc,
                dd.platetype,
                dd.stats,
                dd.status_fqc,
                dd.status_cooling,
                ddp.p_f_label,
                lff.ave_temp_dis,
                lmpd.tgttmrestarttemp1 
            FROM
                app.deba_dump_data dd
                LEFT JOIN dcenter.l2_fu_flftr60 lff ON lff.upid = dd.upid
                LEFT JOIN dcenter.l2_m_primary_data lmpd ON lmpd.upid = dd.upid
                LEFT JOIN app.deba_dump_properties ddp ON dd.upid = ddp.upid 
            WHERE 1=1 
        '''

    conditions = getConditionSQL(self)

    final_sql = base_sql + " " + " ".join(conditions) + " ORDER BY dd.toc LIMIT 2000"
    data, col = queryDataFromDatabase(final_sql)
    return data, col

def getBatchData(self):
    base_sql = '''
                SELECT
	                dd.upid,
	                dd.toc,
	                dd.platetype,
	                dd.tgtwidth,
	                dd.tgtthickness * 1000 as tgtthickness,
	                dd.tgtlength,
	                ddp.p_f_label
                FROM
	                app.deba_dump_data dd
	                LEFT JOIN app.deba_dump_properties ddp ON ddp.upid = dd.upid 
                WHERE
	                1 = 1 
            '''

    conditions = getConditionSQL(self)
    final_sql = base_sql + " " + " ".join(conditions) + " ORDER BY dd.toc "
    data, col = queryDataFromDatabase(final_sql)
    return data, col

def getlabelFlag(upids):
    sql_query = '''
                select 
                    dd.toc,
                    dd.upid,
                    dd.tgtthickness,
                    ddp.p_f_label
                    from app.deba_dump_data dd
                    left join app.deba_dump_properties ddp ON dd.upid = ddp.upid 
                    where {upid}
                    order by dd.upid
                '''.format(upid='dd. upid in' + upids)
    rows, cols = queryDataFromDatabase(sql_query)
    return rows, cols
