def init():
	global numHashes
	global shingle_size
	global samples_directory
	global check_for_minHash_file
	global numBands
	global nextPrime

	# This is the number of components in the resulting MinHash signatures.
	# Correspondingly, it is also the number of random hash functions that
	# we will need in order to calculate the MinHash.

	numHashes = 100
	numBands = 6
	shingle_size = 3
	samples_directory = 'codedatasetsample'
	nextPrime = 4294967311