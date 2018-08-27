import pandas as pd
import json
import os
import copy

KEY_INDEX_NAME = "index_name"
KEY_INDEX_FLAG = "index_flag"

def to_writable(df):
    df = df.copy()
    info = {}
    if isinstance(df.index,pd.MultiIndex):
        new_indexes = []
        is_none = []
        for i,f in enumerate(df.index.names):
            if f is None:
                #df.index.names[i] = "level_{}".format(i)
                new_indexes.append("level_{}".format(i))
                is_none.append(True)
            else:
                new_indexes.append(f)
                is_none.append(False)
        df.index.names = new_indexes
        info[KEY_INDEX_NAME] = copy.copy(df.index.names)
        info[KEY_INDEX_FLAG] = is_none
        df.reset_index(inplace = True)
        return df,info

    else:
        is_none = []
        if df.index.name is None:
            df.index.name = "index"
            is_none.append(True)
        else:
            is_none.append(False)

        info[KEY_INDEX_NAME] = [copy.copy(df.index.name)]
        info[KEY_INDEX_FLAG] = is_none
        df.reset_index(inplace = True)
        return df,info

def reconstruct_index(df,info):
    #in normal index case
    if len(info[KEY_INDEX_NAME]) == 1:
        df = df.set_index(info[KEY_INDEX_NAME][0])
        is_none = info[KEY_INDEX_FLAG][0]
        if is_none:
            df.index.name = None
        else:
            df.index.name = info[KEY_INDEX_NAME]
        return df
    #in multi index case
    else:
        df = df.set_index(info[KEY_INDEX_NAME])
        index_names = []
        for name,flag in zip(info[KEY_INDEX_NAME],info[KEY_INDEX_FLAG]):
            if flag:
                index_names.append(None)
            else:
                index_names.append(name)
        df.index.names = index_names
        return df

def df_to_csv(df,path):
    #save df and info
    df,info = to_writable(df)
    df.to_csv(path,index = False)
    info_path = get_info_path(path)
    save_info(info,info_path)

def csv_to_df(path):
    info_path = get_info_path(path)
    info = load_info(info_path)

    if "index_name" in info:
        df = pd.read_csv(path)
        df = reconstruct_index(df,info)
    else:
        df = pd.read_csv(path)
    return df

def df_to_feather(df,path):
    df,info = to_writable(df)
    df.to_feather(path)
    info_path = get_info_path(path)
    save_info(info,info_path)

def feather_to_df(path):
    info_path = get_info_path(path)
    info = load_info(info_path)

    if "index_name" in info:
        df = pd.read_feather(path)
        df = reconstruct_index(df,info)
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
