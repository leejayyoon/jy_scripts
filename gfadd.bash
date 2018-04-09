#!/bin/bash

inplist=$1



len=${#inplist[*]}
echo "The input array has $len members. They are:"
echo $inplist 
i=0

grid=$2
#(0 8 16 32 64 128 256 512 1024 2048 4096 8192)
glen=${#grid[*]}
echo "The grid  array has $glen members. They are:"
j=0

k=10
feature="3,4"
features=(3 4)
inFolder="./"
out="gfadd" 
outFolder="/$out/"
outNo=10 #number of outliers to report
startDate="12/01/2012"
endDate="12/31/2012"

mkdir $out
echo $len
while [ $i -lt $len ]; do
	while [ $j -lt $glen ]; do
		outlierPointsScores=${inplist[$i]}_${grid[$j]}g_forGnuplot.txt
		echo j={$j}
		echo ${inplist[$i]} 
		echo "# of grid: ${grid[$j]} "
		java -jar GFADD_LOG.jar $k ${grid[$j]} $feature $inFolder ${inplist[$i]} $outFolder $startDate $endDate
		var1=`echo ${inplist[$i]}| sed -e 's/_vs_/ /g'`		
		var2=($var1)
		var3=`echo ${var2[1]}| sed -e 's/_/ /g'`
		bash plot.bash ${inplist[$i]} $out/$outlierPointsScores ${features[0]} ${features[1]} ${grid[$j]} ${var2[0]} ${var3[0]}
		let j++
	done
	let i++
	let j=0
done

echo -e "\e[00;32mDone with lof.bash.\e[00m" 

