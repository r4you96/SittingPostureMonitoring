# Version 1.11
# ADL Classification Comparison for Classical Machine Learning Algorithms
# SVM, kNN, Decision Tree, Random Forest, Multilayer Perceptron Classifier
# @==(^0^)@
# @(^0^)==@
# @==(^0^)@
# @(^0^)==@

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
import random

# Reset any remaining state
tf.keras.backend.clear_session()
# Load data
xy_data = pd.read_csv("C:\\Users\\Choi CheolWoo\\Downloads\\kinect_monitoring\\get_skeletal_all2.csv")
# 첫번째 칼럼(분류의 값)만 제외하고 모든 것을 칼럼별로 Nomalize함
# 분류를 나타내는 첫번째 칼럼은 분류의 값으로 남겨둠
#xy_data.iloc[:,1:] = (xy_data.iloc[:,1:]-xy_data.iloc[:,1:].min()) / (xy_data.iloc[:,1:].max() - xy_data.iloc[:,1:].min())

# Parameters
split_rate = 0.7    # ratio of training and testing set (test the best value)

# Extract features to use and the classification data
xt = xy_data.iloc[:, 1:70].values
yt = xy_data.iloc[:, 0].values

# Suffle the data to increase reliability
shuffle = [[x, y] for x, y in zip(xt, yt)]
#random.shuffle(shuffle)
x_data = [n[0] for n in shuffle]
y_data = [n[1] for n in shuffle]
# Without suffling
#x_data=xt
#y_data=yt

# Splitting the dataset into the Training set and Test set
X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, test_size = split_rate, random_state = 0)

# plot the accuracy results
def plotting(accs, params, label):
    ind = np.arange(len(accs))      # the x locations for the groups
    width = 0.35                    # the width of the bars

    _, ax = plt.subplots()
    rects = ax.bar(ind, accs, width, color='b')
    ax.set_ylabel('accuracy')
    #ax.set_title('Accuracies by ' + label)
    ax.set_xticks(ind)
    ax.set_xticklabels(params)

    # find the max accuracy
    max_index=np.argmax(accs)
    max=accs[max_index]

    for rect in rects:
        height = rect.get_height()
        if height==max:
            rect.set_color('red')
            ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                    '%f' % height,
                    ha='center', va='bottom', color='red')
        else:
            ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                    '%f' % height,
                    ha='center', va='bottom', color='blue')



    plt.show()
    print('Best Result = ' + label + ' : ', params[max_index], ' accuracy : ', accs[max_index])

# list to hold results
accs = []
params = ['SVM', 'kNN', 'DT', 'RF', 'MLP', 'XGB']

# train the model for each model
from sklearn import metrics

# 1. SVM Classifier
from sklearn.svm import SVC
svclassifier = SVC(decision_function_shape='ovo',kernel='linear')
svclassifier.fit(X_train, y_train)
y_pred = svclassifier.predict(X_test)
acc=metrics.accuracy_score(y_test, y_pred)
accs.append(acc)

# 2. kNN Classifier
# import the kNN class from scikit-learn
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors= 4)      # Best result acquired with 10
knn.fit(X_train, y_train)
y_pred=knn.predict(X_test)
acc=metrics.accuracy_score(y_test, y_pred)
accs.append(acc)

# 3. Decision Tree Classifier
from sklearn import tree
# Train the DT model
d_tree = tree.DecisionTreeClassifier(criterion='entropy', random_state=0)
d_tree.fit(X_train, y_train)
# Predict the results
y_pred=d_tree.predict(X_test)
acc=metrics.accuracy_score(y_test, y_pred)
accs.append(acc)

# 4. Random Forest Classifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
# Train the RF model
rf = RandomForestClassifier(n_estimators=300)
rf.fit(X_train, y_train)
# Predict the results
y_pred=rf.predict(X_test)
acc=metrics.accuracy_score(y_test, y_pred)
accs.append(acc)

# 5. Multi Layer Perceptron Classifier
from sklearn.neural_network import MLPClassifier
# Train the RF model
mlp = MLPClassifier(hidden_layer_sizes=1000)
mlp.fit(X_train, y_train)
# Predict the results
y_pred=rf.predict(X_test)
acc=metrics.accuracy_score(y_test, y_pred)
accs.append(acc)

# 6. Extreme Gradient Boost
from xgboost import XGBClassifier
xgb = XGBClassifier(n_estimators = 300)

# 7. Extreme Learning Machine
#from sklearn_extensions.extreme_learning_machines import ELMClassifier


X_train = np.array(X_train)
X_test = np.array(X_test)

xgb.fit(X_train, y_train)
y_pred = xgb.predict(X_test)
acc = metrics.accuracy_score(y_test,y_pred)
accs.append(acc)

plotting(accs, params, 'classifier')
