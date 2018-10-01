import numpy as np
import random as rand

def accept_reject(u, p_sample, scores, tau):
	'''
	return 1 if accept, return 0 if reject.
	'''
	[p_prev, p_new] = p_sample
	[score_prev, score_new] = scores

	accept_threshold = np.exp(score_new/tau)/ np.exp(score_prev/tau)
	accept_threshold *=  p_prev/p_new
	if u >= accept_threshold or accept_threshold>=1 :
		return 1
	return 0


n_iter, n_a, n_sample= 0,0, 10  # num of samples
tau = 0.8
p_prev, p_new = 1.0, 0.7
score_prev, score_new=1.0, 0.7
sample_list=[]
rand.seed(a=1024)
hyp=''
# p_prev # evaluate prob of y* given the proposal distribution \theta_pre
while n_a < n_sample:
	#hyp, p_hyp= # generate hypothesis 

	#score_prev=  #get score
	u = rand.uniform(1,0)
	if accept_reject(u, [p_prev, p_new], [score_prev, score_new], tau):
		sample_list.append(hyp)
		n_a+=1
		print('n_a:', n_a )
	n_iter+=1
print("DONE", '\tn_iter:', n_iter, '\tn_a:',n_a)
