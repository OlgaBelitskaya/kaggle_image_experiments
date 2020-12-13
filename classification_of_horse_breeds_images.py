# -*- coding: utf-8 -*-
"""classification-of-horse-breeds-images.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AGMN_2Xl_fb_lw982I3-TYdq_Ssq11F0

[🌐 Google Colaboratory Variant](https://colab.research.google.com/drive/1uB1PuT_uNGM2tv88ZDkIj6Dhi_Rf91PA)
"""

# Commented out IPython magic to ensure Python compatibility.
# %run ../input/python-recipes/cidhtml.py
idhtml('Code Modules, Functions, & Classes')

import warnings; warnings.filterwarnings('ignore')
import pandas as pd,numpy as np
import h5py,imageio,os,torch,pylab as pl
import tensorflow_hub as th,tensorflow as tf
import tensorflow.keras.layers as tkl
import tensorflow.keras.callbacks as tkc
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing import image as tkimg
from torch.utils.data import DataLoader as tdl
from torch.utils.data import Dataset as tds
from torchvision import transforms,utils,models
import torch.nn.functional as tnnf
import torch.nn as tnn
from PIL import Image
dev=torch.device('cuda:0' \
if torch.cuda.is_available() else 'cpu')
from IPython.core.magic import register_line_magic
print('tensorflow version:',tf.__version__)

def images2array(files_path,img_size,grayscale=False):
    files_list=sorted(os.listdir(files_path))
    n,img_array=len(files_list),[]
    for i in range(n):
        if i%round(.1*n)==0:
            print('=>',end='',flush=True)
        img_path=files_path+files_list[i]
        if (img_path[-4:]=='.png'):
            img=tkimg.load_img(
                img_path,grayscale=grayscale,
                target_size=(img_size,img_size))
        img=tkimg.img_to_array(np.squeeze(img))
        img=np.expand_dims(img,axis=0)/255
        img_array.append(img)
    return np.array(np.vstack(img_array),dtype='float32')
class HorseBreedsData(tds):
    def __init__(self,csv_path,img_dir,transform=None):
        df=pd.read_csv(csv_path,index_col=0)
        self.img_dir=img_dir
        self.csv_path=csv_path
        self.img_paths=df['path']
        self.y=df['label'].values
        self.transform=transform
    def __getitem__(self,index):
        img=Image.open(os.path\
        .join(self.img_dir,self.img_paths[index]))
        img=img.convert('RGB')
        if self.transform is not None: 
            img=self.transform(img)
        lbl=self.y[index]
        return img,lbl
    def __len__(self):
        return self.y.shape[0]

@register_line_magic
def display_examples(data):
    for images,labels in dataloaders[data]:  
        print('Image dimensions: %s'%str(images.shape))
        print('Label dimensions: %s'%str(labels.shape))
        n=np.random.randint(1,3)
        fig=pl.figure(figsize=(9,3))
        for i in range(n,n+4):
            ax=fig.add_subplot(1,4,i-n+1,\
            xticks=[],yticks=[],title=names[labels[i].item()])
            ax.imshow(np.transpose(images[i],(1,2,0)))
        pl.tight_layout(); pl.show()    
        break
@register_line_magic
def display_predict(data):
    if data=='test': x=x_test; y=y_test
    if data=='valid': x=x_valid; y=y_valid 
    kmodel.load_weights(fweights)
    y_predict=kmodel.predict_classes(x)
    fig=pl.figure(figsize=(9,8))
    randch=np.random.choice(
        x.shape[0],size=6,replace=False)
    for i,idx in enumerate(randch):
        ax=fig.add_subplot(2,3,i+1,xticks=[],yticks=[])
        ax.imshow(np.squeeze(x[idx]))
        pred_idx=y_predict[idx]; true_idx=y[idx]
        ti='{} \n({})'.format(
            names[pred_idx],names[true_idx])
        ax.set_title(ti,\
        color=('darkblue' if pred_idx==true_idx else 'darkred'))
    pl.tight_layout(); pl.show()
def show_image(img):
    img=utils.make_grid(img)
    npimg=img.numpy(); tr=(1,2,0)
    pl.figure(figsize=(9,3))
    pl.imshow(np.transpose(npimg,tr))
    pl.xticks([]); pl.tight_layout(); pl.show()

def model_acc(model,data_loader):
    correct_preds,num_examples=0,0    
    for features,targets in data_loader:
        features=features.to(dev)
        targets=targets.to(dev).long()
        logits=model(features)
        _,pred_labels=torch.max(logits,1)
        num_examples+=targets.size(0)
        correct_preds+=(pred_labels==targets).sum()        
    return correct_preds.float()/num_examples*100
def epoch_loss(model,data_loader):
    model.eval()
    curr_loss,num_examples=0.,0
    with torch.no_grad():
        for features,targets in data_loader:
            features=features.to(dev)
            targets=targets.to(dev).long()
            logits=model(features)
            loss=tnnf.cross_entropy(logits,targets,
                                    reduction='sum')
            num_examples+=targets.size(0)
            curr_loss+=loss
        return curr_loss/num_examples
def keras_history_plot(fit_history,fig_size,color='darkblue'):
    keys=list(fit_history.history.keys())
    list_history=[fit_history.history[keys[i]] 
                  for i in range(len(keys))]
    dfkeys=pd.DataFrame(list_history).T
    dfkeys.columns=keys
    fig=pl.figure(figsize=(fig_size,fig_size))
    ax1=fig.add_subplot(2,1,1)
    dfkeys.iloc[:,[0,2]].plot(
        ax=ax1,color=['slategray',color],grid=True)
    ax2=fig.add_subplot(2,1,2)
    dfkeys.iloc[:,[1,3]].plot(
        ax=ax2,color=['slategray',color],grid=True)
    pl.tight_layout(); pl.show()

idhtml('Data Loaders')

img_path='../input/horse-breeds/'; img_size=160
names=['Akhal-Teke','Appaloosa','Orlov Trotter',
       'Vladimir Heavy Draft','Percheron',
       'Arabian','Friesian']
flist=sorted(os.listdir(img_path))
labels=[int(el[:2])-1 for el in flist]
labels=np.array(labels,dtype='int32')
images=images2array(img_path,img_size)
N=labels.shape[0]; n=int(.1*N)
shuffle_ids=np.arange(N)
np.random.RandomState(12).shuffle(shuffle_ids)
images,labels=images[shuffle_ids],labels[shuffle_ids]
x_test,x_valid,x_train=images[:n],images[n:2*n],images[2*n:]
y_test,y_valid,y_train=labels[:n],labels[n:2*n],labels[2*n:]
pd.DataFrame([[x_train.shape,x_valid.shape,x_test.shape],
              [x_train.dtype,x_valid.dtype,x_test.dtype],
              [y_train.shape,y_valid.shape,y_test.shape],
              [y_train.dtype,y_valid.dtype,y_test.dtype]],               
             columns=['train','valid','test'])

train_csv,valid_csv,test_csv=\
'train.csv','valid_csv','test.csv'
img_path2='../input'; img_size2=64
files=[os.path.relpath(os.path.join(dirpath,fn),img_path2) \
for (dirpath,dirnames,filenames) in os.walk(img_path2) \
for fn in filenames if fn.endswith('.png')]
d={'label':[],'breed':[],'file':[],'path':[]}
for f in files:
    _,fn=f.split('/')
    label=int(fn[:2])-1; breed=names[label]        
    d['label'].append(label)
    d['breed'].append(breed)
    d['file'].append(fn)
    d['path'].append(f)
df=pd.DataFrame.from_dict(d)
np.random.seed(123)
ids=np.random.rand(len(df))<.8
df_train=df[ids]; df_test=df[~ids]
df_train.set_index('file',inplace=True)
df_train.to_csv(train_csv)
df_test.set_index('file',inplace=True)
df_test[:df_test.shape[0]//2].to_csv(test_csv)
df_test[df_test.shape[0]//2:].to_csv(valid_csv)
num_classes=np.unique(df['label'].values).shape[0]
print([num_classes,len(files)]); df_test.head()

batch_size=16; num_workers=4; grayscale=False
trans=transforms\
.Compose([transforms.Resize((img_size2,img_size2)),
          transforms.ToTensor()])
train=HorseBreedsData(
    csv_path=train_csv,img_dir=img_path2,transform=trans)
test=HorseBreedsData(
    csv_path=test_csv,img_dir=img_path2,transform=trans)
valid=HorseBreedsData(
    csv_path=valid_csv,img_dir=img_path2,transform=trans)
dataloaders={'train':tdl(dataset=train,batch_size=batch_size,
                         shuffle=True,num_workers=num_workers),
             'test':tdl(dataset=test,batch_size=batch_size,
                        shuffle=True,num_workers=num_workers),
             'valid':tdl(dataset=valid,batch_size=batch_size,
                         shuffle=True,num_workers=num_workers)}

# Commented out IPython magic to ensure Python compatibility.
# %display_examples valid

idhtml('Classifiers')

def premodel(pix,den,mh,lbl,activ,loss):
    model=Sequential([
        tkl.Input((pix,pix,3),name='input'),
        th.KerasLayer(mh,trainable=True),
        tkl.Flatten(),
        tkl.Dense(den,activation='relu'),
        tkl.Dropout(rate=.5),
        tkl.Dense(lbl,activation=activ)])
    model.compile(
        optimizer='adam',metrics=['accuracy'],loss=loss)
    return model
def cb(fw):
    early_stopping=tkc.EarlyStopping(
        monitor='val_loss',patience=20,verbose=2)
    checkpointer=tkc.ModelCheckpoint(
        filepath=fweights,save_best_only=True,verbose=2,
        save_weights_only=True,monitor='val_accuracy',mode='max')
    lr_reduction=tkc.ReduceLROnPlateau(
        monitor='val_loss',verbose=2,patience=5,factor=.8)
    return [checkpointer,early_stopping,lr_reduction]

fweights='/checkpoints'
handle_base='mobilenet_v2_100_160'
mhandle='https://tfhub.dev/google/imagenet/'+\
        '{}/classification/4'.format(handle_base)
kmodel=premodel(img_size,2048,mhandle,7,'softmax',
                'sparse_categorical_crossentropy')
history=kmodel.fit(
    x=x_train,y=y_train,batch_size=16,epochs=50,
    callbacks=cb(fweights),validation_data=(x_valid,y_valid))

keras_history_plot(history,9)

kmodel.load_weights(fweights)
kmodel.evaluate(x_test,y_test,verbose=0)

# Commented out IPython magic to ensure Python compatibility.
# %display_predict test

def kmodel(leaky_alpha):
    model=Sequential()
    model.add(tkl.Conv2D(
        32,(5,5),padding='same', 
        input_shape=(img_size,img_size,3)))
    model.add(tkl.LeakyReLU(alpha=leaky_alpha))    
    model.add(tkl.MaxPooling2D(pool_size=(2,2)))
    model.add(tkl.Dropout(.25))
    model.add(tkl.Conv2D(196,(5,5)))
    model.add(tkl.LeakyReLU(alpha=leaky_alpha))    
    model.add(tkl.MaxPooling2D(pool_size=(2,2)))
    model.add(tkl.Dropout(.25))   
    model.add(tkl.GlobalMaxPooling2D())     
    model.add(tkl.Dense(1024))
    model.add(tkl.LeakyReLU(alpha=leaky_alpha))
    model.add(tkl.Dropout(.25))     
    model.add(tkl.Dense(7))
    model.add(tkl.Activation('softmax'))   
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='nadam',metrics=['accuracy'])   
    return model
kmodel=kmodel(.02)

history=kmodel.fit(
    x_train,y_train,epochs=200,batch_size=64,
    validation_data=(x_valid,y_valid),
    verbose=2,callbacks=cb(fweights))

keras_history_plot(history,9)

kmodel.load_weights(fweights)
kmodel.evaluate(x_test,y_test,verbose=0)

# Commented out IPython magic to ensure Python compatibility.
# %display_predict test

tmodel=models.vgg16(pretrained=True)
for param in tmodel.parameters():
    param.requires_grad=False
tmodel.classifier[3].requires_grad=True
tmodel.classifier[6]=tnn.Sequential(
    tnn.Linear(4096,512),tnn.ReLU(),
    tnn.Dropout(.5),tnn.Linear(512,num_classes))
tmodel=tmodel.to(dev)
optimizer=torch.optim.Adam(tmodel.parameters())

# Commented out IPython magic to ensure Python compatibility.
@register_line_magic
def train_run(epochs):
    epochs=int(epochs)
    for epoch in range(epochs):
        tmodel.train()
        for batch_ids,(features,targets) \
        in enumerate(dataloaders['train']):        
            features=features.to(dev)
            targets=targets.to(dev).long()
            logits=tmodel(features)
            cost=tnnf.cross_entropy(logits,targets)
            optimizer.zero_grad(); cost.backward()
            optimizer.step()
            if not batch_ids%10:
                print ('Epoch: %03d/%03d | Batch: %03d/%03d | Cost: %.4f' 
#                        %(epoch+1,epochs,batch_ids,
                         len(dataloaders['train']),cost))
        tmodel.eval()
        with torch.set_grad_enabled(False):
            print('Epoch: %03d/%03d'%(epoch+1,epochs))
            print('train acc/loss: %.2f%%/%.2f valid acc/loss: %.2f%%/%.2f'%\
                  (model_acc(tmodel,dataloaders['train']),
                   epoch_loss(tmodel,dataloaders['train']),
                   model_acc(tmodel,dataloaders['valid']),
                   epoch_loss(tmodel,dataloaders['valid'])))

# Commented out IPython magic to ensure Python compatibility.
# %train_run 11

tmodel.eval()
with torch.set_grad_enabled(False):
    print('train acc: %.2f%% || test acc: %.2f%%'%\
          (model_acc(tmodel,dataloaders['train']),
           model_acc(tmodel,dataloaders['test'])))

with torch.no_grad():
    for i,(images,labels) in enumerate(dataloaders['test']):
        show_image(images[:3])
        print('\ntrue labels: \n',
              ''.join('%24s'%names[labels[j]] for j in range(3)))
        images=images.to(dev)
        labels=labels.to(dev)
        outputs=tmodel(images)
        _,preds=torch.max(outputs,int(1))
        print('\npredictions: \n',
             ''.join('%24s'%names[preds[j]] for j in range(3)))
        if i==1: break