import settings
import os
import json
import sys
from minhashing import MinHashNumpy
import pickle

minhashes_file = settings.minhash_path
signatures_file = settings.signatures_path
buckets_file = settings.buckets_path

def dataFilesExist():
	return os.path.isfile(minhashes_file) and os.path.isfile(signatures_file) and os.path.isfile(buckets_file)

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


def DumpMinHash(CoeffA,CoeffB,nextPrime):
	print("\nSaving MinHash parameters to file...")
	with open(minhashes_file, 'wb') as f:
		pickle.dump((CoeffA, CoeffB, nextPrime), f, pickle.HIGHEST_PROTOCOL)
	print "DONE"

def DumpSignatures(signatures):
	print("\nSaving Signatures to file...")
	with open(signatures_file, 'wb') as f:
		pickle.dump(signatures, f, pickle.HIGHEST_PROTOCOL)
	print "DONE"

def DumpBuckets(buckets):
	print("\nSaving Buckets to file...")
	with open(buckets_file, 'wb') as f:
		pickle.dump(buckets, f, pickle.HIGHEST_PROTOCOL)
	print "DONE"