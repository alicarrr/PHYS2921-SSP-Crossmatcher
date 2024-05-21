import os
from graphviz import Digraph

# Ensure Graphviz bin directory is in the PATH
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# Create a new directed graph
dot = Digraph(comment='casda_util Flowchart')

# Function: extract_epoch_from_pubdat_catalogue
dot.node('BA', 'Find the epoch from \n file in a public data catalogue\n (extract_epoch_from_pubdat_catalogue)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('BB', 'Input: filename to \n extract epoch from', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('BC', 'Set Cache Folder Path', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BD', 'Is pubdat CSV in cache folder?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('BE', 'Load pubdat CSV to DataFrame', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BF', 'Filter Rows by Filename', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BG', 'Extract and return epoch value', shape='box', style='filled', fillcolor='#d0e0ff')

# Function: casda_search
dot.node('BI', 'Generate a csv of matches\n of a given source with \n CASDA continuum catalogues \n (casda_search)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('BJ', 'Input: the raan and declination of the source, \n search radius, casda credentials, \n whether the  files need to be refreshed,\n and the required output filename', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('BK', 'Set Download Paths, \n set target source coordinates, \n set catalogue search radius', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BN', 'Are casda credentials valid?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('BNN', 'Login to CASDA', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BO', 'Retrieve and Filter Continuum Catalogues\n(get_public_data_table)', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BP', 'Get centre coordinates \n of catalogues, find files within\n the catalogue search radius,\n and stage these files for download', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BS', 'Download XML Files\n(casda.download_files)', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BT', 'Convert XML files to DataFrames\n(convert_xml_to_pandas)', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BU', 'Sort DataFrame by coordinates \n and save them as a csv', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('BW', 'Return this DataFrame of matches', shape='box', style='filled', fillcolor='#d0e0ff')

# Common End
dot.node('BX', 'End Function', shape='ellipse', style='filled', fillcolor='#d0e0ff')

# Define the edges to represent function calls and flow

dot.edge('BA', 'BB')
dot.edge('BB', 'BC')
dot.edge('BC', 'BD')
dot.edge('BD', 'BE', label='Yes')
dot.edge('BD', 'BX', label='No')
dot.edge('BE', 'BF')
dot.edge('BF', 'BG')
dot.edge('BG', 'BX')


dot.edge('BI', 'BJ')
dot.edge('BJ', 'BK')
dot.edge('BK', 'BN')
dot.edge('BN', 'BO', label='Yes')
dot.edge('BN', 'BNN', label='No')
dot.edge('BNN', 'BO')
dot.edge('BO', 'BP')
dot.edge('BP', 'BS')
dot.edge('BS', 'BT')
dot.edge('BT', 'BU')
dot.edge('BU', 'BW')
dot.edge('BW', 'BX')

# Specify a different directory for saving the file
output_directory = os.path.expanduser("~")  # User's home directory
dot.render(os.path.join(output_directory, 'casda_util_flowchart_3'), format='pdf', cleanup=True)

# Output the dot source
print(dot.source)
