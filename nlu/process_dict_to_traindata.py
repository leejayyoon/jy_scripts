import nltk.tokenize
import re
import csv
import pickle
import codecs
# import cPickle as pickle

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def convert_slot_to_BOI(slot_str):
	# doing this, so when we split with >,< 
	# that the delimiter is somehow still preserved		
	slot_str = re.sub('<','<-JY-',slot_str) 
	slot_split = re.split('> <|<|>|',slot_str)
	prefix = "-JY-"
	sentence_arry, BOI_arry, slot_arry=[],[],[]
	flag_inside=False
	for i, token in enumerate(slot_split):
		# print('BOI_arry at iteration %d' %i)
		# print token
		# print BOI_arry
		if len(token)>len(prefix) and token[:len(prefix)]==prefix:
			# we either get beginning of tag or end of tag.	
			if token[len(prefix)]=='/': #end of tag
				# no action when the tag ends.
				flag_inside=False
			else: # begining of tag
				BOI_tag = token[len(prefix):]
				slot_arry.append(BOI_tag)
				tmp_str = 'B-'+BOI_tag
				BOI_arry.append(tmp_str)
				flag_inside=True
		elif flag_inside:
			# for in_token in token.split():
			BOI_count=0
			for in_token in nltk.tokenize.word_tokenize(token):
				assert BOI_tag != ""
				sentence_arry.append(in_token)
				BOI_count+=1
				if BOI_count==1: #skip for the first token, as you alreay put B
					continue
				tmp_str = 'I-'+BOI_tag
				BOI_arry.append(tmp_str)
		else:
			# for in_token in token.split():
			for in_token in nltk.tokenize.word_tokenize(token):
				BOI_arry.append('O')
				sentence_arry.append(in_token)
	return slot_arry, sentence_arry, BOI_arry

def check_tag_validity(slot_str, debug_flag=False):
	left_count = slot_str.count('<')
	left_end_count = slot_str.count('</')
	right_count= slot_str.count('>')
	if debug_flag:
		print(slot)
	if left_count/2 != left_end_count:
		# print 'left_count/2 of <', left_count/2, ' and left_end_count of </', left_end_count,' does not match'
		return False	
	if left_count != right_count:
		# print 'left_count <', left_count, ' and right_count >', right_count,' does not match'
		return False
	return True

def write_list_to_csv(my_list, f_out, append=False, use_unicode=True):
		if append:
			open_flag="a"
		else:
			open_flag="w'"
		# with codecs.open(f_out, open_flag, encoding='utf-8') as f: 
		with open(f_out, open_flag) as f: 
			spamwriter = csv.writer(f)
			for s in my_list: 
				# f.writelines([s.encode('utf-8', 'replace')])
				# spamwriter.writerow([s])
				# if use_unicode:
				spamwriter.writerow([s.encode('utf-8', 'replace')])
				# else:
				# 	spamwriter.writerow([s])

# Data loading
flag_debug= False
datapath="../data/"
in_fname='dom_int_RAWslot_multi_dict.p'
with open(datapath+in_fname,'rb') as f:	
    [dict_dom_int_slot, dict_dom_slot, dict_int_slot]= pickle.load(f)


# Previous sanity checking code.
exception_sentences =[]
for intent, slot_list in dict_int_slot.iteritems():
	for slot in slot_list:
		if  not check_tag_validity(slot) or '><' in slot:
				exception_sentences.append(slot)
# print 'this slot dataset is Valid ! (tag-wise)'
exception_sentences=list(set(exception_sentences))
print('len(exception_sentences) %d' %(len(exception_sentences)))

# files to write
f_sent_out='./sentence_input.txt'
f_BOI_out='./sentence_output.txt'
slot_arry, sentence_arry, BOI_arry =[],[],[] 
count, nonAscii_intents = 0,0
for dom, int_dict in dict_dom_int_slot.iteritems():
	print('dom:\t%s' %dom)
	print('len intent\t%d' %len(int_dict))
	count += 1
	in_count=0
	# if dom=="web":
	for intent, slot_list in int_dict.iteritems():
		print('intent\t%s' %intent)
		if not is_ascii(intent):
			nonAscii_intents+=1
			print('... Skipping non-ascii intent ...')
			continue
		new_slot_list =[]
		if len(slot_list)==0:
			continue
		tot_sentence = []
		tot_BOI=[]
		slot_iter_count=0
		for slot in slot_list: 
			slot = slot.decode('utf-8')
			# exception case handling
			if  not check_tag_validity(slot) or '><' in slot:
				continue
			if not '</' in slot:
				# tokenize sentnece & append in to total sentence
				sentence_arry = nltk.tokenize.word_tokenize(slot)
				tmp_sent = ' '.join(sentence_arry)		
				tot_sentence.append(tmp_sent)
				
				# make BOI (with all O)
				BOI_tmp= 'O ' * len(sentence_arry) 
				tmp_str = "Int:"+ intent + " Dom:"+dom
				tot_BOI.append(BOI_tmp + tmp_str)
				continue
			slot_arry, sentence_arry, BOI_arry = convert_slot_to_BOI(slot)	
			if flag_debug:
				slot_iter_count+=1
				assert slot_iter_count<3
				print('------original_slot-----')
				print(slot)
				print('------slot_arry-----')
				print(slot_arry)
				print('------sentence_arry-----')
				print(sentence_arry)
				print('------BOI_arry-----')
			# 	print BOI_arry
			tmp_str = "Int:"+ intent + " Dom:"+dom
			BOI_arry.append(tmp_str)
			# update setnence, BOI list for training
			tmp_sent = ' '.join(sentence_arry)
			tot_sentence.append(tmp_sent)
			tot_BOI.append(' '.join(BOI_arry))
			# update dict_dom_int_slot	
			new_slot_list += slot_arry
			## previous code to update BOI
			# BOI_elem = ' '.join(BOI_arry)
			# BOI_elem += "\tInt:"+ intent +"\tDom:"+dom
			# tot_BOI.append(BOI_elem)
			# if 'B-' not in BOI_elem:
			# 	print BOI_elem			
		write_list_to_csv(tot_sentence, f_sent_out, append=True)
		# print tot_BOI
		write_list_to_csv(tot_BOI, f_BOI_out, append=True)
		in_count+=1
		if flag_debug:
			print('\tintent:\t%s' %intent)
			print('\tslot_list\t%s' %slot_list)
			print('\t\t tot_setnece:\t%s' %tot_sentence)
			print('\tBOI_list:\t%s' %BOI_arry)
			print('\sentence_arry:\t%s' %sentence_arry)
			print('----------------------')
			assert in_count<10
		dict_dom_int_slot[dom][intent]=list(set(new_slot_list))
		print('\tlen slot\t%d' %len(dict_dom_int_slot[dom][intent]))
	if flag_debug:
		assert count<1

## fixing rest of the dictionaries as well
for dom, slot_list in dict_dom_slot.iteritems(): 
	new_slot_list =[]
	for slot in slot_list:
		slot = slot.decode('utf-8')
		if  not check_tag_validity(slot) or '><' in slot:
			continue
		slot_arry, sentence_arry, BOI_arry = convert_slot_to_BOI(slot)	
		new_slot_list += slot_arry
	dict_dom_slot[dom]=list(set(new_slot_list))
print('fixing dict_dom_slot Done!')

for intent, slot_list in dict_int_slot.iteritems():
	new_slot_list =[]
	for slot in slot_list:
		slot = slot.decode('utf-8')
		if  not check_tag_validity(slot) or '><' in slot:
			continue
		slot_arry, sentence_arry, BOI_arry = convert_slot_to_BOI(slot)	
		new_slot_list += slot_arry
	dict_int_slot[intent]=list(set(new_slot_list))
print('fixing dict_int_slot Done!')

if not flag_debug:
	pickle.dump([dict_dom_int_slot, dict_dom_slot, dict_int_slot, exception_sentences] , open('dom_int_TAGslot_multi_dict.p','wb'))

if __name__ == "__main__":
    main()

# # # another function that I can have list of indices, then put I, B ..
