import settings
import glob
import re
import ntpath
import os
from trace_class import Trace
import ntpath


# # =============================================================================
# # =============================================================================
# # =============================================================================
# #							 Parser
# # =============================================================================
# # =============================================================================
# # =============================================================================


def parse_traces_as_objects(directory, moveToDirecotry=None):
	files = get_files_paths(directory, 'hooklog')  # Getting all files (extension 'hooklog') from given directory
	trace_objects = []

	# For each trace: Parse according to trace object:
	# file name, program name (1st line inside trace), trace data (2nd line to end of trace file)
	for fName in files:
		# Get file name by splitting the path and getting just the file name from path
		path_head, path_tail = ntpath.split(fName)
		file_name = path_tail

		# Get first line of file (program name)
		input_file = open(fName, 'r')
		line = input_file.readline()  # Read first line of file
		program_name = line.strip()  # The program name (strips remove all white spaces at the start and end)

		# Get trace data
		trace_data = []
		for line in input_file:
			line = line.strip()  # strips remove all white spaces at the start and end
			# Search for a pattern which looks for character '#' and some digit 0-9 (\d) afterwards.
			# The '+' means that other digits after the first one don't matter
			match_timestamp = re.search(r'#([\d]+)',
										line)  # regular expression searching for timestamp and return boolean value if found or not # TODO
			if match_timestamp:
				trace_data.append(
					{})  # Appending an empty Python dictionary to program_name (dictionary - set of separated words)
				trace_data[-1]['timestamp'] = match_timestamp.group(1)
				continue
			match_keyvalue = re.search(r'.+=.+', line)  # Regular expression matching all line that include '=' within
			if not match_keyvalue:  # If there is no '=' within the line, insert the line as an "API Name (e.g. 'CreateFile')" and continue to next line of file
				trace_data[-1]['API_Name'] = line
				continue
			line_elements = line.split(
				'=')  # If line includes '=': Splits lines to separate lines (treating '=' as a delimeter)
			trace_data[-1][line_elements[0]] = line_elements[1]  # Append the string after the 1st '='
		# End of file lines looping

		input_file.close()
		trace_objects.append(
			Trace(file_name, program_name, trace_data))  # Append parsed traced as a Trace object to list
		if moveToDirecotry:
			if not os.path.exists(moveToDirecotry):
				os.makedirs(moveToDirecotry)
			os.rename(fName, moveToDirecotry+"/"+ntpath.basename(fName))
	return trace_objects  # Return the list of all traces as Trace objects


# Get the path of traces
def get_files_paths(directory, extension):
	return glob.glob(directory + '/*.' + extension)  # TODO consider iglob


"""
### Old file parser

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


### Old directory files parser
def parse_directory_files(directory):
	files = get_files_paths(directory, 'hooklog')
	parsed_files = []
	for file_name in files:
		parsed_file = parse_file(file_name)
		parsed_files.append(parsed_file)
		#save_parsed_file(fname, parsed_file)
	return parsed_files


### Old saving of parsed files
def save_parsed_file(fname, parsed_traces):
	output_file = open(fname[:-8] + '_parsed.txt', 'a')
	output_file.write('Filename: ' + parsed_traces[0] + ', Number of calls = ' + str(len(parsed_traces) - 1) + '\n')

	for trace in parsed_traces[1:]:
		output_file.write('\n')
		# for key, val in trace.items():
		#	output_file.write(key + ':' + val + ', ' )
		output_file.writelines(str(trace))
		# output_file.write('}')
	output_file.close()

	# w = csv.writer(open(fname[:-8] + '_parsed.csv', 'w'))
	# w.writerow(['Filename',parsed_traces[0]])
	# for trace in parsed_traces[1:]:
	#	 for key, val in trace.items():
	#		 w.writerow([key, val])

# Old extract_API_name function
def extract_API_name(traces):
	return [[t[0],'*'.join([call.get('API_Name') for call in t[1:]])] for t in traces]
"""

# Filter data for every trace to 'program_name', 'parsed data' (calling get_data_as_string function from Trace class)
def extract_APIhKey_name(traces):
	return [[t.get_name(), t.get_data_as_string()] for t in traces]


# Generating the parsed traces as text
def generate_traces_as_text(prasedTracesObjects):
	return extract_APIhKey_name(prasedTracesObjects)
