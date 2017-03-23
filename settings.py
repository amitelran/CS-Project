def init():
	global numHashes
	global shingle_size
	global samples_directory
	global check_for_minHash_file
	global numBands
	global nextPrime
	global hashMax
	global overwriteData
	global minhash_path
	global signatures_path
	global buckets_path
	global coeffA
	global coeffB

	# This is the number of components in the resulting MinHash signatures.
	# Correspondingly, it is also the number of random hash functions that
	# we will need in order to calculate the MinHash.

	numHashes = 100
	numBands = 6
	shingle_size = 3
	samples_directory = 'codedatasetsample'
	nextPrime = 4294967311
	hashMax = 50021
	minhash_path = "minhash_data.json"
	signatures_path = "signatures.json"
	buckets_path = "buckets.json"
	coeffA = None
	coeffB = None
	overwriteData = False