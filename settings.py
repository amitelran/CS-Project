import os

# =============================================================================
#								 Settings
# =============================================================================

# Globalize all of the settings
def init():
	global numHashes
	global shingle_size
	global samples_directory
	global unclassified_traces_directory
	global classified_traces_directory
	global check_for_minHash_file
	global numBands
	global nextPrime
	global hashMax
	global clustered_data_directory
	global minhash_file
	global signatures_file
	global buckets_file
	global traces_file
	global coeffA
	global coeffB
	global overwriteData
	global classifyTraces
	global maxShingleID

	# This is the number of components in the resulting MinHash signatures.
	# Correspondingly, it is also the number of random hash functions that
	# we will need in order to calculate the MinHash.

	numHashes = 100
	maxShingleID = 2 ** 32 - 1					# Record the maximum shingle ID that we assigned.
	numBands = 5								# Number of bands set
	shingle_size = 3							# Size of a shingle
	samples_directory = 'codedatasetsample'		# Reference to traces directory
	unclassified_traces_directory = 'unclassifiedtraces'		# The directory where unclassified traces inserted until classification is made
	classified_traces_directory = 'classifiedtraces'		# The directory where unclassified traces inserted until classification is made
	nextPrime = 4294967311						# Value of next prime number
	hashMax = 50021								# Maximum number of MinHash functions
	clustered_data_directory = "data"			# Directory storing the already clustered traces data
	minhash_file = "minhash_data.pkl"			# Pickle file storing all generated MinHash functions data
	signatures_file = "signatures.pkl"			# Pickle file storing signatures matrix data
	buckets_file = "buckets.pkl"				# Pickle file storing all buckets data
	traces_file = "traces.pkl"					# Pickle file storing all buckets data
	coeffA = None								# 1st Co-efficient for MinHash functions
	coeffB = None								# 2nd Co-efficient for MinHash functions
	overwriteData = False						# Boolean to indicate whether need to overwrite existing MinHash, Signatures & Buckets existing data
	classifyTraces = True						# Boolean to indicate whether need to classify traces or not