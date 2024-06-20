from ..utils import queryDataFromDatabase
def getLabelData(start, end):
    sql = """
        select dd.toc, dd.fqc_label, dd.status_fqc
        from  app.deba_dump_data dd
        where dd.toc between '{start}' and '{end}'
        order by dd.toc
    """.format(start=start, end=end)
    data, columns = queryDataFromDatabase(sql)
    return data, columns
