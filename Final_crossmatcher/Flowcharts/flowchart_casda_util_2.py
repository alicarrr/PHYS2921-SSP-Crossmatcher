import os
from graphviz import Digraph

# Ensure Graphviz bin directory is in the PATH
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# Create a new directed graph
dot = Digraph(comment='casda_util Flowchart')

# Function: get_public_data_table
dot.node('AD', 'Retrieve CASDA continuum \n catalogues as a pandas dataframe \n(get_public_data_table)',
 shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('AE', 'Input: refresh?', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('AEE', 'Does cache exist \n and is refresh false?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('AF', 'Load Cache', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AG', 'Clear Cache\n(delete_directory_contents)', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AH', 'Set TAP URL', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AI', 'Search for Continuum Catalogues', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AJ', 'Filter Good/Uncertain Data', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AK', 'Save Public Data as Cache', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AL', 'Return Public Data', shape='box', style='filled', fillcolor='#d0e0ff')

# Function: casda_search_closest_catalogue
dot.node('AM', 'Find catalogue files corresponding to \n the closest match to a source \n(casda_search_closest_catalogue)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('AN', 'Input: raan and dec \nof the source, casda credentials, \nand whether you want to refresh', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('AO', 'Set download path for XML files,\n set target source coordinates\n and set catalogue search radius', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AQ', 'Are casda credentials valid?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('AR', 'Login to CASDA', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AS', 'Retrieve and filter continuum catalogues\n(get_public_data_table)', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AT', 'Get centre coordinates of catalogues,\n find files within catalogue\n search radius, and stage\n files for download', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AW', 'Download XML files', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AX', 'Convert XML to DataFrame\n(convert_xml_to_pandas)', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AY', 'Sort DataFrame by coordinates\n and return the filename of \n the closest match', shape='box', style='filled', fillcolor='#d0e0ff')


# Common End
dot.node('BX', 'End Function', shape='ellipse', style='filled', fillcolor='#d0e0ff')

# Define the edges to represent function calls and flow
dot.edge('AD','AE')
dot.edge('AE','AEE')
dot.edge('AEE','AF', label='Yes')
dot.edge('AF', 'AJ')
dot.edge('AJ', 'AK')
dot.edge('AK', 'AL')
dot.edge('AL', 'BX')
dot.edge('AEE','AG',label='No')
dot.edge('AG', 'AH')
dot.edge('AH', 'AI')
dot.edge('AI', 'AJ')

dot.edge('AM','AN')
dot.edge('AN', 'AO')
dot.edge('AO', 'AQ')
dot.edge('AQ', 'AS', label='Yes')
dot.edge('AQ', 'AR', label='No')
dot.edge('AR', 'AS')
dot.edge('AS', 'AT')
dot.edge('AT', 'AW')
dot.edge('AW', 'AX')
dot.edge('AX', 'AY')
dot.edge('AY', 'BX')

# Specify a different directory for saving the file
output_directory = os.path.expanduser("~")  # User's home directory
dot.render(os.path.join(output_directory, 'casda_util_flowchart_2'), format='pdf', cleanup=True)

# Output the dot source
print(dot.source)
