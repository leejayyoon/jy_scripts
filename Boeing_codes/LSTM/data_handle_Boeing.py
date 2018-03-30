import sys
import os
import csv
import numpy as np
# from bootstrap import *
import cPickle as pickle
import time

def write_list_to_csv(my_list, f_out):
    with open(f_out, 'wb') as f: 
        spamwriter = csv.writer(f)
        for s in my_list: 
            spamwriter.writerow([s])

def get_target_list( big_small="small"):# getting part_interest_list
    if big_small=="small":
        f_parts_interest = "/app/part-demand/data/small_target.csv"
    elif big_small=="big":
        f_parts_interest = "/app/part-demand/data/big_target.csv"
    count = 0
    parts_interest_list = []
    with open(f_parts_interest) as csvfile:
        next(csvfile)
        spamreader = csv.reader(csvfile)
        for line in spamreader:
            if count%10000 == 0 :
                print count
            parts_interest_list.append(line[0])
            # if big_small=="small":
            #     parts_interest_list.append(line[1]) # -->  this has been merged to the same format
            # elif big_small=="big":
            #     parts_interest_list.append(line[0])
            count += 1
    return parts_interest_list

def get_list_fromCSV(in_file, col):# getting part_interest_list
    count = 0
    parts_interest_list = []
    with open(in_file) as csvfile:
        next(csvfile)
        spamreader = csv.reader(csvfile)
        for line in spamreader:
            if count%10000 == 0 :
                print count
            parts_interest_list.append(line[col])
            count += 1
    return parts_interest_list

def get_dictionary(in_file, value_is_list=True):# getting part_interest_list
    count = 0
    out_dict = {}
    with open(in_file) as csvfile:
        spamreader = csv.reader(open(in_file,'rb'),delimiter=',',quotechar='"') #,quotechar= 
        for line in spamreader:
            # print 'line', line
            if value_is_list:
                out_dict[line[0]]=eval(line[1])
            else:
                out_dict[line[0]]=line[1]
            count += 1
    return out_dict

def load_data(big_small_target, bin_period, boeing_or_aviall):
    print 'Loading timeseires...'
    f_idx2BeoingID= "/app/part-demand/team-repo/data_process/binned_data/unique_boeing.tsv"
    f_boeing_matrix = "/app/part-demand/team-repo/data_process/binned_data/mat_"+bin_period+"_boeing.csv"
    
    if boeing_or_aviall == "aviall":
        f_idx2aviallID= '/app/part-demand/team-repo/data_process/binned_data/unique.tsv'
        f_aviall_matrix='/app/part-demand/team-repo/data_process/binned_data/mat_'+bin_period+'.csv'
        timeseries_mat, part_to_idx = load_timeseries(f_idx2aviallID, f_aviall_matrix, aviall=True) 
    elif boeing_or_aviall == "boeing":
        timeseries_mat, part_to_idx = load_timeseries(f_idx2BeoingID, f_boeing_matrix)
    elif boeing_or_aviall == "intchg":
        f_set_to_part = "/app/part-demand/data/aviall/chain-to-part.csv"
        timeseries_mat, part_to_idx = load_intchg_timeseries(f_idx2BeoingID, f_boeing_matrix, bin_period, f_set_to_part, boeing_intchg="intchg_merged") 
    else:
    	raise ValueError("boeing_or_aviall=" + boeing_or_aviall+ " which should be either aviall, boeing, or intchg")	

    print 'Time series loaded!'
    print 'Loading target lists...'
    
    parts_interest_list = get_target_list(big_small_target)# getting part_interest_list
    print 'Target lists loaded!'

    return timeseries_mat, part_to_idx, parts_interest_list


def load_timeseries(f_idx2PartID, f_matrix, aviall=False):
    # f_idx2PartID= '/app/part-demand/team-repo/data_process/binned_data/unique.tsv'
    # f_month='/app/part-demand/team-repo/data_process/binned_data/mat_month.csv'
    count = 0
    part_to_idx = {}
    with open(f_idx2PartID) as csvfile:
        spamreader = csv.reader(csvfile,delimiter='\t')
        for line in spamreader:
            if count%10000 == 0 :
                print count
            # pirnt line[0]
            # print line[0].split("=")[0]
            if aviall:
                part_id = line[0].split("=")[0]
            else:
                part_id = line[0]
            part_to_idx[part_id]=count
            count += 1
            # if count>10:
            #   break
    # loading the matrix
    timeseries_mat = np.loadtxt(f_matrix,delimiter=',')
    return timeseries_mat, part_to_idx

def load_intchg_timeseries(f_idx2PartID, f_mat_given, bin_period, f_set_to_part, boeing_intchg="intchg_merged"):
    f_mat_pickle = "/app/part-demand/team-repo/data_process/binned_data/"+ boeing_intchg+"_"+bin_period+"_mat.p"
    # if processed file already exists, just load the file.
    if os.path.exists(f_mat_pickle):
        with open(f_mat_pickle,'rb') as f:
            [new_time_series,id_to_matIdx, matIdx_to_id]=pickle.load(f)
            return new_time_series,id_to_matIdx
    else:
    	raise ValueError('the merged file '+ f_mat_pickle + ' does not exist!')

def main():
	time_beg = time.time()
	f_part_to_set = "/app/part-demand/data/aviall/part-to-chain.csv"
	part_to_set = get_dictionary(f_part_to_set, False)
	# parts_interest_list = get_target_list("small")
	# count=0
	# for part_id in small_target_list:
	# 	if part_id not in part_to_set:
	# 		count+=1
	# print count
	boeing_ts, part_to_idx_dict, small_target_list = load_data("small", "month", "boeing")
	intchg_merged_ts, set_to_idx_dict, small_target_list = load_data("small", "month", "intchg")

	time_load  = time.time()
	print 'time on loading ...', time_load-time_beg
	count = 0
	for part_id in small_target_list:
		if part_id in part_to_set:
			set_id = part_to_set[part_id]
			data_array = intchg_merged_ts[set_to_idx_dict[set_id]]
		else:
			data_array = boeing_ts[part_to_idx_dict[part_id]]
			count +=1

	time_fin_iter = time.time()
	print 'time on total iteration ...', time_fin_iter- time_load
	print count
