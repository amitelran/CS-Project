import time
from triangle_matrix import *
#import Levenshtein

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
