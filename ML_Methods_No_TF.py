import sys
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import Augmentor 
import joblib

from sklearn import svm, linear_model, metrics
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, roc_curve, auc
from sklearn.naive_bayes import ComplementNB
from sklearn import ensemble
from sklearn.preprocessing import MinMaxScaler



from ML_Helpers_No_TF import stats

class Methods: 

	def __init__(self, results):
		self.results = results
		self.iterations = results.iterations
		self.type_train = results.type_train
		self.parameters = results.parameters
		self.epochs = results.epochs
		self.verbose = results.verbose
		self.dataset = results.dataset
		self.transfer = results.transfer
		self.dataset = results.dataset
		self.aug = results.aug
		self.imsize = results.imsize
		#opens global database of models that have worked 

	def iterator(self, image_vector, label_vector):
		#add reasonable parameter ranges for all of these 
		for i in range(self.iterations):
			print("_____NEW MODEL NOW TRAINING_____")	
			if(self.type_train == "sgd"):
				self.sgd_method(image_vector, label_vector, self.parameters)
			elif(self.type_train == "svm"):
				self.svm_method(image_vector, label_vector, self.parameters)
			elif(self.type_train == "xgb"):
				self.xgboost_method(image_vector, label_vector, self.parameters)
			elif(self.type_train == "rf"):
				self.random_forest_method(image_vector, label_vector, self.parameters)
			else:
				print("INVALID MODEL TYPE")
	
	def save_model_to_db(self, parms):
		#opens database and deposits statistics to database
		temp = pd.DataFrame.from_dict(parms)
		master = pd.read_pickle("./Algorithm_DB/***statistics_DONTDELETE.pkl")
		master = master.append(temp, sort=True)
		master.to_pickle("./Algorithm_DB/***statistics_DONTDELETE.pkl")

	def parameter_generator(self, range_min, range_max, type_number = "not_exp"):
		#general parameter generator used heavily below
		num = np.random.random() * (range_max- range_min)  + range_min

		if (type_number == "exp"):
			num = 10**num
		return num

	def time_string(self):
		#used to generate unique names for the models
		now = datetime.datetime.now()
		time_nice = str(now.year) +"-"+ str(now.month) +"-"+ str(now.day) +"-"+ str(now.hour) +"-"+ str(now.minute) +"-" + str(now.second)
		return time_nice

	def sgd_method(self, image_vector, label_vector, parameters):
		
		# loss 			- log is reasonable "hinge", "log", "square_hinge", "preceptron", "squared loss"
		# max_iter 		- "epochs" def 1000
		# alpha 		- rate of learning/change def 0.0001 
		# verbose 		- verbose def 0  
		# tol 			- tolerances before premature stop def 1e-3

		#full parameter generator
		alpha 		= self.parameter_generator(-3,-8, "exp")
		max_iter	= self.parameter_generator(3,6,"exp")
		tol 		= self.parameter_generator(-3,-8,"exp")
		loss_array 	= ['log', 'hinge','preceptron','squared_loss']
		loss 		= loss_array[np.random.randint(0, 4)]
		params = {}

		#save parameters generated
		temp_parameters = [[loss, alpha, max_iter, tol]]
		
		#discritize data
		if (int(self.dataset) == 2 or int(self.dataset) == 3):
			#0.2 for eh results on dataset 2/3
			label_vector = np.rint(label_vector + 0.2)
		#split
		X_train, X_test, y_train, y_test = train_test_split(image_vector, label_vector, test_size=0.2)

		#define model
		clf = linear_model.SGDClassifier(loss = 'log',alpha = alpha, max_iter=max_iter, tol=tol, early_stopping= False)	
			
		#extract training time
		t1 = time.time()
		clf.fit(X_train, y_train)
		time_temp = time.time() - t1
		#extract statistics
		params = stats(clf, image_vector, label_vector, X_train, X_test, y_train, y_test, time_temp)
		name = "Algorithm_DB/sgd_" + self.time_string() + ".pkl"

		#save parameters to dictionary
		params["train_time"] = time_temp
		params["dataset"] = self.dataset
		params["ref"] = name 
		params["parameters"] = temp_parameters
		params["aug"]  = False
		params["type"] = "sgd"
		params["imsize"] = self.imsize

		#joblib.dump(clf, name)
		self.save_model_to_db(params)	
	
	def svm_method(self, image_vector, label_vector, parameters):
		###parameters####
		# C 				- penalty def 1.0
		# kernel function 	- linear, rbf, poly, sigmoid, precomputed
		# degree			- of poly def = 3
		# gamma 			- float, def is 1/features for rbf ,poly, sigmoid 
		# coef0				- def 0.0 for poly, sigmoid
		# tol 				- early stopping, def = 1e-3
		# class_weight		- use to adjust class weight, USE {dict, 'balanced'}
		# verbose			- def 0 

		loss_array 	= ['linear','rbf','poly','sigmoid']
		loss 		= loss_array[np.random.randint(0, 3)]
		C 			= self.parameter_generator(5,-5,"exp")
		max_iter 	=  self.parameter_generator(3,6,"exp")
		degree 		= np.random.randint(3, 10)		
		tol 		= self.parameter_generator(-3,-8,"exp")
		coef0 		= 0
		gamma 		= 0
		
		params = {}
		temp_parameters = [[loss, C, degree, gamma, coef0, tol]]

		if (int(self.dataset) == 2 or int(self.dataset) == 3):
			label_vector = np.rint(label_vector)
			#print("percent positive: " + str(np.sum(label_vector)/len(label_vector)))
		#split
		X_train, X_test, y_train, y_test = train_test_split(image_vector, label_vector, test_size=0.2)	
		scaling = MinMaxScaler(feature_range=(-1,1)).fit(X_train)
		X_train = scaling.transform(X_train)
		X_test = scaling.transform(X_test)
		#TODO PARAMETERS HERE
		if(loss == "rbf"):
			clf = svm.SVC(kernel = loss, C = C, probability = True, tol = tol,verbose = self.verbose)		
		elif(loss == "poly"):
			clf = svm.SVC(kernel = loss, C = C, probability = True, tol = tol,verbose = self.verbose)		
		elif(loss == "sigmoid"):
			clf = svm.SVC(kernel = loss, C = C, probability = True, tol = tol,verbose = self.verbose)		
		else:
			clf = svm.SVC(kernel = loss, C = C, probability = True, tol = tol,verbose = self.verbose)		

		#training time
		t1 = time.time()
		clf.fit(X_train, y_train)
		time_temp = str(time.time() - t1)

		params = stats(clf, image_vector, label_vector, X_train, X_test, y_train, y_test, time_temp)
		name = "Algorithm_DB/svm_" + self.time_string() + ".pkl"
		params["train_time"] = time_temp
		params["dataset"] 		= self.dataset
		params["ref"] 			= name 
		params["parameters"] 	= temp_parameters
		params["aug"]  			= False
		params["type"] 			= "svm"


		joblib.dump(clf, name)
		self.save_model_to_db(params)
	
	def xgboost_method(self, image_vector, label_vector, parameters):
		###Parameters###
		# learning_rate 		learning rate for iterations def 0.01
		# max_depth 			tree depth def 4
		# subsample 			percentage of samples used in any round def 0.8
		# colsample_bytree 		percentage of features used per tree def 1
		# n_estimators 			number of trees to build def 100
		# objective 			loss function def "binary:logistic", "binary:logitraw", "binary:hinge"
		# gamma  				controls tree splitting, def 0 
		# alpha = L1 			l1 regularization def 0 
		# lambda = l2 			l2 regularization def 0
		# reg_alpha = 0.3
		# tol  					tolerance def 1e-3
		# silent = false


		objective 		= "binary:logistic"
		colsample_bytree = 0.8
		learning_rate 	= 0.1
		n_estimators 	= 100
		alpha 			= 0
		max_depth 		= 10
		lamb 			= 0
		gamma 			= 0
		n_jobs 			= 1
		subsample 		= 1
		tol 			= 1e-4
		params = {}

		if (int(self.dataset) == 2 or int(self.dataset) == 3):
			label_vector = np.rint(label_vector)
			#print("percent positive: " + str(np.sum(label_vector)/len(label_vector)))


		temp_parameters = {"objective":objective, "learning_rate": learning_rate, "n_estimators": n_estimators, "max_depth": max_depth,"colsample_bytree": colsample_bytree, "alpha": alpha, "gamma":gamma, "lambda":lamb, "subsample": subsample}
		#temp_parameters = {'objective':'binary:logistic', 'n_estimators':2}

		#xg_clas = XGBClassifier()
		gb = ensemble.GradientBoostingClassifier(n_estimators=n_estimators, random_state=0, verbose =1)
		X_train, X_test, y_train, y_test = train_test_split(image_vector, label_vector, test_size=0.2)	
		
		t1 = time.time()
		gb.fit(X_train,y_train)
		time_temp = time.time() - t1
		name = "Algorithm_DB/xgb_" + self.time_string() + ".pkl"


		params = stats(gb, image_vector, label_vector, X_train, X_test, y_train, y_test, time_temp)
		params["train_time"] = time_temp
		params["dataset"] = self.dataset
		params["ref"] = name 
		params["parameters"] = temp_parameters
		params["aug"]  = False
		params["type"] = "xgb"


		joblib.dump(clf, name)
		self.save_model_to_db(params)

	def random_forest_method(self, image_vector, label_vector, parameters):
			# n_estimators 			number of estimators, def 50
			# max_depth 			depth of decision trees, def 5
			# max_features 			number of features, def 1
			# verbose 				def 0
			
			#define baseline values for each term 


			#these algorithms require discrete labels
			if (int(self.dataset) == 2 or int(self.dataset) == 3):
				label_vector = np.rint(label_vector)
				print("percent positive: " + str(np.sum(label_vector)/len(label_vector)))

			X_train, X_test, y_train, y_test = train_test_split(image_vector, label_vector, test_size=0.2)

			clf = RandomForestClassifier(n_estimators = 50, n_jobs=10)

			#obtaining training time
			t1 = time.time()
			clf.fit(X_train,y_train)
			time_temp = time.time() - t1
			#generate vital stats
			params = self.stats(clf, image_vector, label_vector, X_train, X_test, y_train, y_test, time)
			#unique name identifier
			name = "Algorithm_DB/rf_" + self.time_string() + ".pkl"
			params["train_time"] = time_temp
			params["dataset"] 		= self.dataset
			params["ref"] 			= name 
			params["parameters"] 	= temp_parameters
			params["aug"]  			= False
			params["type"] 			= "svm"			
			joblib.dump(clf, name)
			self.save_model_to_db(name, parms)

