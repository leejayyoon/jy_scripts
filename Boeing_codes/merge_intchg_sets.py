import cPickle as pickle

with open("interchg_sets.p",'rb') as f:
    interchg_sets=pickle.load(f)

out_count=0
in_count=0

# for i in range(len(interchg_sets)):
#     print '========', i,":", interchg_sets[i], '========'
#     in_count +=1 
#     if in_count > 10:
#         break

global_interchg_list = []
merged = []
out_count=0
in_count=0
for i in range(len(interchg_sets)):
    if i in merged:
        out_count+=1
        continue 

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
    global_interchg_list.append(list(buf_set))
    # reset the count variables.
    in_count=0
    out_count+=1
    # if out_count > 3:
    #     break

pickle.dump( global_interchg_list, open("merged_interchg_sets_2nd.p","wb"))

