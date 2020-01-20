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


def read_data(path, num=40, mode='inter'):
    train_dict = {}
    test_dict = {}
    categories = []
    for filepath in os.listdir(path):
        if "_"+mode not in filepath:
            continue
        category = filepath.split('.')[0].split('_')[0]
        info = filepath.split('.')[0].split('_')[1]      
        if info == mode:
            print('Reading from:', filepath)
            categories.append(category)
            
            d = np.loadtxt(path+filepath, delimiter=' ')
            d = d[np.random.choice(d.shape[0], num, replace=False)]
            
            train_num = int(num*0.5)
            indices = np.arange(num)
            train_indices = np.random.choice(indices, train_num, replace=False)
            test_indices = np.setdiff1d(indices, train_indices)

            train_dict[category] = d[train_indices].reshape(train_num,d.shape[1],1)
            test_dict[category] = d[test_indices].reshape(num-train_num,d.shape[1],1)
            print('training data size:', train_dict[category].shape)
            print('test data size:', test_dict[category].shape)
    
    return train_dict, test_dict, categories, d.shape[1]
    

path = './'
train_dict, test_dict, categories, data_length = read_data(path, num = 40, mode = 'pi')

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
print(train_dict.keys())

def siamese_model(input_shape):
    """
        Model architecture based on the one provided in: http://www.cs.utoronto.ca/~gkoch/files/msc-thesis.pdf
    """
    
    # Define the tensors for the two input images
    left_input = Input(input_shape)
    right_input = Input(input_shape)
    
    # Convolutional Neural Network
    model = Sequential()
    model.add(Conv1D(64, 5, activation='relu', input_shape=input_shape, kernel_initializer=initialize_weights, kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling1D())
    model.add(Conv1D(128, 3, activation='relu',
                     kernel_initializer=initialize_weights,
                     bias_initializer=initialize_bias, kernel_regularizer=l2(2e-4)))
    model.add(MaxPooling1D())
#     model.add(Conv1D(128, 2, activation='relu', kernel_initializer=initialize_weights,
#                      bias_initializer=initialize_bias, kernel_regularizer=l2(2e-4)))
#     model.add(MaxPooling1D())
    model.add(Conv1D(256, 2, activation='relu', kernel_initializer=initialize_weights,
                     bias_initializer=initialize_bias, kernel_regularizer=l2(2e-4)))
    model.add(Flatten())
    model.add(Dense(4096, activation='sigmoid',
                   kernel_regularizer=l2(1e-3),
                   kernel_initializer=initialize_weights,bias_initializer=initialize_bias))
    
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

clear_session()
model = siamese_model((data_length, 1))
# model = siamese_model_p((data_length, 1))
model.summary()

# plot the siamese model
#plot_model(model, show_shapes=True, show_layer_names=True)

optimizer = Adam(6e-5)
model.compile(loss="binary_crossentropy", optimizer=optimizer)

def get_batch_1(dict_, categories, batch_size):
    
    categories_batch = np.random.choice(categories, batch_size)
#     print(categories_batch)
    
#     First half use same class
    division_point = int(batch_size / 2)
    
    batch_1 = np.zeros((batch_size, data_length, 1))
    batch_2 = np.zeros((batch_size, data_length, 1))

    label = np.zeros((batch_size,))
    
    for i in range(batch_size):
        data_temp = dict_[categories_batch[i]]
        if i <= division_point:
            data_batch = data_temp[np.random.choice(data_temp.shape[0], 2, replace=True)]
            batch_1[i,:,:] = data_batch[0].reshape(data_length,1)
            batch_2[i,:,:] = data_batch[1].reshape(data_length,1)
            label[i] = 1
        else:
            categories_temp = categories.copy()
            categories_temp.remove(categories_batch[i])
            batch_1[i,:,:] = data_temp[rd.randint(0, len(data_temp) - 1)]
            data_temp_2 = dict_[rd.sample(categories_temp, 1)[0]]
            batch_2[i,:,:] = data_temp_2[np.random.choice(data_temp_2.shape[0], 1, replace=True)]
            
#     print(batch_1.shape, batch_2.shape)
    batch_1, batch_2, label = shuffle(batch_1, batch_2, label)
    return batch_1, batch_2, label
    

test_class_index = 0

def get_batch_test(dict_, categories, N, test_class_sequential = False):
    
    global test_class_index
#     print(categories)
    categories_batch = rd.sample(categories, N)
#     print(categories_batch)
    
    if test_class_sequential == True:
        #print("<==========Sequential Test==========>")
        categories_temp = categories.copy()
        categories_temp.remove(categories[test_class_index])
        categories_batch[0] = categories[test_class_index]
        categories_batch[1:] = rd.sample(categories_temp, N - 1)
#         print(categories_batch)
        if test_class_index == int(len(categories) - 1):
            test_class_index = 0
            #print("<==========Sequential Test END==========>")
        else:
            test_class_index += 1
    
    test_data = dict_[categories_batch[0]]
    test_sample = test_data[np.random.choice(test_data.shape[0], 2, replace=True)]
    
    test_sample_copies = np.zeros((N, data_length, 1))
    support_set = np.zeros((N, data_length, 1))
    
    test_sample_copies[0,:,:] = test_sample[0]
    support_set[0,:,:] = test_sample[1]
    
    label = np.zeros((N,))
    label[0,] = 1
    
    for i in range(1, N):
#         print(i, len(dict_[categories_batch[i]]))
        support_data = dict_[categories_batch[i]]
        support_set[i,:,:] = support_data[np.random.choice(support_data.shape[0], 1, replace=True)]
        test_sample_copies[i,:,:] = test_sample[0].copy()
            
#     print(test_image.shape, support_set.shape)
    test_image_copies, support_set, label = shuffle(test_sample_copies, support_set, label)
    return test_image_copies, support_set, label


def test(model, dict_, categories, N, test_num, test_class_sequential = False):
    correct_num = 0
    print("Use " + str(N) + " way one-shot learning on " + str(test_num) + " test sets.")
    
    for i in range(test_num):
        test_image_copies, support_set, label = get_batch_test(dict_, categories, N, test_class_sequential)
        probs = model.predict([test_image_copies, support_set])
#         print(probs)
        if np.argmax(probs) == np.argmax(label):
        
#             print("Bingo!!!")
            correct_num += 1
#         else:
#             print("Ah-oh...")
    accuracy = 1.0 * correct_num / test_num
    print("Accuracy is " + str(accuracy))
    return accuracy

# Hyper parameters
evaluate_every = 10 # interval for evaluating on one-shot tasks
batch_size = 16
n_iter = 2000 # No. of training iterations
N_way = 8 # how many classes for testing one-shot tasks
n_val = 200 # how many one-shot tasks to validate on
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
        val_acc = test(model, test_dict, categories, N_way, n_val)
        #model.save_weights(os.path.join(model_path, 'weights.{}.h5'.format(i)))
        print("Current best: {0}, previous best: {1}".format(val_acc, best))
#         accurracy.append((i, val_acc))
        train_result['iter_num'].append(i)
        train_result['accuracy'].append(val_acc)
        train_result['loss'].append(loss)
        if val_acc >= best:
            best = val_acc
            
# from keras.models import load_model
# model.save('siamese_'+str(best)+'.h5')  # creates a HDF5 file 'my_model.h5'