import io
import argparse
import csv
import numpy as np
import cPickle as pickle


def write_list_to_csv(my_list, f_out):
	with open(f_out, 'wb') as f: 
		spamwriter = csv.writer(f,delimiter='\t')
		for s in my_list: 
			spamwriter.writerow(s)

def process_SR_to_perline(f_in, f_out):
	# f_in = "en-ud-test.Oracle-onlySR"
	# f_out = "en-ud-test.Oracle-SR-perline"

	tot_out_list= []
	with open(f_in,'rb') as txt_in:
		count = 0
		row_count=0
		# for line in spamreader:
		str_list = []
		for line in txt_in:
			count += 1
			# print '----'
			# print line
			lstrip = line.strip()
			if lstrip: # if line is not empty
				# print '---',line
				ls_split = lstrip.split('(')
				if len(ls_split)==2:
					ls_split[1] = '('+ls_split[1] 
				str_list = str_list+ ls_split
			else:  # if empty string is found, then 
				# print str_list
				if str_list:
					tot_out_list.append(str_list)
					row_count+=1
				str_list=[]
				# if count>100:
				# 	break
		if str_list:
			tot_out_list.append(str_list)
			row_count+=1
	print 'processed lines:', row_count
	write_list_to_csv(tot_out_list, f_out)



if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-i", "--input_filename", required=True)
	argparser.add_argument("-o", "--output_filename", required=True)
	args = argparser.parse_args()

	in_path=args.input_filename
	out_path=args.output_filename
	process_SR_to_perline(in_path, out_path)

