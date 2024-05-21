import os
from graphviz import Digraph

# Ensure Graphviz bin directory is in the PATH
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# Create a new directed graph
dot = Digraph(comment='Main Script Flowchart')

# Define the nodes with comments/filenames
dot.node('B', 'Setup Logger', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('C', 'Set working Directory', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('D', 'Login to CASDA', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('E', 'Get options of paths to sample', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('F', 'Find planets in source', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('G', 'Filter for planets with GAIA IDs in\n this sourcelist and save the filtered list', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('I', 'Take one planet from the filtered list. \n Is there another planet?', shape='diamond', style='filled', fillcolor='#d0e0ff')
dot.node('J', 'Correct for proper motion \n using the closest casda catalogue file', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('K', 'Search CASDA for matching files', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('L', 'Crossmatch Results', shape='box', style='filled', fillcolor='#d0e0ff')
dot.node('M', 'End', shape='ellipse', style='filled', fillcolor='#d0e0ff')

# Define the edges
dot.edge('B', 'C')
dot.edge('C', 'D')
dot.edge('D', 'E')
dot.edge('E', 'F')
dot.edge('F', 'G')
dot.edge('G', 'I')
dot.edge('I', 'J',label='yes')
dot.edge('J', 'K')
dot.edge('K', 'L')
dot.edge('L', 'I', label='Next planet')
dot.edge('I', 'M', label='No')

# Add a subgraph with rank settings
with dot.subgraph() as s:
    s.attr(rank='sink')
    s.node('M')

# Specify a different directory for saving the file
output_directory = os.path.expanduser("~")  # User's home directory
dot.render(os.path.join(output_directory, 'main_flowchart'), format='pdf', cleanup=True)

print(dot.source)
