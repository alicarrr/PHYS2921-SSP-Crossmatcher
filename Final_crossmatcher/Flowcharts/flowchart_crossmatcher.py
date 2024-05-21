import os
from graphviz import Digraph

# Ensure Graphviz bin directory is in the PATH
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# Create a new directed graph
dot = Digraph(comment='Crossmatcher Flowchart')

# Define the nodes with function names and actions

# find_planets_in_source
dot.node('C', 'Find all planets in a source file \n (find_planets_in_source)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('D', 'Input: source file', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('E', "Filter the source list for unique planets", shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('F', "Ensure the time column of 'rowupdate' is a datetime option, \n sort the dataframe by 'rowupdate' in descending order, \n and keep the first update which is the newest", shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('I', 'Output: Sorted and filtered source list', shape='parallelogram', style='filled', fillcolor='#d0e0ff')

# crossmatch planets
dot.node('K', 'Crossmatch NASA database \n for a planet with CASDA database\n (crossmatch_planet)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('L', 'Input: source list, search radius,\n name of planet, and filename of casda catalogue', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('M', "Load the CASDA data and proper motion corrected data", shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('O', 'Filter the sorted source list\n for the planet of interest.', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('P', 'Does the planet exist in this list?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('Q', 'Perform Crossmatching using \n objects with celestial coordinates\n(crossmatch)', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('R', 'Return Crossmatch Results and log output', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('T', 'Handle FileNotFoundError', shape='box', style='filled', fillcolor='#d0e0ff')

# Crossmatch
dot.node('U', 'Compare coordinates from a \n CASDA sourcelist against the \n NASA database to see if any files \n with the same position match \n(crossmatch)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('UU', 'Input: source list and \n filename of casda catalogue', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('V', 'Load catalogue data and \n load casda source list', shape='box', style='filled', fillcolor='#d0e0ff')
# Fix connections from here
dot.node('X', 'Is the planet name defined?', shape='diamond', style='filled', fillcolor='#ffd0d0', height='0.5', width='0.5')
dot.node('Y', 'Filter Source List by Planet Name', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('Z', 'Create SkyCoord objects for CASDA \n catalogue and source list', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AA', 'Create SkyCoord objects for source list', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AB', 'Set search radius for crossmatching', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AC', 'Perform crossmatching between \n the CASDA catalogue coordinates \nand source catalogue coordinates', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AD', 'Return crossmatching results', shape='parallelogram', style='filled', fillcolor='#d0e0ff')



# End all functions
dot.node('J', 'End Function Return', shape='ellipse', style='filled', fillcolor='#d0e0ff')


# Define the edges to represent function calls and flow
dot.edge('C', 'D')
dot.edge('D', 'E')
dot.edge('E', 'F')
dot.edge('F', 'I')
dot.edge('I', 'J')

dot.edge('K', 'L')
dot.edge('L', 'M')
dot.edge('M', 'O')
dot.edge('O', 'P')
dot.edge('P', 'Q', label='Yes')
dot.edge('P', 'T', label='No')
dot.edge('Q', 'R')
dot.edge('R', 'J')
dot.edge('T', 'J')


dot.edge('U', 'UU')
dot.edge('UU', 'V')
dot.edge('V', 'X')
dot.edge('X', 'Y', label='Yes')
dot.edge('X', 'Z', label='No')
dot.edge('Y', 'Z')
dot.edge('Z', 'AA')
dot.edge('AA', 'AB')
dot.edge('AB', 'AC')
dot.edge('AC', 'AD')
dot.edge('AD', 'J')

# Specify a different directory for saving the file
output_directory = os.path.expanduser("~")  # User's home directory
dot.render(os.path.join(output_directory, 'crossmatcher_flowchart'), format='pdf', cleanup=True)

# Output the dot source
print(dot.source)
