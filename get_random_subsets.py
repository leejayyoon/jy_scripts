import sys
import io
import argparse
import numpy as np

# python text_processing.py
def get_sample_lines(lines, out_fname,rand_idx,sample_size):
	new_lines = [lines[idx] for idx in rand_idx[:sample_size]]
	with open(out_fname,"w") as fout:
		for item in new_lines:
			fout.write('%s\n' % item)

def make_sample_files(enc_fname, dec_fname, ratio_list =[0.25, 0.5, 0.75]):
	enc_file = open(enc_fname, "r")
	enc_lines = [line.rstrip() for line in enc_file.readlines()]
	dec_file = open(dec_fname, "r")
	dec_lines = [line.rstrip() for line in dec_file.readlines()]
	assert len(enc_lines) == len(dec_lines)
	rand_idx = np.random.permutation( np.arange(len(enc_lines)) )

	# ratio_list = [0.25, 0.5, 0.75]
	for ratio in ratio_list:
		enc_out_fname = enc_fname + '_ratio'+str(ratio)
		dec_out_fname = dec_fname + '_ratio'+str(ratio)
		sample_size = int(np.floor(ratio*len(enc_lines)))
		print 'sample_size', sample_size
		get_sample_lines(enc_lines, enc_out_fname, rand_idx, sample_size)
		get_sample_lines(dec_lines, dec_out_fname, rand_idx, sample_size)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-fenc", "--enc_filename", required=True)
    argparser.add_argument("-fdec", "--dec_filename", required=True)
    argparser.add_argument("-r", "--ratio_list")
    args = argparser.parse_args()

    if args.ratio_list:
    	ratio_list = args.ratio.split(',')
    else:
    	ratio_list = [0.25,0.5,0.75]
    make_sample_files(args.enc_filename, args.dec_filename, ratio_list =ratio_list)
    # make_sample_files('../datadir/split-train_encode', '../datadir/split-train_decode')
