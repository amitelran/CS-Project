import binascii
import time
import settings
import re
import trace_class
# =============================================================================
#               Convert Documents To Sets of Shingles
# =============================================================================

# Function that receives traces as input, and converts the data to shingles according to the
# shingle size set in settings.py

def convertToShingles(docs):
    print "Shingling " + str(len(docs)) + " docs..."

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

    for i in range(0, numDocs):                # For every trace, convert its' data to shingles
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
        for j in range(len(doc) - settings.shingle_size + 1):
            shingle = doc[j:j + settings.shingle_size]
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
#               Convert Documents To Sets of API Shingles
# =============================================================================



def convertToAPIcalls(docs):
    print "Shingling " + str(len(docs)) + " docs as API calls..."
    docsAsAPIcalls = []
    numDocs = len(docs)
    docNames = []

    t0 = time.time()
    totalAPIShingles = 0

    for i in range(0, numDocs):  # For every trace, convert its' data to shingles
        doc = docs[i]
        doc = doc[1]
        APIshinglesInDoc = set()            # Set empty set

        # Hash the shingle to a 32-bit integer.
        # Add the hash value to the list of shingles for the current document.
        # Note that set objects will only add the value to the set if the set
        # doesn't already contain it.
        api_calls_array = doc.split("*")                        # Split API calls to different elements
        api_calls_array = filter(None, api_calls_array)         # filter all empty elements ''

        # Get all sets of size 'settings.apiCall_per_Shingle' to create a shingle from multiple API calls
        api_calls_shingle = [api_calls_array[i:i + settings.apiCalls_per_shingle] for i in range(len(api_calls_array) - 2)]
        for apis_set in api_calls_shingle:
            apis_set_joined_string = '*'.join(apis_set)         # Join set of API calls as a single string
            crc = binascii.crc32(apis_set_joined_string) & 0xffffffff
            APIshinglesInDoc.add(crc)

        # Store the completed list of shingles for this document in the dictionary.
        docsAsAPIcalls.append(APIshinglesInDoc)

        # Count the number of shingles across all documents.
        totalAPIShingles = totalAPIShingles + len(APIshinglesInDoc)

    # Report how long shingling took.
    print('\nShingling ' + str(numDocs) + ' docs as API calls took %.2f sec.' % (time.time() - t0))
    print('\nAverage API shingles per doc: %.2f' % (totalAPIShingles / numDocs))
    return docsAsAPIcalls



def setTracesShingles(traces):
    print "Shingling " + str(len(traces)) + " traces..."
    # The current shingle ID value to assign to the next new shingle we
    # encounter. When a shingle gets added to the dictionary, we'll increment this
    # value.
    curShingleID = 0
    # Create a dictionary of the articles, mapping the article identifier (e.g.,
    # "t8470") to the list of shingle IDs that appear in the document.

    numDocs = len(traces)
    t0 = time.time()
    totalShingles = 0
    for t in traces:
        doc = t.get_data_as_string()
        shinglesInDoc = set()
        for j in range(len(doc) - settings.shingle_size + 1):
            shingle = doc[j:j + settings.shingle_size]
            crc = binascii.crc32(shingle) & 0xffffffff
            shinglesInDoc.add(crc)
        t.set_shingles(shinglesInDoc)

    print('\nShingles are set. ' 'took %.2f sec.' % (time.time() - t0))
    print('\nAverage shingles per doc: %.2f' % (totalShingles / numDocs))
