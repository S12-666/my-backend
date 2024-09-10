from ..utils import queryDataFromDatabase
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
