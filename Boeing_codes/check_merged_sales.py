f_in = "/app/part-demand/team-repo/jylee/merged_sales.tsv"
count = 0
with open(f_in) as f:
        for line in f:
        	ls = line.split('\t')
    		count+=1
        	if len(ls)>5:
        		print 'error on line',count, 'separated tokens: ', ls

print "I am done"


