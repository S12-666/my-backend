from ..utils import queryDataFromDatabase
import pandas as pd
def get_singel(upid):
    sql = """
        SELECT
	        upid,
	        toc,
	        platetype,
	        stats 
        FROM
	        app.deba_dump_data 
        WHERE
	        upid = '{upid}';
    """.format(upid = upid)
    data, columns = queryDataFromDatabase(sql)
    return data, columns

def get_specific_train_data(cooling_status, platetype, target):
    labels_map = {
        'pa': 1,
        'pf': 2,
        'pn': 3,
        'ps': 4,
        'gs': 5
    }
    index = labels_map.get(target)
    sql = '''
        SELECT
	        dd.upid,
	        dd.stats,
	        ddpc.plabel,
	        dd.status_cooling 
        FROM
	        app.deba_dump_data dd
	    LEFT JOIN app.deba_dump_properties_copy1 ddpc ON dd.upid = ddpc.upid 
        WHERE
	        dd.status_cooling = {cooling_status} 
	    AND ( ddpc.plabel :: INTEGER [] ) [ {index} ]!= 2
	    -- AND dd.platetype = '{platetype}'
	    LIMIT 5000
    '''.format(cooling_status=cooling_status,index = index, platetype= platetype)
    data, columns = queryDataFromDatabase(sql)

    return data, columns

def get_unsupervised_train_data(cooling_status, platetype, target):
    labels_map = {
        'pa': 1,
        'pf': 2,
        'pn': 3,
        'ps': 4,
        'gs': 5
    }
    index = labels_map.get(target)
    sql = '''
        SELECT
	        dd.upid,
	        dd.stats,
	        ddpc.plabel,
	        dd.status_cooling 
        FROM
	        app.deba_dump_data dd
	    LEFT JOIN app.deba_dump_properties_copy1 ddpc ON dd.upid = ddpc.upid 
        WHERE
	        dd.status_cooling = {cooling_status} 
	    -- AND dd.platetype = '{platetype}'
	    -- AND ( ddpc.plabel :: INTEGER [] ) [ {index} ]!= 2
	    LIMIT 5000
    '''.format(cooling_status=cooling_status,index = index, platetype= platetype)
    data, columns = queryDataFromDatabase(sql)

    return data, columns


def get_upid(upid):
    sql = '''
        SELECT
	        dd.upid,
	        dd.platetype,
	        dd.status_cooling,
	        ddp.p_f_label 
        FROM
	        app.deba_dump_data dd
	        LEFT JOIN app.deba_dump_properties ddp ON dd.upid = ddp.upid 
        WHERE
	        dd.upid = '{upid}'
    '''.format(upid=upid)

    data, columns = queryDataFromDatabase(sql)
    return data, columns


