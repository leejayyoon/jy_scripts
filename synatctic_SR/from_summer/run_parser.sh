#!/bin/bash

## call run_parser.sh train/test/development

#/psi/datarepository/ldc/treebank_3/parsed
train_dev=$1 #'test'
category=$2 #'nw'
subcategory=$3 #'wsj'
data_head_dir=$4
if [ -z "$data_head_dir" ]
	then
	data_dir="${HOME}/repository/data/ontonotes-parse-trees-new/${train_dev}/${category}/${subcategory}"
else
	data_dir=$data_head_dir"/${train_dev}/${category}/${subcategory}"
fi
out_dir="./new_datadir"
# mkdir -p $out_dir
out_dir=$out_dir"/${category}"
# mkdir -p $out_dir
out_dir=$out_dir/$subcategory
# mkdir -p $out_dir

# 'development' --> 'dev' for convenience
if [ $train_dev == "development" ]
	then
	train_dev="dev"
fi
python DataUtils.py --in_path=$data_dir --out_path=$out_dir/"split-${train_dev}"
# Procedures
# 1. source run_parser.sh	   # chnage trees to SR

# 2. source separte_encdec.sh  # separate enc, dec from one file.
# generates input file_name -->  file_name + ".encode" ."decode"
sh ../separate_encdec.sh $out_dir $out_dir "split-${train_dev}"
rm $out_dir/"split-${train_dev}"

# 3. python convert-SR2sR.py   # change SR to sR
sR_file="${out_dir}/split-${train_dev}.decode"
SR_file="${out_dir}/split-${train_dev}.decode_temp" 
mv $sR_file $SR_file 
python ../convert-SR2sR.py -i $SR_file -o $sR_file
rm $SR_file
# 4. get_random_subsets.py (if I want partial dataset)
