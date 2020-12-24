import numpy as np
from xgboost import XGBClassifier
from xgboost import plot_importance
from sklearn.model_selection import GridSearchCV
from matplotlib import pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import random
import pandas as pd

xy_data = pd.read_csv("C:\\Users\\Choi CheolWoo\\Downloads\\get_skeletal.csv",delimiter=',', dtype=np.float32)

# call data
xt = xy_data.iloc[:, 1:70].values
yt = xy_data.iloc[:, 0].values

shuffle = [[x, y] for x, y in zip(xt, yt)]
random.shuffle(shuffle)
x_data = [n[0] for n in shuffle]
y_data = [n[1] for n in shuffle]

# xgb hparmas
num_classes = 5     # number of class
num_estimators = 300      # num of models in RF (test the best value)
learning_rate = 0.1
max_depth = 1000000
num_features = len(xt[0])   # number of features
es_rounds = 10

# data params
split_rate = 0.3    # ratio of training and testing set (test the best value)

X_train, X_test, Y_train, Y_test = train_test_split(x_data, y_data, test_size = split_rate, random_state = 10)
X_train = np.array(X_train)
X_test = np.array(X_test)

# xgb classifier initiation
xgb = XGBClassifier(n_estimators = num_estimators, learning_rate = learning_rate, max_depth=max_depth)
xgb.fit(X_train, Y_train)

outputs = xgb.predict(X_test)
print(confusion_matrix(Y_test, outputs))
print(classification_report(Y_test, outputs))

# xgb classifier statics
'''
xgb_param_grid ={
    'n_estimators' : [300, 350 ,400,450, 500,550, 600, 650],
    'max_depth' :  [20, 25, 30, 35, 40, 45, 50, 55,]
}

xgb_grid = GridSearchCV(xgb, param_grid = xgb_param_grid, scoring="accuracy", n_jobs= -1, verbose =1 )
xgb_grid.fit(X_train, Y_train)

print("best mean acc : {0:.4f}".format(xgb_grid.best_score_))
print("best params : ", xgb_grid.best_params_)
'''

fig, ax = plt.subplots()
plot_importance(xgb, ax=ax)
plt.show()