import numpy as np
import pandas as pd
from .define import data_names, without_cooling_data_names
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
def rawDataToModelData(data_df):
    data_matrix = []
    labels_matrix = []
    feature_length = max(len(data_names), len(without_cooling_data_names))
    for idx, row in data_df.iterrows():
        status_cooling = row['status_cooling']
        if status_cooling == 0:
            iter_names = data_names
            labels = getpfList(row['p_f_label'])
        else:
            iter_names = without_cooling_data_names
            labels = getpfList(row['p_f_label'])
        item_data = []
        for name in iter_names:
            try:
                item_data.append(row['stats'][name])
            except:
                item_data.append(0)
        item_data = list(map(lambda x: 0.0 if x is None else x, item_data))
        item_data = fillListTail(item_data, feature_length, 0)
        data_matrix.append(item_data)
        labels_matrix.append(labels)
    return data_matrix, labels_matrix
