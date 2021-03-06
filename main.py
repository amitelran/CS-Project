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
import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer



# def Sergey(docs,JcrdSim,LevSim,i,j):
#	 print('*******************************\nPair : %s and %s' % (docs[i][0], docs[j][0]))
#	 print('\n Trace of %s representation (length= %d):\n %s \n\n\n' % (docs[i][0], len(docs[i][1]), docs[i][1]))
#	 print('\n Trace of %s representation (length= %d):\n %s \n\n\n' % (docs[j][0], len(docs[j][1]), docs[j][1]))
#	 print('Jaccard= %.3f' % JcrdSim[getTriangleIndex(i,j,len(docs))])
#	 print('Lev= %.3f' % LevSim[getTriangleIndex(i, j, len(docs))])
#	 print('*******************************\n\n')


class ClassifyEventHandler(FileSystemEventHandler):
	def __init__(self):
		self.count = 0
		self.classifyFiles = False

	def handleFile(self, event):
		if not event.is_directory and not self.classifyFiles:
			self.classifyFiles = True

	def on_created(self, event):
		self.handleFile(event)

	def on_modified(self, event):
		self.handleFile(event)

def main():
	t0 = time.time()		# Store beginning time to measure running time

	# Check whether there is already Minhash, Signatures & Buckets data exists. If so, load the existing data.
	# else, generate MinHash functions, Signatures & Buckets data, and store this data by exporting to files.
	if not settings.overwriteData and dump_load_args.dataFilesExist():
		try:
			sigs,buckets,clusters, traces = dump_load_args.LoadMinHashSignaturesBuckets()
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


	else:		# (If no data exists, generate MinHash, Signatures & Buckets data and export (a.k.a dump) to files

		#tracesObjects = trace_parser.parse_traces_as_objects(settings.samples_directory)
		tracesObjectsMalicious = trace_parser.parse_traces_as_objects(settings.training_data_malicious_directory)
		tracesObjectsBenign = trace_parser.parse_traces_as_objects(settings.training_data_benign_directory)
		tracesObjects = tracesObjectsMalicious + tracesObjectsBenign

		#docs_as_strings = trace_parser.generate_traces_as_text(tracesObjects)
		#docsAsShingles = shingles.convertToShingles(docs_as_strings)

		shingles.setTracesShingles(tracesObjects)

		minhashing.setRandomCoeffs()
		#dump_load_args.DumpMinHash(settings.coeffA,settings.coeffB,settings.nextPrime)
		#sigs = minhashing.MinHashNumpy(docsAsShingles)
		sigs = minhashing.setTracesMinHashSignatures(tracesObjects)

		#dump_load_args.DumpSignatures(sigs)
		# lsh.findRB(sigs,docsAsShingles,1,1,2,0.9)
		buckets, clusters = lsh.build_buckets(sigs, settings.numBands, settings.numHashes / settings.numBands, tracesObjects)

	# print buckets
	#sim_comparison.bucketsReport(buckets)
	lsh.print_clusters_stat(clusters)

	if settings.classifyTraces:		# Need to classify traces (Indicating boolean is 'ON')

		# Get unclassified traces from the unclassified-traces directory, and parse them as text
		# classified_directory = None

		path = settings.unclassified_traces_directory
		event_handler = ClassifyEventHandler()
		for dirpath, dirnames, files in os.walk(settings.test_data_directory):
			if files:
				event_handler.classifyFiles = True
		observer = Observer()
		observer.schedule(event_handler, path, recursive=True)
		observer.start()
		try:
			while True:
				time.sleep(2)
				if event_handler.classifyFiles:
					event_handler.classifyFiles = False

					if (settings.testLabeledData):
						tracesObjectsMalicious = trace_parser.parse_traces_as_objects(settings.test_data_malicious_directory)
						tracesObjectsBenign = trace_parser.parse_traces_as_objects(settings.test_data_benign_directory)
						testDocsObjects = tracesObjectsMalicious + tracesObjectsBenign
					else:
						testDocsObjects = trace_parser.parse_traces_as_objects(settings.test_data_unlabeled_directory)
					# new_docsObjects = trace_parser.parse_traces_as_objects(unclassified_directory, classified_directory)
					if len(testDocsObjects) == 0:
						continue

					test_docs_as_strings = trace_parser.generate_traces_as_text(testDocsObjects)

					# Classification of unclassified traces:
					print "\nStarting classification...\n"
					if settings.mode is settings.Modes.shingles_mode:

						# shingles.setTracesShingles(testDocsObjects)
						# new_sigs = minhashing.setTracesMinHashSignatures(testDocsObjects)
						new_docsAsShingles = shingles.convertToShingles(test_docs_as_strings)
						new_sigs = minhashing.MinHashNumpy(new_docsAsShingles)  # New signatures matrix
						# print docsAsShingles
						# numOfDocs = len(new_docs)

						# lsh.findRB(sigs,docsAsShingles,1,1,2,0.9)
					else:
						if settings.mode is settings.Modes.APIs_mode:
							new_docsAsAPIcalls = shingles.convertToAPIcalls(test_docs_as_strings)
							new_sigs = minhashing.MinHashNumpy(new_docsAsAPIcalls)  # New signatures matrix
							#TODO use setTracesShingles() and setTracesMinHashSignatures()

					# print("\n******************* Malicious- Mediods ***************")
					# lsh.calc_trace_distance_from_all_mediods(clusters, tracesObjectsMalicious)
					# print("\n*******************************\n\n")
					# print("\n\n******************* Benign-Mediods ***************")
					# lsh.calc_trace_distance_from_all_mediods(clusters,tracesObjectsBenign)
					# print("\n*******************************\n\n")

					classify = lsh.classify_new_data(new_sigs, settings.numBands, settings.numHashes / settings.numBands, buckets, testDocsObjects)  # Finally, classify the un-classified traces
					# buckets = lsh.lsh(sigs, settings.numBands, settings.numHashes / settings.numBands)
					classifyTraceLabels(classify, new_sigs, testDocsObjects)

		except KeyboardInterrupt:
			observer.stop()
		observer.join()


	print('\nTotal flow time took %.2f sec.' % (time.time() - t0))
# def classify_new_trace(trace,BUCKETS):
# 	mal_counter = 0
# 	benign_counter = 0
# 	for bucket in BUCKETS:
# 		for traces in bucket:
# 			if trace.isMal:
# 				mal_counter += 1
# 			if trace.isBenign:
# 				benign_counter += 1
def PredictMalicious(mal_count,benign_count):
	M = 1652
	B = 30

	return True if (mal_count / float(M)) > (benign_count / float(B)) else False

def classifyTraceLabels(classify, new_sigs, testDocsObjects):
	err_m = 0
	err_b = 0
	m_traces = 0
	b_traces = 0

	print "Label Classification Results:"
	print "========================="
	for i in range(len(new_sigs)):
		print
		print "Trace File Name: \"%s\"" % testDocsObjects[i].get_filename()
		print "Program Name: \"%s\"" % testDocsObjects[i].get_name()
		testDocsObjects[i].display_classification_time()
		for j in range(len(classify[i])):
			# print "\tBand #%d: bucket %d: %d neighbors" % (j + 1, classify[i][j][0], len(classify[i][j][1]))
			bucket_neighbors = classify[i][j][1]
			bucket_neighbors_count = len(bucket_neighbors)
			malicious_bucket_neighbors_count = sum(1 for n in bucket_neighbors if n.get_is_malicious() == True)
			benign_bucket_neighbors_count = sum(1 for n in bucket_neighbors if n.get_is_malicious() == False)
			print "\tband# %d: bucket index %d: %d neighbors" % (j, classify[i][j][0], bucket_neighbors_count)
			print "\t\t Malicious: %d (%.3f), Benign %d (%.3f)" % (malicious_bucket_neighbors_count,
			                                                       float(
				                                                       malicious_bucket_neighbors_count / bucket_neighbors_count) if bucket_neighbors_count != 0 else 0,
			                                                       benign_bucket_neighbors_count,
			                                                       float(
				                                                       benign_bucket_neighbors_count / bucket_neighbors_count) if bucket_neighbors_count != 0 else 0)
		unique_nbors = set.union(*[set(bucket[1]) for bucket in classify[i]])
		unique_nbors_cnt = len(unique_nbors)
		benign_unique_nbors_cnt = sum(1 for n in unique_nbors if n.get_is_malicious() == False)
		malicious_unique_nbors_cnt = sum(1 for n in unique_nbors if n.get_is_malicious() == True)

		print "\t>> Total unique neighbors: %d" % unique_nbors_cnt
		# print "\t>> Total unique neighbors: %d" % benign_unique_nbors_cnt
		# print "\t>> Total unique neighbors: %d" % malicious_unique_nbors_cnt
		print "\t\t Malicious: %d (%.3f), Benign %d (%.3f)" % (malicious_unique_nbors_cnt,
		                                                       float(
			                                                       malicious_unique_nbors_cnt / unique_nbors_cnt) if unique_nbors_cnt != 0 else 0,
		                                                       benign_unique_nbors_cnt,
		                                                       float(
			                                                       benign_unique_nbors_cnt / unique_nbors_cnt) if unique_nbors_cnt != 0 else 0)
		pred_mal = PredictMalicious(malicious_unique_nbors_cnt,benign_unique_nbors_cnt)
		tag_mal = True if testDocsObjects[i].get_is_malicious() else False
		print "\tPredicted classification: %s" % ("Malicious" if pred_mal else "Benign")
		print "\tTrue classification: %s" % ("Malicious" if tag_mal else "Benign")
		if pred_mal == tag_mal:
			print "\t\t\t>> success :-)"
		else:
			print "\t\t\t>> error :-("
			if tag_mal:
				err_m += 1
			else:
				err_b += 1
		if tag_mal:
			m_traces += 1
		else:
			b_traces += 1

	print "\n\tError rate:"
	print "\tAmong all traces: %f" % ((err_m+err_b) / float(len(new_sigs)))
	print "\tAmong Benign traces: %f" % (err_b / float(b_traces))
	print "\tAmong Malicious traces: %f" % (err_m / float(m_traces))


def printClassifResults1(classify, new_sigs, testDocsObjects):
	print "Classification results 1:"
	print "========================="
	for i in range(len(new_sigs)):
		print
		print "Trace File Name: \"%s\"" % testDocsObjects[i].get_filename()
		print "Program Name: \"%s\"" % testDocsObjects[i].get_name()
		testDocsObjects[i].display_classification_time()
		for j in range(len(classify[i])):
			print "\tBand #%d: bucket %d: %d neighbors" % (j + 1, classify[i][j][0], len(classify[i][j][1]))
		all_neighbors = set.union(*[set(bucket[1]) for bucket in classify[i]])
		print "\t\t>> Total unique neighbors: %d" % len(all_neighbors)

def printClassifResults2(classify, new_sigs, testDocsObjects):
	print "Classification Results :"
	print "========================="
	for i in range(len(new_sigs)):
		print
		print "Trace File Name: %s" % testDocsObjects[i].get_filename()
		print("Program Name: %s" % testDocsObjects[i].get_name())
		print("Malicious: %r" % (testDocsObjects[i].get_is_malicious()))


		if True:
			print "Buckets details:"
			for j in range(len(classify[i])):
				bucket_neighbors = classify[i][j][1]
				bucket_neighbors_count = len(bucket_neighbors)
				malicious_bucket_neighbors_count = sum(1 for n in bucket_neighbors if n.get_is_malicious() == True)
				benign_bucket_neighbors_count = sum(1 for n in bucket_neighbors if n.get_is_malicious() == False)
				print "\tband# %d: bucket index %d: %d neighbors" % (j, classify[i][j][0], bucket_neighbors_count)
				print "\t\t Malicious: %d (%.3f), Benign %d (%.3f)" % (malicious_bucket_neighbors_count,
																   float(
																	   malicious_bucket_neighbors_count / bucket_neighbors_count) if bucket_neighbors_count != 0 else 0,
																   benign_bucket_neighbors_count,
																   float(
																	   benign_bucket_neighbors_count / bucket_neighbors_count) if bucket_neighbors_count != 0 else 0)

		unique_nbors = set.union(*[set(bucket[1]) for bucket in classify[i]])
		unique_nbors_cnt = len(unique_nbors)
		benign_unique_nbors_cnt = sum(1 for n in unique_nbors if n.get_is_malicious() == False)
		malicious_unique_nbors_cnt = sum(1 for n in unique_nbors if n.get_is_malicious() == True)

		print "\t>> Total unique neighbors: %d" % unique_nbors_cnt
		#print "\t>> Total unique neighbors: %d" % benign_unique_nbors_cnt
		#print "\t>> Total unique neighbors: %d" % malicious_unique_nbors_cnt
		print "\t\t Malicious: %d (%.3f), Benign %d (%.3f)" % (malicious_unique_nbors_cnt,
														   float(
															   malicious_unique_nbors_cnt / unique_nbors_cnt) if unique_nbors_cnt != 0 else 0,
														   benign_unique_nbors_cnt,
														   float(
															   benign_unique_nbors_cnt / unique_nbors_cnt) if unique_nbors_cnt != 0 else 0)


if __name__ == '__main__':
	main()
