from ..utils import queryDataFromDatabase

def getFQCDetialSQL(conditions):
    sql = '''
        SELECT
            dd.upid,
            lmpd.slabid,
            dd.toc,
            lcp.thick,
            lcp.width / 1000 AS width,
            lcp.length / 1000 AS length,
            dd.tgtthickness * 1000 AS tgtthickness,
            dd.tgtwidth,
            dd.tgtlength,
            dd.fqc_label,
            ddp.p_f_label,
            ddp.p_data,
            ddpc.pred_label,
	        ddpc.msg
        FROM
            app.deba_dump_data dd
            LEFT JOIN dcenter.l2_m_primary_data lmpd ON lmpd.upid = dd.upid
            LEFT JOIN dcenter.l2_cc_pdi lcp ON lcp.slab_no = lmpd.slabid
            LEFT JOIN app.deba_dump_properties ddp ON ddp.upid = dd.upid
            LEFT JOIN app.deba_dump_properties_copy1 ddpc ON ddpc.upid = dd.upid
        WHERE
	        {conditions}
        ORDER BY
	        dd.toc
    '''.format(conditions = conditions)
    data, columns = queryDataFromDatabase(sql)
    return data, columns