def init():
	global numHashes
	global shingle_size
	global samples_directory
	global unclassified_traces_directory
	global check_for_minHash_file
	global numBands
	global nextPrime
	global hashMax
	global minhash_path
	global signatures_path
	global buckets_path
	global coeffA
	global coeffB
	global overwriteData
	global classifyTraces
	global maxShingleID

	# This is the number of components in the resulting MinHash signatures.
	# Correspondingly, it is also the number of random hash functions that
	# we will need in order to calculate the MinHash.

	numHashes = 100
	# Record the maximum shingle ID that we assigned.
	maxShingleID = 2 ** 32 - 1
	numBands = 5
	shingle_size = 3
	samples_directory = 'codedatasetsample'
	unclassified_traces_directory = 'unclassifiedtraces'
	nextPrime = 4294967311
	hashMax = 50021
	minhash_path = "data//minhash_data.pkl"
	signatures_path = "data//signatures.pkl"
	buckets_path = "data//buckets.pkl"
	coeffA = None
	coeffB = None
	overwriteData = False
	classifyTraces = True