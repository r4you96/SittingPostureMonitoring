import tensorflow as tf
from numpy import *
import numpy as np
from sklearn import svm
from sklearn.preprocessing import OneHotEncoder
from sklearn import datasets
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import pickle
import joblib
if __name__ == "__main__":
    get_file = "C:\\Users\\Choi CheolWoo\\Downloads\\kinect_monitoring\\get_skeletal_all2.csv"
    test = np.loadtxt(get_file, delimiter=',', dtype=np.float32)
    #맨 처음 원소인 인덱스와 1~31번까지 총 30개의 원소를 추출 분리
    index = test[:, :1]
    x_data = test[:, 34:70]
    #x_data = test[:, 1:18 , 34:40]

    data_num = [0, 0, 0, 0, 0]
    # check data
    for i in range(len(index)):
        now_index = int(index[i]) - 1
        data_num[now_index] = data_num[now_index] + 1

    for i in range(len(data_num)):
        print("%d 번째 데이터의 갯수는 : %d" % (i, data_num[i]))

    re_index = np.reshape(index, (1, size(index)))
    re_index = re_index[0]

    y_test, y_train, x_test, x_train = train_test_split(re_index, x_data, test_size=0.3, shuffle= True)

    #rbf, poly, linear
    model = svm.SVC(decision_function_shape='ovo', kernel= "linear")
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    print(y_pred)
    acc = metrics.accuracy_score(y_test ,y_pred)
    print(acc)

    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred, digits=4))

    saved_model = pickle.dumps(model)
    joblib.dump(model, 'saved_model.pkl')


