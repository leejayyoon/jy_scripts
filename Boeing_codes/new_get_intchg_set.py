import cPickle as pickle

f_interchange = "/app/part-demand/data/parts/STEP_PER_INTERCHANGEABILITY.txt"
# out_file = "/net/psn02hom/home/z/zi871e/"

interchg_sets = [[],[],[],[],[],[],[]]
global_interchg_set = set()
local_interchg_set = [set(),set(),set(),set(),set(),set()]
count = 0
new_count = 0
set_idx=0
with open(f_interchange) as f:
    next(f)
    for line in f:
        if new_count%100 == 0 :
            print count
        new_insert_flag = True
        ls = line.split('_Z_')
        prev_part = ls[0]
        new_part = ls[3]
        if (prev_part in local_interchg_set[set_idx]) or (new_part in local_interchg_set[set_idx]):
            new_insert_flag = False
        if new_insert_flag:
            interchg_sets[set_idx].append(set([prev_part,new_part]))
            # print "appended"
        else:
            # print "added to origianl set !!!!!!!!!!"
            # print prev_part, new_part
            for x in interchg_sets[set_idx]:
                if prev_part in x:
                    x.add(new_part)
                    insert_flag = True
                elif new_part in x:
                    x.add(prev_part)
                    insert_flag = True
            # print count 
        local_interchg_set[set_idx].update([prev_part,new_part])
        count += 1
        new_count +=1 
        if new_count ==73000:
            global_interchg_set.update(local_interchg_set[set_idx])
            set_idx += 1
            print 'set_idx shifted to', set_idx
            new_count = 0
        # if count >20 :
        #   break

pickle.dump( [interchg_sets, local_interchg_set]  , open("interchg_sets_new.p","wb"))

