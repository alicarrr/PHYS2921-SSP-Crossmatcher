import os
from graphviz import Digraph

# Ensure Graphviz bin directory is in the PATH
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# Create a new directed graph
dot = Digraph(comment='Proper Motion Flowchart')

# Define the nodes with function names and actions

# filter for gaia
dot.node('C', 'Filter for planets with \n a GAIA DR2 and TICv8 Code \n(filter_for_gaia)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('D', 'Input: Sorted list of sources\n from NASA', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('E', "Remove rows without a GAIA ID\n from the source list", shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('F', "Filter to only include planets\n with a GAIA DR2 number", shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('G', "Remove rows without a system \n parameter reference and TICv8 number", shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('I', 'Output: fully filtered source \n list following criteria above', shape='parallelogram', style='filled', fillcolor='#d0e0ff')


# proper_correct_planet
dot.node('T', 'Proper motion correct a planet\n(proper_correct_planet)', shape='ellipse', style='filled', fillcolor='#d0e0ff')
dot.node('U', 'Input: dataframe of sources and\n name of planet to be corrected', shape='parallelogram', style='filled', fillcolor='#d0e0ff')
dot.node('V', 'Is the source dataframe \n empty?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('W', 'Filter rows based on \n the planet name', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('X', 'Is the number of \nfiltered rows empty?', shape='diamond', style='filled', fillcolor='#ffd0d0')
dot.node('Y', 'Initialize Coordinates for Planet', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('Z', 'Apply space motion to \n propagate until the epoch \n from the input', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AA', 'Update original DataFrame \n with corrected coordinates \n accounting for proper motion', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('AB', 'Return updated DataFrame \n with proper motion correction', shape='parallelogram', style='filled', fillcolor='#d0e0ff')


dot.node('J', 'End Function Return', shape='ellipse', style='filled', fillcolor='#d0e0ff')

# Define the edges to represent function calls and flow
dot.edge('C', 'D')
dot.edge('D', 'E')
dot.edge('E', 'F')
dot.edge('F', 'G')
dot.edge('G', 'I')
dot.edge('I', 'J')


dot.edge('T', 'U')
dot.edge('U', 'V')
dot.edge('V', 'W', label='No')
dot.edge('V', 'J', label='Yes')
dot.edge('W', 'X')
dot.edge('X', 'Y', label='No')
dot.edge('X', 'J', label='Yes')
dot.edge('Y', 'Z')
dot.edge('Z', 'AA')
dot.edge('AA', 'AB')
dot.edge('AB', 'J')

# Specify a different directory for saving the file
output_directory = os.path.expanduser("~")  # User's home directory
dot.render(os.path.join(output_directory, 'proper_motion_2_functions_flowchart'), format='pdf', cleanup=True)

# Output the dot source
print(dot.source)
