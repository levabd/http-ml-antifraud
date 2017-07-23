# coding=utf-8

import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import os 


def LineHandler(line):
    elements = line.split(',', 2)
    main_row = {'id': elements[0], 'ip': elements[1]}
    value_row = {}
    ordered_row = {}
    if bool(elements[2] and elements[2].strip()):
        try:
            value_row.update(json.loads(elements[2].translate(str.maketrans("'", "\n"))))
            order = -2 # ip and id
            for header, val in value_row.items():
                order += 1
                if order > 0: ordered_row.update({header: order})
            main_row['User_Agent'] = value_row['User-Agent']
        except:
            pass
    return main_row, value_row, ordered_row


def ParseSingleLog(path_to_log):
    with open (path_to_log, 'r') as input_stream:
        main_table = []
        value_table = []
        ordered_table = []
        for line in input_stream:
            # !!! i'm not sure in this
            # line = line.lower()
            main_row, value_row, ordered_row = LineHandler(line)
            main_table.append(main_row)
            value_table.append(value_row) 
            ordered_table.append(ordered_row)
    return main_table, value_table, ordered_table


def ParseLogsFromFolder(folder_path, log_index_begin=0, log_index_end=0,  only_order=False):
    main_table = []
    value_table = []
    order_table = []
    read_counter = 0
    for file_in_folder in tqdm(os.listdir(path=folder_path), mininterval=2):
        if read_counter < log_index_begin:
            read_counter += 1
            continue
        if read_counter >= log_index_end:
            return main_table, value_table, order_table
        if '.log' in file_in_folder: 
            main_sample, value_sample, order_sample = ParseSingleLog(folder_path + file_in_folder)
            if not only_order:
                value_table.extend(value_sample)
            order_table.extend(order_sample)
            main_table.extend(main_sample)
            read_counter += 1
    return main_table, value_table, order_table 


def GetBotSample(distr_log_index_begin, distr_log_index_end, 
                 base_log_index_begin, base_log_index_end):
    """
    :param distr_log_index_begin: Логи для распределения юзерагентов (стартовый номер лога)
    :param distr_log_index_end: Логи для распределения юзерагентов (конечый номер лога)
    :param base_log_index_begin: Логи для генерации ботов (стартовый номер лога)
    :param base_log_index_end: Логи для генерации ботов (конечый номер лога)
    :return: main DataFrame, values DataFrame, order DataFrame
    """
    main_data, _, _ = ParseLogsFromFolder(
        'Logs/', distr_log_index_begin, distr_log_index_end, only_order=False)
    df = pd.DataFrame(main_data)
    del(main_data)
    distribution_frame = df.User_Agent.value_counts() / df.shape[0] 
    cumulative_frame = np.cumsum(distribution_frame)
    
    main_data, values_data, order_data = ParseLogsFromFolder(
        'Logs/', base_log_index_begin, base_log_index_end, only_order=False)
    main_df = pd.DataFrame(main_data)
    
    sample_user_agents = []
    norm_koef = distribution_frame.sum()
    for sample_index in range(main_df.shape[0]):
        uniform_value = np.random.rand() * norm_koef 
        sample_user_agents.append(
            distribution_frame[cumulative_frame > uniform_value].index[0])
    sample_user_agents = pd.Series(sample_user_agents)
    
    main_df.User_Agent = sample_user_agents
    
    return main_df, values_data, order_data
