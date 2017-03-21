import binascii
import time
import settings

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

