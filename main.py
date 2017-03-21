import time
import lsh
import shingles
import est_jaccard
import trace_class
import minhashing
import sim_comparison
import settings



# # =============================================================================
# # =============================================================================
# # =============================================================================
# #                             Parser
# # =============================================================================
# # =============================================================================
# # =============================================================================

# def Sergey(docs,JcrdSim,LevSim,i,j):
#     print('*******************************\nPair : %s and %s' % (docs[i][0], docs[j][0]))
#     print('\n Trace of %s representation (length= %d):\n %s \n\n\n' % (docs[i][0], len(docs[i][1]), docs[i][1]))
#     print('\n Trace of %s representation (length= %d):\n %s \n\n\n' % (docs[j][0], len(docs[j][1]), docs[j][1]))
#     print('Jaccard= %.3f' % JcrdSim[getTriangleIndex(i,j,len(docs))])
#     print('Lev= %.3f' % LevSim[getTriangleIndex(i, j, len(docs))])
#     print('*******************************\n\n')


def main():
    settings.init()
    t0 = time.time()
    docs = trace_class.generate_traces_as_text()
    #docs = docs[0:50]
    #docs = random.sample(docs,30)
    docsAsShingles = shingles.convertToShingles(docs)
    numOfDocs = len(docs)
    sigs = minhashing.MinHashNumpy(docsAsShingles)
    lsh.findRB(sigs,docsAsShingles,1,1,2,0.9)
    print('\nTotal flow time took %.2f sec.' % (time.time() - t0))

if __name__ == '__main__':
    main()
