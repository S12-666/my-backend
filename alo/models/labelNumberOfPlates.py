from ..utils import queryDataFromDatabase
def getLabelData(start, end, type):

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
