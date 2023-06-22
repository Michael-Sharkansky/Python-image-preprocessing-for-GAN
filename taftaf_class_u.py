# classification with augmentation, and using Xception pretrained net
#Programmed by Michael Sharkansky

import numpy as np
import csv
import tensorflow as tf
import matplotlib.pyplot as plt
import sys
import os
import keras
from keras import layers
from keras import models
from keras.utils import plot_model
from keras.layers import Input, LSTM, Dense
from keras.models import Model
from keras import regularizers
from keras import optimizers
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import VGG16
from keras.applications.xception import Xception
from keras.models import *
from keras.layers import *
from keras.optimizers import *
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import sklearn.metrics
import time
from datetime import datetime
import io
import pickle
import pandas as pd
import json
import cv2  # use: pip install opencv-contrib-python
import platform
#GUI with tkinter, see https://likegeeks.com/python-gui-examples-tkinter-tutorial/
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog

p_system=platform.system()

if p_system=="windows" or p_system=="Windows":
	drive_in="C:"
	general_dir_in=drive_in+r"\temp\dl"
	drive_out="C:"
	general_dir_out=drive_out+r"\temp\dl"
	root2=r"\Taftafot"
else:
	general_dir_in="/media/dextr/Passport1/DeepLearning/image-to-image/temp/dl"
	general_dir_in="/media/dextr/Passport1/DeepLearning/image-to-image/temp/dl"
	root2="Taftafot"
model_type=3    # 0 seq , 1 transfer xception, 2 transfer vgg16 , 3 - unet
train_conv_blocks_last=True # train the last set of blocks of Xception, or all of it is untrainable

epochs=120 				# the number of iterations through a dataset
batch_size=20  			# groups of images fed into the model per step
categories = 3

do_train=True
do_predict=True
base_dir=os.path.join(general_dir_in,root2)
print("base_dir: ",base_dir)
train_dir=os.path.join(base_dir+"256")
train_dir=os.path.join(train_dir+"train")
print("train_dir: ",train_dir)
validation_dir=os.path.join(base_dir+"256")
validation_dir=os.path.join(validation_dir+"validate")
print("validation_dir: ", validation_dir)
test_dir=os.path.join(base_dir+"256")
test_dir=os.path.join(test_dir+"test")
print("test_dir: ", test_dir)
results_dir=os.path.join(general_dir_out,root2)
results_dir=os.path.join(results_dir,"results")
print("results_dir: ", results_dir)
stamp_start=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

activation='softmax' 	# sigmoid (binary) softmax (multiple)
verbose = 1
embeddings_freq = 1
histogram_freq = 0 # to prevent ValueError: If printing histograms, validation_data must be provided, and cannot be a generator.

heigth=256	#544
width=256	#328
image_size=(width,heigth)
input_shape=(width,heigth,3)

standartize=True
rescale_train = 1.0
rescale_predict = 1.0
deployable=False

model_created=FALSE
model=None
embeddings_layer_names = []
current=1
transfer="sxvu"  # s, x or v or u

suffix="_"+transfer[model_type:model_type+1]+"_e"+str(epochs)

if not os.path.exists(base_dir):
    print("ERROR: base folder not found {}, !!!!!!!".format(base_dir))
    input("Press Enter to continue...")

total_files_train=sum([len(files) for r,d,files in os.walk(train_dir)])
total_files_validation=sum([len(files) for r,d,files in os.walk(validation_dir)])
total_files_test=sum([len(files) for r,d,files in os.walk(test_dir)])

steps_per_epoch=int(total_files_train / batch_size) # see DL/P p.136-137,  the number of batches per epoch, =total_files / batch_size

if not os.path.exists(results_dir):
    os.mkdir(results_dir)
print("Output to folder: ",results_dir)
if total_files_train % batch_size != 0:
        print("WARNING: Q-ty of train files does not divide squarely into batches!!!!!!!!!!!!!!!!!!!!!!")
if total_files_validation % batch_size != 0:
        print("WARNING: Q-ty of validation files does not divide squarely into batches!!!!!!!!!!!!!!!!!!!!!!")
if total_files_test % batch_size != 0:
        print("WARNING: Q-ty of test files does not divide squarely into batches!!!!!!!!!!!!!!!!!!!!!!")


log_file_name = os.path.join(results_dir, "_log_" + stamp_start + suffix + ".log")
log_file = open(log_file_name, 'wt')
log_file.write("{} {} of {}\n".format(stamp_start, os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__))))
log_file.write("Log file: {} \n".format(log_file_name))
log_file.write("Data: {} \n".format(train_dir))
log_file.write("epochs={} model_type={}   activation: {} steps_per_epoch={} standartize={}\n".format(
                epochs,transfer[model_type:model_type+1], activation, steps_per_epoch,standartize))

def count_categories():
    global categories
    categories=0
    for r, d, f in os.walk(train_dir):
        for folder in d:
            categories=categories+1

def get_model_summary(model):
    stream = io.StringIO()
    model.summary(print_fn=lambda x: stream.write(x + '\n'))
    summary_string = stream.getvalue()
    stream.close()
    return summary_string
#===========================================================================================================

def create_seq_model():
    global embeddings_layer_names
    global  model_type
    global input_shape
    if model_type==1:
        log_file.write("Seq Xception functional base model \n")
        log_file.write("Comment: with Flatten instead of GlobalAveragePooling2D ,  dense dropuout layers, standartize {} \n".format(epochs))
        #see https://stackoverflow.com/questions/48890758/pre-training-keras-xception-and-inceptionv3-models
        conv_base = Xception(weights='imagenet',  #VGG16  Xception
                            include_top=False, # remove GlobalAveragePooling2D and Dense(1000) layers, pooling=avr returns the first one
							#pooling='avg',	   # adds GlobalAveragePooling2D back (don't !!!)
                            input_shape=input_shape)
        conv_base.trainable = False
        output=conv_base.output
        #output = GlobalAveragePooling2D()(output)
        output=Flatten()(output)  # converts array of batch into single, must!
        #output=Dense(128, activation='relu', name='dense_last_2')(output)
        #output=Dropout(0.1)(output)
        output=Dense(1024, activation='relu', name='dense_last_1')(output)  #
        output=Dense(categories, activation=activation, name='dense_last')(output)
        model=Model(conv_base.input,output)
        if train_conv_blocks_last:
            set_trainable = False
            for layer in conv_base.layers:
                if layer.name == 'block14_sepconv1' :   #down from this layer in the Xception
                    set_trainable = True
                    print("Trainable from here.")
                if set_trainable:
                    layer.trainable = True
                    print(layer.name, " is Trainable.")
                else:
                    layer.trainable = False

        model.compile(loss='categorical_crossentropy',
                      #optimizer=optimizers.RMSprop(lr=1e-4),  # Adam(lr=1e-4) ?
                      optimizer=optimizers.Adam(lr=1e-4),  # or 'nadam' ?
                      metrics=['mae', 'acc'])
        conv_base.summary()
        embeddings_layer_names = [ 'dense_last_1', 'dense_last']


    elif model_type == 2:
        log_file.write("Seq VGG16 functional base model \n")
        # see https://stackoverflow.com/questions/48890758/pre-training-keras-xception-and-inceptionv3-models
        conv_base = VGG16(weights='imagenet',  # VGG16  Xception
                             include_top=False,
                             # remove GlobalAveragePooling2D and Dense(1000) layers, pooling=avr returns the first one
                             # pooling='avg',	   # adds GlobalAveragePooling2D back (don't !!!)
                             input_shape=input_shape)
        conv_base.trainable = False
        output = Flatten()(conv_base.output)  # converts array of batch into single, must!
        output = Dropout(0.1)(output)
        output = Dense(512, activation='relu', name='dense_last_1')(output)
        output = Dense(categories, activation=activation, name='dense_last')(output)
        model = Model(conv_base.input, output)
        if train_conv_blocks_last:
            set_trainable = False
            for layer in conv_base.layers:
                if  layer.name == 'block5_conv1':  # down from this layer in the VGG16
                    set_trainable = True
                    print("Trainable from here.")
                if set_trainable:
                    layer.trainable = True
                    print(layer.name, " is Trainable.")
                else:
                    layer.trainable = False
        conv_base.summary()
        embeddings_layer_names = [ 'dense_last_1', 'dense_last']
        model.compile(loss='categorical_crossentropy',
                      optimizer=optimizers.RMSprop(lr=1e-4),  # or 'nadam' ?
                      metrics=['mae', 'acc'])


    elif model_type==0:
        log_file.write("Sequential conv model \n")
        model = models.Sequential()
        model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape, name='conv2d_01'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu', name='conv2d_02'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(128, (3, 3), activation='relu', name='conv2d_03'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(128, (3, 3), activation='relu', name='conv2d_04'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Flatten())
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(512, activation='relu', name='dense_05'))
        model.add(layers.Dense(categories, activation=activation, name='dense_last'))

        embeddings_layer_names = ['dense_01', 'conv2d_01', 'conv2d_02',
                                  'conv2d_03', 'conv2d_04', 'dense_05', 'dense_last']  # layers of the model

        model.compile(loss='categorical_crossentropy',
                      optimizer=optimizers.RMSprop(lr=1e-4),  # or 'nadam' ?
                      metrics=['mae', 'acc'])
    elif model_type == 3:
            model = create_unet_model()
    else:
        model=None
        print("MODEL TYPE ERROR!!!!!!!!!!!!!!")

    log_file.write("Compiled Model summary: \n{} \n".format(get_model_summary(model)))
    log_file.write("Optimizer: {}\n".format(model.optimizer))

    model_created=True
    return model
#========================================================================================================
# from site: https://github.com/zhixuhao/unet : Implementation of deep learning framework -- Unet, using Keras
def create_unet_model(pretrained_weights=None, input_size=input_shape):
    global embeddings_layer_names
    log_file.write("UNet model \n")

    inputs = Input(input_size)
    conv1 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(inputs)
    conv1 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)
    conv4 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool3)
    conv4 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
    drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

    conv5 = Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(pool4)
    conv5 = Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
    drop5 = Dropout(0.5)(conv5)

    up6 = Conv2D(512, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(drop5))
    merge6 = concatenate([drop4, up6], axis=3)  #size must be the same!
    conv6 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge6)
    conv6 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)

    up7 = Conv2D(256, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv6))
    merge7 = concatenate([conv3, up7], axis=3)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge7)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)

    up8 = Conv2D(128, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv7))
    merge8 = concatenate([conv2, up8], axis=3)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge8)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)

    up9 = Conv2D(64, 2, activation='relu', padding='same', kernel_initializer='he_normal')(
        UpSampling2D(size=(2, 2))(conv8))
    merge9 = concatenate([conv1, up9], axis=3)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge9)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    #conv9 = Conv2D(2, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    #conv9 = Conv2D(4, 1, activation='sigmoid')(conv9)
    conv9 = Conv2D(32, 1, activation='relu')(conv9)

    den_add = Flatten()(conv9)  # converts array of batch into single, must!
    #den_add=Dense(128, activation='relu', name='dense_last_2')(den_add)
    output = Dense(1024, activation='relu', name='dense_last_1')(den_add)  #
    #den_add=Dropout(0.1)(den_add)
    den11  = Dense(categories, activation='softmax', name='dense_last')(den_add)

    model = Model(input=inputs, output=den11)

    model.compile(loss='categorical_crossentropy',
                  optimizer=optimizers.RMSprop(lr=1e-4),  # Adam(lr=1e-4) ?
                  metrics=['mae', 'acc'])

    embeddings_layer_names = []

    if (pretrained_weights):
        model.load_weights(pretrained_weights)

    return model


#==========================================================================================================

#reopen the log to commint it.
def reopen_log():
    global log_file
    log_file.close()
    log_file = open(log_file_name, 'a+')
#===========================================================================================================


def plot_fit_history(history, file_name):
    global log_file
    history_dict = history.history
    loss_values = history_dict['loss']
    val_loss_values = history_dict['val_loss']
    epochs = range(1, len(loss_values) + 1)
    plt.clf()
    plt.plot(epochs, loss_values, 'bo', label='Training loss')
    plt.plot(epochs, val_loss_values, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    global current
    plot_name=file_name.replace("_@@@","_loss"+str(current))
    plt.savefig(plot_name)  # save the plotted graph
    #plt.show()
    log_file.write("Training and validation loss plot: {}  \n".format(plot_name) )

    plt.clf()
    acc = history_dict['acc']
    val_acc = history_dict['val_acc']
    plt.plot(epochs, acc, 'bo', label='Training acc')
    plt.plot(epochs, val_acc, 'b', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plot_name=file_name.replace("_@@@","_acc"+str(current))
    plt.savefig(plot_name)  # save the plotted graph
    log_file.write("Training and validation accuracy plot: {}  \n".format(plot_name) )
#===========================================================================================================

def save_model():
    global model, results_dir, deployable
    stamp = "{:02d}{:02d}".format(datetime.now().hour, datetime.now().minute)
    flcnt = "#{:03d}_".format(current)  # running rumber for file uniquness
    model_file_name='classify_'+flcnt+stamp_start+"_@"+stamp+suffix
    model_file = os.path.join(results_dir, model_file_name +'.hdf5')
    # save structure and weights with optimizer state to allow continued traing with the model
    model.save(model_file, overwrite=True, include_optimizer=True)  # see https://stackoverflow.com/questions/42763094/how-to-save-final-model-using-keras
    with open(os.path.join(results_dir, model_file_name +'.bin'), "wb") as output_file:  # save the model as binary object dump
        pickle.dump(model, output_file)

    #plot_model(model,show_shapes=True, to_file=os.path.join(results_dir, model_file_name +'.png'))  #plot the model graph. from keras.utils
    if deployable:
        save_model_for_deployment(model_file_name)
    print("Model saved to ", model_file, flush=True)
    log_file.write("Model saved to {} and to binary dump.\n".format(model_file) )


#save model as json and weights as hd5 for deployment
def save_model_for_deployment(model_file_name):
    global model
    model_file = os.path.join(results_dir, model_file_name +'_weights.hd5')
    model.save_weights(model_file)
    log_file.write("Weights saved to {} for deployment.\n".format(model_file) )

    # save as JSON
    model_file = os.path.join(results_dir, model_file_name +'_model.json')
    json_string = model.to_json()
    json_file = open(model_file, 'wt')
    json_file.write("{}".format(json_string))
    json_file.close()
    log_file.write("Model saved to {} for deployment.\n".format(model_file) )

    # save structure and weights without optimizer state (for deployment)
    model_file = os.path.join(results_dir, model_file_name +'_no_optimizer.h5')
    model.save(model_file, overwrite=True, include_optimizer=False)  # see https://stackoverflow.com/questions/42763094/how-to-save-final-model-using-keras

def load_model():   #load the model from hdf5 structure file
    global log_file
    global model
    global model_created
    model_file = filedialog.askopenfilename(title="Load model file", filetypes=(("HDF5 files", "*.hdf5"), ("All files", "*.*")))     #open file dialog
    model = keras.models.load_model(model_file, compile=True)  #model was saved as compiled, however setting to false  gives: "RuntimeError: You must compile a model before training/testing. Use `model.compile(optimizer, loss)`."
    print("Model loaded from ", model_file, flush=True)
    log_file.write("Loaded Model summary from {}:\n{} \n".format(model_file,get_model_summary(model)) )
    model_created = TRUE
#===================================================================================================================================


def load_model_bin():       # load the model from binary object dump
    global log_file
    global model
    global model_created
    model_file = filedialog.askopenfilename(title="Load model file", filetypes=(("Binary files", "*.bin"), ("All files", "*.*")))     #open file dialog
    with open(model_file, "wb") as input_file:
        pickle.dump(model, input_file)

    print("Model loaded from binary:", model_file, flush=True)
    log_file.write("Loaded Model summary from binary {}:\n{} \n".format(model_file,get_model_summary(model)) )
    model_created = TRUE
#===================================================================================================================================


def train():
    global model
    global rescale_train

    if model_type==1 :
        rescale_train = 1./255
    elif model_type==0 or  model_type==2 or  model_type==3 :
        rescale_train = 1./255
    log_file.write("rescale_train={}\n".format(rescale_train))

    stamp = "{:02d}{:02d}".format(datetime.now().hour, datetime.now().minute)
    flcnt = "#{:03d}_".format(current)  # running rumber for file uniquness
    model_file_name='classify_'+flcnt+stamp_start+"_@"+stamp+suffix
    model_file_c = os.path.join(results_dir, model_file_name +'_weights.hd5')

    callbacks = [
        # Connect to TensorBoard: tensorboard --logdir=<folder>,  see at //localhost:6006
        keras.callbacks.TensorBoard(
            log_dir=results_dir,
            histogram_freq=histogram_freq,
            batch_size=batch_size,
            write_graph=True,
            write_grads=True,
            write_images=True,
            #embeddings_freq=embeddings_freq,  # num of epochs, requires embeddings_data provided.
            #embeddings_layer_names=embeddings_layer_names,  # layers of the model
            #embeddings_data=embeddings_data,
            #embeddings_metadata=metadata_file,  # contains y_test
        ),
        #auto-save the best model so far
        keras.callbacks.callbacks.ModelCheckpoint(
            model_file_c, 
            monitor='val_acc', #val_loss
            verbose=1, 
            save_best_only=True, 
            save_weights_only=False, 
            mode='auto',        # depends on 'monitor'
            period=1)
        # ,
        # # Interrupts training when accuracy has stopped improving for more than patience=n (1) epoch (that is, n+1 epochs)
        # keras.callbacks.EarlyStopping(
        #     monitor='acc',
        #     patience=1,
        #     verbose=verbose,
        # )
    ]

    train_datagen = ImageDataGenerator(rescale=rescale_train,
                                        rotation_range=40,   # with augmentation
                                        width_shift_range=0.2,
                                        height_shift_range=0.2,
                                        shear_range=0.2,
                                        zoom_range=0.2,
                                        horizontal_flip=True,
                                        vertical_flip=True,
                                        samplewise_center=standartize,
                                        samplewise_std_normalization=standartize,
                                       )

    test_datagen = ImageDataGenerator(rescale=rescale_train,
                                      samplewise_center=standartize,
                                      samplewise_std_normalization=standartize,
                                      )
    #see https://medium.com/@vijayabhaskar96/tutorial-image-classification-with-keras-flow-from-directory-and-generators-95f75ebe5720
    train_generator = train_datagen.flow_from_directory(
                                    train_dir,
                                    target_size=image_size,
                                    batch_size=batch_size,
                                    class_mode='categorical')
    validation_generator = test_datagen.flow_from_directory(
                                    validation_dir,
                                    target_size=image_size,
                                    batch_size=batch_size,
                                    class_mode='categorical',
                                    )   # or None?

    history = model.fit_generator(
                            train_generator,
                            steps_per_epoch=steps_per_epoch,
                            epochs=epochs,
                            #callbacks=callbacks,
                            validation_data=validation_generator,
                            validation_steps=50 )
    print("train done.")
    save_model()
    label_map = (train_generator.class_indices)
    print(label_map)
    log_file.write("Label map:\n {} \n".format(label_map))
    json.dump(label_map, open(results_dir+"label"+suffix+".txt", 'w'))    #save labels

    history_dict = history.history  # plot estimations
    if history_dict.get('val_loss') != None and history_dict.get('val_acc') != None:  # fit with validation_data parm?
        a_plot_file = 'plot_' +stamp_start+ '_@@@' + suffix+ '.png'
        fname = os.path.join(results_dir, a_plot_file)
        plot_fit_history(history, fname)
    reopen_log()
#========================================================================================= train

#running prediction
def predict():
    global model
    global rescale_predict
    print("Run prediction. ",test_dir, flush=True)
    log_file.write("Prediction: {}\n".format(test_dir))

    labels = {0: 'Garlic_Bad', 1: 'Garlic_Good', 2: 'Garlic_Kavush', 3: 'Garlic_Skin'}
    if os.path.exists(results_dir+"label"+suffix+".txt"):
        labels2 = json.load(open(results_dir+"label"+suffix+".txt"))
        labels = dict(zip(labels2.values(), labels2.keys()))    # switch key and data in the dict
    print(labels)

    sample_count=total_files_test
    if model_type==1 :
        rescale_predict = 1./255
    elif model_type==0 or  model_type==2 or  model_type==3 :
        rescale_predict = 1.0

    log_file.write("rescale_predict={}\n".format(rescale_predict))

    i=0
    #                   for Xception must resize the image here!
    datagen = ImageDataGenerator( rescale=rescale_predict,  #see https://github.com/keras-team/keras/issues/3477
                                    samplewise_center = standartize,
                                    samplewise_std_normalization = standartize,
                                )
    predict_generator = datagen.flow_from_directory(
                    test_dir,
                    target_size=image_size,
                    batch_size=batch_size,
                    shuffle=False, #to keep the file order
                    class_mode="categorical")
    predict_generator.reset()
    for inputs_batch, labels_batch in predict_generator:
        print("iteration {}".format(i), flush=True)
        features_batch = model.predict_generator(predict_generator,steps=np.ceil(sample_count/batch_size))
        #see https://stackoverflow.com/questions/52270177/how-to-use-predict-generator-on-new-images-keras
        # https://github.com/keras-team/keras/issues/11117
        # https://github.com/keras-team/keras/issues/3477
        predicted_class_indices = np.argmax(features_batch, axis=1)
        print(features_batch.shape,'\n', features_batch)
        predictions = [labels[k] for k in predicted_class_indices]
        filenames = predict_generator.filenames
        results = pd.DataFrame({"Filename": filenames,
                                "Predictions": predictions})
        results.to_csv(results_dir+"results"+suffix+".csv", index=False)
        print(results, flush=True)
        log_file.write("Predicted Labels:\n{}\n".format(results))
        log_file.write("Result probabilities:\n{}\n".format(features_batch))
        reopen_log()
        good_count=0
        for row in results.itertuples(index=True, name='Pandas'):
            if getattr(row, "Filename").find(getattr(row, "Predictions")[:2])>=0 :
                good_count=good_count+1
        print("Good count={}".format(good_count))
        log_file.write("Good count={} of {}\n".format(good_count,len(filenames)))
        #features[i * batch_size : (i + 1) * batch_size] = features_batch
        #labels[i * batch_size : (i + 1) * batch_size] = labels_batch
        i += 1
        if i * batch_size >= sample_count:
            break
#======================================================================================================= predict

model=create_seq_model()

reopen_log()

if do_train:
    count_categories()
    train()
else:
    load_model_bin()

if do_predict:
    predict()
	
print(
    "epochs={} model_type={} activation={} steps_per_epoch={} standartize={}\n".format(
                epochs,transfer[model_type:model_type+1], activation, steps_per_epoch,standartize))
log_file.write(
    "epochs={} model_type={} activation={} steps_per_epoch={} standartize={}\n".format(
                epochs,transfer[model_type:model_type+1], activation, steps_per_epoch,standartize))
stamp=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)
log_file.write("END: from {} to {} ".format(stamp_start, stamp))

log_file.close()
print("END: from {} to {}, {} ".format(stamp_start, stamp,suffix), flush=True)
#input("Press Enter to continue...")
