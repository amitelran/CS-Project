import settings
import os
import json
import sys
from minhashing import MinHashNumpy
import pickle

# ===========================================================================================================
#            Output MinHash, Signatures and Buckets data to files or Load data from existing files
# ===========================================================================================================

directory = settings.clustered_data_directory						# Get directory of clustered data from settings.py
minhashes_file = os.path.join(directory, settings.minhash_file)		# Get MinHash data file
signatures_file = os.path.join(directory, settings.signatures_file)	# Get Signatures data file
buckets_file = os.path.join(directory, settings.buckets_file)		# Get buckets data file

# Check if there are already existing MinHash, Signatures & Buckets data files
def dataFilesExist():
	return os.path.isfile(minhashes_file) and os.path.isfile(signatures_file) and os.path.isfile(buckets_file)

# Check whether there is an existing path for data files directory. If not, create a directory.
def makeSurePathExists():
	if not os.path.exists(directory):
		os.makedirs(directory)

# If MinHash, Signatures & Buckets data files exist --> load them to get former data
def LoadMinHashSignaturesBuckets():
	print "\nLoading Signatures, MinHash parameters and Buckets..."
	if dataFilesExist():
		with open(signatures_file, 'rb') as f:
			signatures = pickle.load(f)
		with open(minhashes_file, 'rb') as f:
			settings.coeffA, settings.coeffB, settings.nextPrime = pickle.load(f)
		with open(buckets_file, 'rb') as f:
			buckets = pickle.load(f)
		print "DONE"
		return signatures,buckets
	raise Exception("Some data files not found...")

# Dump MinHash calculated data to MinHash data file in set directory
def DumpMinHash(CoeffA,CoeffB,nextPrime):
	makeSurePathExists()
	print("\nSaving MinHash parameters to file...")
	with open(minhashes_file, 'wb') as f:
		pickle.dump((CoeffA, CoeffB, nextPrime), f, pickle.HIGHEST_PROTOCOL)
	print "DONE"

# Dump Signatures calculated data to MinHash data file in set directory
def DumpSignatures(signatures):
	makeSurePathExists()
	print("\nSaving Signatures to file...")
	with open(signatures_file, 'wb') as f:
		pickle.dump(signatures, f, pickle.HIGHEST_PROTOCOL)
	print "DONE"

# Dump Buckets calculated data to MinHash data file in set directory
def DumpBuckets(buckets):
	makeSurePathExists()
	print("\nSaving Buckets to file...")
	with open(buckets_file, 'wb') as f:
		pickle.dump(buckets, f, pickle.HIGHEST_PROTOCOL)
	print "DONE"