#Courtney Comrie and Sam Freitas
#ECE 523 Final Project
#UNET-CNN for segmenting brains from the skull

import numpy as np #import needed libraries and commands
import pandas as pd 
import matplotlib.pyplot as plt
import cv2
from cv2 import imread
import os
import sys
from tqdm import tqdm
import random
import warnings
from itertools import chain
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dropout, Lambda, Conv2D, Conv2DTranspose, MaxPooling2D, concatenate
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras import backend as K
import tensorflow as tf
import shutil
import glob
from natsort import natsorted

from dynamic_unet import dynamic_unet_cnn

plt.ion() #turn ploting on

#dataset_path = r"C:\Users\cjoy1\Documents\Grad School\Second Year Spring\ECE 523\Homework\Final_Project\mr_images_png" #initialize paths and dataset
dataset_path = os.getcwd()
image_path = os.path.join(dataset_path, "testing")
dataset = pd.read_csv('dataset.csv')

def data_generator(image_path, height, width): #function for generating data

    dataset = natsorted(glob.glob(os.path.join(image_path,'*.png')))

    images = np.zeros((len(dataset),height,width,3), dtype = np.uint8) #initialize training sets (and testing sets)

    sys.stdout.flush() #write everything to buffer ontime 

    for i, this_img_path in enumerate(dataset):

        image = imread(this_img_path)

        img_resized = cv2.resize(image,(height,width))

        images[i] = img_resized

    return images

def plot_figures(image,pred_mask,num): #function for plotting figures
    plt.figure(num,figsize=(12,12))
    plt.subplot(131)
    plt.imshow(image)
    plt.title("Input Image")
    plt.subplot(132)
    plt.imshow(pred_mask.squeeze(),cmap='gray')
    plt.title('Predicted Mask')
 

total = len(dataset) #set variables
test_split = 0.2
height = 128
width = 128
channels = 3 
batch_size = 32

num_layers_of_unet = 4
starting_kernal_size = 16

model = dynamic_unet_cnn(height,width,channels,num_layers_of_unet,starting_kernal_size)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'], run_eagerly = True)
model.summary() #display model summary

model = load_model('lightsaver_weights.h5') #load weights

#model = load_model("lightsaver_weights.h5") #reload model for testing
images = data_generator(image_path,height,width) #get test set
images = images / 255 #thresh y_test
# results = model.evaluate(X_test,y_test,steps=1) #get evaluation results

output_path = os.path.join(os.getcwd,'output_images')
try:
    os.mkdir(output_path)
except:
    shutil.rmtree(output_path)
    os.mkdir(output_path)

count = 1 #counter for figures in for loops
for image in images: #for loop for plotting images
    
    img = image.reshape((1,height,width,channels)).astype(np.uint8)
    pred_mask = model.predict(img)
    pred_mask = (pred_mask > 0.5).astype(np.uint8)

    plot_figures(image,pred_mask, count)
    count += 1

    if count>10:
        break

plt.ioff()
plt.show()