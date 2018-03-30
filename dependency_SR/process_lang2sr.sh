# germanic=( en nl no de)
germanic=(de)
romance=(fr pt es ro it)
train_dev_test=(train dev test)


for i in "${germanic[@]}"
do
	for j in "${train_dev_test[@]}"
	do
		bash convert-conllu-SRperline.sh $i $j
	done
done

