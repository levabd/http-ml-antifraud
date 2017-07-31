#!/usr/bin/env python

import psutil
import pandas as pd
import numpy as np
from tqdm import tqdm


class ThresholdPredictions:
    """
    Multilabel prediction methods based on predict pragma vector and threshold
    """

    def __init__(self, user_agent_list, clf = None):
        """
        :param user_agent_list: User Agent list for classification
        :param clf: Classifier
        """
        self.__ua = user_agent_list
        self.__clf = clf

    def return_ua(self, index):
        """
        :param index: Class index
        :return: User Agent label for class
        """
        return self.__ua[index]

    def return_prediction_ua(self, predictions):
        """
        :param predictions: prediction vector
        :return: User Agent label for prediction vector
        """
        for i, label in enumerate(predictions):
            if label == 1:
                return self.return_ua(i)

    def return_thresholded_prediction_ua(self, predictions, alpha):
        """
        :param predictions: prediction vector
        :param alpha: threshold
        :return: User Agent label for prediction vector
        """
        ua_list = []
        for i, proba in enumerate(predictions):
            if proba > alpha:
                ua_list.append(self.return_ua(i))
        return ua_list

    def predict(self, x_test, y_test, alpha, memory_warn=True):
        """
        :param x_test: X test sample
        :param y_test: y test sample
        :param alpha: Threshold
	    :param memory_warn: If True doesn`t start calculation if memory not enougth
        :return: frame of true User Agent names from test sample, frame of list Predicted 
                 User Agent, list of bool true if at least one predicted User Agent equal 
                 true User Agent, list of answer count
        """
        mem = psutil.virtual_memory()
        if (x_test.shape[0] * len(self.__ua) * 8 > mem.free) and memory_warn:
            print("Not enought memory for predict proba calculation")
            return False

        predictions_proba = self.__clf.predict_proba(x_test)

        y_test_names = pd.DataFrame(y_test).apply(
            lambda l: self.return_prediction_ua(l), axis=1)
        y_predicted = pd.DataFrame(predictions_proba).apply(
            lambda l: self.return_thresholded_prediction_ua(l, alpha), axis=1)

        compare_answers = []
        answers_count = []
        for i, y_tst in tqdm(enumerate(y_test_names)):
            current_answer = True
            if y_tst not in y_predicted[i]:
                current_answer = False
            compare_answers.append(current_answer)
            answers_count.append(len(y_predicted[i]))

        return y_test_names, y_predicted, compare_answers, answers_count

    def bot_predict(self, label_binarizer_test, x_test, y_test, alpha, memory_warn=True):
        """
        :param label_binarizer: label binarizer for y_test
        :param x_test: X test sample
        :param y_test: y test sample
        :param alpha: Threshold
        :param memory_warn: If True doesn`t start calculation if memory not enougth
        :return: frame of true User Agent names from test sample, frame of list Predicted
                 User Agent, list of bool true if at least one predicted User Agent equal
                 true User Agent, list of bot answer, list of answer count
        """
        mem = psutil.virtual_memory()
        if (x_test.shape[0] * len(self.__ua) * 8 > mem.free) and memory_warn:
            print("Not enought memory for predict proba calculation")
            return False

        predictions_proba = self.__clf.predict_proba(x_test)

        y_test_names = label_binarizer_test.inverse_transform(y_test)
        y_predicted = pd.DataFrame(predictions_proba).apply(
            lambda l: self.return_thresholded_prediction_ua(l, alpha), axis=1)

        compare_answers = []
        answers_count = []
        is_bot = []
        for i, y_tst in tqdm(enumerate(y_test_names)):
            current_answer = True
            current_is_bot = False
            if y_tst not in y_predicted[i]:
                current_answer = False
                current_is_bot = True
            # Header isn't bot if User Agent not yet met
            if y_tst not in self.__ua:
                current_is_bot = None
            is_bot.append(current_is_bot)
            compare_answers.append(current_answer)
            answers_count.append(len(y_predicted[i]))

        return y_test_names, y_predicted, compare_answers, is_bot, answers_count

    @staticmethod
    def score(alpha, y_sample, y_cross_val):
        """
        :param alpha: Threshold
        :param y_sample: y sample
        :param y_cross_val: y from cross_val_predict
        :return: true if at least one predicted User Agent equal true User Agent
        """
        correct_answers = 0
        answers_count = []
        for i, y_labels in tqdm(enumerate(y_sample)):
            for j, y_answer in enumerate(y_labels):
                answers_count.append(np.count_nonzero(y_cross_val[i] > alpha))
                if (y_answer == 1) and (y_cross_val[i][j] > alpha):
                    correct_answers += 1

        return correct_answers / len(y_sample), np.average(answers_count)
