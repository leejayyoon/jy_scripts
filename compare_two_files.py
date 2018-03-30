import io
import argparse

import os
import csv
import cPickle as pickle

argparser = argparse.ArgumentParser()
argparser.add_argument("-i1", "--input1", required=True)
argparser.add_argument("-i2", "--input2", required=True)
argparser.add_argument("-o", "--output_filename", required=True)
args = argparser.parse_args()

# # parse/validate arguments
# argparser = argparse.ArgumentParser()
# argparser.add_argument("-i", "--input_filename", required=True)
# argparser.add_argument("-o", "--output_filename", required=True)
# argparser.add_argument("-d", "--delimiter", default="_")
# argparser.add_argument("-c", "--columns", default="2,5", help="comma-delimited list of column numbers (one-based) to be copy for each token to the output file.")
# args = argparser.parse_args()

# columns = args.columns.split(',')
# columns = [int(column)-1 for column in columns]

def write_list_to_csv(my_list, f_out):
    with open(f_out, 'wb') as f: 
        spamwriter = csv.writer(f)
        for s in my_list: 
            spamwriter.writerow([s])

def get_list_fromCSV(in_file, col):# getting part_interest_list
        count = 0
        out_list = []
        with open(in_file) as csvfile:
            next(csvfile)
            spamreader = csv.reader(csvfile)
            for line in spamreader:
                if count%10000 == 0 :
                    print count
                out_list.append(line[col])
                count += 1
        return out_list

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

def load_pickle(f_pickle):
    if os.path.exists(f_pickle):
        with open(f_pickle,'rb') as f:
                out_list=pickle.load(f)
    return out_list

def dump_pickle(in_list, f_pickle):
    pickle.dump(in_list,open(f_pickle,'wb'))



# file1
# file2
# diff_file="official_account_differene"
# list1=get_list_fromCSV(file1, 0)
# list2=get_list_fromCSV(file2, 0)

# list_diff=list(set(list2)-set(list1))
# write_list_to_csv()