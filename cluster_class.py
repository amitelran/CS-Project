# =============================================================================
#                               Cluster (bucket) Class
# =============================================================================

import settings
import sys

class Cluster:
    def __init__(self, cluster_id):
        self.cluster_id = cluster_id
        self.cluster_traces = []
        self.num_traces = 0
        self.num_benign_traces = 0
        self.num_malicious_traces = 0
        self.num_unlabeled_traces = 0
        self.medioid = None
        self.distance_vector = []



    # Append a trace to cluster
    def append_trace(self, trace):
        self.cluster_traces.append(trace)
        self.num_traces += 1
        if (trace.is_malicious == True):
            self.num_malicious_traces += 1
        else:
            if (trace.is_malicious == False):
                self.num_benign_traces += 1
            else:
                self.num_unlabeled_traces += 1


    # Compute benign ratio
    def benign_ratio(self):
        if (self.num_malicious_traces == 0):
            return 100.0
        else:
            return (float(self.num_benign_traces / (self.num_traces * 1.0)))


    # Print traces in cluster
    def print_cluster_traces(self):
        print("\n-------------- Cluster %d traces --------------" % self.cluster_id)
        for t in self.cluster_traces:
            print("%s\t | %s\t" % (t.file_name, t.program_name))



    # Print cluster data
    def print_cluster_data(self):
        print("\n------------------------------")
        print("Cluster ID: %d " % self.cluster_id)
        print("%d traces | %d malicious traces | %d benign traces | %.3f%% Benign"
              % (self.num_traces, self.num_malicious_traces, self.num_benign_traces, self.benign_ratio()))

        print("Distance from other clusters:")
        sys.stdout.write("Cluster ID:       \t\t")
        for cluster in self.distance_vector:
            otherCluster = cluster[-1]
            if (otherCluster.benign_ratio() >= settings.benign_threshold):
                sys.stdout.write("++%-*s" % (10, otherCluster.cluster_id))
            else:
                sys.stdout.write("%-*s" % (10, otherCluster.cluster_id))

        print("")
        sys.stdout.write("Cluster Similarity:\t\t")
        for cluster in self.distance_vector:
            otherCluster = cluster[-1]
            if (otherCluster.benign_ratio() >= settings.benign_threshold):
                sys.stdout.write("%-*.4f" % (12, cluster[1]))
            else:
                sys.stdout.write("%-*.4f" % (10, cluster[1]))

        print("")

