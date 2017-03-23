import settings
import os
import json
import sys
from minhashing import MinHashNumpy

minhashes_file = settings.minhash_path
signatures_file = settings.signatures_path
buckets_file = settings.buckets_path

def dataFilesExist():
	return os.path.isfile(minhashes_file) and os.path.isfile(signatures_file) and os.path.isfile(buckets_file)

def LoadMinHashSignaturesBuckets():
	print "\nLoading Signatures, MinHash parameters and Buckets..."
	if dataFilesExist():
		with open(signatures_file,'r') as jfile:
			signatures = json.load(jfile)
		with open(minhashes_file,'r') as jfile:
			settings.coeffA, settings.coeffB, settings.nextPrime = json.load(jfile)
		with open(buckets_file,'r') as jfile:
			buckets = json.load(jfile)
		print "DONE"
		return signatures,buckets
	raise Exception("Some data files not found...")


def DumpMinHash(CoeffA,CoeffB,nextPrime):
	print("\nSaving MinHash parameters to file...\n")
	with open(minhashes_file, 'w') as jfile:
		json.dump((CoeffA, CoeffB, nextPrime), jfile)

def DumpSignatures(signatures):
	print("\nSaving Signatures to file...\n")
	with open(signatures_file, 'w') as jfile:
		json.dump(signatures, jfile)

def DumpBuckets(buckets):
	print("\nSaving Buckets to file...\n")
	with open(buckets_file, 'w') as jfile:
		json.dump(buckets, jfile)