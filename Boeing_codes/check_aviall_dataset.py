import csv

# CHECKING Aviall time series dataset. (combined pre-sap, post-sap)
f_parts2idx= '/app/part-demand/team-repo/data_process/adams_binning/unique.tsv'
count = 0
part_set = set()
duplicate_dict = {}
d_count = 0
with open(f_parts2idx) as csvfile:
	spamreader = csv.reader(open(f_parts2idx,'rb'),delimiter='\t')
	for line in spamreader:
	    if count%10000 == 0 :
	        print count
	    Boeing_partid = line[0].split("=")[0]
	    if Boeing_partid in part_set:
	    	# print 'aviall part:', line[0], 'boeing part:', line[0].split("=")[0]
	    	if Boeing_partid in duplicate_dict:
	    		duplicate_dict[Boeing_partid] +=1
	    	else:
	    		duplicate_dict[Boeing_partid] =1
	    	d_count+=1
	    else:
	    	part_set.add(Boeing_partid)
	    count += 1


print '# of parts:', count
print '# of Boeing parts:', len(part_set)
print '# of duplicates:', d_count
print '# of Boeing parts with duplicates:', len(duplicate_dict)

# of parts: 295961
# of Boeing parts: 257884
# of duplicates: 38077
# of Boeing parts with duplicates: 30484


# CHECKING Aviall interchangeability dataset.
# part_to_set = {}
# set_of_parts_intchg = set()
count = 0
d_count=0
duplicate_part_intchg ={}
intchg_part_set_boeing =set()
intchg_part_set_aviall =set()
f_interchange = "/app/part-demand/data/aviall/aviall-part-interchangeability.csv"
with open(f_interchange) as csvfile:
    spamreader = csv.reader(csvfile,delimiter=',',quotechar='"')
    spamreader.next()
    for line in spamreader:
        if count%10000 == 0:
            print count
        set_id = line[0]
        aviall_part_id = line[5]
        if aviall_part_id in ['G50009201442040=E7','G5000-0920-1442-0400=E7']:
    		print aviall_part_id
        	print set_id
        # if aviall_part_id in intchg_part_set_aviall:
        # 	print aviall_part_id
        # 	print set_id
        intchg_part_set_aviall.add(aviall_part_id)
        #
        Boeing_partid = aviall_part_id.split("=")[0]
        if Boeing_partid in intchg_part_set_boeing:
	    	if Boeing_partid in duplicate_part_intchg:
	        	duplicate_part_intchg[Boeing_partid] +=1
	        else:
	        	duplicate_part_intchg[Boeing_partid] = 1
	        d_count +=1
        else:
        	intchg_part_set_boeing.add(Boeing_partid)
        count += 1
        # if part_id in part_to_set:
        # 	part_to_set[part_id].add(set_id)
        # else: 
        # 	part_to_set[part_id] = set([set_id])
        # set_of_parts_intchg.add(part_id)
print '# of parts:', count
print '# of Boeing parts:', len(intchg_part_set)
print '# of duplicates:', d_count
print '# of Boeing parts with duplicates:', len(duplicate_part_intchg)
print '# of parts in intchg_part_set_aviall:', len(intchg_part_set_aviall)

# of parts: 250988
# of Boeing parts: 173585
# of duplicates for Boeing perspective: 77403
# of Boeing parts with duplicates: 69684
# duplicate aviall_part_id in the interchangeability set: 1) G50009201442040=E7, 2) G5000-0920-1442-0400=E7
# interchangeability set for duplicate: 005056B900B21EE58588CFCE557FCA4D, 005056B927901ED58588DC799A110999

