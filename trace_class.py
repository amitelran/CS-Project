import settings
import glob
import re
import ntpath

# =============================================================================
#                               Trace Class
# =============================================================================

class Trace:
    def __init__(self, file_name, program_name, data):
        self.file_name = file_name
        self.program_name = program_name
        self.data = data
        self.is_malicious = True  # Variable to indicate if trace is malicious or benign

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



# # =============================================================================
# # =============================================================================
# # =============================================================================
# #                             Parser
# # =============================================================================
# # =============================================================================
# # =============================================================================


def parse_traces_as_objects(directory):
    files = get_files_paths(directory, 'hooklog')
    trace_objects = []
    for fName in files:
        # Get file name
        path_head, path_tail = ntpath.split(fName)
        file_name = path_tail

        # Get first line of file (trace name)
        input_file = open(fName, 'r')
        line = input_file.readline()    # Read first line of file
        program_name = [line.strip()]     # the program name (strips remove all white spaces at the start and end)

        # Get trace data
        trace_data = []
        for line in input_file:
            line = line.strip()  # strips remove all white spaces at the start and end
            # Search for a pattern which looks for character '#' and some digit 0-9 (\d) afterwards.
            # The '+' means that other digits after the first one don't matter
            match_timestamp = re.search(r'#([\d]+)',line)  # regular expression searching for timestamp and return boolean value if found or not # TODO
            if match_timestamp:
                trace_data.append({})  # appending an empty Python dictionary to program_name (dictionary - set of separated words)
                trace_data[-1]['timestamp'] = match_timestamp.group(1)
                continue
            match_keyvalue = re.search(r'.+=.+', line)  # API Name # TODO
            if not match_keyvalue:
                trace_data[-1]['API_Name'] = line
                continue
            line_elements = line.split('=')  # Splits lines separated with '='
            trace_data[-1][line_elements[0]] = line_elements[1]
        # End of file lines looping

        input_file.close()
        trace_objects.append(Trace(file_name, program_name, trace_data))
        # trace_objects[-1].display_file_name()
        # trace_objects[-1].display_program_name()
        # trace_objects[-1].display_data()
        # print
    return trace_objects


def get_files_paths(directory, extension):
    return glob.glob(directory + '/*.' + extension)  # TODO consider iglob


def parse_file(file_path):
    input_file = open(file_path, 'r')
    line = input_file.readline()
    trace = [line.strip()]  # the program name
    for line in input_file:
        line = line.strip()
        match_timestamp = re.search(r'#([\d]+)', line)   # timestamp # TODO
        if match_timestamp:
            trace.append({})
            trace[-1]['timestamp'] = match_timestamp.group(1)
            continue

        match_keyvalue = re.search(r'.+=.+', line)  # API Name # TODO
        if not match_keyvalue:
            trace[-1]['API_Name'] = line
            continue

        line_elements = line.split('=')
        trace[-1][line_elements[0]] = line_elements[1]
    input_file.close()
    return trace


def parse_directory_files(directory):
    files = get_files_paths(directory, 'hooklog')
    parsed_files = []
    for file_name in files:
        parsed_file = parse_file(file_name)
        parsed_files.append(parsed_file)
        #save_parsed_file(fname, parsed_file)
    return parsed_files


def save_parsed_file(fname, parsed_traces):
    output_file = open(fname[:-8] + '_parsed.txt', 'a')
    output_file.write('Filename: ' + parsed_traces[0] + ', Number of calls = ' + str(len(parsed_traces) - 1) + '\n')

    for trace in parsed_traces[1:]:
        output_file.write('\n')
        # for key, val in trace.items():
        #    output_file.write(key + ':' + val + ', ' )
        output_file.writelines(str(trace))
        # output_file.write('}')
    output_file.close()

    # w = csv.writer(open(fname[:-8] + '_parsed.csv', 'w'))
    # w.writerow(['Filename',parsed_traces[0]])
    # for trace in parsed_traces[1:]:
    #     for key, val in trace.items():
    #         w.writerow([key, val])


def extract_API_name(traces):
    return [[t[0],'*'.join([call.get('API_Name') for call in t[1:]])] for t in traces]


def extract_APIhKey_name(traces):
    return [[t[0], '*'.join([(str(call.get('API_Name')) + '@' + str(call.get('hKey'))) for call in t[1:]])] for t in traces]

def generate_traces_as_text():
    parsed_traces_as_objects = parse_traces_as_objects(settings.samples_directory)
    parsed_traces = parse_directory_files(settings.samples_directory)
    #parsed_traces = parse_directory_files('C:\\Users\\ghanayim\\Google Drive\\Virtualized Cloud Security\\DataSets\\MixAll_hooklogs_labeledBNGN')
    return extract_APIhKey_name(parsed_traces)