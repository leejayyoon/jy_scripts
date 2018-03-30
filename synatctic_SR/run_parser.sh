#!/bin/bash

#/psi/datarepository/ldc/treebank_3/parsed
data_dir="${HOME}/repository/data/LDC99T42_WSJ_parse/TREEBANK_3/PARSED/MRG/WSJ"
python ./src/parsing/DataUtils.py --in_path=$data_dir --out_path=./datadir/split_
