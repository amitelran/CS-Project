from real_similarities import calcJaccard
from cluster_class import Cluster
import settings
import json
import dump_load_args
import trace_class
import numpy

# ================================================================================================================================
#	 LSH (Locality Sensitive Hashing \ Near-Neighbour Search) calculation, Buckets building, Classification of unclassified traces
# ================================================================================================================================

## Definitons:

	## Candidate pair - Any pair of traces that hashed to the same bucket for any of the hashings.
		##  We check only candidate pairs for similarity.
	## True Positives - similiar trace pairs that hash to the same bucket under at least one of the hash functions.
	## False Positives - dissimilar trace pairs that hash to the same bucket.
	## False Negatives - similar trace pairs that don't hash to the same bucket.

	## Given MinHash signatures, we will divide the signature matrix into B bands, each band consisting R rows.
		## for each band, there is a hash function that takes vectors of R integers(the portion of
		## one column within that band) and hashes them to some large number of buckets.
		## We use a separate bucket array for each band, so columns with the same vector in
		## different bands will not hash to the same bucket.

# =============================================================================

# Build buckets for traces classification:
# Takes the signatures matrix 'sigs', divide it to 'b' bands, each with 'r' rows, hashes each band and saves the
# index of the respective trace (by signature index) in the hash 2 dimensional array ([band-number][hash-result]).

traces = dict()

def build_buckets(sigs, b, r, docsObjects):
	print "\nBuilding buckets with LSH...\n"
	hashMax = settings.hashMax		# Get the maximal number of hash functions as set in settings.py
	buckets = dict()
	clusters = dict()

	# Hashing for each of the bands (number of bands as set by 'b' input)
	for i in range(b):
		for j in range(0, len(sigs)):		# Go through all line elements in a band row (number of columns of signatures matrix)
			#print("i = "+str(i)+", j = "+str(j))
			#print(sigs[j][b*(i):b*(i)+r])
			#curTrace = docsObjects[j].get_filename()

			curTrace = docsObjects[j]
			start = b*i				# start point of the band
			if i == b-1:			# If reached to the last band, band's end is till the end of sigs (None respresents absence of a value)
				end = None
			else:
				end = b*i + r		# If not the last band, set 'end' as the start of the band plus number of rows in a single band

			curHash = int(hash(tuple(sigs[j][start:end]))) % hashMax		# Hash current band

			# Add current bucket(curHash) to the trace that the current signature represent
			if curTrace in traces:
				traces[curTrace].append(curHash)
			else:
				traces[curTrace] = [curHash]

			# Check for membership of current hashing in the buckets dictionary structure:
			# If already existing bucket for hash value --> append to the corresponding bucket
			# else, map the new bucket according to the hashing value
			if curHash in buckets:
				buckets[curHash].append(curTrace)
			else:
				buckets[curHash] = [curTrace]

			# Add trace to cluster (if cluster does not exist, create the cluster first)
			if curHash in clusters:
				clusters[curHash].append_trace(curTrace)
			else:
				clusters[curHash] = Cluster(curHash)
				clusters[curHash].append_trace(curTrace)

	# Calculate medioids for clusters, and compute distance vector for each of the clusters
	print("Number of clusters (buckets): %d" % len(clusters))
	calc_clusters_medioids(clusters)
	#medioids_compare(clusters)
	#for clusterKey, clusterValue in clusters.items():
	#	clusterValue.print_cluster_data()

	#dump_load_args.DumpBuckets(buckets)			# Dump data into buckets data file
	#dump_load_args.DumpTraces(traces)			# Dump data into traces data file
	#dump_load_args.DumpClusters(clusters)
	return buckets, clusters



# Build different buckets array for each band separately
def build_buckets2(sigs, b, r, docsObjects):
	print "\nBuilding buckets for each band in sigs separately with LSH...\n"
	hashMax = settings.hashMax		# Get the maximal number of hash functions as set in settings.py
	buckets = dict()
	medioids = dict()

	# Hashing for each of the bands (number of bands as set by 'b' input)
	for i in range(b):
		buckets_i = dict()					# Initialize new buckets set for single band
		for j in range(0, len(sigs)):		# Go through all line elements in a band row (number of columns of signatures matrix)
			#print("i = "+str(i)+", j = "+str(j))
			#print(sigs[j][b*(i):b*(i)+r])
			curTrace = docsObjects[j]
			start = b*i				# start point of the band
			if i == b-1:			# If reached to the last band, band's end is till the end of sigs (None respresents absence of a value)
				end = None
			else:
				end = b*i + r		# If not the last band, set 'end' as the start of the band plus number of rows in a single band
			curHash = int(hash(tuple(sigs[j][start:end]))) % hashMax

			# Add current bucket(curHash) to the trace that the current signature represent
			if curTrace in traces:
				traces[curTrace].append(curHash)
			else:
				traces[curTrace] = [curHash]

			# Check for membership of current hashing in the buckets dictionary structure:
			# If already existing bucket for hash value --> append to the corresponding bucket
			# else, map the new bucket according to the hashing value
			if curHash in buckets_i:
				buckets_i[curHash].append(curTrace)
			else:
				buckets_i[curHash] = [curTrace]

			if j == (len(sigs)-1):
				medioids[i] = calc_clusters_medioids(buckets_i)
				buckets[i] = buckets_i
				#print("buckets["+str(i)+"]:")
				#print(buckets_i)

	dump_load_args.DumpBuckets(buckets)			# Dump data into buckets data file
	dump_load_args.DumpTraces(traces)			# Dump data into traces data file
	#print traces
	print("build_buckets2: ")
	print(buckets)
	return buckets



# Classify new incoming traces (similar way to the build_buckets function above)
def classify_new_data(sigs, b, r, buckets, docsObjects):
	print "\nClassifying with LSH...\n"
	hashMax =  settings.hashMax
	neighbors = [list() for _ in range(len(sigs))]
	for i in range(b):
		for j in range(len(sigs)):
			#print("i = "+str(i)+", j = "+str(j))
			#print(sigs[j][b*(i):b*(i)+r])
			curTrace = docsObjects[j].get_filename()
			start = b*i
			if i == b-1:
				end = None
			else:
				end = b*i+r
			curHash = int(hash(tuple(sigs[j][start:end]))) % hashMax

			if curTrace in traces:
				traces[curTrace].append(curHash)
			else:
				traces[curTrace] = [curHash]

			if curHash in buckets:
				# buckets[i][curHash].append(j)
				neighbors[j].append((curHash,buckets[curHash]))
			else:
				# buckets[i][curHash] = [j]
				neighbors[j].append((curHash,[]))
	# dump_load_args.DumpBuckets(buckets)
	# dump_load_args.DumpTraces(traces)
	# print traces
	return neighbors


# Classify data separately for each of the bands
def classify_new_data2(sigs, b, r, buckets, docsObjects):
	print "\nClassifying with LSH with separated buckets for each of the bands...\n"
	hashMax = settings.hashMax
	neighbors = [list() for _ in range(len(sigs))]
	#for i in range(0, len(buckets)):
		#print("\nbuckets[" + str(i) + "]: ", i,  buckets[i])
		#for j in buckets[i]:
			#print(j, buckets[i][j])
			#print(list(buckets[i][j]))

	for i in range(b):
		print("\nclassify new data 2 buckets[i]:")
		#print("len of buckets["+str(i)+"]: ", len(buckets[i]))
		print("bucket["+str(i)+"]: ", buckets[i])
		#print("len of sigs[i]: ", len(sigs))
		for j in range(len(sigs)):
			#print("i = "+str(i)+", j = "+str(j))
			#print(sigs[j][b*(i):b*(i)+r])
			curTrace = docsObjects[j].get_filename()
			start = b*i
			if i == b-1:
				end = None
			else:
				end = b*i+r
			curHash = int(hash(tuple(sigs[j][start:end]))) % hashMax

			if curTrace in traces:
				traces[curTrace].append(curHash)
			else:
				traces[curTrace] = [curHash]

			if curHash in buckets[i]:
				# buckets[i][curHash].append(j)
				#for k in buckets[i]:
					#neighbors[j].append((curHash, buckets[i][k]))
				print('bucket['+str(i)+']['+str(curHash)+']: ', buckets[i][curHash])
				#print('neighbors['+str(j)+']: ', neighbors[j])
				neighbors[j].append((curHash, buckets[i][curHash]))
				print("neighbors["+str(j)+"].append: ", neighbors[j])
			else:
				# buckets[i][curHash] = [j]
				neighbors[j].append((curHash, []))

			if j == (len(sigs)-1):
				print("neighbors["+str(i)+"]:")
				print(neighbors[j])
				print("")
	# dump_load_args.DumpBuckets(buckets)
	# dump_load_args.DumpTraces(traces)
	# print traces

	print("neighborrrrrrrrrrrrrrrrrrrrrrrs2:")
	for j in neighbors:
		print(j)
	return neighbors

# =============================================================================

# Function that experiments with different Bands & Rows values,
# and finds the optimal Bands & Rows values according to a given weight and similarity threshold.

def findRB(signatures,docsAsShingles,jumps,falsePositivesWeight,falseNegativesWeight,similarityThreshold):
	numOfAllTruePairs = 0
	bestNumOfBands = 0			# Insert to this variable what is the optimal number of bands
	minValue = float("inf")		# float("inf"): Unbounded upper value (no number would be greater than this representation of infinity)

	# Accumulate total number of all relatively similar pairs (If similarity is greater than the similarity threshold)
	for sim in calcJaccard(docsAsShingles):
		numOfAllTruePairs = numOfAllTruePairs + (sim > similarityThreshold)

	# For each band check:
	for numOfBands in range(jumps,settings.numHashes/2,jumps):
		buckets = build_buckets(signatures, numOfBands, settings.numHashes / numOfBands)
		candidates = set()
		for bucketArray in buckets:
			for bucket in bucketArray:
				if (len(bucket) >= 2):
					b = list(bucket);
					for i in range(len(b)):
						for j in range(i + 1, len(b)):
							candidates.add(frozenset([b[i], b[j]]))		# The frozenset type is immutable and hashable -- its contents cannot be altered after is created; however, it can be used as a dictionary key or as an element of another set.

		i = 1
		numOfTruePositives = 0
		# Accumulate number of True Positives pairs of traces
		for pair in candidates:
			pairList = list(pair)
			# print("pair #"+str(i)+": "+str(pairList))
			i = i + 1
			if (calcJaccard([docsAsShingles[pairList[0]], docsAsShingles[pairList[1]]])[0] > similarityThreshold):
				numOfTruePositives = numOfTruePositives + 1
		# print(buckets)
		falsePositives = len(candidates) - numOfTruePositives		# Accumulate number of False Positives as the completion of True Positives regarding number of candidates
		falseNegatives = numOfAllTruePairs - numOfTruePositives		# Accumulate number of False Negatives as the completion of True Positives regarding to the total number of all truely similar pairs
		print("============ B = "+str(numOfBands)+", R = "+str(settings.numHashes/numOfBands)+" ==========")
		print("similar pairs (above "+str(similarityThreshold)+"): " + str(numOfTruePositives) + " out of " + str(len(candidates)))
		print("false positives: " + str(falsePositives) + ", false negatives: " + str(falseNegatives))
		print("========================================\n")
		curValue = falsePositivesWeight*falsePositives + falseNegativesWeight*falseNegatives;	# Value for current iteration
		# If the value received for current iteration is less than current minimal value, set minimum indicating variables accordingly
		if curValue < minValue:
			minValue = curValue
			bestNumOfBands = numOfBands
		if(falsePositives > (len(candidates))/2):	# If False Positives for current bands setting is greater than half the number of candidates, break iteration
			break

	print("Best parameters with FP weight = "+str(falsePositivesWeight)+", FN weight = "+str(falseNegativesWeight)+":")
	print("B = "+str(bestNumOfBands)+", R = "+str(settings.numHashes/bestNumOfBands))
	return [bestNumOfBands,settings.numHashes/bestNumOfBands]



# ================================================================================================================================
#				Compute medioid for every cluster (=bucket), given buckets array
# ================================================================================================================================


def calc_clusters_medioids(clusters):
	print("\nCreating cluster medioids...")
	medioids = dict()								# Initialize medioids dictionary

	for clusterKey, clusterValue in clusters.items():
		cluster_traces = clusters[clusterKey].cluster_traces
		medioid_trace = cluster_traces[-1]						# Initialize medioid trace to be the last (in case of single trace in a bucket)
		maximal_mediod_value = 0

		# Iterate over every trace in the bucket (reset values)
		for t1 in cluster_traces:
			t1_medioid_value = 0
			t1_shingles = t1.get_shingles()

			# Iterate over every other trace in the bucket and accumulate Jaccard similarities
			for t2 in cluster_traces:
				if t1 is t2:
					continue
				t2_shingles = t2.get_shingles()

				union_size = float(len(t1_shingles.union(t2_shingles)))
				if union_size == 0:
					t1_medioid_value += 0
				else:
					t1_medioid_value += (len(t1_shingles.intersection(t2_shingles)) / union_size)

			#print(t1, t1_medioid_value)

			# Update medioid value and the medioid trace
			if (t1_medioid_value > maximal_mediod_value):
				maximal_mediod_value = t1_medioid_value
				medioid_trace = t1

			# When reached the last trace in the bucket, append the medioid value to the medioids data structure
			if (t1 is cluster_traces[-1]):
				medioids[clusterKey] = ((medioid_trace, maximal_mediod_value))
				clusters[clusterKey].medioid = ((medioid_trace, maximal_mediod_value))

	#print("\nCalculated medioids:")
	#print(medioids)
	#return medioids

"""
def calc_buckets_medioids(buckets):
	print("\nCreate cluster medioids:")
	print(buckets)
	medioids = dict()								# Initialize medioids dictionary

	for bucket in buckets.keys():
		print("\nbucket:")
		print(bucket)
		medioid_trace = buckets[bucket][-1]			# Initialize medioid trace to be the last (in case of single trace in a bucket)
		maximal_mediod_value = 0

		# Iterate over every trace in the bucket (reset values)
		for t1 in buckets[bucket]:
			t1_medioid_value = 0
			t1_shingles = t1.get_shingles()

			# Iterate over every other trace in the bucket and accumulate Jaccard similarities
			for t2 in buckets[bucket]:
				if t1 is t2:
					continue
				t2_shingles = t2.get_shingles()
				t1_medioid_value += (len(t1_shingles.intersection(t2_shingles)) / float(len(t1_shingles.union(t2_shingles))))

			#print(t1, t1_medioid_value)

			# Update medioid value and the medioid trace
			if (t1_medioid_value > maximal_mediod_value):
				maximal_mediod_value = t1_medioid_value
				medioid_trace = t1

			# When reached the last trace in the bucket, append the medioid value to the medioids data structure
			if (t1 is buckets[bucket][-1]):
				medioids[bucket] = ((medioid_trace, maximal_mediod_value))
				print("Chosen medioid:")
				print(medioids[bucket])

	#print("\nCalculated medioids:")
	#print(medioids)
	#return medioids
"""

def calc_trace_distance_from_all_mediods(clusters, traces):
	""""""
	print("Calculating %d traces distances from all mediods" % len(traces))
	averages = []
	medians = []
	maxes = []

	for trace in traces:
		traceShingles = trace.get_shingles()
		jSims = []
		# Iterate over all buckets medioids in the medioids dictionary
		label = trace.get_malicious_benign_label()
		print("\n\n%s Trace: %s , filename(MD5): %s" % (label, trace.get_name(), trace.get_filename()) )
		for index1, clusterKey in enumerate(clusters):
			cluster = clusters[clusterKey]
			medioidTrace = cluster.medioid[0]
			medioid_shingles = medioidTrace.get_shingles()

			union_size = float(len(traceShingles.union(medioid_shingles)))
			if union_size == 0:
				trace_medioid_JSim = 0
			else:
				trace_medioid_JSim = (
					len(traceShingles.intersection(medioid_shingles)) / union_size)

			jSims.append(trace_medioid_JSim)

		jSims_numpy_array = numpy.array(jSims)
		avg = numpy.mean(jSims_numpy_array)
		averages.append(avg)
		SD = numpy.std(jSims_numpy_array)  # sqrt(mean(abs(x - x.mean())**2))
		median = numpy.median(jSims_numpy_array)
		medians.append(median)
		max = numpy.max(jSims_numpy_array)
		maxes.append(max)
		min = numpy.min(jSims_numpy_array)
		print("\tAverage JSim from mediods: %f, SD: %f " % (avg, SD))
		print("\tMedian:%f" % median)
		print("\tMax:%f , Min: %f"% (max, min))

	print("\n ~~~~~~~~~~~~~~ Summary ~~~~~~~~~~~~~")
	cnt, maxes_min, maxes_max, maxes_median, maxes_avg, maxes_std = get_count_min_max_median_avg_stdd(maxes)
	print("Maxes: max:%f, median:%f avg:%f, sd:%f" % (maxes_max,maxes_median,maxes_avg,maxes_std))
	print(str(maxes) + "\n")
	#plot_hist(maxes)
	return averages, medians, maxes


def get_count_min_max_median_avg_stdd(numbers_list):#TODO move to other module
	""" returns the count,min, max, median, avg, std """
	numpyarray = numpy.array(numbers_list)
	min = numpy.max(numpyarray)
	max = numpy.max(numpyarray)
	median = numpy.median(numpyarray)
	avg = numpy.mean(numpyarray)
	std = numpy.std(numpyarray)
	return len(numbers_list),min, max, median, avg, std

def plot_hist(x):
	#import matplotlib.pyplot as plt
	#plt.hist(x, normed=True, bins=30)
	#plt.show()

	import pylab as p

	y, binEdges = numpy.histogram(x, bins=100)
	bincenters = 0.5 * (binEdges[1:] + binEdges[:-1])
	p.plot(bincenters, y, '-')
	p.show()


# ================================================================================================================================
#				Calculate clusters (buckets) medioids distance using Jaccard similarity
# ================================================================================================================================


def medioids_compare(clusters):
	#print("\n================= Medioids Similarity =================")

	# Iterate over all buckets medioids in the medioids dictionary
	print("\nCalculating medioids distances...\n")
	for index1, clusterKey1 in enumerate(clusters):
		cluster1 = clusters[clusterKey1]
		medioid1 = cluster1.medioid[0]
		medioid1_shingles = medioid1.get_shingles()

		# Iterate and calculates medioids similarity to all other buckets (using the indexes, we don't calculate twice)
		for index2, clusterKey2 in enumerate(clusters):
			if (index1 >= index2):
				continue

			cluster2 = clusters[clusterKey2]
			medioid2 = cluster2.medioid[0]
			medioid2_shingles = medioid2.get_shingles()
			medioidsJaccSim = (len(medioid1_shingles.intersection(medioid2_shingles)) / float(len(medioid1_shingles.union(medioid2_shingles))))
#TODO zero devision
			cluster1.distance_vector.append((clusterKey2, medioidsJaccSim, cluster2))
			cluster2.distance_vector.append((clusterKey1, medioidsJaccSim, cluster1))

	#print("\n====================================================\n")


	"""
	def medioids_compare(medioids):
		print("\n================= Medioids Similarity =================")

		# Iterate over all buckets medioids in the medioids dictionary
		for index1, bucketKey1 in enumerate(medioids):
			medioid1 = medioids[bucketKey1][0]
			medioid1_shingles = medioid1.get_shingles()

			# Iterate and calculates medioids similarity to all other buckets (using the indexes, we don't calculate twice)
			for index2, bucketKey2 in enumerate(medioids):
				if (index1 >= index2):
					continue

				medioid2 = medioids[bucketKey2][0]
				medioid2_shingles = medioid2.get_shingles()
				medioidsJaccSim = (len(medioid1_shingles.intersection(medioid2_shingles)) / float(len(medioid1_shingles.union(medioid2_shingles))))

				print("\n------------------------------")
				print("Buckets: %d %d " % (bucketKey1, bucketKey2))
				print(medioid1, medioid2)
				print(medioidsJaccSim)

		print("\n====================================================\n")
	"""


# ================================================================================================================================
#				Print clusters data
# ================================================================================================================================
def print_clusters_stat(clusters):
	print("\n================= Clusters Sizes Statistics =================")

	#clusters_sizes = [len(c.cluster_traces) for c in clusters]
	clusters_sizes = []
	for clusterKey, clusterValue in clusters.items():
		cluster_traces = clusters[clusterKey].cluster_traces
		clusters_sizes.append(len(cluster_traces))


	cluster_size_numpy_array = numpy.array(clusters_sizes)
	median = numpy.median(cluster_size_numpy_array)
	avg = numpy.mean(cluster_size_numpy_array)
	SD = numpy.std(cluster_size_numpy_array)
	max = numpy.max(cluster_size_numpy_array)
	min = numpy.min(cluster_size_numpy_array)
	num_of_singleton_clusters = len([s for s in clusters_sizes if s == 1])

	print("Count:%d, Median:%d, Max:%d , Min: %d,Singleton Clusters:%d" % (len(clusters_sizes),median,max,min,num_of_singleton_clusters))
	print("Average size:%f, SD: %f" % (avg,SD))
	print("====================================================\n")


def print_clusters_data(clusters):
	print("\n================= Clusters Data =================")
	print(settings.benign_threshold)
	for cluster in clusters.keys():
		cluster.print_cluster_data()
	print("\n====================================================\n")
