import sys
import os
import csv
import numpy as np
# from bootstrap import *
import cPickle as pickle
import matplotlib
from matplotlib import colors
from matplotlib import pyplot as plt



my_color = {"grey": colors.colorConverter.to_rgb("#4D4D4D"),
            "blue": colors.colorConverter.to_rgb("#5DA5DA"),
            "orange": colors.colorConverter.to_rgb("#FAA43A"),
            "green": colors.colorConverter.to_rgb("#60BD68"),
            "pink": colors.colorConverter.to_rgb("#F17CB0"),
            "brown": colors.colorConverter.to_rgb("#B2912F"),
            "purple": colors.colorConverter.to_rgb("#B276B2"),
            "yellow": colors.colorConverter.to_rgb("#DECF3F"),
            "red": colors.colorConverter.to_rgb("#F15854")}

shape = {"point":	".",
		"pixel":	",",
		"circle":	"o",
		"triangle_down":	"v",
		"triangle_up":	"^",
		"triangle_left":	"<",
		"triangle_right":	">",
		"tri_down":	"1",
		"tri_up":	"2",
		"tri_left":	"3",
		"tri_right":	"4",
		"octagon":	"8",
		"square":	"s",
		"pentagon":	"p",
		"star":	"*",
		"hexagon1":	"h",
		"hexagon2":	"H"}


def write_list_to_csv(my_list, f_out):
	with open(f_out, 'wb') as f: 
		spamwriter = csv.writer(f)
		for s in my_list: 
			spamwriter.writerow([s])

def estimate_params(data, x_prev=None, n_zero=0, n_one=0, n_zero_to_one=0, n_one_to_one=0, nz_dist={}):
	#Count statistics for forming distribution.
	if x_prev is None:
		x_prev = 0 # if one forgets to add x_prev, then it is safe to assume,
		# beginning of the sales was 0 since it never existed
	if len(data)>1: # at the very first parameter estimation. (to avoid double counts in other cases)
		if x_prev:
			n_one +=1
			if x_prev in nz_dist:
				nz_dist[x_prev]+=1
			else:
				nz_dist[x_prev]=1
		else:
			n_zero +=1

	for x_cur in data[0:]:
		if x_cur:
			n_one += 1
			# estimate nz distribution
			if x_cur in nz_dist:
				nz_dist[x_cur]+=1
			else:
				nz_dist[x_cur]=1
			if x_prev:
				n_one_to_one+=1
			else:
				n_zero_to_one+=1
		else:
			n_zero += 1
		x_prev = x_cur
	# for now, just count, but we can also do,
	# given numpy array x is a occruence vector. (numbers not bigger than 0.)
	# sum(x) = n_one, len(x)-sum(x)=n_zero,
	# sum(x)-sum(x[:-1]*x[1:])
	# build nz_dist 
	count_list = nz_dist.keys()
	count_dist = np.array(nz_dist.values())
	count_dist_cdf = np.cumsum(count_dist)
	if n_one:
		p_one2one= n_one_to_one/(n_one+0.0)
	else:
		p_one2one =0

	if n_zero:
		p_zero2one= n_zero_to_one/(n_zero+0.0)
	else:
		p_zero2one=0

	distribution = [p_zero2one, p_one2one, count_list, count_dist_cdf]
	stats = [n_zero, n_one, n_zero_to_one, n_one_to_one, nz_dist]
	# sanity check
	if np.sum(count_dist) != n_one:
		raise ValueError("the nonzero count is not consistent in count_dist sum %d and n_one %d." \
						% (np.sum(count_dist), n_one))

	return [distribution, stats]


# Use this sample distribution to generate 2-5
# L = 3  # lead-time to look at.
# n_bootstrap = 5
def predict_leadtime(x_cur, distribution, n_one, L=3, n_bootstrap=5):
	np.random.seed(256)
	[p_zero2one, p_one2one, count_list, count_dist_cdf] = distribution
	LTD_dist = {}
	for i_bs in range(n_bootstrap):
		f_list= np.zeros([L+1,1])
		f_list[0] = x_cur
		# generate the random sequence from the	
		for i in range(L):
			f_list[i+1] = f_list[i]*np.random.binomial(1,p_one2one) +\
								 (1-f_list[i])*np.random.binomial(1,p_zero2one) 
		# at this point, f_list is just 0 or 1. --> get L random samples (uniform and standard deviation)
		unif_samples = np.random.uniform([0,n_one,L])
		z_samples = np.random.randn(L) #standard normal samples
		for i in range(L):
			if f_list[i+1]: # if the state is predicted as nonzero
				sample_idx = np.where( count_dist_cdf > unif_samples[i] )[0][0]
				temp = count_list[sample_idx]
				f_list[i+1] = temp + np.sqrt(temp)*z_samples[i] # or  np.random.randn(1)
				if f_list[i+1]<0: # if nonzero, just return original temp.
					f_list[i+1] = temp
		LTD_i = np.sum(f_list[1:])

		if LTD_i in LTD_dist:
			LTD_dist[LTD_i] += 1 # increase count:
		else:
			LTD_dist[LTD_i] =1

	if np.sum(LTD_dist.values()) != n_bootstrap:
		raise ValueError("the nonzero count is not consistent in count_dist sum %d and n_one %d." \
						% (np.sum(LTD_dist.values()), n_bootstrap))

	mean_estimate = np.sum(np.array(LTD_dist.keys())*np.array(LTD_dist.values())) /(n_bootstrap+0.0)
	# LTD_dist #dist_estimate 

	return mean_estimate



def get_taregt_list(f_parts_interest):# getting part_interest_list
	# f_parts_interest = "/app/part-demand/data/targetPN.csv/combined.csv"
	count = 0
	parts_interest_list = []
	with open(f_parts_interest) as csvfile:
		spamreader = csv.reader(csvfile)
		for line in spamreader:
		    if count%10000 == 0 :
		        print count
		    parts_interest_list.append(line[0])
		    count += 1
	return parts_interest_list

def get_setid(): ### funciton in progress ...
	count =0
	for part in parts_interest_list:
		count +=1
		if part in part_to_set:
			print 'part', part
			print month_mat[part_to_idx[part], :]
			set_id = list(part_to_set[part])[0]
			print 'set_id', set_id
			print merged_series[set_to_idx[set_id],:]
		if count> 20:
			break

	return set_id

def load_data(f_idx2aviallID, f_matrix, f_parts_interest, bin_period, boeing_or_aviall ):
	print 'Loading timeseires...'
	if boeing_or_aviall == "Boeing":
		timeseries_mat, part_to_idx = load_boeing_timeseries(f_idx2aviallID, f_matrix, bin_period)
	elif boeing_or_aviall == "Aviall":
		timeseries_mat, part_to_idx = load_timeseries(f_idx2aviallID, f_matrix)	
	elif boeing_or_aviall == "intchg":
		print "intchg system not ready yet, but coming soon ..."

	print 'Time series loaded!'
	print 'Loading target lists...'
	parts_interest_list = get_taregt_list(f_parts_interest)# getting part_interest_list
	print 'Target lists loaded!'

	return timeseries_mat, part_to_idx, parts_interest_list

def analyze_bstrap_result(n_bootstrap, lead_time, bin_period="month",boeing_or_aviall="Boeing"):
	# Define input files that I need to read from.
	f_idx2aviallID= '/app/part-demand/team-repo/data_process/binned_data/unique.tsv'
	f_matrix='/app/part-demand/team-repo/data_process/binned_data/mat_'+bin_period+'.csv'
	f_parts_interest = "/app/part-demand/data/targetPN.csv/combined.csv"
	# Bootstrap results
	f_bstrap_out = "bootstrap_result_"+boeing_or_aviall+"_nbs"+ str(n_bootstrap)+"_lead"+str(lead_time)+".p"
	f_bstrap_analysis = "bootstrap_result_"+boeing_or_aviall+"_nbs"+ str(n_bootstrap)+"_lead"+str(lead_time)+"_analysis.p"
	f_bstrap_old = "bootstrap_result_"+boeing_or_aviall+".p"
	# parameters 
	L = lead_time
	timeseries_mat, part_to_idx, parts_interest_list = load_data(f_idx2aviallID, f_matrix, f_parts_interest, bin_period, boeing_or_aviall )
	#load the bootstrap result now
	# f_bstrap_out = "bootstrap_result_Aviall_nbs5_lead3.p"
	with open(f_bstrap_out,"rb") as f:
		[part_pred_id_list, part_pred_list] = pickle.load(f)
	# this is just for the first genearation runs.
	norm_MSE_list = []
	unnorm_MSE_list = []
	print 'len(part_pred_list)', len(part_pred_list)
	print 'len(part_pred_id_list)', len(part_pred_id_list)
	for i in range(len(part_pred_list)):
		# get bootstrap results
		part_id = part_pred_id_list[i]
		local_pred_list = part_pred_list[i]
		# orgiinal time series for plotting
		mat_idx = part_to_idx[part_id]
		timeseries_true = timeseries_mat[mat_idx,:]
		if np.sum(timeseries_true)==0:
			#if it's zero time series ther is no reason to see bootstrap results
			continue
		if len(timeseries_true)/2 < L:
			print 'skipping part id', part_id, 'since the lead time', L, 'is longer than half of time series to be anlayzed', len(timeseries_true)/2.0
		# part_pred_rslt[i][0]
		# FOR CONVERTING OLD VERION TO CURRNET VERSION
		if part_id != parts_interest_list[i]:
			raise AssertionError('wrong part id match. Saved one:'+part_pred_rslt[count][0]+'expected one:'+ part_id)
		# else:
		# 	part_pred_id_list.append(part_pred_rslt[count][0]) 
		# 	part_pred_list.append(part_pred_rslt[count][1]) 
		# if count > 10: 
		# 	break
		# print 'len(local_pred_list)', len(local_pred_list), 'type',type(local_pred_list)
		# print 'len(local_pred_list[i])', len(local_pred_list[i])
		# print 'np.array(local_pred_list).shape', np.array(local_pred_list).shape
		# [mean_error, mean_true, mean_estimate] = local_pred_list # all numpy arrays
		mean_error = np.array(local_pred_list)[:,0]
		mean_true = np.array(local_pred_list)[:,1]
		nz_idx = np.nonzero(mean_true)
		norm_error = mean_error[nz_idx]/mean_true[nz_idx]
		# mean_estimate = np.array(local_pred_list)[:,2]		
		unnorm_MSE =  np.nanmean(np.sqrt((mean_error*mean_error)))
		norm_MSE = np.nanmean(np.sqrt(norm_error*norm_error))
		# 
		# print 'unnorm_MSE', unnorm_MSE
		# print 'norm_MSE', norm_MSE
		# if i>10:
		# 	break
		unnorm_MSE_list.append(unnorm_MSE)
		norm_MSE_list.append(norm_MSE)
		#
	unnorm_MSE_list = np.array(unnorm_MSE_list)
	norm_MSE_list = np.array(norm_MSE_list)		
	# pickle.dump([part_pred_id_list, part_pred_list], open(f_bstrap_out,"wb") )
	print 'mean of unnormalized MSE over ', len(part_pred_list), 'parts: ', np.nanmean(unnorm_MSE_list)
	print 'mean of normalized MSE over ', len(part_pred_list), 'parts: ', np.nanmean(norm_MSE_list)
	# print 'norm_MSE_list.index(nan)', norm_MSE_list.index(np.nan)
	sorted_idx_normMSE =  np.argsort(norm_MSE_list)
	print 'smallest error indices', sorted_idx_normMSE[:10]
	print 'errors', norm_MSE_list[sorted_idx_normMSE[:10]]
	# plot(np.argsort(norm_MSE_list)[1:10])
	# plot after sort
	pickle.dump([part_pred_id_list, unnorm_MSE_list, norm_MSE_list], open(f_bstrap_analysis ,"wb") )

	# plot the sorted scores
	plt.plot(np.arange(len(norm_MSE_list)), norm_MSE_list[sorted_idx_normMSE])
	plt.xlabel("parts (sorted by MSE value)")
	plt.ylabel("normalized MSE per part")
	plt.savefig("sorted_normMSE.pdf")

	# plot original timeseries

	# plot the means!jy25


# def plot_results(org_timeseries, mean_error, mean_true, normalize=True):


def load_timeseries(f_idx2aviallID, f_matrix):
	# f_idx2aviallID= '/app/part-demand/team-repo/data_process/binned_data/unique.tsv'
	# f_month='/app/part-demand/team-repo/data_process/binned_data/mat_month.csv'
	count = 0
	part_list_mat = []
	part_to_idx = {}
	with open(f_idx2aviallID) as csvfile:
		spamreader = csv.reader(csvfile,delimiter='\t')
		for line in spamreader:
		    if count%10000 == 0 :
		        print count
		    part_list_mat.append(line[0])
		    # pirnt line[0]
		    # print line[0].split("=")[0]
		    part_id = line[0].split("=")[0]
		    part_to_idx[part_id]=count
		    count += 1
		    # if count>10:
		    # 	break
	# loading the matrix
	timeseries_mat = np.loadtxt(f_matrix,delimiter=',')
	return timeseries_mat, part_to_idx

def load_boeing_timeseries(f_idx2aviallID, f_matrix, bin_period):
	f_boeing_mat = "Boeing_"+bin_period+"_mat.p"
	# if processed file already exists, just load the file.
	if os.path.exists(f_boeing_mat):
		with open("Boeing_month_mat.p",'rb') as f:
			[boeing_time_series,boeingID_to_matIdx, idx_to_boeingID]=pickle.load(f)
			f_matID_to_boeingID = "idx_to_boeingID.csv"
			write_list_to_csv(idx_to_boeingID, f_matID_to_boeingID)
			return boeing_time_series,boeingID_to_matIdx
	partidx_dict = {}
	count = 0
	with open(f_idx2aviallID) as csvfile:
		spamreader = csv.reader(open(f_idx2aviallID,'rb'),delimiter='\t')
		for line in spamreader:
		    if count%10000 == 0 :
		        print count
		    # part_list.append(line[0])
		    boeing_part_id = line[0].split("=")[0]
		    if boeing_part_id in partidx_dict:
		    	partidx_dict[boeing_part_id].append(count)
		    else:
		    	partidx_dict[boeing_part_id]=[count]
		    count += 1
	# load timeseries data in AVIALL ID
	timeseries_data = np.loadtxt(f_matrix,delimiter=',')
	print '# of timesereis:', len(timeseries_data)
	# merge the time series. 
	row = 0
	idx_to_boeingID = []
	boeingID_to_matIdx={}
	boeing_time_series = np.zeros([len(partidx_dict),timeseries_data.shape[1]])
	#iterate through Boeing ID, and merge matrix to BOEING ID matrix!
	for boeing_id, av_part_mxidx in partidx_dict.iteritems():
		idx_to_boeingID.append(boeing_id)
		boeingID_to_matIdx[boeing_id]=row
		# print boeing_id
		# for mat_row_idx in av_part_mxidx:
			# boeing_time_series[row,:]= np.sum((boeing_time_series[row,:], timeseries_data[mat_row_idx,:]),axis=0)
		boeing_time_series[row,:]= np.sum(timeseries_data[av_part_mxidx,:],axis=0)
		row += 1
		if row%10000 ==0:
			print 'row:',row
	# SAVE processed files.
	pickle.dump([boeing_time_series,boeingID_to_matIdx, idx_to_boeingID],open(f_boeing_mat,'wb'))
	f_boeing_mat_csv = "Boeing_"+bin_period+"_mat.csv"
	np.savetxt( f_boeing_mat_csv,boeing_time_series, delimiter=",")
	f_matID_to_boeingID = "idx_to_boeingID.csv"
	write_list_to_csv(idx_to_boeingID, f_matID_to_boeingID)
	return boeing_time_series, boeingID_to_matIdx

def run_bootstrap(n_bootstrap, lead_time, bin_period="month",boeing_or_aviall="Boeing"):
	# get timeseries
	# input: f_idx2partid, f_matrix
	# return: part_to_idx (dictionary), month_mat or biweekly_mat (numpy array) 
	f_idx2aviallID= '/app/part-demand/team-repo/data_process/binned_data/unique.tsv'
	f_matrix='/app/part-demand/team-repo/data_process/binned_data/mat_'+bin_period+'.csv'
	f_bstrap_out = "bootstrap_result_"+boeing_or_aviall+"_nbs"+ str(n_bootstrap)+"_lead"+str(lead_time)+".p"
	f_parts_interest = "/app/part-demand/data/targetPN.csv/combined.csv"
	timeseries_mat, part_to_idx, parts_interest_list = load_data(f_idx2aviallID, f_matrix, f_parts_interest, bin_period, boeing_or_aviall )
	
	# if boeing_or_aviall == "Boeing":
	# 	timeseries_mat, part_to_idx = load_boeing_timeseries(f_idx2aviallID, f_matrix, bin_period)
	# elif boeing_or_aviall == "Aviall":
	# 	timeseries_mat, part_to_idx = load_timeseries(f_idx2aviallID, f_matrix)	
	# print boeing_or_aviall
	# print timeseries_mat.shape
	# print 'Time series loaded!'
	# f_parts_interest = "/app/part-demand/data/targetPN.csv/combined.csv"
	# parts_interest_list = get_taregt_list(f_parts_interest)# getting part_interest_list
	# print 'Target lists loaded!'

	L =lead_time # lead_time
	count =0
	part_pred_list =[]
	part_pred_id_list=[]
	for part_id in parts_interest_list:
		# find the part idx, and visit tha matrix.
		# print 'part_id', part_id, 'idx:', part_to_idx[part_id]
		timeseries =  timeseries_mat[part_to_idx[part_id],:]
		# print 'shape', timeseries.shape
		data_cur = timeseries[1:len(timeseries)/2]
		x_prev = timeseries[0] # initializing x_prev
		# parameter initialization --> make sure to re-initialize for each part.
		# run bootstrap method incrementally.
		[n_zero, n_one, n_zero_to_one, n_one_to_one, nz_dist] = [0,0,0,0,{}]
		if len(timeseries)/2 < L:
			print 'skipping part id', part_id, 'since the lead time is longer than time series to be anlayzed'
			print 'len(timeseries)', len(timeseries), 'len/2', len(timeseries)/2 , 'L:, ',L
			print 'len(timeseries)/2 < L', len(timeseries)/2.0 < L
			continue
		
		local_pred_list = []
		local_error_list = []
		for i in range(len(timeseries)/2-1,len(timeseries)-L):
			[distribution, stats] \
				=estimate_params(data_cur, x_prev, n_zero, n_one, n_zero_to_one, n_one_to_one, nz_dist)
			#unpack
			[n_zero, n_one, n_zero_to_one, n_one_to_one, nz_dist] = stats
			#
			x_cur = timeseries[i]
			mean_estimate = predict_leadtime(x_cur, distribution,n_one, L,n_bootstrap)
			mean_true =  np.sum(timeseries[range(i+1,i+L+1)])/(L+0.0)
			mean_error = mean_estimate -mean_true
			local_pred_list.append([mean_error, mean_true, mean_estimate])
			local_error_list.append(mean_error)
			# update x_prev and x_cur
			x_prev = x_cur
			data_cur = [timeseries[i+1]]
		#
		print 'error:', np.mean(local_error_list)
		part_pred_list.append(local_pred_list)
		part_pred_id_list.append(part_id)
		count +=1 
		if count % 100==0:
			print 'count',count
			pickle.dump([part_pred_id_list, part_pred_list], open(f_bstrap_out,"wb") )

	pickle.dump([part_pred_id_list, part_pred_list], open(f_bstrap_out,"wb") )


    # '''previous code, because interchangeability is now merged 
	# # with open("Aviall_interchg_sets.p",'rb') as f:
	# #     [boeingID_to_set, part_to_set, set_to_part]=pickle.load(f)

	# # # part_to_set = {}
	# # # set_of_parts_intchg = set()
	# # # for key, values in part_to_set_aviall.iteritems():
	# # # 	part_to_set[key]=values


	# # # part_to_set dictionary (in Boeing format)
	# # part_to_set = {}
	# # set_of_parts_intchg = set()
	# # count = 0
	# # f_interchange = "/app/part-demand/data/aviall/aviall-part-interchangeability.csv"
	# # with open(f_interchange) as csvfile:
	# #     spamreader = csv.reader(csvfile,delimiter=',',quotechar='"')
	# #     spamreader.next()
	# #     for line in spamreader:
	# #         if count%10000 == 0:
	# #             print count
	# #         set_id = line[0]
	# #         part_id = line[5].split("=")[0]
	# #         if part_id in part_to_set:
	# #         	part_to_set[part_id].add(set_id)
	# #         else: 
	# #         	part_to_set[part_id] = set([set_id])
	# #         set_of_parts_intchg.add(part_id)
	# #         count+=1
	# '''

if __name__ == "__main__":
    out_dir= sys.argv[1]
    n_bootstrap = int(sys.argv[2])
    lead_time = int(sys.argv[3])
    if len(sys.argv)>4:
    	bin_period = sys.argv[4]
    else: 
    	bin_period = "month"
    if len(sys.argv)>5:
    	boeing_or_aviall = sys.argv[5]
    else:
    	boeing_or_aviall="Boeing"
    print 'n_bootstrap', n_bootstrap
    print 'lead_time', lead_time
    print 'bin_period', bin_period
    print 'id format', boeing_or_aviall
    # run_bootstrap(n_bootstrap, lead_time,bin_period=bin_period ,boeing_or_aviall=boeing_or_aviall)
    analyze_bstrap_result(n_bootstrap, lead_time,bin_period=bin_period ,boeing_or_aviall=boeing_or_aviall)


