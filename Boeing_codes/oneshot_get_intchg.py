import cPickle as pickle

f_interchage="/app/part-demand/data/aviall/aviall-part-interchangeability.csv"
#f_interchange = "/app/part-demand/data/parts/STEP_PER_INTERCHANGEABILITY.txt"
# out_file = "/net/psn02hom/home/z/zi871e/"

interchg_sets = []
global_interchg_set = set()
count = 0
with open(f_interchange) as f:
    next(f)
    for line in f:
        if count%100 == 0 :
            print count
        new_insert_flag = True
        ls = line.split('_Z_')
        #ls = line.split('_Z_')
        prev_part = ls[0]
        new_part = ls[3]
        if (prev_part in global_interchg_set) or (new_part in global_interchg_set):
            new_insert_flag = False
        if new_insert_flag:
            interchg_sets.append(set([prev_part,new_part]))
            # print "appended"
        else:
            # print "added to origianl set !!!!!!!!!!"
            # print prev_part, new_part
            buf_set = set()
            for x in interchg_sets:
                delete_flag=False
                if prev_part in x:
                    x.add(new_part)
                    buf_set = buf_set.union(x)
                    delete_flag = True
                elif new_part in x:
                    x.add(prev_part)
                    buf_set = buf_set.union(x)
                    delete_flag = True

                if delete_flag: #removal of already combined sets
                    interchg_sets.remove(x)
            interchg_sets.append(buf_set)
            # print count 
        global_interchg_set.update([prev_part,new_part])
        count += 1
        # if count >20 :
        #   break

pickle.dump( interchg_sets, open("interchg_sets_oneshot.p","wb"))
