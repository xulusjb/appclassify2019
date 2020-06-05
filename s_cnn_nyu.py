import sys
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
#matplotlib inline

import time

import tensorflow as tf
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Conv2D, ZeroPadding2D, Activation, Input, concatenate
from keras.layers import Conv1D, ZeroPadding1D
from keras.models import Model
from keras.backend import clear_session

from keras.layers.normalization import BatchNormalization
from keras.layers.pooling import MaxPooling2D
from keras.layers.pooling import MaxPooling1D
from keras.layers.merge import Concatenate
from keras.layers.core import Lambda, Flatten, Dense
from keras.initializers import glorot_uniform, RandomNormal
from keras.utils.vis_utils import plot_model

from keras.engine.topology import Layer
from keras.regularizers import l2
from keras import backend as K

from sklearn.utils import shuffle

import random as rd

from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())

K.tensorflow_backend._get_available_gpus()
import tensorflow as tf
tf.__version__


def read_data(path, num=200, mode='px', max_length = 3000, ratio = 0.8):  # num: sample number , ratio : train data / all
    train_dict = {}
    test_dict = {}
    categories = []
    for filepath in os.listdir(path):
        if "_"+mode not in filepath:
            continue
        category = filepath.split('.')[0].split('_')[0]
        info = filepath.split('.')[0].split('_')[1]      
        print(filepath)
        if info == mode:
            X= []
            print('Reading from:', filepath)
            categories.append(category)
            
            #d = np.loadtxt(path+filepath, delimiter=' ')  < =====load a dataset where length is the same
            #load when padding is needed for data
            with open(filepath, "r") as rfile:
                s = rfile.read()
            resample_index = 0
            for line in s.split("\n"):
                if resample_index > num * 10:
                    continue
                nums = line.split(" ")
                if len(nums) > 1:
                    truenums = [int(i) for i in nums]
                    if len(truenums) < max_length:
                        truenums = truenums+([0] * (max_length - len(truenums) + 1))  #padding zero
                    X.append(truenums[0:max_length])
                    resample_index += 1
            d = np.asarray(X)
            #if category == 'netflix' or 'msn': # for the category with few data, we pick the data repeatedly
            if len(d) < num:
                d = d[np.random.choice(d.shape[0], num, replace=True)]
            else:
                d = d[np.random.choice(d.shape[0], num, replace=False)]
            
            train_num = int(num*ratio)
            indices = np.arange(num)
            train_indices = np.random.choice(indices, train_num, replace=False)
            test_indices = np.setdiff1d(indices, train_indices)

            train_dict[category] = d[train_indices].reshape(train_num,d.shape[1],1)
            test_dict[category] = d[test_indices].reshape(num-train_num,d.shape[1],1)
            print('training data size:', train_dict[category].shape)
            print('test data size:', test_dict[category].shape)
    # return the train_dic and test_dict for each category, no Y index included.
    return train_dict, test_dict, categories, d.shape[1]

#def initialize_weights(shape, dtype, name=None):
def initialize_weights(shape, name=None):
    """
        The paper, http://www.cs.utoronto.ca/~gkoch/files/msc-thesis.pdf
        suggests to initialize CNN layer weights with mean as 0.0 and standard deviation of 0.01
    """
    return np.random.normal(loc = 0.0, scale = 1e-2, size = shape)

#def initialize_bias(shape, dtype, name=None):
def initialize_bias(shape, name=None):
    """
        The paper, http://www.cs.utoronto.ca/~gkoch/files/msc-thesis.pdf
        suggests to initialize CNN layer bias with mean as 0.5 and standard deviation of 0.01
    """
    return np.random.normal(loc = 0.5, scale = 1e-2, size = shape)

def siamese_model(input_shape):
    """
        Model architecture based on the one provided in: http://www.cs.utoronto.ca/~gkoch/files/msc-thesis.pdf
    """
    
    # Define the tensors for the two input images
    
    left_input = Input(input_shape)
    right_input = Input(input_shape)
    
    # Convolutional Neural Network  # current_base 256 128 128 64
    #now 1 -> 
    model = Sequential()
    #64 5
    model.add(Conv1D(256,8, activation='relu', input_shape=input_shape, 
                     kernel_initializer=initialize_weights,
                     kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling1D())
    model.add(Conv1D(256, 8, activation='relu',
                     kernel_initializer=initialize_weights, bias_initializer=initialize_bias,
                     kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling1D())
    model.add(Conv1D(128, 6, activation='relu',
                     kernel_initializer=initialize_weights, bias_initializer=initialize_bias,
                     kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling1D())
    model.add(Conv1D(128, 4, activation='relu',
                     kernel_initializer=initialize_weights, bias_initializer=initialize_bias,
                     kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling1D())
    model.add(Flatten())
    
    #4096
    model.add(Dense(1024, activation='relu', kernel_initializer=initialize_weights,bias_initializer=initialize_bias, kernel_regularizer=l2(1e-3)))
                   
    
    model.add(Dense(128, activation='relu', kernel_initializer=initialize_weights,bias_initializer=initialize_bias, kernel_regularizer=l2(1e-3)))
                   
    
    
    # Generate the encodings (feature vectors) for the two images
    encoded_l = model(left_input)
    encoded_r = model(right_input)
    
    # Add a customized layer to compute the absolute difference between the encodings
    L1_layer = Lambda(lambda tensors:K.abs(tensors[0] - tensors[1]))
    L1_distance = L1_layer([encoded_l, encoded_r])
    
    # Add a dense layer with a sigmoid unit to generate the similarity score
    prediction = Dense(1,activation='sigmoid',bias_initializer=initialize_bias)(L1_distance)
    
    # Connect the inputs with the outputs
    siamese_net = Model(inputs=[left_input,right_input],outputs=prediction)
    
    # return the model
    return siamese_net


# the data for training for each iteration
def get_batch_1(dict_, categories, batch_size):
    
    categories_batch = np.random.choice(categories, batch_size)  #get an array with batch_size number of category names
    
#     print(categories_batch)
    
#     First half use same class
    division_point = int(batch_size / 2)
    
    batch_1 = np.zeros((batch_size, data_length, 1))
    batch_2 = np.zeros((batch_size, data_length, 1))

    label = np.zeros((batch_size,))
    
    for i in range(batch_size):
        data_temp = dict_[categories_batch[i]]  # this train data pair belong to which category
        if i <= division_point:  # same category pairs
            data_batch = data_temp[np.random.choice(data_temp.shape[0], 2, replace=True)]
            batch_1[i,:,:] = data_batch[0].reshape(data_length,1)
            batch_2[i,:,:] = data_batch[1].reshape(data_length,1)
            label[i] = 1  # model output for same category
        else:  #  different category
            categories_temp = categories.copy()
            categories_temp.remove(categories_batch[i])
            batch_1[i,:,:] = data_temp[rd.randint(0, len(data_temp) - 1)]
            data_temp_2 = dict_[rd.sample(categories_temp, 1)[0]]
            batch_2[i,:,:] = data_temp_2[np.random.choice(data_temp_2.shape[0], 1, replace=True)]
            
#     print(batch_1.shape, batch_2.shape)
    batch_1, batch_2, label = shuffle(batch_1, batch_2, label)
    return batch_1, batch_2, label
    

# for a test flow, randomly generate the N labelled flow vectors to compare with it, the first vector of the N vectors is the same with the test flow and should output 1, others 0
def get_batch_test(dict_, categories, N, test_class_sequential = False):
    global test_class_index
    categories_batch = rd.sample(categories, N)
    
    if test_class_sequential == True:
        #print("<==========Sequential Test==========>")
        categories_temp = categories.copy()
        categories_temp.remove(categories[test_class_index])
        categories_batch[0] = categories[test_class_index]
        categories_batch[1:] = rd.sample(categories_temp, N - 1)
        if test_class_index == int(len(categories) - 1):
            test_class_index = 0
            #print("<==========Sequential Test END==========>")
        else:
            test_class_index += 1
    test_data = dict_[categories_batch[0]]
    test_sample = test_data[np.random.choice(test_data.shape[0], 2, replace=True)]  #test_smaple[0] the test flow, [1] is the first vector in N comparing vectors
    test_sample_copies = np.zeros((N, data_length, 1))    # copy test flow N times to compare with the N labeled flows
    support_set = np.zeros((N, data_length, 1))  # N labeled flows to be compared with the test flow. The first one should be of the sample category with the test flow.
    test_sample_copies[0,:,:] = test_sample[0]
    support_set[0,:,:] = test_sample[1]
    
    label = np.zeros((N,))
    label[0,] = 1
    
    
    categories_except_test = categories.copy()
    categories_except_test.remove(categories_batch[0])
    for i in range(1, N):
        if categories_batch[i] == categories_batch[0]:
            categories_batch[i] = rd.choice(categories_except_test)
        support_data = dict_[categories_batch[i]]
        support_set[i,:,:] = support_data[np.random.choice(support_data.shape[0], 1, replace=True)]
        test_sample_copies[i,:,:] = test_sample[0].copy()
            
#     print(test_image.shape, support_set.shape)
    test_image_copies, support_set, label = shuffle(test_sample_copies, support_set, label)
    return test_image_copies, support_set, label


def test(model, dict_, categories, N, test_num, test_class_sequential = False):
    correct_num = 0
    print("Use " + str(N) + " way one-shot learning on " + str(test_num) + " test sets.")
    totalloadtime = 0
    totalcalcutime = 0
    for i in range(test_num):  # test test_num cases
        time1 = time.time()
        test_image_copies, support_set, label = get_batch_test(dict_, categories, N, test_class_sequential)
        time2 = time.time()
        probs = model.predict([test_image_copies, support_set])
        time3 = time.time()
        totalloadtime += (time2 - time1)
        totalcalcutime += (time3 - time2)
        if np.argmax(probs) == np.argmax(label):
            correct_num += 1
    accuracy = 1.0 * correct_num / test_num
    print("Accuracy is " + str(accuracy))
    return accuracy, totalloadtime / totalcalcutime
    

path = './'
train_dict, test_dict, categories, data_length = read_data(path,  mode = 'px')
print(train_dict.keys())
clear_session()
print("session cleared")
model = siamese_model((data_length, 1))
print("model constructed")
# model = siamese_model_p((data_length, 1))
model.summary()

# plot the siamese model
#plot_model(model, show_shapes=True, show_layer_names=True)

#optimizer = Adam(6e-5)
optimizer = Adam(lr=0.001)
model.compile(loss="binary_crossentropy", optimizer=optimizer)
#model.compile(loss="categorical_hinge",optimizer=optimizer)
test_class_index = 0

# Hyper parameters
evaluate_every = 10 # interval for evaluating on one-shot tasks
#batch_size = 16
batch_size = 256# No. of training pairs for each iteration (half of same category and half different)
n_iter = 2000 # No. of training iterations
N_way = 2 # how many classes for testing one-shot tasks
#n_val = 200
n_val = 100 # how many one-shot tasks (test flows) to validate on
best = -1

print("Starting training process!")
print("-------------------------------------")
t_start = time.time()
train_result = {
    'iter_num':[],
    'accuracy':[],
    'loss':[]
}

# model.reset_states()

for i in range(1, n_iter+1):
    batch_1, batch_2, label = get_batch_1(train_dict, categories, batch_size)
    loss = model.train_on_batch([batch_1, batch_2], label)
    if i % evaluate_every == 0:
        print("\n ------------- \n")
        print("Time for {0} iterations: {1} mins".format(i, (time.time()-t_start)/60.0))
        print("Train Loss: {0}".format(loss)) 
        timestart = time.time()
        val_acc , lc_ratio = test(model, test_dict, categories, N_way, n_val)
        timeend = time.time()
        print("sample numbers: ", n_val)
        print("timeused: ", timeend  - timestart)
        print("average time for sample: ", (timeend - timestart)/n_val)
        print("lc_ratio: ", lc_ratio)
        #model.save_weights(os.path.join(model_path, 'weights.{}.h5'.format(i)))
        print("Current best: {0}, previous best: {1}".format(val_acc, best))
        #accurracy.append((i, val_acc))
        train_result['iter_num'].append(i)
        train_result['accuracy'].append(val_acc)
        train_result['loss'].append(loss)
        if val_acc >= best:
            best = val_acc
            
from keras.models import load_model
model.save('siamese_'+str(best)+'.h5')  # creates a HDF5 file 'my_model.h5'
