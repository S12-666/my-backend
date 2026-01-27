from ..utils import queryDataFromDatabase

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

