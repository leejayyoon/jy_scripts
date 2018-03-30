#!/bin/bash
# by Jay-Yoon Lee
# example: source convert-conllu-SRperline.sh en train none

lang=$1 # en
train_test_val=$2 #train, test, val
lang_sub=$3
# data_folder='../../data/ud-treebanks-v1.4/' 
data_folder='../../data/multi-language/ud-treebanks-v1.4/' 
directory='./'
out_folder="./datadir/${lang}" #'../../structured_LSTM/datadir/'
mkdir -p $out_folder

# if else on en, 
# if [ $lang != "en" ]
# 	then
# 	if [ $lang_sub == "esl" ]
# 		then
# 			lang_dir="UD_English-ESL"
# 			lang="${lang}_{lang_sub}"
# 	elif [ $lang_sub == "test" ]
# 		then
# 			lang_dir="UD_English-LinES"
# 			lang="${lang}_{lang_sub}"
# 	else
# 		lang_dir="UD_English"
# 	fi	
# fi
lang_dir="UD_$lang"


f_conllu="${data_folder}/${lang_dir}/${lang}-ud-${train_test_val}.conllu"
f_conll06="${lang}-ud-${train_test_val}.conll06"
f_sentence="${lang}-ud-${train_test_val}.sentence-per-line"
f_oracle="${lang}-ud-${train_test_val}.Oracle"
f_oracle_onlySR="${f_oracle}-onlySR"
f_oracle_SR_perline="${f_oracle}-SR-perline"

# 1. conllu —> conll06 
echo "\n------------------------"
echo "converting conllu format to conll06"
echo "python convert-conllu-to-conll06.py -i $f_conllu -o $f_conll06"
python convert-conllu-to-conll06.py -i $f_conllu -o $f_conll06

# 2. conll06 —> sentence per-line
# python convert-conll-format-to-sent-per-line.py -i $f_conll06 -o $f_sentence
echo "\n------------------------"
echo "[Encoder data]: Generating sentence on one line per example"
echo "python convert-conll-to-text.py -i $f_conll06 -o $f_sentence"
python convert-conll-to-text.py -i $f_conll06 -o $f_sentence


# # 3. generate oracle
echo "\n------------------------"
echo "[Decoder data]: Generating oracle shift reduce ..."
echo "java -jar ParserOracleArcStdWithSwap.jar -t -1 -l 1 -c $f_conll06 > $f_oracle"
time java -jar ParserOracleArcStdWithSwap.jar -t -1 -l 1 -c $f_conll06 > $f_oracle
rm $f_conll06

# # 4. oracle —> odd # lines —> SR per line
echo "\n------------------------"
echo "Getting shift reduce in one line per example ..."
echo "awk 'NR%2==1' $f_oracle > $f_oracle_onlySR"
awk 'NR%2==1' $f_oracle > $f_oracle_onlySR
echo "python convert_seq_shiftreduce.py -i $f_oracle_onlySR -o $f_oracle_SR_perline"
python convert_seq_shiftreduce.py -i $f_oracle_onlySR -o $f_oracle_SR_perline
rm $f_oracle_onlySR


cp $f_sentence ${out_folder}/${lang}-ud-${train_test_val}_encode
cp $f_oracle_SR_perline ${out_folder}/${lang}-ud-${train_test_val}_decode
mv $f_oracle ${out_folder}/

rm $f_sentence
rm $f_oracle_SR_perline