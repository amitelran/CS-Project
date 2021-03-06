# =============================================================================
#                               Trace Class
# =============================================================================

import time
import settings

class Trace:
    def __init__(self, file_name, program_name, data):
        self.file_name = file_name
        self.program_name = program_name
        self.raw_data = data
        self.classification_time = time.strftime("%c")     # Classification time occurrence of trace
        #self.classification_bucket = None
        self.is_malicious = None           # Variable to indicate if trace is malicious or benign
        self.shingles = None
        self.signature = None


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

    # Check whether trace is classified as benign or malicious, or unlabeled if unclassified
    def is_malicious_check(self):
        if (self.is_malicious == True):
            print "Trace is malicious"
        else:
            if (self.is_malicious == False):
                print "Trace is not malicious"
            else:
                if (self.is_malicious == None):
                    print "Trace is unlabeled"

    def get_malicious_benign_label(self):
        if (self.is_malicious == True):
            return "Malicious"
        else:
            if (self.is_malicious == False):
                return "Benign"
            else:
                if (self.is_malicious == None):
                    return "Unlabeled"

    # Change trace status from current status (as benign or malicious) to the new given boolean status
    def change_status(self, newStatus):
        self.is_malicious = newStatus

    # Trace's name getter (1st line of trace's file)
    def get_name(self):
        return self.program_name

    def get_is_malicious(self):
        return self.is_malicious

    # Trace's file's name getter
    def get_filename(self):
        return self.file_name

    # Getting raw data
    def get_raw_data(self):
        return self.rawdata

    # Parse raw data as string when called
    def get_data_as_string(self):
        return '*'.join([(str(call.get('API_Name')) + '@' + str(call.get('hKey'))) for call in self.raw_data[:]])


    # Parse raw data as API call string
    def get_api_data_as_string(self):
        api_calls_data = []
        for call in self.raw_data[:]:
            API_call = str(call.get('API_Name'))
            if (str(call.get('hKey')) != 'None'):
                API_call += '@' + (str(call.get('hKey')))
            if (str(call.get('lpFileName')) != 'None'):
                API_call += '@' + (str(call.get('lpFileName')))
            if (str(call.get('Return')) != 'None'):
                API_call += '@' + (str(call.get('Return')))
            if (str(call.get('desiredAccess')) != 'None'):
                API_call += '@' + (str(call.get('desiredAccess')))
            api_calls_data.append(API_call)

        # Generate accumulated string of API calls, delimeted by '*'
        APIs = ''
        for api_call in api_calls_data:
            APIs += '*' + api_call

        return APIs


    def get_shingles(self):
        return self.shingles

    def set_shingles(self, shingles):
        self.shingles = shingles

    def get_signature(self):
        return self.signature

    def set_signature(self, sig):
        self.signature = sig
