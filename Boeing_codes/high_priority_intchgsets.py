import cPickle as pickle

with open("interchg_sets.p",'rb') as f:
    interchg_sets=pickle.load(f)

# get the related sets first
#iterate over the important file list
fname_hpp = "/app/part-demand/data/targetPN.csv/combined.csv"
  #high priority parts
hpp_interchg_sets = []
merged = []
count=0

with open(fname_hpp) as f:
	for line in f:
		ls = line.split("\n")
		buf_set = set()
		insert_flag = False
		for i in range(len(interchg_sets)):
			if i in merged:
				continue
			if ls[0] in interchg_sets[i]:
				buf_set = buf_set.union(interchg_sets[i])
				merged.append(i)
				insert_flag=True
    	
    	if insert_flag: # if there were no overlapping data at all, skip.
    		hpp_interchg_sets.append(buf_set)
		count+=1
		if count % 1000 == 0:
			print count

pickle.dump( hpp_interchg_sets, open("cleaned_hpp_interchg_sets.p","wb"))


# save the related sets onto pickle format.


# 
