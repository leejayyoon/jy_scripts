import sys
import csv
# import numpy as np
import cPickle as pickle
# from decimal import *
# import string

csv.field_size_limit(sys.maxsize)

def write_list_to_csv(my_list, f_out):
    with open(f_out, 'wb') as f:
        spamwriter = csv.writer(f)
        for s in my_list:
            spamwriter.writerow([s])


def get_dictionary(in_file, list_or_dict="dict", key_col=0, val1_col=1, val2_col=2):# getting part_interest_list
    count = 0
    out_dict = {}
    with open(in_file,'rb') as csvfile:
        spamreader = csv.reader(csvfile,delimiter='\t')#,quotechar='"') #,quotechar= 
        # if list_or_dict == "dict":
        for line in spamreader:
            # for case insensitive comparison.
            val1=line[val1_col]
            val2=line[val2_col]
            if line[key_col] in out_dict.keys():
                if val1 in out_dict[line[key_col]]:
                    out_dict[line[key_col]][val1].append(val2)
                else:
                    out_dict[line[key_col]][val1]=[val2]
            else:
                out_dict[line[key_col]]={}
                out_dict[line[key_col]][val1]=[val2]
            count += 1
            if count %10000 ==0:
                print 'count:', count
    return out_dict

def get_mul_dictionary(in_file, list_or_dict="dict", key_col=0, val1_col=1, val2_col=2):# getting part_interest_list
    count = 0
    dict_dom_int_slot = {}
    dict_dom_slot = {}
    dict_int_slot = {}
    with open(in_file,'rb') as csvfile:
        next(csvfile)
        spamreader = csv.reader(csvfile,delimiter='\t')#,quotechar='"') #,quotechar= 
        # if list_or_dict == "dict":
        for line in spamreader:
            # for case insensitive comparison.
            dom = line[key_col]
            intent=line[val1_col]
            slot=line[val2_col]
            if dom in dict_dom_int_slot.keys():
                # case where domain exists
                if intent in dict_dom_int_slot[dom]:
                    dict_dom_int_slot[dom][intent].append(slot)
                else:
                    dict_dom_int_slot[dom][intent]=[slot]
            else:
                # domain dose not exist
                dict_dom_int_slot[dom]={}
                dict_dom_int_slot[dom][intent]=[slot]

            if dom in dict_dom_slot.keys():
                if slot not in dict_dom_slot[dom]:
                    dict_dom_slot[dom].append(slot)
            else:
                dict_dom_slot[dom]=[slot]

            if intent in dict_int_slot.keys():
                if slot not in dict_int_slot[intent]:
                    dict_int_slot[intent].append(slot)
            else:
                dict_int_slot[intent]=[slot]


            count += 1
            if count %10000 ==0:
                print 'count:', count
    return dict_dom_int_slot, dict_dom_slot, dict_int_slot

def main():
    fname="../../data/cortana_20170323_domain_intent_slot.tsv"
    # dom_int_slot_dict =get_dictionary(fname, "dict") ## what I orgiinally had.
    [dict_dom_int_slot, dict_dom_slot, dict_int_slot] = get_mul_dictionary(fname, "dict")

    # ##  fixing duplicate slots issue
    count=0
    new_slot_list=[]
    print 'dict_dom_int_slot length:\t', len(dict_dom_int_slot)
    for dom, int_dict in dict_dom_int_slot.iteritems():
        assert (len(int_dict)==len(set(int_dict.keys())))
        count+=1
        print count
        for intent, slot_list in int_dict.iteritems():
            dict_dom_int_slot[dom][intent] = list(set(slot_list))
    print '----------------dict_dom_int_slot processing done!'

    for dom, slot_list in dict_dom_slot.iteritems(): 
        dict_dom_slot[dom]=list(set(slot_list))
    print '----------------dict_dom_slot processing done!'

    for intent, slot_list in dict_int_slot.iteritems():
        dict_int_slot[intent]=list(set(slot_list))
    print '----------------dict_int_slot processing done!'


    #print dom_int_slot_dict
    # pickle.dump(dom_int_slot_dict, open('dom_int_slot_dict.p','wb'))
    # This is old approach
    # pickle.dump([dict_dom_int_slot, dict_dom_slot, dict_int_slot] , open('dom_int_slot_multi_dict.p','wb'))
    pickle.dump([dict_dom_int_slot, dict_dom_slot, dict_int_slot] , open('dom_int_RAWslot_multi_dict.p','wb'))

    # with open('dom_int_slot_multi_dict.p','rb') as f:
    #     [dict_dom_int_slot, dict_dom_slot, dict_int_slot]= pickle.load(f)



if __name__ == "__main__":
    main()