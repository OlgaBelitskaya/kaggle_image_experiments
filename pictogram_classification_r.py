# -*- coding: utf-8 -*-
"""pictogram-classification-r.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WTp-KoFxPXbvm2qW9kaJnbbMO2PN4l-X

<h1 class='font-effect-3d' style='font-family:Smokum; color:#ff355e;'>Code Modules & Styles</h1>
"""

library(IRdisplay)
library(repr); library(stringr)
library(tensorflow); library(keras)
library(imager); library(R6)

display_html("<style> 
@import url('https://fonts.googleapis.com/css?family=Smokum|Roboto&effect=3d'); 
a,h4 {color:slategray; font-family:Roboto; text-shadow:3px 3px 3px #bbb;}
span {color:black; font-family:Roboto; text-shadow:3px 3px 3px #bbb;}
div.output_prompt,div.output_area pre {color:slategray;}
div.input_prompt,div.output_subarea {color:#ff355e;}      
div.output_stderr pre {background-color:gainsboro;}  
div.output_stderr {background-color:slategrey;}     
</style>")

"""<h1 class='font-effect-3d' style='font-family:Smokum; color:#ff355e;'>Data Exploration</h1>"""

fpath<-"../input/art-pictogram/pictograms/"
manners<-c('pictogram','contour','sketch')
objects<-c('flower','bird','butterfly','tree',
           'plane','crane','dog','horse',
           'deer','truck','car','cat',
           'frog','ship','fish','house')
pics<-list.files(fpath)
fl<-length(pics)
pics<-data.frame(c(1:fl),pics)
colnames(pics)<-c('number','file')
pics$file<-c(array_reshape(as.matrix(pics['file']),fl))
labels1<-as.integer(str_extract(pics$file,'[0-9][0-9]'))-1
labels2<-as.integer(str_extract(pics$file,'[0-9][0-9][0-9]'))-1
pics$label1<-labels1
pics$manner<-c(array_reshape(as.matrix(manners[labels1+1]),fl))
pics$label2<-labels2
pics$object<-c(array_reshape(as.matrix(objects[labels2+1]),fl))
str(pics)

tail(pics,20)

options(repr.plot.width=8,repr.plot.height=3)
par(mar=c(2,2,2,2))
pics$manner %>% 
    table() %>% barplot(col=rainbow(3,start=.52,end=1))

options(repr.plot.width=11,repr.plot.height=3)
par(mar=c(2,2,2,2))
pics$object %>% 
    table() %>% barplot(col=rainbow(16,start=.52,end=1))

options(repr.plot.width=4,repr.plot.height=4)
par(mar=c(2,2,2,2))
img_path<-paste0(fpath,pics$file[[500]])
img<-keras::image_load(img_path,target_size=c(64,64))
img<-image_to_array(img)/255
img<-array_reshape(img,c(1,64,64,3)); dim(img)
im<-load.image(img_path); dim(im); plot(im)

options(repr.plot.width=4,repr.plot.height=4)
par(mar=c(2,2,2,2))
img<-keras::image_load(img_path,target_size=c(64,64),
                       grayscale=TRUE)
img<-image_to_array(img)
img<-array_reshape(img,c(1,64,64,1)); dim(img)
im<-load.image(img_path); dim(im); plot(im)

"""<h1 class='font-effect-3d' style='font-family:Smokum; color:#ff355e;'>Data Processing</h1>"""

labels1<-keras::to_categorical(labels1,3)
labels2<-keras::to_categorical(labels2,16)
print(labels1[1,]); print(labels2[1,])

image_paths<-list.files(fpath,recursive=TRUE,full.names=TRUE)
image_paths<-image_paths[1:length(image_paths)]
image_paths[3:4]

image_loading<-function(image_path) {
    image<-keras::image_load(image_path,grayscale=TRUE,
                             target_size=c(64,64))
    image<-image_to_array(image)/255
    image<-array_reshape(image,c(1,dim(image)))
    return(image) }

images<-lapply(image_paths,image_loading)
images<-array_reshape(images,c(-1,64,64,1))
c(dim(images),dim(labels1),dim(labels2))

dd<-c(-1,64*64); indices<-sample(1:fl)
train_indices<-indices[1:round(.7*fl)]
valid_indices<-indices[(round(.7*fl)+1):round(.85*fl)]
test_indices<-indices[(round(.85*fl)+1):fl]
images<-array_reshape(images,dd)
x_train<-images[train_indices,]
x_train<-array_reshape(x_train,c(-1,64,64,1))
y_train<-labels1[train_indices,]
x_valid<-images[valid_indices,]
x_valid<-array_reshape(x_valid,c(-1,64,64,1))
y_valid<-labels1[valid_indices,]
x_test<-images[test_indices,]
x_test<-array_reshape(x_test,c(-1,64,64,1))
y_test<-labels1[test_indices,]
c(dim(x_train),dim(x_valid),dim(x_test),
  dim(y_train),dim(y_valid),dim(y_test))

options(repr.plot.width=4,repr.plot.height=4)
par(mar=c(2,2,2,2))
rn<-sample(1:50,1)
imgs<-array_reshape(x_train,c(-1,64,64))
plot(as.raster(imgs[rn,1:64,1:64]))
l2<-which(y_train[rn,1:3]==1)
print(manners[l2])

"""<h1 class='font-effect-3d' style='font-family:Smokum; color:#ff355e;'>Manner Classification</h1>"""

mlp_model<-keras_model_sequential()
mlp_model %>%  
layer_dense(64,input_shape=c(64*64)) %>%  
layer_activation("relu") %>%  
layer_batch_normalization() %>%  
layer_dense(128) %>%  
layer_activation("relu") %>%  
layer_batch_normalization() %>%
layer_dense(256) %>%  
layer_activation("relu") %>%  
layer_batch_normalization() %>%
layer_dense(512) %>%  
layer_activation("relu") %>%  
layer_dropout(.2) %>% 
layer_dense(3) %>%    
layer_activation("softmax")
mlp_model %>%
    compile(loss="categorical_crossentropy",
            optimizer="adam",metrics="accuracy")
summary(mlp_model)

cb<-list(callback_model_checkpoint("mlp_best_weights.h5",
                                   save_best_only=T),
         callback_reduce_lr_on_plateau(monitor="val_loss",
                                       factor=.75)) 
mlp_fit<-mlp_model %>%
    fit(x=array_reshape(x_train,dd),y=y_train,
        shuffle=T,batch_size=64,epochs=100,callbacks=cb,
        validation_data=list(array_reshape(x_valid,dd),y_valid))

options(repr.plot.width=9,repr.plot.height=6)
plot(mlp_fit)

mlp_fit_df<-as.data.frame(mlp_fit)
mlp_fit_df[281:300,]

load_model_weights_hdf5(mlp_model,"mlp_best_weights.h5")
mlp_model %>% 
    evaluate(array_reshape(x_test,dd),y_test)

cnn_model<-keras_model_sequential()
cnn_model %>%  
layer_conv_2d(filter=32,kernel_size=c(5,5),
              padding="same",
              input_shape=c(64,64,1)) %>%  
layer_activation("relu") %>%  
layer_max_pooling_2d(pool_size=c(2,2)) %>%  
layer_dropout(.25) %>%
layer_conv_2d(filter=196,kernel_size=c(5,5),
              padding="same") %>% 
layer_activation("relu") %>%
layer_max_pooling_2d(pool_size=c(2,2)) %>%  
layer_dropout(.25) %>%
layer_global_average_pooling_2d() %>%  
layer_dense(1024) %>%  
layer_activation("tanh") %>%  
layer_dropout(.25) %>%  
layer_dense(64) %>%  
layer_activation("tanh") %>%  
layer_dropout(.25) %>%
layer_dense(3) %>%    
layer_activation("softmax")
cnn_model %>%
    compile(loss="categorical_crossentropy",
            optimizer="nadam",metrics="accuracy")
summary(cnn_model)

cb<-list(callback_model_checkpoint("cnn_best_weights.h5",
                                   save_best_only=T),
         callback_reduce_lr_on_plateau(monitor="val_loss",
                                       factor=.75))        
cnn_fit<-cnn_model %>%
    fit(x=x_train,y=y_train,shuffle=T,batch_size=16,epochs=100,
        validation_data=list(x_valid,y_valid),callbacks=cb)

options(repr.plot.width=9,repr.plot.height=6)
plot(cnn_fit)

cnn_fit_df<-as.data.frame(cnn_fit)
cnn_fit_df[281:300,1:4]

load_model_weights_hdf5(cnn_model,"cnn_best_weights.h5")
cnn_model %>% evaluate(x_test,y_test)

rnn_model<-keras_model_sequential()
rnn_model %>%  
layer_lstm(196,return_sequences=T,
           input_shape=c(1,64*64)) %>%  
layer_lstm(196,return_sequences=T) %>%
layer_lstm(196) %>%
layer_dense(512) %>%  
layer_activation("relu") %>%
layer_dense(3) %>%    
layer_activation("softmax")
rnn_model %>%
    compile(loss="categorical_crossentropy",
            optimizer="adam",metrics="accuracy")
summary(rnn_model)

cb<-list(callback_model_checkpoint("rnn_best_weights.h5",
                                   save_best_only=T),
         callback_reduce_lr_on_plateau(monitor="val_loss",
                                       factor=.75))
dd2<-c(-1,1,64*64)
rnn_fit<-rnn_model %>%
    fit(x=array_reshape(x_train,dd2),y=y_train,
        shuffle=T,batch_size=16,epochs=100,callbacks=cb,
        validation_data=list(array_reshape(x_valid,dd2),y_valid))

options(repr.plot.width=9,repr.plot.height=6)
plot(rnn_fit)

rnn_fit_df<-as.data.frame(rnn_fit)
rnn_fit_df[281:300,1:4]

load_model_weights_hdf5(rnn_model,"rnn_best_weights.h5")
rnn_model %>% evaluate(array_reshape(x_test,dd2),y_test)