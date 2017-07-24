#!/usr/bin/env python

import pandas as pd


class ThresholdPredictions:
    """
    Multilabel prediction methods based on predict pragma vector and threshold
    """

    def __init__(self, user_agent_list):
        """
        :param user_agent_list: User Agent list for classification
        """
        self.__top_ua = user_agent_list

    def return_ua(self, index):
        """
        :param index: Class index
        :return: User Agent label for class
        """
        return self.__top_ua[index]

    def return_prediction_ua(self, predictions):
        """
        :param predictions: prediction vector
        :return: User Agent label for prediction vector
        """
        for i, label in enumerate(predictions):
            if label == 1:
                return self.return_ua(i)

    def return_thresolded_prediction_ua(self, predictions, alpha):
        """
        :param predictions: prediction vector
        :param alpha: prediction vector
        :return: User Agent label for prediction vector
        """
        ua_list = []
        for i, proba in enumerate(predictions):
            if proba > alpha:
                ua_list.append(self.return_ua(i))
        return ua_list

    def smart_prediction(self, clf, x_test, y_test, alpha):
        """
        :param clf: Classifyer
        :param x_test: X test sample
        :param y_test: y test sample
        :param alpha: Threshold
        :return: list of list true User Agent names from test sample, list of list Predicted 
                 User Agent, list of bool true if at least one predicted User Agent equal 
                 true User Agent, list of answer count
        """
        predictions_proba = clf.predict_proba(x_test)

        y_test_names = pd.DataFrame(y_test).apply(
            lambda l: self.return_prediction_ua(l), axis=1)
        y_predicted = pd.DataFrame(predictions_proba).apply(
            lambda l: self.return_thresolded_prediction_ua(l, alpha), axis=1)

        compare_answers = []
        answers_count = []
        for i, y_tst in enumerate(y_test_names):
            current_answer = True
            if y_tst not in y_predicted[i]:
                current_answer = False
            compare_answers.append(current_answer)
            answers_count.append(len(y_predicted[i]))

        return y_test_names, y_predicted, compare_answers, answers_count

    @staticmethod
    def score(alpha, y, y_cross_val):
    	"""
    	:param alpha: Threshold
    	:param y: y sample
    	:param y_cross_val: y from cross_val_predict
    	:return: true if at least one predicted User Agent equal true User Agent
    	"""
    	correct_answers = 0
    	answers_count = []
    	for i, y_labels in enumerate(y):
    	    for j, y_answ in enumerate(y_labels):
            	answers_count.append(np.count_nonzero(y_cross_val[i] > alpha))
            	if (y_answ == 1) and (y_cross_val[i][j] > alpha):
                    correct_answers += 1

    	return correct_answers / len(y), np.average(answers_count)

