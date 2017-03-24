from real_similarities import calcJacaard
import settings
import json
import dump_load_args

def build_buckets(sigs, b, r):
	print "\nBuilding buckets with LSH...\n"
	hashMax =  settings.hashMax

	buckets = list()
	for i in range(b):
		buckets.append(dict())
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
			if curHash in buckets[-1]:
				buckets[-1][curHash].append(j)
			else:
				buckets[-1][curHash] = [j]
	dump_load_args.DumpBuckets(buckets)
	return buckets

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
			if curHash in buckets[i]:
				# buckets[i][curHash].append(j)
				neighbors[j].append(buckets[i][curHash])
			else:
				# buckets[i][curHash] = [j]
				neighbors[j].append([])
	# dump_load_args.DumpBuckets(buckets)
	return neighbors

def findRB(signatures,docsAsShingles,jumps,falsePositivesWeight,falseNegativesWeight,similarityThreshold):
	numOfAllTruePairs = 0
	bestNumOfBands = 0
	minValue = float("inf")

	for sim in calcJacaard(docsAsShingles):
		numOfAllTruePairs = numOfAllTruePairs + (sim > similarityThreshold)

	for numOfBands in range(jumps,settings.numHashes/2,jumps):

		buckets = build_buckets(signatures, numOfBands, settings.numHashes / numOfBands)
		candidates = set()
		for bucketArray in buckets:
			for bucket in bucketArray:
				if (len(bucket) >= 2):
					b = list(bucket);
					for i in range(len(b)):
						for j in range(i + 1, len(b)):
							candidates.add(frozenset([b[i], b[j]]))
		i = 1
		numOfTruePositives = 0
		for pair in candidates:
			pairList = list(pair)
			# print("pair #"+str(i)+": "+str(pairList))
			i = i + 1
			if (calcJacaard([docsAsShingles[pairList[0]], docsAsShingles[pairList[1]]])[0] > similarityThreshold):
				numOfTruePositives = numOfTruePositives + 1
		# print(buckets)
		falsePositives = len(candidates) - numOfTruePositives
		falseNegatives = numOfAllTruePairs - numOfTruePositives
		print("============ B = "+str(numOfBands)+", R = "+str(settings.numHashes/numOfBands)+" ==========")
		print("similar pairs (above "+str(similarityThreshold)+"): " + str(numOfTruePositives) + " out of " + str(len(candidates)))
		print("false positives: " + str(falsePositives) + ", false negatives: " + str(falseNegatives))
		print("========================================\n")
		curValue=falsePositivesWeight*falsePositives + falseNegativesWeight*falseNegatives;
		if curValue < minValue:
			minValue = curValue
			bestNumOfBands = numOfBands
		if(falsePositives > (len(candidates))/2):
			break
	print("Best parameters with FP weight = "+str(falsePositivesWeight)+", FN weight = "+str(falseNegativesWeight)+":")
	print("B = "+str(bestNumOfBands)+", R = "+str(settings.numHashes/bestNumOfBands))
	return [bestNumOfBands,settings.numHashes/bestNumOfBands]