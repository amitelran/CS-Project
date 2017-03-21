import random
import time
import settings
import json

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
    coeffA = pickRandomCoeffs(settings.numHashes, maxShingleID)
    coeffB = pickRandomCoeffs(settings.numHashes, maxShingleID)

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
        for j in range(0, settings.numHashes):

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
    # signatures = numpy.array(signatures)
    # Calculate the elapsed time (in seconds)
    elapsed = (time.time() - t0)
    print("\nGenerating MinHash signatures took %.2fsec" % elapsed)
    print("\nOutput MinHash signatures to json file")
    with open('Minhash_Data.json', 'a') as jfile:
        json.dump(signatures,jfile)
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
