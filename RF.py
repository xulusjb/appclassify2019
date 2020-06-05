import numpy as np
from scipy.stats import kurtosis, skew
from sklearn import preprocessing
from sklearn import svm
from sklearn import tree
from sklearn import neighbors
from sklearn import linear_model
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
import random
import time
import random

SAMPLE= 500
#SAMPLETEST = 50
marco = 3000
cate_num = 2
if cate_num == 2:
        #category_list = ['a','f','i','r','s','so','t','w','email','vpn_email','p2p','vpn_p2p']
        #category_list = ['origin', 'riot', 'apple', 'msn', 'microsoft', 'xbox', 'spotify', 'qq', 'slack', 'leagueoflegends','steam','skype' \  <----25 app
        #,'facebook', 'netflix', 'cloudfront', 'epic', 'google', 'icloud', 'adobe', 'battle', 'twitter', 'roblox', 'discord', 'bilibili', 'nvidia']
        category_list = ['origin', 'riot', 'apple', 'msn', 'microsoft', 'xbox', 'spotify', 'qq', 'slack', 'leagueoflegends','steam','skype'   # <--23 app \
        ,'facebook', 'cloudfront', 'google', 'icloud', 'adobe', 'battle', 'twitter', 'roblox', 'discord', 'bilibili', 'nvidia']
        #category_list = ['origin', 'msn', 'xbox',  'slack' , 'cloudfront', 'icloud', 'battle', 'twitter',  'discord',  'nvidia']  #<-------------95%
        
        #category_list = ['riot', 'apple', 'microsoft', 'spotify', 'qq', 'leagueoflegends','steam','skype', 'facebook', 'google', 'adobe', 'roblox', 'bilibili']  # < -------------70%
        #category_list =  ['origin', 'msn', 'cloudfront', 'twitter',  'nvidia','apple','adobe']
        #ilist = random.sample(range(0, 23), 10)
        #tlist = []
        #for item in ilist:
        #	tlist.append(category_list[item])
        #print(tlist)
        #category_list = tlist
        print("len of category:", len(category_list))
else:
        category_list = ['g','gc','gd','gdr','gf','tb','tr','y']
para_label = 'px'

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
                        break
                nums = line.split(" ")
                if len(nums) > 1:
                        truenums = [int(i) for i in nums]
                        #rescale the first 19 interval time
                        #intval_list = truenums[0:packetlength]
                        #rescaled_intval_list = [int(float(i) *255 / 100000) for i in truenums[0:packetlength]]
                        #truenums = rescaled_intval_list+ truenums[packetlength:marco]
                        if len(truenums) < marco:
                                truenums = truenums+([0] * (marco - len(truenums) + 1))
                        #avg = int(np.average(truenums))
                        #mean = int(np.mean(truenums))
                        #median = int(np.median(truenums))
                        #var = int(np.var(truenums))
                        #std = int(np.std(truenums))
                        #zerocount = truenums.count(0)
                        #seventy = np.percentile(truenums, 75)
                        #twenty = np.percentile(truenums, 25)
                        #skewness = abs(int(skew(truenums)*200))
                        #kurto = abs(int(kurtosis(truenums)*200))
                        #statlist = [avg, mean,median,std,zerocount,seventy,twenty,skewness,kurto]
                        #truenums = truenums+statlist
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
len_value=[3000]
value = [150]
print("n_estimators: ",value)
for i in len_value:
        print(i)
        #clf=RandomForestClassifier(n_estimators=i)
        clf=RandomForestClassifier( n_estimators = 200)
        #clf = svm.SVC()
        #clf = neighbors.KNeighborsClassifier()
        #clf = tree.DecisionTreeClassifier(max_depth=20, criterion='entropy',max_leaf_nodes=50)
        #clf = GaussianNB()
        #clf=tree.DecisionTreeClassifier()
        #clf = linear_model.LogisticRegression()
        print(truetrainX)
        print(truetrainX.shape)
        clf.fit(truetrainX[:,:i],truetrainY)
        a = time.time()
        predY = clf.predict(truetestX[:,:i])
        b = time.time()

        accuracy = metrics.accuracy_score(truetestY, predY)
        result.append(accuracy)
        
        # Extract single tree
        print("tree depth:.........",[estimator.tree_.max_depth for estimator in clf.estimators_])
        # Export as dot file

        # Convert to png using system command (requires Graphviz)
        print(confusion_matrix(truetestY, predY))
        print("   {0}  {1}".format("  ".join([str(i) for i in range(0,10)]), " ".join(str(i) for i in range(10,24))))
        #predX = clf.predict(truetrainX[:,:i])
        #print(confusion_matrix(truetrainY, predX))
        print("time used:",b-a)
        print("avg time used:",(b-a)/len(truetestX))
        print("accuracy: ", accuracy)
        print("precision: ", precision_score(truetestY, predY, average='micro'))
        print("recall: ", recall_score(truetestY, predY, average='micro'))
        print("F1 score: ",  f1_score(truetestY, predY, average='micro'))

print(len_value)
print(result)

import cPickle
# save the classifier
with open('my_dumped_classifier.pkl', 'wb') as fid:
    cPickle.dump(clf, fid)    
