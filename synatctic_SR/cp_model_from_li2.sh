#!/bin/bash
dom_list=(tc bc wb pt bn bncnn bc_sub)
lr=0.01
c_syn=0.5

for dom in "${dom_list[@]}"
do
	rl_dir="rl_${dom}dir"
	model_dir="model_dir_2/WSJpars_gnmtenc_h256_l3_attBA_archgnmt_glorot_uniform_dr0.5_adam_clip5_synapticTrue_wsj_LAST2"
	model_dir=$model_dir"/${rl_dir}/rl_train_lr${lr}_bs128_SimpleBaseline_normlen_syn${c_syn}_inftrainTrue"
	if [ ! -d $model_dir ]; then
		echo "Copying for domain: ${dom}"
		CMD="scp -r lop1:~/repository/rl2-continual/${model_dir}/copy_dir ${model_dir}"
		echo "$CMD"
		bash -c "$CMD"
	else
		echo "model_dir alrady exists for domain: ${dom}"
	fi
done
