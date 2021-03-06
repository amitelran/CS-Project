#import os
#import enum

# =============================================================================
#								 Settings
# =============================================================================

# Enum for shingling modes
class Modes:
	shingles_mode, APIs_mode = range(2)


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
	global mode
	global apiCalls_per_shingle
	global benign_threshold

	global training_data_directory
	global training_data_benign_directory
	global training_data_malicious_directory
	global test_data_directory
	global test_data_unlabeled_directory
	global test_data_benign_directory
	global test_data_malicious_directory
	global test_data_unlabeled_directory
	global testLabeledData


	numHashes = 100								# number of random hash functions,number of components in the resulting MinHash signatures
	maxShingleID = 2 ** 32 - 1					# Record the maximum shingle ID that we assigned.
	numBands = 10								# Number of bands set
	shingle_size = 13							# Size of a shingle (in shingles_mode)
	apiCalls_per_shingle = 3					# Number of API calls to be set as a single shingle (in APIs_mode)
	nextPrime = 4294967311  					# Value of next prime number
	hashMax = 50021  							# Buckets hash table size
	benign_threshold = 70/(100 * 1.0)			# Benign threshold for cluster (=bucket)


	samples_directory = 'codedatasetsample'		# Reference to traces directory
	unclassified_traces_directory = 'unclassifiedtraces'		# The directory where unclassified traces inserted until classification is made
	classified_traces_directory = 'classifiedtraces'		# The directory where classified traces are inserted after classification is made

	training_data_directory = 'classif1_traindata'	# Directory for training data containing two sub-directories: benign and malicious.
	#training_data_directory = 'trainingdataStam'
	# training_data_directory = 'trnSergey50'	# Directory for training data containing two sub-directories: benign and malicious.

	training_data_benign_directory = training_data_directory + '/benign'	# Sub-directory of the trainingdata directory containing benign traces.
	training_data_malicious_directory = training_data_directory + '/malicious'	# Sub-directory of the trainingdata directory containing malicious traces

	test_data_directory = 'classif1_testdata'
	test_data_unlabeled_directory = test_data_directory+'/unlabeled'
	test_data_benign_directory = test_data_directory+'/benign'
	test_data_malicious_directory = test_data_directory+'/malicious'


	clustered_data_directory = "data"			# Directory storing the already clustered traces data
	minhash_file = "minhash_data.pkl"			# Pickle file storing all generated MinHash functions data
	signatures_file = "signatures.pkl"			# Pickle file storing signatures matrix data
	buckets_file = "buckets.pkl"				# Pickle file storing all buckets data
	buckets_file = "clusters.pkl"				# Pickle file storing all buckets data
	traces_file = "traces.pkl"					# Pickle file storing all buckets data
	coeffA = None								# 1st Co-efficient for MinHash functions
	coeffB = None								# 2nd Co-efficient for MinHash functions

	overwriteData = True						# Boolean to indicate whether need to overwrite existing MinHash, Signatures & Buckets existing data
	classifyTraces = True						# Boolean to indicate whether need to classify traces or not
	testLabeledData = True						# Boolean to indicate what mode to test: one mode of testing 'benign' and 'malicious', the other mode of testing with 'unlabeled'

	# Set shingling mode
	mode = Modes.shingles_mode

