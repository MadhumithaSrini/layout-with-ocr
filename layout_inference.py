import sys
import requests
import tarfile
import json
import numpy as np
from os import path
from PIL import Image
from PIL import ImageFont, ImageDraw
from glob import glob
from matplotlib import pyplot as plt
import cv2

import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()
import argparse
from detectron2.engine import DefaultTrainer, default_argument_parser, default_setup, hooks, launch

# import some common libraries
import numpy as np
import os, json, cv2, random
from google.colab.patches import cv2_imshow

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.utils.visualizer import ColorMode

from detectron2.structures import BoxMode
import yaml
from detectron2.data.datasets import register_coco_instances

config_filePath = "configs/layout_parser_configs"

index = 1
config_filesDict = {}
for cfile in os.listdir(config_filePath):
    config_filesDict[index] = cfile
    print(index,":",cfile)
    index+=1

print(" ")
chosenFile = input("choose the model for the inference : ")
print("Selected Model = ",config_filesDict[int(chosenFile)])

config_file = config_filePath + '/' + config_filesDict[int(chosenFile)]
print(" ")
config_name = config_filesDict[int(chosenFile)]

custom_config = "custom_labels_weights.yml"
with open(custom_config, 'r') as stream:
    custom_yml_loaded = yaml.safe_load(stream)

#CAPTURE MODEL WEIGHTS
model_weights = custom_yml_loaded['MODEL_CATALOG'][config_name]
label_mapping = custom_yml_loaded['LABEL_CATALOG']["Sanskrit_Finetuned"]

print(model_weights)

# Choosing the image for the inference
input_image_path = 'test_img/'
input_choice = input("Choose a random image (yes/no) : ")
isRandom = True
if input_choice == 'no':
    isRandom = False
if isRandom == False:
    image_name = input("Enter the image name : ")
    input_image_path = image_name
else:
    random_image_name = random.choice(os.listdir(input_image_path))
    input_image_path = input_image_path + random_image_name

print("Selected image = ",input_image_path)
print(" ")

# Setting the confidence threshold
confidence_threshold = float(input("Set the confidence threshold, choose from 0 to 1 (eg: 0.7) : "))
print(" ")

# Getting the output folder
output_folderName = input("Please enter the output folder name : ")

if not os.path.exists(output_folderName):
    os.makedirs(output_folderName)

#SET CUSTOM CONFIGURATIONS

cfg = get_cfg()
cfg.merge_from_file(config_file)
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold # set threshold for this model
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 5

print("ROI Heads is taken as",cfg.MODEL.ROI_HEADS.NUM_CLASSES)

cfg.MODEL.WEIGHTS =  model_weights

# GET PREDICTIONS

predictor = DefaultPredictor(cfg)
im = cv2.imread(input_image_path)
cv2_imshow(im)
outputs = predictor(im)

# SAVE PREDICTIONS

img = Image.open(input_image_path)
c=0
for score, box, label in zip(scores, boxes, labels):
    x_1, y_1, x_2, y_2 = box
    label_name = label_mapping[label]
    if not os.path.isdir(f"{output_folderName}/{label_name}"):
        os.mkdir(f"{output_folderName}/{label_name}")
    img_cropped = img.crop((box))
    img_name = label_name + "_" + str(c) + ".jpg"
    im1 = img_cropped.save(f"{output_folderName}/{label_name}/{img_name}")
    c+=1
