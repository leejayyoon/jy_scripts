import cPickle as pickle
# import pickle
# with open('dom_int_slot_dict.p','rb') as f:
#     dom_int_slot_dict= pickle.load(f)
with open('dom_int_slot_multi_dict.p','rb') as f:
    [dict_dom_int_slot, dict_dom_slot, dict_int_slot]= pickle.load(f)

count = 0
for dom, int_dict in dict_dom_int_slot.iteritems():
	print 'dom:\t', dom
	# count +=len(int_dict)
	print 'len intent\t', len(int_dict)
	assert (len(int_dict)==len(set(int_dict.keys())))
	count += 1
	if count >3: 
		break
	for intent, slot_list in int_dict.iteritems():
		print '\tintent:\t', intent
		print '\tslot_list:\t', 
		for slot in slot_list:
			print '\t\tslot:\t', slot
		# print '\tlen slot:\t', len(set(slot_list))
		# int_dict[intent] = list(set(slot_list))
		# assert (len(slot_list)==len(set(slot_list))) 


count=0
new_slot_list=[]
for dom, int_dict in dict_dom_int_slot.iteritems():
	assert (len(int_dict)==len(set(int_dict.keys())))
	count += 1
	if count> 3:
		break
	for intent, slot_list in int_dict.iteritems():
		print '\tintent:\t', intent
		for slot in slot_list:
			if '</' in slot:
				new_slot_list.append(slot)
		# dict_dom_int_slot[dom][intent]=new_slot_list
		print '\tlen slot:\t', len(set(slot_list))
		print '\tlen new slot:\t', len(set(new_slot_list))
		assert (len(slot_list)==len(set(slot_list))) 
		assert (len(new_slot_list)==len(set(new_slot_list))) 



for dom, slot_list in dict_dom_slot.iteritems():
	print 'dom:\t', dom
	# print 'len slot\t', len(slot_list)
	print 'len_set_slot\t', len(set(slot_list))
	# assert (len(slot_list)==len(set(slot_list)))

slot_int_dict={}
for intent, slot_list in dict_int_slot.iteritems():
	for slot in slot_list:
		if slot not in slot_int_dict:
			slot_int_dict[slot]=[intent]
		else:
			slot_int_dict[slot].append(intent)
	# print 'intent:\t', intent
	# # print 'len slot\t', len(slot_list)
	# print 'len_set_slot\t', len(set(slot_list))
	# assert (len(slot_list)==len(set(slot_list)))
