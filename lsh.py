from real_similarities import calcJaccard
import settings
import json
import dump_load_args
import trace_class

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

	# Hashing for each of the bands (number of bands as set by 'b' input)
	for i in range(b):
		for j in range(0, len(sigs)):		# Go through all line elements in a band row (number of columns of signatures matrix)
			#print("i = "+str(i)+", j = "+str(j))
			#print(sigs[j][b*(i):b*(i)+r])
			curTrace = docsObjects[j].get_filename()
			start = b*i				# start point of the band
			if i == b-1:			# If reached to the last band, band's end is till the end of sigs (None respresents absence of a value)
				end = None
			else:
				end = b*i + r		# If not the last band, set 'end' as the start of the band plus number of rows in a single band
			curHash = int(hash(tuple(sigs[j][start:end]))) % hashMax		# Hash current band
			#print(curHash)

			# Add current bucket(curHash) to the trace that the current signature represent
			if curTrace in traces:
				traces[curTrace].append(curHash)
			else:
				traces[curTrace] = [curHash]

			# Check for membership of current hashing in the buckets dictionary structure:
			# If already existing bucket for hash value --> append to the corresponding bucket
			# else, map the new bucket according to the hashing value
			if curHash in buckets:
				buckets[curHash].append(j)
			else:
				buckets[curHash] = [j]
	dump_load_args.DumpBuckets(buckets)			# Dump data into buckets data file
	dump_load_args.DumpTraces(traces)			# Dump data into traces data file
	#print traces
	return buckets

# Build different buckets array for each band separately
def build_buckets2(sigs, b, r, docsObjects):
	print "\nBuilding buckets for each band in sigs separately with LSH...\n"
	hashMax = settings.hashMax		# Get the maximal number of hash functions as set in settings.py
	buckets = dict()

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
			curHash = int(hash(tuple(sigs[j][start:end]))) % hashMax		# Hash current band

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
			#print(curHash

			if curTrace in traces:
				traces[curTrace].append(curHash)
			else:
				traces[curTrace] = [curHash]

			print(curHash)
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

