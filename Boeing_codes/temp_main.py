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

def write_list_to_csv(my_list, f_out):
	with open(f_out, 'wb') as f: 
		spamwriter = csv.writer(f)
		for s in my_list: 
			spamwriter.writerow([s])


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

n_bootstrap=5
lead_time=3
bin_period="month"
boeing_or_aviall="Boeing"

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
sorted_idx_unnormMSE =  np.argsort(unnorm_MSE_list)
# print 'smallest norm error indices', sorted_idx_normMSE[:10]
print 'smallest norm errors', norm_MSE_list[sorted_idx_normMSE[:10]]
print 'smallest unnorm error indices', unnorm_MSE_list[sorted_idx_unnormMSE[:10]]
# plot(np.argsort(norm_MSE_list)[1:10])
# plot after sort
pickle.dump([part_pred_id_list, unnorm_MSE_list, norm_MSE_list], open(f_bstrap_analysis ,"wb") )

# plot the sorted scores
plt.plot(np.arange(len(norm_MSE_list)), norm_MSE_list[sorted_idx_normMSE])
plt.xlabel("parts (sorted by MSE value)")
plt.ylabel("normalized MSE per part")
plt.savefig("sorted_normMSE.pdf")

# execfile("temp_main.py")
