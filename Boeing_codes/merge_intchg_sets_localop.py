import cPickle as pickle

with open("interchg_sets.p",'rb') as f:
    interchg_sets=pickle.load(f)

with open("intermediate_merged.p",'rb') as f:
    [out_count,merged, global_interchg_list]=pickle.load(f)



# for i in range(len(interchg_sets)):
#     print '========', i,":", interchg_sets[i], '========'
#     in_count +=1 
#     if in_count > 10:
#         break
# global_interchg_list = []
# merged = []
local_interchg_list= []

# out_count=0
in_count=0
max_iter = len(interchg_sets)

for i in range(out_count, out_count+100):
    if i in merged:
        out_count+=1
        continue 
    if i == len(interchg_sets):
    	break

    buf_set = interchg_sets[i]
    merged.append(i) # keep merged sets
    
    if out_count%10 == 0:
        print '==============iteration', i, '=================='
    # print '========', i,":", interchg_sets[i], '========'
    for j in range(i+1,len(interchg_sets)):
        if j in merged:
            continue 
        if buf_set & interchg_sets[j]:
            buf_set = buf_set.union(interchg_sets[j])
            merged.append(j)
    local_interchg_list.append(buf_set)
    # reset the count variables.
    in_count=0
    out_count+=1
    # if out_count > 3:
    #     break
global_interchg_list = global_interchg_list + local_interchg_list
pickle.dump( [out_count,merged, global_interchg_list], open("intermediate_merged.p","wb"))

