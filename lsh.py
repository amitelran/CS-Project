from real_similarities import calcJaccard
import settings
import json
import dump_load_args

# Build buckets for traces classification
def build_buckets(sigs, b, r):
	print "\nBuilding buckets with LSH...\n"
	hashMax =  settings.hashMax
	buckets = dict()
	for i in range(b):
		for j in range(0,len(sigs)):
			#print("i = "+str(i)+", j = "+str(j))
			#print(sigs[j][b*(i):b*(i)+r])
			start=b*i
			if i == b-1:
				end = None
			else:
				end = b*i+r
			curHash = int(hash(tuple(sigs[j][start:end]))) % hashMax
			#print(curHash)
			if curHash in buckets:
				buckets[curHash].append(j)
			else:
				buckets[curHash] = [j]
	dump_load_args.DumpBuckets(buckets)
	return buckets

# Classifty new incoming traces
def classify_new_data(sigs, b, r, buckets):
	print "\nClassifying with LSH...\n"
	hashMax =  settings.hashMax
	neighbors = [list() for _ in range(len(sigs))]
	for i in range(b):
		for j in range(len(sigs)):
			#print("i = "+str(i)+", j = "+str(j))
			#print(sigs[j][b*(i):b*(i)+r])
			start=b*i
			if i == b-1:
				end = None
			else:
				end = b*i+r
			curHash = int(hash(tuple(sigs[j][start:end]))) % hashMax
			#print(curHash
			if curHash in buckets:
				# buckets[i][curHash].append(j)
				neighbors[j].append((curHash,buckets[curHash]))
			else:
				# buckets[i][curHash] = [j]
				neighbors[j].append((curHash,[]))
	# dump_load_args.DumpBuckets(buckets)
	return neighbors

#
def findRB(signatures,docsAsShingles,jumps,falsePositivesWeight,falseNegativesWeight,similarityThreshold):
	numOfAllTruePairs = 0
	bestNumOfBands = 0			# Insert to this variable what is the optimal number of bands
	minValue = float("inf")		# float("inf"): Unbounded upper value (no number would be greater than this representation of infinity)

	# Accumulate total number of all relatively similar pairs (If similarity is greater than the similarity threshold)
	for sim in calcJaccard(docsAsShingles):
		numOfAllTruePairs = numOfAllTruePairs + (sim > similarityThreshold)

	# Build buckets and check for optimal band size
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