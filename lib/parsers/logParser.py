#!/usr/bin/env python

import json
import os
import time
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.sparse import hstack
from tqdm import tqdm

from lib.parsers.udgerWrapper import is_crawler, get_ua


class LogParser:
    """
    Prepare data for learning
    """

    def __init__(self, log_folder):
        """
        :param log_folder: Log folder
        """
        self.__log_folder = log_folder
        self.__main_table = []
        self.__value_table = []
        self.__order_table = []

    @staticmethod
    def __line_handler(line, filter_crawlers, parse_ua, start_log_time, finish_log_time):
        elements = line.split(',', 2)

        if int(elements[0]) < start_log_time or int(elements[0]) > finish_log_time:
            return False

        if filter_crawlers:
            if not elements[1]:
                return False
            else:
                if is_crawler(elements[1]):  # client ip
                    return False

        main_row = {'timestamp': elements[0], 'ip': elements[1]}
        value_row = {}
        ordered_row = {}
        if bool(elements[2] and elements[2].strip()):
            # noinspection PyBroadException
            try:
                value_row.update(json.loads(elements[2].translate(str.maketrans("'", "\n"))))
                order = -2  # ip and timestamp
                for header, _ in value_row.items():
                    order += 1
                    if order > 0:
                        ordered_row.update({header: order})
                if not parse_ua:
                    main_row['User_Agent'] = value_row['User-Agent']
                else:
                    ua_obj = get_ua(value_row['User-Agent'])
                    main_row = {
                        'timestamp': elements[0],
                        'ip': elements[1],
                        'ua_family_code': ua_obj['ua_family_code'],
                        'ua_version': ua_obj['ua_version'],
                        'ua_class_code': ua_obj['ua_class_code'],
                        'device_class_code': ua_obj['device_class_code'],
                        'os_family_code': ua_obj['os_family_code'],
                        'os_code': ua_obj['os_code']
                    }
            except:
                pass
        return main_row, value_row, ordered_row

    def __parse_single_log(self, path_to_log, filter_crawlers, parse_ua, start_log_time, finish_log_time):
        with open(path_to_log, 'r') as input_stream:
            main_table = []
            value_table = []
            ordered_table = []
            for line in input_stream:
                line = self.__line_handler(line, filter_crawlers, parse_ua, start_log_time, finish_log_time)
                if line:
                    main_row, value_row, ordered_row = line
                    main_table.append(main_row)
                    value_table.append(value_row)
                    ordered_table.append(ordered_row)
        return main_table, value_table, ordered_table

    def __parse_logs_from_folder(self, start_log_index, finish_log_index, filter_crawlers, parse_ua,
                                 start_log_time=0, finish_log_time=time.time()):
        files_in_folder = os.listdir(path=self.__log_folder)
        if finish_log_index > len(files_in_folder) - 1:
            finish_log_index = len(files_in_folder) - 1
        for i in tqdm(range(start_log_index, finish_log_index)):
            if '.log' in files_in_folder[i]:
                main_sample, value_sample, order_sample = self.__parse_single_log(
                    self.__log_folder + files_in_folder[i], filter_crawlers, parse_ua, start_log_time, finish_log_time)
                self.__value_table.extend(value_sample)
                self.__order_table.extend(order_sample)
                self.__main_table.extend(main_sample)

        return self.__main_table, self.__value_table, self.__order_table

    def parse_train_sample(self, start_log_index=0, finish_log_index=1,
                           filter_crawlers=False, parse_ua=False):
        """
        :param start_log_index: started index
        :param finish_log_index: started index
        :param filter_crawlers: Use crawler filter udger.com
        :param parse_ua: Parse user agent. Main Table will contain tuple rather than the value
        :return: tuple main_table, value_table, order_table
        """
        self.__parse_logs_from_folder(start_log_index, finish_log_index, filter_crawlers, parse_ua)
        return self.__main_table, self.__value_table, self.__order_table

    def parse_train_sample_by_time(self, start_log_time=0, finish_log_time=time.time(),
                                   filter_crawlers=False, parse_ua=False):
        """
        :param start_log_time: down limit for log timestamp
        :param finish_log_time: upper limit for log timestamp
        :param filter_crawlers: Use crawler filter udger.com
        :param parse_ua: Parse user agent. Main Table will contain tuple rather than the value
        :return: tuple main_table, value_table, order_table
        """
        self.__parse_logs_from_folder(0, 10000, filter_crawlers, parse_ua, start_log_time, finish_log_time)
        return self.__main_table, self.__value_table, self.__order_table

    def parse_bot_sample(self, distr_start_log_index, distr_finish_log_index, base_start_log_index,
                         base_finish_log_index, filter_crawlers=False, parse_ua=False):
        """
        :param distr_start_log_index: started distribution logs index
        :param distr_finish_log_index: end of distribution logs index
        :param base_start_log_index: started values logs index
        :param base_finish_log_index: end of values logs index
        :param filter_crawlers: Use crawler filter udger.com
        :param parse_ua: Parse user agent. Main table will contain tuple rather than the value
        :return: tuple main_table, value_table, order_table
        """
        print('Start parsing logs for distribution')
        main_data, _, _ = self.__parse_logs_from_folder(distr_start_log_index, distr_finish_log_index,
                                                        filter_crawlers, parse_ua)
        main_frame = pd.DataFrame(main_data)
        distribution_frame = main_frame.User_Agent.value_counts() / main_frame.shape[0]
        cumulative_frame = np.cumsum(distribution_frame)

        print('Start parsing logs for values')
        main_data, self.__value_table, self.__order_table = self.__parse_logs_from_folder(
            base_start_log_index, base_finish_log_index, filter_crawlers, parse_ua)
        self.__main_table = pd.DataFrame(main_data)

        sample_user_agents = []
        norm_coefficient = distribution_frame.sum()
        print('Bots Generation')
        for _ in tqdm(range(self.__main_table.shape[0])):
            uniform_value = np.random.rand() * norm_coefficient
            sample_user_agents.append(
                distribution_frame[cumulative_frame > uniform_value].index[0])
        sample_user_agents = pd.Series(sample_user_agents)

        self.__main_table.User_Agent = sample_user_agents

        return self.__main_table, self.__value_table, self.__order_table

    def reassign_orders_values(self, order_data, values_data):
        """
        :param order_data: key orders for header
        :param values_data: key values for header
        """
        self.__order_table = order_data
        self.__value_table = values_data

        return True

    def prepare_data(self, orders_vectorizer, values_vectorizer, important_orders_keys_set,
                     important_values_keys_set, fit_dict=False, pca=None, fit_pca=False):
        """
        :param orders_vectorizer: feature_extraction.DictVectorizer for order_data
        :param values_vectorizer: feature_extraction.DictVectorizer for values_data
        :param important_keys_set: set of important keys
        :param fit_dict: fit or not to fit dict vectorizers
        :param pca: data reduction by PCA. Do not use by default
        :param fit_pca: fit or not to fit PCA
        :return: sparce matrix with ordered and value features
        """
        trimmed_orders_data = []

        for row_index in tqdm(range(len(self.__order_table))):
            tmp_row = {}
            for key in important_orders_keys_set:
                if key in self.__order_table[row_index]:
                    tmp_row[key] = self.__order_table[row_index][key]
            trimmed_orders_data.append(tmp_row)

        pairs_dict_list = []
        for row_idx in tqdm(range(len(trimmed_orders_data)), mininterval=2):
            pairs_dict = {}
            for first_p, second_p in combinations(trimmed_orders_data[row_idx], 2):
                if trimmed_orders_data[row_idx][first_p] < trimmed_orders_data[row_idx][second_p]:
                    pairs_dict['{0} < {1}'.format(first_p, second_p)] = 1
                else:
                    pairs_dict['{0} < {1}'.format(second_p, first_p)] = 1
            pairs_dict_list.append(pairs_dict)


        if fit_dict:
            orders_vectorizer.fit(pairs_dict_list)
        sparse_dummy = orders_vectorizer.transform(pairs_dict_list).astype(np.int8)

        if not (pca is None):
            if fit_pca:
                pca.fit(sparse_dummy)
            pairs_dict_list = pca.transform(sparse_dummy)

        print('Sparse dummy orders shape: \n{0}'.format(sparse_dummy.shape))

        trimmed_values_data = []

        for row_index in tqdm(range(len(self.__value_table))):
            tmp_row = {}
            for key in important_values_keys_set:
                if key in self.__value_table[row_index]:
                    tmp_row[key] = self.__value_table[row_index][key]
            trimmed_values_data.append(tmp_row)

        if fit_dict:
            values_vectorizer.fit(trimmed_values_data)
        sparse_dummy_values = values_vectorizer.transform(trimmed_values_data).astype(np.int8)

        print('Sparse dummy values shape: \n{0}'.format(sparse_dummy_values.shape))

        return hstack((sparse_dummy, sparse_dummy_values))
