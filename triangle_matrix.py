import numpy
import sys

# =============================================================================
#                     Define Triangle Matrices
# =============================================================================

# Define virtual Triangle matrices to hold the similarity values (return empty matrix with required size).
def createTriangleMatrixNumpy(numDocs):
    # Calculate the number of elements needed in our triangle matrix
    numElems = int(numDocs * (numDocs - 1) / 2)

    # Initialize empty list to store the similarity values.
    # Caution!! numpy.empty initializes list faster, but with garbage data inside.
    # Must ensure all garbage data is overwritten while program flow.
    matrix = numpy.empty(numElems)
    return matrix

"""
### Old "CreateTriangleMatrix" before using Numpy
def createTriangleMatrix(numDocs):
    # Define virtual Triangle matrices to hold the similarity values.

    # Calculate the number of elements needed in our triangle matrix
    numElems = int(numDocs * (numDocs - 1) / 2)

    # Initialize empty list to store the similarity values.
    return [0 for x in range(numElems)]
"""

# Function to map a 2D matrix coordinate into a 1D index.
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
    # This indexing scheme is taken from pg. 211 of:
    # http://infolab.stanford.edu/~ullman/mmds/ch6.pdf
    # adapted for a 0-based index.
    # Note: The division by two should NOT truncate, it needs to be a float.
    k = int(i * (numDocs - (i + 1) / 2.0) + j - i) - 1
    return k
