import os, json, argparse
import ML_Methods, Image_Tools
import pandas as pd
from PIL import Image 
import numpy as np
import matplotlib.pyplot as plt

#image processor and retrival might be made into a separate module 

def imaging_processor(dataset, size = 256., tf_aug = False):

	list_label_images= [] 
	list_images = []

	dataset = int(dataset)
	print("dataset number: \t" + str(dataset))
	
	if (dataset == 1):		
		return Image_Tools.load_A(size, tf_aug)

	if (dataset == 2):
		return Image_Tools.load_B(size, tf_aug)
				
	if (dataset == 3): 
		#tempA = load_A(imagesize)
		list_images_B, list_label_images_B= Image_Tools.load_B(size, tf_aug)
		list_images_A, list_label_images_A= Image_Tools.load_A(size, tf_aug)

		print(np.shape(list_images_B))
		print(np.shape(list_images_A))
		list_images = np.concatenate((list_images_A,list_images_B))
		list_label_images = np.concatenate((list_label_images_A,list_label_images_B))
		
		return list_images, list_label_images

	if (dataset == 4):
		#added for 
		print("other microscopy images")
	
def model_branch(results, image_vector, label_vector):


	if(results.parameters == {}):
	
		if(results.sgd):
			print("SGD model selected..")
			results.type_train = "sgd"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)

		elif(results.svm):
			print("SVM model selected...")
			results.type_train = "svm"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)
			
		elif(results.nn):
			print("NN model selected...")
			results.type_train = "nn"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)
			
		elif(results.cnn):
			print("CNN model selected...")
			results.type_train = "cnn"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)
			
		elif(results.xgb):
			print("xgb model selected...")
			results.type_train = "xgb"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)


		elif(results.rf):
			print("Loading Random Forest")
			results.type_train = "rf"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)

		elif(results.resnet):
			print("Loading Resnet")
			results.type_train = "resnet"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)

		elif(results.lenet):
			print("Loading Lenet Structure")
			results.type_train = "lenet"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)

		else:
			print("Defaulting to CNNs...")
			results.type_train = "cnn"
			ml = ML_Methods.Methods(results)
			ml.iterator(image_vector, label_vector)

	
	else: 
		print("add custom options, NOT WORKING YET")

if  __name__=="__main__":
	#arguement parsing for options 
	parser = argparse.ArgumentParser(description='Model Selector and Parameters')

	
	parser.add_argument("--sgd", action = 'store_true' , dest= 'sgd', default = False,  help = "increase output printing")
	parser.add_argument("--svm", action = 'store_true' , dest= 'svm', default = False,  help = "increase output printing")
	parser.add_argument("--nn", action = 'store_true' , dest= 'nn', default = False,  help = "increase output printing")
	parser.add_argument("--cnn", action = 'store_true' , dest= 'cnn', default = False,  help = "increase output print ing")
	parser.add_argument("--xgb",action = 'store_true' , dest= 'xgb', default = False,  help = "increase output printing")
	parser.add_argument("--rf",action = 'store_true' , dest= 'rf', default = False,  help = "random forest")
	
	parser.add_argument("--resnet",action = 'store_true' , dest= 'resnet', default = False,  help = "resnet")
	parser.add_argument("--lenet",action = 'store_true' , dest= 'lenet', default = False,  help = "resnet")
	
	parser.add_argument("--gocrazy",action = 'store_true' , dest= 'crazy', default = False,  help = "zoo of random models")

	parser.add_argument("-v","--verbose", action = 'store_true' , dest= 'verbose', default = False,  help = "increase output printing")
	parser.add_argument("--augment", action = 'store_true', dest= "aug", default = False, help = "Augment data using basic transformations")
	parser.add_argument('-custom',action="store",  dest = 'parameters', default = {}, type=json.loads)
	parser.add_argument("-iter", action = "store", dest = "iterations",default = 1,  help= "number of random models tested")
	parser.add_argument("-imsize", action = "store", dest = "imsize",default = 256,  help= "number of models")
	parser.add_argument("-epochs", action = "store", dest = "epochs",default = 50,  help= "epochs")
	parser.add_argument("-dataset", action = "store", dest = "dataset", default = 3, help = "choose which dataset for training")
	parser.add_argument("-transfer", action = "store", dest = "transfer", default = 1, help = "pretrained networks")

	results = parser.parse_args()
	results.iterations = int(results.iterations)
	results.imsize = int(results.imsize)
	results.epochs = int(results.epochs)

	#generate images using image_processor 

	print("______________Options Selected_____________")
	print("verbose: \t\t"+str(results.verbose))
	print("# of models trained:\t"+ str(results.iterations))
	if(results.parameters == {}):
		print("custom parameters? \tFalse")
	else:
		print("custom parameters? \tTrue")
	print("size of ea. images: \t" + str(results.imsize))
	print("Zoo of models? \t\t" + str(results.crazy))
	#print("Dataset to be used:\t" + str(results.dataset))
	print("___________________________________________")
	print("loading images for training...")
	############## maybe process this once and simply load a database/numpy array of it 
	#add_distrorion_factor

	tf_aug = False
	if ((results.cnn or results.nn) and results.aug):
		tf_aug = True
	
	image_vector, label_vector = imaging_processor(results.dataset,results.imsize, tf_aug)
	####temp

	##############
	print("images loaded")

	if (results.crazy == True):
		for i in range(50):
			results.custom = False 
			results.iterations = 1 
			results.epochs = 30
			#select random parameters
			model_branch(results, image_vector, label_vector)
			print("something")

	else:
		model_branch(results, image_vector, label_vector)


	











