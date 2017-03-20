#from __future__ import division
import sys
import random
import time
import binascii
import glob, re
#import Levenshtein
import numpy
import matplotlib.pyplot as pyplot
import datetime
import ntpath
#from parser import generate_traces_as_text


# This is the number of components in the resulting MinHash signatures.
# Correspondingly, it is also the number of random hash functions that
# we will need in order to calculate the MinHash.
numHashes = 100
shingle_size = 3
SAMPLESDIR = 'codedatasetsample'


# =============================================================================
#               Convert Documents To Sets of Shingles
# =============================================================================

def convertToShingles(docs):
    print("Shingling docs...")

    # The current shingle ID value to assign to the next new shingle we
    # encounter. When a shingle gets added to the dictionary, we'll increment this
    # value.
    curShingleID = 0

    # Create a dictionary of the articles, mapping the article identifier (e.g.,
    # "t8470") to the list of shingle IDs that appear in the document.
    docsAsShingleSets = [];
    numDocs = len(docs)
    docNames = []

    t0 = time.time()

    totalShingles = 0

    for i in range(0, numDocs):
        doc = docs[i]
        docID = doc[0]
        doc = doc[1]

        # Maintain a list of all document IDs.
        # docNames.append(docID)

        # 'shinglesInDoc' will hold all of the unique shingle IDs present in the
        # current document. If a shingle ID occurs multiple times in the document,
        # it will only appear once in the set (this is a property of Python sets).
        shinglesInDoc = set()
        #TEMP
        #shinglesInDocStrList = []
        #shinglesInDocStrSet = set()
        #TEMP

        # Hash the shingle to a 32-bit integer.
        # Add the hash value to the list of shingles for the current document.
        # Note that set objects will only add the value to the set if the set
        # doesn't already contain it.
        for j in range(len(doc) - shingle_size + 1):
            shingle = doc[j:j + shingle_size]
            #shingle =bytes(shingle, 'UTF-8')
            crc = binascii.crc32(shingle) & 0xffffffff
            shinglesInDoc.add(crc)
            # shinglesInDocStrList.append(shingle)
            # shinglesInDocStrSet.add(shingle)

        ##TEMP
        ##print(len(shinglesInDocStrList))
        ##print("shinglesInDocStrList:",shinglesInDocStrList)

        # output_file = open('/Users/MGanayim/Desktop/ShingleTest/' +docID + '_shingles.txt', 'a')
        # output_file.write('docID: ' + docID + ', doc Index: ' + str(len(docsAsShingleSets)) + ', Number of shingles = ' + str(len(shinglesInDocStrList)) + ', Number of unique shingles = ' + str(len(shinglesInDocStrSet)) + '. Shingles:' + '\n')
        # output_file.write('\n'.join(shinglesInDocStrList))
        # output_file.close()
        #TEMP

        # Store the completed list of shingles for this document in the dictionary.
        docsAsShingleSets.append(shinglesInDoc)

        # Count the number of shingles across all documents.
        totalShingles = totalShingles + len(shinglesInDoc)

    # Report how long shingling took.
    print('\nShingling ' + str(numDocs) + ' docs took %.2f sec.' % (time.time() - t0))
    print('\nAverage shingles per doc: %.2f' % (totalShingles / numDocs))

    return docsAsShingleSets


# =============================================================================
#                     Define Triangle Matrices
# =============================================================================

def createTriangleMatrixNumpy(numDocs):
    # Define virtual Triangle matrices to hold the similarity values.

    # Calculate the number of elements needed in our triangle matrix
    numElems = int(numDocs * (numDocs - 1) / 2)

    # Initialize empty list to store the similarity values.
    # Caution!! numpy.empty initializes list faster, but with garbage data inside.
    # Must ensure all garbage data is overwritten while program flow.
    matrix = numpy.empty(numElems)
    return matrix


def createTriangleMatrix(numDocs):
    # Define virtual Triangle matrices to hold the similarity values.

    # Calculate the number of elements needed in our triangle matrix
    numElems = int(numDocs * (numDocs - 1) / 2)

    # Initialize empty list to store the similarity values.
    return [0 for x in range(numElems)]


# Define a function to map a 2D matrix coordinate into a 1D index.
def getTriangleIndex(i, j, numDocs):
    # If i == j that's an error.
    if i == j:
        sys.stderr.write("Can't access triangle matrix with i == j")
        sys.exit(1)
    # If j < i just swap the values.
    if j < i:
        temp = i
        i = j
        j = temp

    # Calculate the index within the triangular array.
    # This fancy indexing scheme is taken from pg. 211 of:
    # http://infolab.stanford.edu/~ullman/mmds/ch6.pdf
    # adapted for a 0-based index.
    # Note: The division by two should not truncate, it
    #       needs to be a float.
    k = int(i * (numDocs - (i + 1) / 2.0) + j - i) - 1
    return k


# =============================================================================
#                 Calculate Jaccard Similarities
# =============================================================================
# In this section, we will directly calculate the Jaccard similarities by
# comparing the sets. This is included here to show how much slower it is than
# the MinHash approach.

def calcJacaard(docsAsShingleSets):
    #print("\nCalculating Jaccard Similarities...")

    numDocs = len(docsAsShingleSets)
    JSim = createTriangleMatrixNumpy(numDocs)

    t0 = time.time()  # Time the calculation.

    # For every document pair...
    for i in range(0, numDocs):

        # Print progress every 100 documents.
        #if (i % 100) == 0:
        #    print("  (" + str(i) + " / " + str(numDocs) + ")")

        s1 = docsAsShingleSets[i]
        for j in range(i + 1, numDocs):
            # Retrieve the set of shingles for document j.
            s2 = docsAsShingleSets[j]
            # Calculate and store the actual Jaccard similarity.
            JSim[getTriangleIndex(i, j, numDocs)] =(len(s1.intersection(s2)) / float(len(s1.union(s2))))
            ## TEMP
            # print('1 - Jaccard(' + str(i) + ',' + str(j) + ')=' + str(JSim[getTriangleIndex(i, j, numDocs)]))

    # Calculate the elapsed time (in seconds)
    elapsed = (time.time() - t0)
    #print("\nCalculating all Jaccard Similarities took %.2fsec" % elapsed)

    return JSim


# =============================================================================
#                 Calculate Levenstien Distance
# =============================================================================
def calcLev(docs):
    print("\nCalculating Levenshtein Similarities...")

    numDocs = len(docs)
    LevSim = createTriangleMatrixNumpy(numDocs)
    t0 = time.time()  # Time the calculation.

    for i in range(0, numDocs):
        # Print progress every 100 documents.
        if (i % 100) == 0:
            print("  (" + str(i) + " / " + str(numDocs) + ")")

        s1 = docs[i][1]
        for j in range(i + 1, numDocs):
            s2 = docs[j][1]
            # Calculate and store the normalized levenstien similarity.
            LevSim[getTriangleIndex(i, j, numDocs)] = Levenshtein.distance(s1,s2) / float(max(len(s1), len(s2)))
            ##TEMP
            # print('NormED(' + str(i) + ',' + str(j) + ')=' + str(LevSim[getTriangleIndex(i, j, numDocs)]) + ', Lengths:'+ str(len(s1)) + ',' + str(len(s2)))


    # Calculate the elapsed time (in seconds)
    elapsed = (time.time() - t0)
    print("\nCalculating all Levenshtein Similarities took %.2fsec" % elapsed)

    return LevSim


def lev(a, b):
    if not a: return len(b)
    if not b: return len(a)
    return min(lev(a[1:], b[1:]) + (a[0] != b[0]), lev(a[1:], b) + 1, lev(a, b[1:]) + 1)


# =============================================================================
#                     Calculate Est Jacaard
# =============================================================================

def calcEstJacaard(docsAsShingleSets):
    print('\nComparing all signatures...')

    signatures = MinHash(docsAsShingleSets)

    numDocs = len(docsAsShingleSets)
    estJSim = createTriangleMatrixNumpy(numDocs)

    # Time this step.
    t0 = time.time()

    # For each of the test documents...
    for i in range(0, numDocs):
        # Get the MinHash signature for document i.
        signature1 = signatures[i]

        # For each of the other test documents...
        for j in range(i + 1, numDocs):

            # Get the MinHash signature for document j.
            signature2 = signatures[j]

            count = 0
            # Count the number of positions in the minhash signature which are equal.
            for k in range(0, numHashes):
                count = count + (signature1[k] == signature2[k])

            # Record the percentage of positions which matched.
            estJSim[getTriangleIndex(i, j, numDocs)] = (count / float(numHashes))
            #TEMP
            # print('EstJaccard(' + str(i) + ',' + str(j) + ')=' + str(estJSim[getTriangleIndex(i, j, numDocs)]))


    # Calculate the elapsed time (in seconds)
    elapsed = (time.time() - t0)

    print("\nComparing MinHash signatures took %.2fsec" % elapsed)

    return estJSim


# =============================================================================
#                 Generate MinHash Signatures
# =============================================================================

def MinHashNumpy(docsAsShingleSets):
    print('\nGenerating random hash functions...')
    t0 = time.time()  # Time the calculation.

    # Record the maximum shingle ID that we assigned.
    maxShingleID = 2 ** 32 - 1

    # We need the next largest prime number above 'maxShingleID'.
    # I looked this value up here:
    # http://compoasso.free.fr/primelistweb/page/prime/liste_online_en.php
    nextPrime = 4294967311

    # Our random hash function will take the form of:
    #   h(x) = (a*x + b) % c
    # Where 'x' is the input value, 'a' and 'b' are random coefficients, and 'c' is
    # a prime number just greater than maxShingleID.

    # Generate a list of 'k' random coefficients for the random hash functions,
    # while ensuring that the same value does not appear multiple times in the
    # list.

    # For each of the 'numHashes' hash functions, generate a different coefficient 'a' and 'b'.
    coeffA = pickRandomCoeffs(numHashes, maxShingleID)
    coeffB = pickRandomCoeffs(numHashes, maxShingleID)

    ## TEMP
    # print('Random Hash Functions: h(x) = (a*x + b) % c :')
    # print('a coeff : ' + str(coeffA))
    # print('b coeff : ' + str(coeffB))
    # print('c : ' + str(nextPrime))

    print('\nGenerating MinHash signatures for all documents...')

    # List of documents represented as signature vectors
    signatures = []
    # Rather than generating a random permutation of all possible shingles,
    # we'll just hash the IDs of the shingles that are *actually in the document*,
    # then take the lowest resulting hash code value. This corresponds to the index
    # of the first shingle that you would have encountered in the random order.
    numDocs = len(docsAsShingleSets)

    for i in range(0, numDocs):

        # Print progress every 100 documents.
        if (i % 100) == 0:
            print("  (" + str(i) + " / " + str(numDocs) + ")")

        shingleIDSet = docsAsShingleSets[i]
        # The resulting minhash signature for this document.
        signature = []

        # For each of the random hash functions...
        for j in range(0, numHashes):

            # For each of the shingles actually in the document, calculate its hash code
            # using hash function 'i'.

            # Track the lowest hash ID seen. Initialize 'minHashCode' to be greater than
            # the maximum possible value output by the hash.
            minHashCode = nextPrime + 1

            # For each shingle in the document...
            for shingleID in shingleIDSet:
                # Evaluate the hash function.
                hashCode = (coeffA[j] * shingleID + coeffB[j]) % nextPrime

                # Track the lowest hash code seen.
                if hashCode < minHashCode:
                    minHashCode = hashCode

            # Add the smallest hash code value as component number 'i' of the signature.
            signature.append(minHashCode)

        # Store the MinHash signature for this document.
        signatures.append(signature)
        # TEMP
        # print('Doc index ['+ str(i) +'] signatures:' + str(signature))
    # Convert signatures matrix to numpy array
    signatures = numpy.array(signatures)
    # Calculate the elapsed time (in seconds)
    elapsed = (time.time() - t0)
    print("\nGenerating MinHash signatures took %.2fsec" % elapsed)
    print("\nOutput MinHash signatures to text file")
    with open('Minhash_Data.txt', 'a') as text_file:
        numpy.savetxt(text_file, signatures, fmt='%9s', newline="\n")
        text_file.write(datetime.datetime.now().strftime("\nDate: %Y-%m-%d, %H:%M:%S\n"))
        text_file.write("\n================================================================================================\n\n\n")
    return signatures


"""
def MinHash(docsAsShingleSets):
    print('\nGenerating random hash functions...')
    t0 = time.time()  # Time the calculation.

    # Record the maximum shingle ID that we assigned.
    maxShingleID = 2 ** 32 - 1

    # We need the next largest prime number above 'maxShingleID'.
    # I looked this value up here:
    # http://compoasso.free.fr/primelistweb/page/prime/liste_online_en.php
    nextPrime = 4294967311

    # Our random hash function will take the form of:
    #   h(x) = (a*x + b) % c
    # Where 'x' is the input value, 'a' and 'b' are random coefficients, and 'c' is
    # a prime number just greater than maxShingleID.

    # Generate a list of 'k' random coefficients for the random hash functions,
    # while ensuring that the same value does not appear multiple times in the
    # list.

    # For each of the 'numHashes' hash functions, generate a different coefficient 'a' and 'b'.
    coeffA = pickRandomCoeffs(numHashes, maxShingleID)
    coeffB = pickRandomCoeffs(numHashes, maxShingleID)

    ## TEMP
    # print('Random Hash Functions: h(x) = (a*x + b) % c :')
    # print('a coeff : ' + str(coeffA))
    # print('b coeff : ' + str(coeffB))
    # print('c : ' + str(nextPrime))

    print('\nGenerating MinHash signatures for all documents...')

    # List of documents represented as signature vectors
    signatures = []
    # Rather than generating a random permutation of all possible shingles,
    # we'll just hash the IDs of the shingles that are *actually in the document*,
    # then take the lowest resulting hash code value. This corresponds to the index
    # of the first shingle that you would have encountered in the random order.
    numDocs = len(docsAsShingleSets)

    for i in range(0, numDocs):

        # Print progress every 100 documents.
        if (i % 100) == 0:
            print("  (" + str(i) + " / " + str(numDocs) + ")")

        shingleIDSet = docsAsShingleSets[i]
        # The resulting minhash signature for this document.
        signature = []

        # For each of the random hash functions...
        for j in range(0, numHashes):

            # For each of the shingles actually in the document, calculate its hash code
            # using hash function 'i'.

            # Track the lowest hash ID seen. Initialize 'minHashCode' to be greater than
            # the maximum possible value output by the hash.
            minHashCode = nextPrime + 1

            # For each shingle in the document...
            for shingleID in shingleIDSet:
                # Evaluate the hash function.
                hashCode = (coeffA[j] * shingleID + coeffB[j]) % nextPrime

                # Track the lowest hash code seen.
                if hashCode < minHashCode:
                    minHashCode = hashCode

            # Add the smallest hash code value as component number 'i' of the signature.
            signature.append(minHashCode)

        # Store the MinHash signature for this document.
        signatures.append(signature)
        #TEMP
        #print('Doc index ['+ str(i) +'] signatures:' + str(signature))

    # Calculate the elapsed time (in seconds)
    elapsed = (time.time() - t0)
    print("\nGenerating MinHash signatures took %.2fsec" % elapsed)
    return signatures
"""

def pickRandomCoeffs(k, maxShingleID):
    # Create a list of 'k' random values.
    randList = []

    while k > 0:
        # Get a random shingle ID.
        randIndex = random.randint(0, maxShingleID)

        # Ensure that each random number is unique.
        while randIndex in randList:
            randIndex = random.randint(0, maxShingleID)

        # Add the random number to the list.
        randList.append(randIndex)
        k = k - 1

    return randList

def CompareSimilarities(Sim1,Sim2):
    delta = [(x - y) for x, y in zip(Sim1, Sim2)]
    avg_delta = sum(delta) / float(len(delta))
    max_delta = max(delta)
    min_delta = min(delta)
    median_delta = numpy.median(numpy.array(delta))

    print('Delta- Avg: %.3f, Max: %.3f, Min: %.3f, Median: %.3f' % (avg_delta,max_delta,min_delta,median_delta))

def CompareSimilarities_RelativeError(Sim1,Sim2):
    relative_err = [abs(x - y) / x for x, y in zip(Sim1, Sim2) if x != 0 ]
    avg_relative_err = numpy.mean(numpy.array(relative_err)) # (sum(relative_err) / float(len(relative_err)))
    max_relative_err = max(relative_err)
    min_relative_err = min(relative_err)
    median_relative_err = numpy.median(numpy.array(relative_err))
    SD_relative_err = numpy.std(numpy.array(relative_err)) #sqrt(mean(abs(x - x.mean())**2))
    Var_relative_err = numpy.var(numpy.array(relative_err)) #sqrt(mean(abs(x - x.mean())**2))

    print('Relative Error- Avg: %.3f, Max: %.3f, Min: %.3f, Median: %.3f, SD: %.3f, Var: %.3f' % (avg_relative_err,max_relative_err,min_relative_err,median_relative_err,SD_relative_err,Var_relative_err))
    pyplot.hist(relative_err, histtype='step', bins = 1500, normed=True,range=(0.94,1.01))
    pyplot.xlabel('Relative error: | J - EstJ | / j.   Range limited to [0.8,1.1]')
    pyplot.ylabel('Frequency')
    pyplot.show()

def CheckMono(Sim1,Sim2):
    if len(Sim1) != len(Sim2):
        print('num of pairs in Sim1 are not equal to num of pairs in Sim2')
        return
    numPairs = len(Sim1)
    t0 = time.time()  # Time the calculation.
    print('Monotonicity Check...')
    mismatch_count = 0
    mismatch_indicies = []
    for i in range(0,numPairs):
        if (i % 2000) == 0:
            print("  (" + str(i) + " / " + str(numPairs) + ")")
        for j in range(i + 1, numPairs):
            x = Sim1[i] -Sim1[j]
            y = Sim2[i] - Sim2[j]
            if x * y < 0:
                mismatch_count += 1
                mismatch_indicies.append([i,j])

    elapsed = (time.time() - t0)
    print("\nMonotonicity Check took %.2fsec" % elapsed)
    numPairsOfPairs = int(numPairs * (numPairs - 1) / 2)
    count = len(mismatch_indicies)
    print('Count of mismatches %d out of %d pairs of pairs. percent: %.3f %%' % (count, numPairsOfPairs, 100*count / float(numPairsOfPairs)))


# =============================================================================
#                               Trace Class
# =============================================================================

class Trace:
    def __init__(self, file_name, trace_name, data):
        self.file_name = file_name
        self.trace_name = trace_name
        self.data = data
        self.is_malicious = True  # Variable to indicate if trace is malicious or benign

    def display_file_name(self):
        print "Trace's file name: ", self.file_name

    def display_trace_name(self):
        print "Trace Name: ", self.trace_name

    def display_data(self):
        print "Trace Data: ", self.data

    def is_malicious_check(self):
        if self.is_malicious:
            print "Trace is malicious"
        else:
            print "Trace is not malicious"

    def change_status(self):
        self.is_malicious = not self.is_malicious



# # =============================================================================
# # =============================================================================
# # =============================================================================
# #                             Parser
# # =============================================================================
# # =============================================================================
# # =============================================================================


def parse_traces_as_objects(directory):
    files = get_files_paths(directory, 'hooklog')
    trace_objects = []
    for fName in files:
        # Get file name
        path_head, path_tail = ntpath.split(fName)
        file_name = path_tail

        # Get first line of file (trace name)
        input_file = open(fName, 'r')
        line = input_file.readline()    # Read first line of file
        trace_name = [line.strip()]     # the program name (strips remove all white spaces at the start and end)

        # Get trace data
        trace_data = []
        for line in input_file:
            line = line.strip()  # strips remove all white spaces at the start and end
            # Search for a pattern which looks for character '#' and some digit 0-9 (\d) afterwards.
            # The '+' means that other digits after the first one don't matter
            match_timestamp = re.search(r'#([\d]+)',line)  # regular expression searching for timestamp and return boolean value if found or not # TODO
            if match_timestamp:
                trace_data.append({})  # appending an empty Python dictionary to trace_name (dictionary - set of separated words)
                trace_data[-1]['timestamp'] = match_timestamp.group(1)
                continue
            match_keyvalue = re.search(r'.+=.+', line)  # API Name # TODO
            if not match_keyvalue:
                trace_data[-1]['API_Name'] = line
                continue
            line_elements = line.split('=')  # Splits lines separated with '='
            trace_data[-1][line_elements[0]] = line_elements[1]
        # End of file lines looping

        input_file.close()
        trace_objects.append(Trace(file_name, trace_name, trace_data))
        trace_objects[-1].display_file_name()
        trace_objects[-1].display_trace_name()
        trace_objects[-1].display_data()
        print
    return trace_objects


def get_files_paths(directory, extension):
    return glob.glob(directory + '/*.' + extension)  # TODO consider iglob


def parse_file(file_path):
    input_file = open(file_path, 'r')
    line = input_file.readline()
    trace = [line.strip()]  # the program name
    for line in input_file:
        line = line.strip()
        match_timestamp = re.search(r'#([\d]+)', line)   # timestamp # TODO
        if match_timestamp:
            trace.append({})
            trace[-1]['timestamp'] = match_timestamp.group(1)
            continue

        match_keyvalue = re.search(r'.+=.+', line)  # API Name # TODO
        if not match_keyvalue:
            trace[-1]['API_Name'] = line
            continue

        line_elements = line.split('=')
        trace[-1][line_elements[0]] = line_elements[1]
    input_file.close()
    return trace


def parse_directory_files(directory):
    files = get_files_paths(directory, 'hooklog')
    parsed_files = []
    for file_name in files:
        parsed_file = parse_file(file_name)
        parsed_files.append(parsed_file)
        #save_parsed_file(fname, parsed_file)
    return parsed_files


def save_parsed_file(fname, parsed_traces):
    output_file = open(fname[:-8] + '_parsed.txt', 'a')
    output_file.write('Filename: ' + parsed_traces[0] + ', Number of calls = ' + str(len(parsed_traces) - 1) + '\n')

    for trace in parsed_traces[1:]:
        output_file.write('\n')
        # for key, val in trace.items():
        #    output_file.write(key + ':' + val + ', ' )
        output_file.writelines(str(trace))
        # output_file.write('}')
    output_file.close()

    # w = csv.writer(open(fname[:-8] + '_parsed.csv', 'w'))
    # w.writerow(['Filename',parsed_traces[0]])
    # for trace in parsed_traces[1:]:
    #     for key, val in trace.items():
    #         w.writerow([key, val])


def extract_API_name(traces):
    return [[t[0],'*'.join([call.get('API_Name') for call in t[1:]])] for t in traces]


def extract_APIhKey_name(traces):
    return [[t[0], '*'.join([(str(call.get('API_Name')) + '@' + str(call.get('hKey'))) for call in t[1:]])] for t in traces]

def generate_traces_as_text():
    parsed_traces_as_objects = parse_traces_as_objects('C:\Users\Amir\Desktop\Project\Code Data sets sample')
    parsed_traces = parse_directory_files(SAMPLESDIR)
    #parsed_traces = parse_directory_files('C:\\Users\\ghanayim\\Google Drive\\Virtualized Cloud Security\\DataSets\\MixAll_hooklogs_labeledBNGN')
    return extract_APIhKey_name(parsed_traces)

# # =============================================================================
# # =============================================================================
# # =============================================================================
# #                             Parser
# # =============================================================================
# # =============================================================================
# # =============================================================================

def Sergey(docs,JcrdSim,LevSim,i,j):
    print('*******************************\nPair : %s and %s' % (docs[i][0], docs[j][0]))
    print('\n Trace of %s representation (length= %d):\n %s \n\n\n' % (docs[i][0], len(docs[i][1]), docs[i][1]))
    print('\n Trace of %s representation (length= %d):\n %s \n\n\n' % (docs[j][0], len(docs[j][1]), docs[j][1]))
    print('Jaccard= %.3f' % JcrdSim[getTriangleIndex(i,j,len(docs))])
    print('Lev= %.3f' % LevSim[getTriangleIndex(i, j, len(docs))])
    print('*******************************\n\n')

def lsh(sigs,b,r):
    hashMax =  50021

    buckets = list()
    for i in range(b):
        buckets.append({})
        buckets[-1] = [[] for tmp in range(hashMax)]
        for j in range(0,len(sigs)):
            #print("i = "+str(i)+", j = "+str(j))
            #print(sigs[j][b*(i):b*(i)+r])
            start=b*i
            if (i==b-1):
                end=None
            else:
                end=b*i+r
            curHash=int(hash(tuple(sigs[j][start:end]))) % hashMax
            #print(curHash)
            buckets[-1][curHash].append(j)
    return buckets

def findRB(signatures,docsAsShingles,jumps,falsePositivesWeight,falseNegativesWeight,similarityThreshold):
    numOfAllTruePairs = 0
    bestNumOfBands = 0
    minValue = float("inf")

    for sim in calcJacaard(docsAsShingles):
        numOfAllTruePairs = numOfAllTruePairs + (sim > similarityThreshold)

    for numOfBands in range(jumps,numHashes/2,jumps):

        buckets = lsh(signatures, numOfBands, numHashes/numOfBands)
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
        print("============ B = "+str(numOfBands)+", R = "+str(numHashes/numOfBands)+" ==========")
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
    print("B = "+str(bestNumOfBands)+", R = "+str(numHashes/bestNumOfBands))
    return [bestNumOfBands,numHashes/bestNumOfBands]

def main():
    t0 = time.time()
    docs = generate_traces_as_text()
    #docs = docs[0:50]
    #docs = random.sample(docs,30)
    docsAsShingles = convertToShingles(docs)
    numOfDocs = len(docs)
    sigs = MinHashNumpy(docsAsShingles)
    findRB(sigs,docsAsShingles,1,1,2,0.9)
    print('\nTotal flow time took %.2f sec.' % (time.time() - t0))

if __name__ == '__main__':
    main()
