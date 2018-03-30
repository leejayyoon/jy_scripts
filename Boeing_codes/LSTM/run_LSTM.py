#!/usr/bin/python 
import numpy as np
import cPickle as pickle
import time
import sys 
import io
import h5py
import data_handle_Boeing as dh

from keras.models import Sequential
# from keras.models import Graph
from keras.layers.core import Dense, Activation, RepeatVector, Reshape
from keras.layers import Embedding, Merge
from keras.layers.recurrent import LSTM
from keras.models import model_from_json
from sklearn.preprocessing import MinMaxScaler

norm_mse_list = []
mmmpa_list = []
#control model folder, f_out folder to save results in different folder

def prep_data(data_array, prev_steps, test_beg, test_end, normalize=False):
	'''
		Assumes that data_array already has 0 beginning trenched.
	'''
	prev_steps = prev_steps + 1 # considering how array indexing works with len() & open bracket on the right side
	data_mx = []
	for i in range(len(data_array) - prev_steps):
		data_mx.append(data_array[i: i + prev_steps])

	data_mx = np.array(data_mx)

	# test_beg = len(data_array)-15 # right now, 2016 Aug is the last one & test_beg = 2015 June, test_end = 2016 June
	# test_end = len(data_array)-2 # 
	train = data_mx[:test_beg, :]
	test = data_mx[test_beg: test_end, :]
	np.random.shuffle(train)
	x_train = train[:, :-1]
	y_train = train[:, -1]
	x_test = test[:, :-1]
	y_test = test[:, -1]

	# normalize data
	if normalize:
		scaler = MinMaxScaler(feature_range=(0, 1)) 
		x_train = scaler.fit_transform(x_train)
		x_test = scaler.fit_transform(x_test)
		y_train = scaler.fit_transform(y_train)
		y_test = scaler.fit_transform(y_test)
	# LSTM input structure: [samples, time steps, features]
	x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1)) 
	x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))  

	return [x_train, y_train, x_test, y_test]

def make_filename(input_path,part_id,directory="raw"):
	return input_path + "/" + directory + "/" + part_id + ".csv"

def runLSTM(item_nm, X_train, X_test, y_train, y_test, binary_on=False, hidden_neurons =32, n_epoch= 100):
	''' params
		item_nm: string to identify each part_id
		X_train, X_test: (samples, time steps, input dim)
		y_train, y_test: (nb_samples, output_dim).
		hidden_neuron: is the dimension for the c_t & h_t
		binary_on: whether I want the output to be classification problem.
	'''
	in_neurons = X_train.shape[-1] # input dimension: size of the last dim of X_train
	out_neurons = X_train.shape[-1] #
	n_batch = int(round(len(X_train)/4.0))
	print 'batch size', n_batch

	model = Sequential()
	model.add(LSTM(hidden_neurons, input_dim=in_neurons, return_sequences=False))
	model.add(Dense(out_neurons, input_dim=hidden_neurons))
	model.add(Activation("linear")) # do not use sigmoid as it will only limit the capacity.
	model.compile(loss='mean_squared_error', optimizer="rmsprop")

	print "model compiled."
	print "n_epoch", n_epoch 
	if binary_on :
		temp = np.divide(y_train,np.abs(y_train))
		y_train_label = np.where(temp>0,temp,-1)
		temp = np.divide(y_test,np.abs(y_test))
		y_test_label = np.where(temp>0,temp,-1)
		hist = model.fit(X_train, y_train_label, batch_size=n_batch, nb_epoch=n_epoch, validation_split=0.1)  
	else:
		hist = model.fit(X_train, y_train, batch_size=n_batch, nb_epoch=n_epoch, validation_split=0.1)  

	print "model trained and saving the model to h5py ..."
	json_string = model.to_json() # to save the model
	fhandle = open('model/'+item_nm+'model_architecture.json', 'w')
	fhandle.write(json_string)
	fhandle.close()
	model.save_weights('model/'+item_nm+'model_weight.h5', overwrite=True) # saving the model weights to Json

	# to read from this
	# model = model_from_json(open('my_model_architecture.json').read())
	# model = model_from_json(json_string) # in order to retreive the model
	print "Prediction and recording rmse ..."

	predicted = model.predict(X_test)
	predicted = np.nan_to_num(np.array(predicted)) # converting nan to 0
	predicted[predicted < 0] = 0
	# print 'predicted.shape', predicted.shape  
	# print 'y_train.shape', y_test.shape  
	# print 'y_test.shape', y_test.shape  
	y_test = np.expand_dims(y_test,axis=1)
	# sqr_err = np.square(predicted - y_test)
	y_train_mean = np.mean(y_train,axis=0) 
	# print 'y_train_mean.shape', y_train_mean.shape, (y_test-y_train_mean).shape
	norm_sqr_err = np.square((y_test-predicted)/(y_test-y_train_mean))
	norm_mse = np.mean(norm_sqr_err)
	# print 'y_test:', y_test, 'predicted:', predicted
	# print 'min:', np.minimum(y_test, predicted), ', max:', np.maximum(y_test,predicted)
	# print 'min.shape:', np.minimum(y_test, predicted).shape, ', max.shape:', np.maximum(y_test,predicted).shape
	numerator = np.minimum(y_test, predicted)
	denominator = np.maximum(y_test,predicted)
	MMMPA = numerator/denominator
	MMMPA[(np.isclose(numerator,0) & np.isclose(denominator,0))] = 1.0
	MMMPA = np.mean(MMMPA)

	# print 'MMMPA', mmmpa
	print 'mean MMMPA', MMMPA
	print 'mean_norm_sqr_err', norm_mse
	# print 'sqr_err', norm_sqr_err
	# print 'sqr_err.shape', norm_sqr_err.shape
	# sqr_err = sqr_err/np.max(sqr_err,axis=0)
	# rmse = np.sqrt(sqr_err.mean(axis=0))

	return norm_mse, MMMPA#hist.history
	# print 'Mean error: ', ( ((predicted - y_test_label)/2) ** 2).mean(axis=0).mean()  # Printing RMSE
	# print 'RMSE: ', np.sqrt(( ((predicted - y_test_label)) ** 2).mean(axis=0)).mean()  # Printing RMSE


def main():     
	''' objective type, classification (up, down?) '''
	prev_steps = 6
	num_hidden = 64
	binary_on = False
	n_epoch = 100
	# prev_steps = sys.argv[1]	 # string (needed just for the filename)
	# hidden_neurons = int(sys.argv[2]) # 60, 120, 240, 480, 1000
	# binary_on = sys.argv[3]      # 0 (almost always 0, since Alex doesn't want binary)
	# if(len(sys.argv)>3):
	# 	n_epoch = int(sys.argv[4])
	# 	data_saved = int(sys.argv[5])
	# else:
	# 	n_epoch = 50
	# data_saved = int(sys.argv[6])
	# snp_on = int(sys.argv[7])
	# model_type = sys.argv[8] # plain, emb, conv 

	# data loading
	time_beg = time.time()
	f_part_to_set = "/app/part-demand/data/aviall/part-to-chain.csv"
	part_to_set = dh.get_dictionary(f_part_to_set, False)
	# parts_interest_list = get_target_list("small")
	# count=0
	# for part_id in small_target_list:
	# 	if part_id not in part_to_set:
	# 		count+=1
	# print count
	boeing_ts, part_to_idx_dict, small_target_list = dh.load_data("small", "month", "boeing")
	intchg_merged_ts, set_to_idx_dict, small_target_list = dh.load_data("small", "month", "intchg")

	time_load  = time.time()
	print 'time on loading ...', time_load-time_beg
	print '========= Data is prepared ========'
	print 'Running LSTM on each part ...'
	# data processing info
	count = 0
	cut_off_first = 35
	# lists for results
	# norm_mse_list = []
	# mmmpa_list = []
	
	f_out = './exp_0509/normalized_out_lookback'+str(prev_steps)+'_nh'+str(num_hidden)+'_epoch'+str(n_epoch)
	# for normalization
	normalize=True		
	# loop for trainig LSTM of each model
	iter_count  = 0
	for part_id in small_target_list:
		t_lstm_beg = time.time() 
		if part_id in part_to_set:
			set_id = part_to_set[part_id]
			data_array = intchg_merged_ts[set_to_idx_dict[set_id]]
			if(data_array.shape[0]!= 115):
				print part_id
			data_array = data_array[cut_off_first:]
		else:
			data_array = boeing_ts[part_to_idx_dict[part_id]]
			if(data_array.shape[0]!= 115):
				print part_id
			data_array = data_array[cut_off_first:]
			count +=1

		test_beg = len(data_array)-15 # right now, 2016 Aug is the last one & test_beg = 2015 June, test_end = 2016 June
		test_end = len(data_array)-2 # 
		[x_train, y_train, x_test, y_test] = prep_data(data_array, prev_steps, test_beg, test_end, normalize)

		[norm_MSE, MMMPA] = runLSTM(str(part_id), x_train, x_test, y_train, y_test, binary_on=False, hidden_neurons =64, n_epoch= 100)
		norm_mse_list.append(norm_MSE)
		mmmpa_list.append(MMMPA)
		iter_count +=1
		print '=========== LSTM took', time.time()-t_lstm_beg,'for iter count: ', iter_count,' ( part ID: ', part_id,')=========='
		# save the result
		if iter_count%100 ==0 :
			pickle.dump([norm_mse_list, mmmpa_list],open(f_out,'wb'))

	time_fin_iter = time.time()
	print 'time on total iteration ...', time_fin_iter- time_load
	pickle.dump([ small_target_list,norm_mse_list, mmmpa_list],open(f_out,'wb'))



if __name__ == "__main__":     
    main()

    ## toy example
	# prev_steps = 6
	# num_hidden = 64
	# binary_on = False
	# n_epoch = 100
	# # test set
	# rads = np.linspace(-np.pi, np.pi, 100)
	# data_array = np.sin(rads)
	# test_beg = len(data_array)-15 # right now, 2016 Aug is the last one & test_beg = 2015 June, test_end = 2016 June
	# test_end = len(data_array)-2 # 

	# t_start = time.time()
	# [x_train, y_train, x_test, y_test] = prep_data(data_array, prev_steps, test_beg, test_end)
	# t_prep = time.time()
	# print '===========it took', t_prep-t_start,'for data prep=========='
	# [rmse, history] = runLSTM("test_run_", x_train, x_test, y_train, y_test, binary_on=False, hidden_neurons =64, n_epoch= 100)
	# print '===========it took', time.time()-t_prep,'for LSTM training=========='


