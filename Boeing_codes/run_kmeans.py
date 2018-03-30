import numpy as np
from scipy import cluster
from sklearn.cluster import KMeans as km
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA


# given data X
np.random.seed(123)
X = np.reshape( np.random.uniform(0,100,60), (10,6) )


#getting the elbow
# cluster_list = [km(n_clusters=i,init='k-means++',random_state=0).fit(X) for i in range(1,10)]
cluster_list = [cluster.vq.kmeans(X,i) for i in range(1,10)]
var_list = [var for (cent,var) in cluster_list]
plt.plot(range(1,10),var_list,marker="o")
plt.xlabel("variance")
plt.ylabel("size of cluster (k)")
plt.savefig("kmeans_var_size.pdf")

# add save function for the plot
plt.cla()
plt.clf()
plt.close()

# choose lowest # of clusters to use $k$
k = int(raw_input("Enter cluster size, please: "))

cent, var = cluster_list[k]
#use vq() to get as assignment for each obs.
assignment,cdist = cluster.vq.vq(X,cent)
# replace X to PCA mapped values.
pca = PCA(n_components=2)
# pca.fit(X)
Xp = pca.fit_transform(X)
plt.scatter(Xp[:,0], Xp[:,1], c=assignment)
# pyplot.show()
# plt.legend(bbox_to_anchor=(0, 1), loc='upper right', ncol=1)
plt.xlabel("dimension 1")
plt.ylabel("dimension 2")
plt.savefig("kmeans_result.pdf")
plt.cla()
plt.clf()
plt.close()
