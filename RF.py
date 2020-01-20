import numpy as np
from sklearn import preprocessing
from sklearn import svm
from sklearn import tree
from sklearn import neighbors
from sklearn import linear_model
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn import metrics
from sklearn.model_selection import train_test_split
import random
import time
SAMPLE= 40
SAMPLETEST = 50
marco = 8019
cate_num = 2
if cate_num == 2:
        category_list = ['a','f','i','r','s','so','t','w']
else:
        category_list = ['g','gc','gd','gdr','gf','tb','tr','y']
para_label = 'pi'

#loaddata
packetlength = 19
X = []
Y = []
for cate in category_list:
        resample_index = 0

        file_name = cate+"_"+para_label+".txt"
        print(file_name)
        with open(file_name, "r") as rfile:
                s = rfile.read()
        for line in s.split("\n"):
                if resample_index > SAMPLE:
                        continue
                nums = line.split(" ")
                if len(nums) > 1:
                        truenums = [int(i) for i in nums]
                        #rescale the first 19 interval time
                        intval_list = truenums[0:packetlength]
                        rescaled_intval_list = [int(float(i) *255 / 100000) for i in truenums[0:packetlength]]
                        truenums = rescaled_intval_list+ truenums[packetlength:marco]
                        X.append(truenums[0:marco])
                        resample_index += 1
                        Y.append(category_list.index(cate))
X = np.asarray(X)
Y = np.asarray(Y)

truetrainX, truetestX, truetrainY, truetestY = train_test_split(X, Y, test_size=0.1, random_state=42)

result  = []
#for i in range(10,300,30):
#       value.append(i)
#len_value=[50,500,1000,1500,3000,4000,8000]
len_value=[8000]
value = [150]
print("n_estimators: ",value)
for i in len_value:
        print(i)
        #clf=RandomForestClassifier(n_estimators=i)
        #clf=RandomForestClassifier()
        #clf = svm.SVC()
        #clf = neighbors.KNeighborsClassifier()
        #clf = tree.DecisionTreeClassifier(max_depth=20, criterion='entropy',max_leaf_nodes=50)
        clf=tree.DecisionTreeClassifier()
        #clf = linear_model.LogisticRegression()
        clf.fit(truetrainX[:,:i],truetrainY)
        predY = clf.predict(truetestX[:,:i])
        accuracy = metrics.accuracy_score(truetestY, predY)
        result.append(accuracy)
        #print("accuracy: ", accuracy)
        #print(confusion_matrix(truetestY, predY))
        #predX = clf.predict(truetrainX[:,:i])
        #print(confusion_matrix(truetrainY, predX))
print(len_value)
print(result)