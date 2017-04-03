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
			sigs,buckets,traces = dump_load_args.LoadMinHashSignaturesBuckets()
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
		buckets = lsh.build_buckets(sigs, settings.numBands, settings.numHashes / settings.numBands, docsObjects)
		# print buckets

	if settings.classifyTraces:		# Need to classify traces (Indicating boolean is 'ON')

		# First, get unclassified traces from the unclassified-traces directory, and parse them as text
		unclassified_directory = settings.unclassified_traces_directory
		classified_directory = settings.classified_traces_directory
		# classified_directory = None

		path = settings.unclassified_traces_directory
		event_handler = ClassifyEventHandler()
		for dirpath, dirnames, files in os.walk(unclassified_directory):
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

					new_docsObjects = trace_parser.parse_traces_as_objects(unclassified_directory, classified_directory)
					new_docs_as_strings = trace_parser.generate_traces_as_text(new_docsObjects)

					# docs = docs[0:50]
					# docs = random.sample(docs,30)

					# Classification of unclassified traces:
					print "\nStarting classification...\n"
					new_docsAsShingles = shingles.convertToShingles(new_docs_as_strings)
					# print docsAsShingles
					# numOfDocs = len(new_docs)
					new_sigs = minhashing.MinHashNumpy(new_docsAsShingles)  # New signatures matrix
					# lsh.findRB(sigs,docsAsShingles,1,1,2,0.9)
					classify = lsh.classify_new_data(new_sigs, settings.numBands, settings.numHashes / settings.numBands,
					                                 buckets, new_docsObjects)  # Finally, classify the un-classified traces
					# buckets = lsh.lsh(sigs, settings.numBands, settings.numHashes / settings.numBands)

					print "Classification results:"
					print "========================="
					for i in range(len(new_sigs)):
						print
						print "Trace File Name: \"%s\"" % new_docsObjects[i].get_filename()
						print "Program Name: \"%s\"" % new_docsObjects[i].get_name()
						new_docsObjects[i].display_classification_time()
						for j in range(len(classify[i])):
							print "\tBand #%d: bucket %d: %d neighbors" % (j + 1, classify[i][j][0], len(classify[i][j][1]))
						all_neighbors = set.union(*[set(bucket[1]) for bucket in classify[i]])
						print "\t\t>> Total unique neighbors: %d" % len(all_neighbors)

		except KeyboardInterrupt:
			observer.stop()
		observer.join()


	print('\nTotal flow time took %.2f sec.' % (time.time() - t0))

if __name__ == '__main__':
	main()
