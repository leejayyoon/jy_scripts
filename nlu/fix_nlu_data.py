#fix_nlu_data

import cPickle as pickle
# with open('dom_int_slot_multi_dict.p','rb') as f:
with open('dom_int_slot_multi_dict_OLD.p','rb') as f:	
    [dict_dom_int_slot, dict_dom_slot, dict_int_slot]= pickle.load(f)

# first chceck whether you have non-slot dataset in the old dictionary or not.
## simply by printing ...
# 


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

# ## fixing no tag slots.
# count=0
# cnt=0
# tag_cnt = 0
# print 'dict_dom_int_slot length:\t', len(dict_dom_int_slot)
# for dom, int_dict in dict_dom_int_slot.iteritems():
# 	count+=1
# 	print count
# 	for intent, slot_list in int_dict.iteritems():
# 		new_slot_list=[]
# 		for slot in slot_list:
# 			cnt+=1
# 			if '</' in slot:
# 				tag_cnt+=1
# 				new_slot_list.append(slot)
# 		dict_dom_int_slot[dom][intent]=new_slot_list
# print '----------------dict_dom_int_slot processing done!'
# print '--------'
# print 'cnt', cnt
# print 'nt_cnt', cnt - tag_cnt

# cnt=0
# tag_cnt = 0
# for dom, slot_list in dict_dom_slot.iteritems(): 
# 	new_slot_list=[]
# 	for slot in slot_list:
# 		cnt+=1
# 		if '</' in slot:
# 			new_slot_list.append(slot)
# 			tag_cnt+=1
# 	dict_dom_slot[dom]=new_slot_list
# print '--------'
# print 'cnt', cnt
# print 'nt_cnt', cnt - tag_cnt

# cnt=0
# tag_cnt = 0
# for intent, slot_list in dict_int_slot.iteritems():
# 	new_slot_list=[]
# 	for slot in slot_list:
# 		cnt+=1
# 		if '</' in slot:
# 			tag_cnt+=1
# 			new_slot_list.append(slot)
# 	dict_int_slot[intent]=new_slot_list
# print '--------'
# print 'cnt', cnt
# print 'nt_cnt', cnt - tag_cnt

#sanity check
for dom, int_dict in dict_dom_int_slot.iteritems():
	assert (len(int_dict)==len(set(int_dict.keys())))
	for intent, slot_list in int_dict.iteritems():
		assert (len(slot_list)==len(set(slot_list))) 
print 'SANITY_CHECK: dict_dom_int_slot done!'

for dom, slot_list in dict_dom_slot.iteritems(): 
	assert (len(slot_list)==len(set(slot_list)))
print 'SANITY_CHECK: dict_dom_slot done!'

for intent, slot_list in dict_int_slot.iteritems():
	assert (len(slot_list)==len(set(slot_list)))
print 'SANITY_CHECK: dict_int_slot done!'

pickle.dump([dict_dom_int_slot, dict_dom_slot, dict_int_slot] , open('dom_int_RAWslot_multi_dict.p','wb'))

