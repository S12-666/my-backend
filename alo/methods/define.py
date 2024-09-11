specifications = ['tgtwidth', 'tgtplatelength2', 'tgtthickness', 'tgtdischargetemp', 'tgttmplatetemp']
analysis_condition = ['tgtplatelength2', 'tgtwidth', 'tgtplatethickness', 'dischargetemp', 'tmplatetemp', 'cooling_start_temp', 'cooling_stop_temp', 'cooling_rate', 'steelspec']
data_names = [
    "charging_temp_act", "tgtplatelength2", "tgtplatethickness2", "tgtwidth", "slab_length", "slab_thickness", "slab_weight_act", "slab_width",
    "ave_temp_1", "ave_temp_2", "ave_temp_dis", "ave_temp_pre", "ave_temp_soak", "ave_temp_entry_1", "ave_temp_entry_2", "ave_temp_entry_pre",
    "ave_temp_entry_soak", "center_temp_dis", "center_temp_entry_1", "center_temp_entry_2", "center_temp_entry_pre", "center_temp_entry_soak",
    "temp_uniformity_dis", "temp_uniformity_entry_1", "temp_uniformity_entry_2", "temp_uniformity_entry_pre", "temp_uniformity_entry_soak",
    "skid_temp_dis", "skid_temp_entry_1", "skid_temp_entry_2", "skid_temp_entry_pre", "skid_temp_entry_soak", "staying_time_1", "staying_time_2",
    "staying_time_pre", "staying_time_soak", "sur_temp_dis", "sur_temp_entry_1", "sur_temp_entry_2", "sur_temp_entry_pre", "sur_temp_entry_soak",
    "meas_temp_0", "meas_temp_1", "meas_temp_10", "meas_temp_11", "meas_temp_12", "meas_temp_13", "meas_temp_14", "meas_temp_15", "meas_temp_16",
    "meas_temp_17", "meas_temp_18", "meas_temp_19", "meas_temp_2", "meas_temp_3", "meas_temp_4", "meas_temp_5", "meas_temp_6", "meas_temp_7",
    "meas_temp_8", "meas_temp_9", "t_0", "t_1", "t_2", "t_3", "t_4", "t_5", "t_6", "pass",
    "crownbody", "crownhead", "crowntail", "crowntotal", "devcrownbody", "devcrownhead", "devcrowntail",
    "devcrowntotal", "devfinishtempbody", "devfinishtemphead", "devfinishtemptail", "devfinishtemptotal", "wedgebody", "wedgehead",
    "wedgetotal", "devwedgebody", "devwedgehead", "devwedgetail", "devwedgetotal", "finishtempbody", "finishtemphead", "finishtemptail", "finishtemptotal",
    "avg_fct", "avg_p1",
    "avg_p5", "avg_sct", "max_fct", "max_p1", "max_p2", "max_p5", "max_sct", "min_fct", "min_p1",
    "min_p2", "min_p5", "min_sct", "std_fct", "std_p1", "std_p2", "std_p5", "std_sct"
]
without_cooling_data_names = [
    "charging_temp_act", "tgtplatelength2", "tgtplatethickness2", "tgtwidth", "slab_length", "slab_thickness", "slab_weight_act", "slab_width",
    "ave_temp_1", "ave_temp_2", "ave_temp_dis", "ave_temp_pre", "ave_temp_soak", "ave_temp_entry_1", "ave_temp_entry_2", "ave_temp_entry_pre",
    "ave_temp_entry_soak", "center_temp_dis", "center_temp_entry_1", "center_temp_entry_2", "center_temp_entry_pre", "center_temp_entry_soak",
    "temp_uniformity_dis", "temp_uniformity_entry_1", "temp_uniformity_entry_2", "temp_uniformity_entry_pre", "temp_uniformity_entry_soak",
    "skid_temp_dis", "skid_temp_entry_1", "skid_temp_entry_2", "skid_temp_entry_pre", "skid_temp_entry_soak", "staying_time_1", "staying_time_2",
    "staying_time_pre", "staying_time_soak", "sur_temp_dis", "sur_temp_entry_1", "sur_temp_entry_2", "sur_temp_entry_pre", "sur_temp_entry_soak",
    "meas_temp_0", "meas_temp_1", "meas_temp_10", "meas_temp_11", "meas_temp_12", "meas_temp_13", "meas_temp_14", "meas_temp_15", "meas_temp_16",
    "meas_temp_17", "meas_temp_18", "meas_temp_19", "meas_temp_2", "meas_temp_3", "meas_temp_4", "meas_temp_5", "meas_temp_6", "meas_temp_7",
    "meas_temp_8", "meas_temp_9", "t_0", "t_1", "t_2", "t_3", "t_4", "t_5", "t_6", "pass",
    "crownbody", "crownhead", "crowntail", "crowntotal", "devcrownbody", "devcrownhead", "devcrowntail",
    "devcrowntotal", "devfinishtempbody", "devfinishtemphead", "devfinishtemptail", "devfinishtemptotal", "wedgebody", "wedgehead",
    "wedgetotal", "devwedgebody", "devwedgehead", "devwedgetail", "devwedgetotal", "finishtempbody", "finishtemphead", "finishtemptail", "finishtemptotal"
]
data_names_meas = [
    "meas_temp_0", "meas_temp_1", "meas_temp_10", "meas_temp_11", "meas_temp_12", "meas_temp_13", "meas_temp_14", "meas_temp_15", "meas_temp_16",
    "meas_temp_17", "meas_temp_18", "meas_temp_19", "meas_temp_2", "meas_temp_3", "meas_temp_4", "meas_temp_5", "meas_temp_6", "meas_temp_7",
    "meas_temp_8", "meas_temp_9"
]
flag_names = ["pa", "pf", "pn", "ps", "gs"]
def meas_index():
    i1 = data_names.index(data_names_meas[0])
    i2 = data_names.index(data_names_meas[-1])
    return [i1, i2]
def name_index(key):
    try:
        idx = data_names.index(key)
    except:
        idx = -1
    return idx
