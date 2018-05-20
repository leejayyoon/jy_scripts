import io
import argparse
import csv
import numpy as np
import os
import cPickle as pickle


def make_copy_dir(in_dir, to_dir_name="copy_dir"):
	# make dir "copy_dir" "copy_dir/synaptic"
	if to_dir_name=="copy_dir":
		metric_dirs=['best_bleu', 'best_evalb']
		from_dir = in_dir
		cp_dir=in_dir+"/"+to_dir_name
	else:
		metric_dirs=[]
		from_dir=in_dir+"/"+to_dir_name
		cp_dir=in_dir+"/copy_dir/"+ to_dir_name

	cp_syn_dir =cp_dir +"/synaptic"


	if not os.path.exists(cp_dir):
		os.makedirs(cp_dir)
		# print("os.makedirs(%s)"%cp_dir)
    	
    	if not os.path.exists(cp_syn_dir):
    		os.makedirs(cp_syn_dir)
    		# print("os.makedirs(%s)" %cp_syn_dir)
	
		# copy checkpoint, hparams, synaptic/checkpoint
		# print("cp %s/checkpoint %s/" %(from_dir, cp_dir))
		# print("cp %s/hparams %s/" %(from_dir, cp_dir))
		# print("cp %s/checkpoint %s/" %(from_dir+"/synaptic", cp_syn_dir))
		os.system("cp %s/checkpoint %s/" %(from_dir, cp_dir))
		os.system("cp %s/hparams %s/" %(from_dir, cp_dir))
		if to_dir_name == "copy_dir":
			os.system("cp %s/rl_train.log %s/" %(from_dir, cp_dir))
		os.system("cp %s/checkpoint %s/" %(from_dir+"/synaptic", cp_syn_dir))
	
	# read checkpoint --> copy latest ckpt files. rl.ckpt-# , synaptic/rl_syn.ckpt
	ckpt_path=from_dir+"/checkpoint"
	with open(ckpt_path, 'rb') as f: 
		final_ckpt_line = f.readline()
	ckpt_num = int(final_ckpt_line.split('"')[1].split('-')[1])
	# print("cp %s/rl.ckpt-%d.* %s/" %(from_dir, ckpt_num, cp_dir))
	# print("cp %s/rl_syn.ckpt-%d.* %s/" %(from_dir+"/synaptic", ckpt_num, cp_syn_dir))
	os.system("cp %s/rl.ckpt-%d.* %s/" %(from_dir, ckpt_num, cp_dir))
	os.system("cp %s/rl_syn.ckpt-%d.* %s/" %(from_dir+"/synaptic", ckpt_num, cp_syn_dir))

	for metric_dir in metric_dirs:
		make_copy_dir(in_dir, to_dir_name=metric_dir)

	


	# do the same thing for best_evalb
	# do the same thing for best_bleu


if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("-i", "--input_path", required=True)
	# argparser.add_argument("-o", "--output_filename", required=True)
	args = argparser.parse_args()

	in_path=args.input_path
	make_copy_dir(in_path)

