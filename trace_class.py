# =============================================================================
#                               Trace Class
# =============================================================================

import time


class Trace:
    def __init__(self, file_name, program_name, data):
        self.file_name = file_name
        self.program_name = program_name
        self.raw_data = data
        self.classification_time = time.strftime("%c")     # Classification time occurrence of trace
        #self.classification_bucket = None
        # Variable to indicate if trace is malicious or benign
        self.is_malicious = True                            # TODO get this value as parameter

    # Display trace's file's name
    def display_file_name(self):
        print "Trace's file name: ", self.file_name

    # Display trace's program name (1st line of trace's file)
    def display_program_name(self):
        print "Program Name: ", self.program_name

    # Display trace's data
    def display_data(self):
        print "Trace Data: ", self.data

    # Display trace's classification time
    def display_classification_time(self):
        print "Trace classification date & time: ", self.classification_time

#   # Display trace's classification bucket
#   def display_classification_bucket(self):
#        print "Trace's classification bucket: ", self.classification_bucket

    # Check whether trace is classified as benign or malicious
    def is_malicious_check(self):
        if self.is_malicious:
            print "Trace is malicious"
        else:
            print "Trace is not malicious"

    # Change trace status from current status (as benign or malicious) to the opposite status when called
    def change_status(self):
        self.is_malicious = not self.is_malicious

    # Trace's name getter (1st line of trace's file)
    def get_name(self):
        return self.program_name

    # Trace's file's name getter
    def get_filename(self):
        return self.file_name

    # Getting raw data
    def get_raw_data(self):
        return self.rawdata

    # Parse raw data as string when called
    def get_data_as_string(self):
        return '*'.join([(str(call.get('API_Name')) + '@' + str(call.get('hKey'))) for call in self.raw_data[:]])