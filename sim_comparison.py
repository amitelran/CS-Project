import numpy
import time
from matplotlib import pyplot
import settings


# Similarities comparison
def bucketsReport(buckets):
    print "MinHash parameters:"
    print "\tCoeffA: " + str(settings.coeffA)
    print "\tCoeffB: " + str(settings.coeffB)
    print "\tnextPrime: " + str(settings.nextPrime)
    print "\n\n\Buckets Report: %d buckets" % len(buckets)
    for b,ns in buckets.iteritems():
        print "(*)Bucket #%d, has %d traces" % (b, len(ns))
        jSims = []
        for i in range(0,len(ns)):
            for j in range(i+1, len(ns)):
                s1 = ns[i].get_shingles()
                s2 = ns[j].get_shingles()
                jSim = (len(s1.intersection(s2)) / float(len(s1.union(s2))))
                # print str(jSim)
                jSims.append(jSim)
        avg = numpy.mean(numpy.array(jSims))
        SD = numpy.std(numpy.array(jSims)) #sqrt(mean(abs(x - x.mean())**2))
        print "\tJSim - AVG: %f, SD %f " % (avg, SD)
        print "\tBucket Traces list:'"
        print "\t\t" + '\n\t\t'.join([(t.get_name() + ' / ' + t.get_filename()) for t in ns])



# Similarities comparison
def CompareSimilarities(Sim1,Sim2):
    delta = [(x - y) for x, y in zip(Sim1, Sim2)]
    avg_delta = sum(delta) / float(len(delta))
    max_delta = max(delta)
    min_delta = min(delta)
    median_delta = numpy.median(numpy.array(delta))
    print('Delta- Avg: %.3f, Max: %.3f, Min: %.3f, Median: %.3f' % (avg_delta,max_delta,min_delta,median_delta))

# Similarities comparison calculation of relative error
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

# Checking monotonicity of similarities input
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

