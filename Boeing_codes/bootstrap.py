import csv
import numpy as np
import cPickle as pickle
import argparse

# Write the function for the bootstrap.


# Estimate transition probabilities & nz distirbutions from the observed dataset.
# n_zero = 0
# n_one = 0
# n_zero_to_one = 0
# n_one_to_one = 0
# nz_dist = {}
def estimate_params(data, x_prev=None, n_zero=0, n_one=0, n_zero_to_one=0, n_one_to_one=0, nz_dist={}):
	#Count statistics for forming distribution.
	if x_prev is None:
		x_prev = 0 # if one forgets to add x_prev, then it is safe to assume,
		# beginning of the sales was 0 since it never existed
	if len(data)>1: # at the very first parameter estimation. (to avoid double counts in other cases)
		if x_prev:
			n_one +=1
			if x_prev in nz_dist:
				nz_dist[x_cur]+=1
			else:
				nz_dist[x_cur]=1
		else:
			n_zero +=1

	for x_cur in data[0:]:
		if x_cur:
			n_one += 1
			# estimate nz distribution
			if x_cur in nz_dist:
				nz_dist[x_cur]+=1
			else:
				nz_dist[x_cur]=1
			if x_prev:
				n_zero_to_one+=1
			else:
				n_one_to_one+=1
		else:
			n_zero += 1
		x_prev = x_cur
	# for now, just count, but we can also do,
	# given numpy array x is a occruence vector. (numbers not bigger than 0.)
	# sum(x) = n_one, len(x)-sum(x)=n_zero,
	# sum(x)-sum(x[:-1]*x[1:])
	# build nz_dist 
	count_list = nz_dist.keys()
	count_dist = np.array(nz_dist.values())
	count_dist_cdf = np.cumsum(count_dist)
	p_one2one= n_one_to_one/(n_one+0.0)
	p_zero2one= n_zero_to_one/(n_zero+0.0)

	distribution = [p_zero2one, p_one2one, count_list, count_dist_cdf]
	stats = [n_zero, n_one, n_zero_to_one, n_one_to_one, nz_dist]
	# sanity check
	if np.sum(count_dist) != n_one:
		raise ValueError("the nonzero count is not consistent in count_dist sum %d and n_one %d." \
						% (np.sum(count_dist), n_one))

	return [distribution, stats]


# Use this sample distribution to generate 2-5
# L = 3  # lead-time to look at.
# n_bootstrap = 5
def predict_leadtime(x_cur, distribution, L=3,n_bootstarp=5):
	np.random.seed(256)
	[p_zero2one, p_one2one, count_list, count_dist_cdf] = distribution
	LTD_dist = {}
	for i_bs in n_bootstrap:
		f_list= np.zeros(L+1,1)
		f_list[0] = x_cur
		# generate the random sequence from the	
		for i in range(L):
			f_list[i+1] = f_list[i]*np.random.binomial(1,p_one2one) +\
								 (1-f_list[i])*np.random.binomial(1,p_zero2one) 
		# at this point, f_list is just 0 or 1. --> get L random samples (uniform and standard deviation)
		unif_samples = np.random.uniform([0,n_one,L])
		z_samples = np.random.randn(L) #standard normal samples
		for i in range(L):
			if f_list[i+1]: # if the state is predicted as nonzero
				sample_idx = np.where( count_dist_cdf > unif_samples[i] )[0][0]
				temp = count_list[sample_idx]
				f_lsit[i+1] = temp + np.sqrt(temp)*z_samples[i] # or  np.random.randn(1)
				if f_list[i+1]<0: # if nonzero, just return original temp.
					f_list[i+1] = temp
		LTD_i = np.sum(f_list[1:])

		if LTD_i in LTD_dist:
			LTD_dist[LTD_i] += 1 # increase count:
		else:
			LTD_dist[LTD_i] =1

	if np.sum(LTD_dist.values()) != n_bootstrap:
		raise ValueError("the nonzero count is not consistent in count_dist sum %d and n_one %d." \
						% (np.sum(LTD_dist.values()), n_bootstrap))

	mean_estimate = np.sum(LTD_dist.keys()*LTD_dist.values())/(n_bootstrap+0.0)
	# LTD_dist #dist_estimate 

	return mean_estimate


# sample random number.
# get the nz counts
	# jitter --> JITTERED  = x* + \sqrt{X*}

#obsolete code in getting random L sequqence
		# if f_list[i]: #nonzero
		# 	f_list[i+1] = np.random.binomial(1,p_one2one) #binomial(n, p[, size])	Draw samples from a binomial distrib
		# 	sample_idx = np.where( count_dist_cdf > unif_samples[i] )[0][0]
		# 	f_list[i+1] = 
		# 	# or 
		# else: #zero just pass.
		# 	f_list[i+1] = np.random.binomial(1,p_zero2one)



# def main(L=3,n_bs=5):


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     # parser.add_argument('changes', nargs='*',
#     #                     help='Changes to default values',
#     #                     default = '')
#     # # test params
#     parser.add_argument('--L', help="Lead time argument",
#                         default=3)
#     parser.add_argument('--n_bs', help="Number of times to bootstrap",
#                         default=5)
# 	args = parser.parse_args()
#     main(args.L,args.n_bs)
