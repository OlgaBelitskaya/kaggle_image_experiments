# -*- coding: utf-8 -*-
"""classification-of-tomato-images.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YQUCsw0jqPT63AIv9z1-PQgMLTuHvBsa

## Code Modules & Functions
"""

import warnings; warnings.filterwarnings('ignore')
import pandas as pd,numpy as np,tensorflow as tf
import os,pylab as pl
from sklearn.metrics import accuracy_score,hamming_loss
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier as KNC
from sklearn.neural_network import MLPClassifier
from keras.preprocessing import image as kimage
from tqdm import tqdm
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES=True 
fpath='../input/tomato-cultivars/'

def path_to_tensor(img_path,fpath=fpath):
    img=kimage.load_img(fpath+img_path, 
                        target_size=(160,160))
    x=kimage.img_to_array(img)
    return np.expand_dims(x,axis=0)
def paths_to_tensor(img_paths):
    tensor_list=[path_to_tensor(img_path) 
                 for img_path in tqdm(img_paths)]
    return np.vstack(tensor_list)

"""## Data"""

names=['Kumato','Beefsteak','Tigerella',
       'Roma','Japanese Black Trifele',
       'Yellow Pear','Sun Gold','Green Zebra',
       'Cherokee Purple','Oxheart','Blue Berries']
flist=sorted(os.listdir(fpath))
labels=np.array([int(el[:2]) for el in flist],
               dtype='int32')-1
images=np.array(paths_to_tensor(flist),
                dtype='float32')/255
N=labels.shape[0]; n=int(.2*N)
shuffle_ids=np.arange(N)
np.random.RandomState(12).shuffle(shuffle_ids)
images,labels=images[shuffle_ids],labels[shuffle_ids]
x_test,x_train=images[:n],images[n:]
y_test,y_train=labels[:n],labels[n:]

pd.DataFrame([[x_train.shape,x_test.shape],
              [x_train.dtype,x_test.dtype],
              [y_train.shape,y_test.shape],
              [y_train.dtype,y_test.dtype]],               
             columns=['train','test'])

k=np.random.randint(40)
print('Label: ',y_test[k],
      names[y_test[k]])
pl.figure(figsize=(3,3))
pl.imshow((x_test[k]));

x_train=x_train.reshape(-1,160*160*3)
y_train=y_train.reshape(-1,1)
x_test=x_test.reshape(-1,160*160*3)
y_test=y_test.reshape(-1,1)

"""## Sklearn Classifiers"""

def classifier_fit_score(classifier,x_train,x_test,y_train,y_test):
    classifier.fit(x_train,y_train)     
    y_clf_train=classifier.predict(x_train)
    y_clf_test=classifier.predict(x_test)        
    acc_clf_train=round(accuracy_score(y_train,y_clf_train),4)
    acc_clf_test=round(accuracy_score(y_test,y_clf_test),4) 
    loss_clf_train=round(hamming_loss(y_train,y_clf_train),4)
    loss_clf_test=round(hamming_loss(y_test,y_clf_test),4)  
    return [y_clf_train,y_clf_test,acc_clf_train,acc_clf_test,
            loss_clf_train,loss_clf_test]

[y_rfc_train,y_rfc_test,acc_rfc_train,
 acc_rfc_test,loss_rfc_train,loss_rfc_test]=\
classifier_fit_score(RFC(),x_train,x_test,y_train,y_test)
print(classification_report(y_test,y_rfc_test))

[y_lsvc_train,y_lsvc_test,acc_lsvc_train,
 acc_lsvc_test,loss_lsvc_train,loss_lsvc_test]=\
classifier_fit_score(svm.LinearSVC(),
                     x_train,x_test,y_train,y_test)
print(classification_report(y_test,y_lsvc_test))

pl.figure(figsize=(10,5)); t=50; x=range(t)
pl.scatter(x,y_test[:t],marker='*',s=400,
           color='#ff355e',label='Real data')
pl.scatter(x,y_rfc_test[:t],marker='v',
           s=100,color='darkorange',label='Random Forest')
pl.scatter(x,y_lsvc_test[:t],marker='s',s=50,
           color='darkred',label='SVM LinearSVC')
pl.xlabel('Observations'); pl.ylabel('Targets') 
pl.title('Classifiers. Test Results')
pl.legend(loc=2,fontsize=10); pl.show()

[y_knc_train,y_knc_test,acc_knc_train,
 acc_knc_test,loss_knc_train,loss_knc_test]=\
classifier_fit_score(KNC(),x_train,x_test,y_train,y_test)
print(classification_report(y_test,y_knc_test))

mlpc=MLPClassifier(hidden_layer_sizes=(512,),
                   max_iter=60,solver='sgd',
                   verbose=1,random_state=1,
                   learning_rate_init=.005)
[y_mlpc_train,y_mlpc_test,acc_mlpc_train,
 acc_mlpc_test,loss_mlpc_train,loss_mlpc_test]=\
classifier_fit_score(mlpc,x_train,x_test,y_train,y_test)

print(classification_report(y_test,y_mlpc_test))

pl.figure(figsize=(10,5)); t=50; x=range(t)
pl.scatter(x,y_test[:t],marker='*',s=400,
           color='#ff355e',label='Real data')
pl.scatter(x,y_knc_test[:t],marker='v',
           s=100,color='darkorange',label='KNeighbors')
pl.scatter(x,y_mlpc_test[:t],marker='s',s=50,
           color='darkred',label='MLP')
pl.xlabel('Observations'); pl.ylabel('Targets') 
pl.title('Classifiers. Test Results')
pl.legend(loc=2,fontsize=10); pl.show()

acc_train=[acc_rfc_train,acc_lsvc_train,
           acc_knc_train,acc_mlpc_train]
acc_test=[acc_rfc_test,acc_lsvc_test,
          acc_knc_test,acc_mlpc_test]
loss_train=[loss_rfc_train,loss_lsvc_train,
            loss_knc_train,loss_mlpc_train]
loss_test=[loss_rfc_test,loss_lsvc_test,
           loss_knc_test,loss_mlpc_test]
cols=['Random Forest','SVM LinearSVC',
      'KNeighbors','MLP']
pd.DataFrame([acc_train,acc_test,
              loss_train,loss_test],
            index=['accuracy train','accuracy test',
                   'loss train','loss test'],
            columns=cols)