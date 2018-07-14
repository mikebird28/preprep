import pandas as pd
import json
import os

KEY_INDEX_NAME = "index_name"
KEY_INDEX_FLAG = "index_flag"

def df_to_csv(df,path):
    info = {}
    #index name
    index_name = df.index.name
    #True if index name is "index"
    index_flag = False

    if index_name is "index":
        index_flag = True
    if index_name is None:
        index_name = "index"

    info[KEY_INDEX_NAME] = index_name
    info[KEY_INDEX_FLAG] = index_flag

    #save df and info
    df = df.reset_index()
    df.to_csv(path,index = False)
    info_path = get_info_path(path)
    save_info(info,info_path)

def csv_to_df(path):
    info_path = get_info_path(path)
    info = load_info(info_path)

    index_name = info[KEY_INDEX_NAME]
    index_flag = info[KEY_INDEX_FLAG]

    if "index_name" in info:
        df = pd.read_csv(path)
        df = df.set_index(index_name)
        if not index_flag:
            df.index.name = None
    else:
        df = pd.read_csv(path)
    return df

def df_to_feather(df,path):
    info = {}
    #index name
    index_name = df.index.name
    #True if index name is "index"
    index_flag = False

    if index_name is "index":
        index_flag = True
    if index_name is None:
        index_name = "index"

    info[KEY_INDEX_NAME] = index_name
    info[KEY_INDEX_FLAG] = index_flag

    #save df and info
    df = df.reset_index()
    df.to_feather(path)
    info_path = get_info_path(path)
    save_info(info,info_path)

def feather_to_df(path):
    info_path = get_info_path(path)
    info = load_info(info_path)

    index_name = info[KEY_INDEX_NAME]
    index_flag = info[KEY_INDEX_FLAG]

    if "index_name" in info:
        df = pd.read_feather(path)
        df = df.set_index(index_name)
        if not index_flag:
            df.index.name = None
    else:
        df = pd.read_feather(path)
    return df

def save_info(info,path):
    with open(path,"w") as fp:
        json.dump(info,fp)

def load_info(path):
    if not os.path.exists(path):
        return {}
    with open(path) as fp:
        info = json.load(fp)
    return info

def get_info_path(raw_path):
    root,ext = os.path.splitext(raw_path)
    filename = root + ".json"
    return filename
