# =============================================================================
#                               Trace Class
# =============================================================================


class Trace:
    def __init__(self, file_name, program_name, data):
        self.file_name = file_name
        self.program_name = program_name
        self.raw_data = data
        # Variable to indicate if trace is malicious or benign
        self.is_malicious = True  # TODO get this value as parameter

    def display_file_name(self):
        print "Trace's file name: ", self.file_name

    def display_program_name(self):
        print "Program Name: ", self.program_name

    def display_data(self):
        print "Trace Data: ", self.data

    def is_malicious_check(self):
        if self.is_malicious:
            print "Trace is malicious"
        else:
            print "Trace is not malicious"

    def change_status(self):
        self.is_malicious = not self.is_malicious

    def get_name(self):
        return self.program_name

    def get_filename(self):
        return self.file_name

    def get_raw_data(self):
        return self.rawdata

    def get_data_as_string(self):
        return '*'.join([(str(call.get('API_Name')) + '@' + str(call.get('hKey'))) for call in self.raw_data[:]])