import os
from graphviz import Digraph

# Ensure Graphviz bin directory is in the PATH
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# Create a new directed graph
dot = Digraph(comment='casda_util Flowchart')

# Function: convert_xml_to_pandas
dot.node('I', 'Convert an xml file\n to a pandas dataframe\n(convert_xml_to_pandas)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('J', 'Input: xml file name', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('M', 'Read xml file and convert\n this to a Pandas DataFrame', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('N', 'Output: DataFrame', shape='parallelogram', style='filled', fillcolor='#d0e0ff')

# Function: check_casda_cache
dot.node('O', 'Checks if pubdat cache \n already exists\n(check_casda_cache)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('R', 'Does the directory for\n the public data cache exist, using the \n directory path to pubdat-YYYY-MM-DD.csv?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('S', 'List the files in the directory\n and filter files following the expected\n pattern of pubdat naming', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('T', 'Is a file following the\n expected pattern found?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('U', 'Return True', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('U2', 'Return False', shape='box', style='filled', fillcolor='#d0e0ff')

# Function: pandas_to_csv
dot.node('V', 'Convert a pandas\n dataframe to a csv\n(pandas_to_csv)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('W', 'Input: filename of output,\n download path, dataframe', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('W2', 'Is the directory found?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('X', 'Create Directory', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('Y', 'Save DataFrame to CSV in directory', shape='box', style='filled', fillcolor='#d0e0ff')

# Function: delete_directory_contents
dot.node('Z', 'Clear files in cache folder\n(delete_directory_contents)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('AA', 'Input: directory path', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('AB', 'List Files in Directory', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AC', 'Iterate Over Files and Delete', shape='box', style='filled', fillcolor='#d0e0ff')

# Common End
dot.node('BX', 'End Function', shape='ellipse', style='filled', fillcolor='#d0e0ff')

# Define the edges to represent function calls and flow

dot.edge('I', 'J')
dot.edge('J', 'M')
dot.edge('M', 'N')
dot.edge('N', 'BX')

dot.edge('O', 'R')
dot.edge('R', 'S', label='Yes')
dot.edge('R', 'BX', label='No')
dot.edge('S', 'T')
dot.edge('T', 'U', label='Yes')
dot.edge('T', 'U2', label='No')
dot.edge('U', 'BX')
dot.edge('U2', 'BX')

dot.edge('V', 'W')
dot.edge('W', 'W2')
dot.edge('W2', 'X',label='No')
dot.edge('W2', 'Y',label='Yes')
dot.edge('X', 'Y')
dot.edge('Y', 'BX')

dot.edge('Z', 'AA')
dot.edge('AA', 'AB')
dot.edge('AB', 'AC')
dot.edge('AC', 'BX')

# Specify a different directory for saving the file
output_directory = os.path.expanduser("~")  # User's home directory
dot.render(os.path.join(output_directory, 'casda_util_flowchart_part_1'), format='pdf', cleanup=True)

# Output the dot source
print(dot.source)
