#%%
import pandas as pd
import numpy as np

import scipy.sparse
import sklearn.feature_extraction

import matplotlib.pylab as plt

from tqdm import tqdm
import platform

pd.set_option("display.max_rows", 10)
pd.set_option('display.max_columns', 1100)

import os

#%%

print(platform.processor())
print('cpu\t\t: {}'.format(os.cpu_count()))

from logParser import ParseLogsFromFolder

main_data, values_data, order_data = ParseLogsFromFolder('Logs/', 10, only_order=False)

main = pd.DataFrame(main_data)
#del(main_data)

print('Хэдэры первых 100 юзер-агентов составляют: {:.2%}'.format(
    main.User_Agent.value_counts()[:100].sum() / main.shape[0]))

main_top_100 = main[main.User_Agent.isin(main.User_Agent.value_counts()[:100].index.tolist())]

orders_vectorizer = sklearn.feature_extraction.DictVectorizer(sparse=True, dtype=float)
sparse_orders = orders_vectorizer.fit_transform(order_data).astype(np.int8)
del(order_data)
print('Sparse orders: \n{0}'.format(sparse_orders[:3]))
print(type(sparse_orders))

print('Sparse orders: \n{0}'.format(sparse_orders[:6]))

sparse_orders_top_100 = sparse_orders[main_top_100.index]

#%%
from itertools import combinations

pairs_dict_list = []
for row_index in tqdm(range(sparse_orders_top_100.shape[0]), mininterval=2):
    pairs_dict = {}
    for pair_first, pair_second in combinations(sparse_orders_top_100[row_index].indices, 2):
        name_first = orders_vectorizer.feature_names_[pair_first]
        name_second = orders_vectorizer.feature_names_[pair_second]
        if sparse_orders_top_100[row_index, pair_first] < sparse_orders_top_100[row_index, pair_second]:
            pairs_dict['{0} < {1}'.format(name_first, name_second)] = 1
        else:
            pairs_dict['{0} < {1}'.format(name_second, name_first)] = 1
    pairs_dict_list.append(pairs_dict)

dummy_vectorizer = sklearn.feature_extraction.DictVectorizer(sparse=True, dtype=float)
sparse_dummy = dummy_vectorizer.fit_transform(pairs_dict_list).astype(np.int8)
print('Sparse dummy: \n{0}'.format(sparse_dummy[:3]))
print(type(sparse_dummy))

#%%

from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split, KFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve, f1_score, make_scorer
from sklearn.multiclass import OneVsRestClassifier

y = main_top_100.User_Agent

X_train, X_test, y_train, y_test = train_test_split(sparse_dummy, y, test_size=0.33, random_state=42)

clf = OneVsRestClassifier(LogisticRegression(random_state=42), n_jobs=1)
clf.fit(X_train, y_train)

#%%
answer = clf.predict(X_test)