import settings
settings.init()

import time
import lsh
import shingles
import est_jaccard
import trace_class
import minhashing
import sim_comparison
import dump_load_args
import trace_parser
import sys



# def Sergey(docs,JcrdSim,LevSim,i,j):
#	 print('*******************************\nPair : %s and %s' % (docs[i][0], docs[j][0]))
#	 print('\n Trace of %s representation (length= %d):\n %s \n\n\n' % (docs[i][0], len(docs[i][1]), docs[i][1]))
#	 print('\n Trace of %s representation (length= %d):\n %s \n\n\n' % (docs[j][0], len(docs[j][1]), docs[j][1]))
#	 print('Jaccard= %.3f' % JcrdSim[getTriangleIndex(i,j,len(docs))])
#	 print('Lev= %.3f' % LevSim[getTriangleIndex(i, j, len(docs))])
#	 print('*******************************\n\n')


def main():
	t0 = time.time()
	if not settings.overwriteData and dump_load_args.dataFilesExist():
		try:
			sigs,buckets = dump_load_args.LoadMinHashSignaturesBuckets()
			# print
			# print "Buckets:"
			# print buckets
			# print "Signatures:"
			# print sigs
			# print "MinHash parameters:"
			# print "\tCoeffA: " + str(settings.coeffA)
			# print "\tCoeffB: " + str(settings.coeffB)
			# print "\tnextPrime: " + str(settings.nextPrime)
			# print

		except:
			print "Error loading data from files"
			print "Error type: " + str(sys.exc_type)
			print "Terminating..."
			return
	else:
		docsObjects = trace_parser.parse_traces_as_objects(settings.samples_directory)
		docs_as_strings = trace_parser.generate_traces_as_text(docsObjects)
		# docs = docs[0:50]
		# docs = random.sample(docs,30)
		docsAsShingles = shingles.convertToShingles(docs_as_strings)
		# print docsAsShingles
		# numOfDocs = len(docsAsShingles)
		minhashing.setRandomCoeffs()
		dump_load_args.DumpMinHash(settings.coeffA,settings.coeffB,settings.nextPrime)
		sigs = minhashing.MinHashNumpy(docsAsShingles)
		dump_load_args.DumpSignatures(sigs)
		# lsh.findRB(sigs,docsAsShingles,1,1,2,0.9)
		buckets = lsh.build_buckets(sigs, settings.numBands, settings.numHashes / settings.numBands)
		# print buckets

	if settings.classifyTraces:
		new_docsObjects = trace_parser.parse_traces_as_objects(settings.unclassified_traces_directory)
		new_docs_as_strings = trace_parser.generate_traces_as_text(new_docsObjects)

		# docs = docs[0:50]
		# docs = random.sample(docs,30)

		print "\nStarting classification...\n"

		new_docsAsShingles = shingles.convertToShingles(new_docs_as_strings)
		# print docsAsShingles
		# numOfDocs = len(new_docs)
		new_sigs = minhashing.MinHashNumpy(new_docsAsShingles)
		# lsh.findRB(sigs,docsAsShingles,1,1,2,0.9)
		classify = lsh.classify_new_data(new_sigs, settings.numBands, settings.numHashes / settings.numBands, buckets)
		# buckets = lsh.lsh(sigs, settings.numBands, settings.numHashes / settings.numBands)

		print "Classification results:"
		print "========================="
		for i in range(len(new_sigs)):
			print
			print "Trace File Name: \"%s\"" % new_docsObjects[i].get_filename()
			print "Program Name: \"%s\"" % new_docsObjects[i].get_name()
			for j in range(len(classify[i])):
				print "\tBucket #%d: %d neighbors" % (j + 1, len(classify[i][j]))
			all_neighbors = set.union(*[set(bucket) for bucket in classify[i]])
			print "\t\t>> Total unique neighbors: %d" % len(all_neighbors)

	print('\nTotal flow time took %.2f sec.' % (time.time() - t0))

if __name__ == '__main__':
	main()
