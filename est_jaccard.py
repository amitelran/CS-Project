from minhashing import MinHashNumpy
from triangle_matrix import *
import time
import settings


# =============================================================================
#                     Calculate Est Jacaard
# =============================================================================

def calcEstJacaard(docsAsShingleSets):
    print('\nComparing all signatures...')

    signatures = MinHashNumpy(docsAsShingleSets)

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
            for k in range(0, settings.numHashes):
                count = count + (signature1[k] == signature2[k])

            # Record the percentage of positions which matched.
            estJSim[getTriangleIndex(i, j, numDocs)] = (count / float(settings.numHashes))
            #TEMP
            # print('EstJaccard(' + str(i) + ',' + str(j) + ')=' + str(estJSim[getTriangleIndex(i, j, numDocs)]))


    # Calculate the elapsed time (in seconds)
    elapsed = (time.time() - t0)

    print("\nComparing MinHash signatures took %.2fsec" % elapsed)

    return estJSim