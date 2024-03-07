from collections import defaultdict
import csv
import pandas as pd

def loadcsv(file, keymap, iter):
    """
    Load data from a CSV file and organize it into a dictionary.

    Parameters:
    - file: CSV file already loaded using pandas.
    - keymap: A dictionary mapping column names in the CSV to desired keys in the output dictionary.
              For example, {'CSVColumnName': 'DesiredKeyName'}.
    - iter: The column name used as the key/id for each row in the output dictionary.

    Returns:
    - A dictionary with keys derived from the 'iter' column, each containing a sub-dictionary with keys and values based on 'keymap'.
    - An error message string if 'iter' is not a valid column name or if duplicate keys/ids are found.
    """
    
    # Initialize the output dictionary
    fileDict = {}
    
    # Check if the 'iter' column exists in the CSV
    if iter not in file.columns:
        return "Error: " + str(iter) + " not a valid header in " + str(file)
    
    # Iterate through each row in the CSV
    for _,  row in file.iterrows():
        id = row[iter]
        # Check for duplicate keys/ids
        if id in fileDict:
            return "Error: Duplicate key/id on " + str(iter) + ":" + str(row[iter])
        
        # Initialize a sub-dictionary for each unique id
        fileDict[id] = {}
        
        # Map CSV columns to desired keys based on 'keymap'
        for col, key in keymap.items():
            fileDict[id][key] = row[col]

    return fileDict


def freq_loadcsv(filename, indict, key, nullcase = "nan",delim = '; ',start=0, end=None, suff='', types = int, net=True):
    """
    Load and process CSV to update frequencies in nodes, edges, and an input dictionary.

    Parameters:
    - filename: Path to the CSV file.
    - indict: Dictionary to update with frequencies.
    - key: Column name to process for nodes and edges.
    - nullcase: String representing null or ignored values.
    - delim: Delimiter used to split the column values.
    - start: Starting index to slice each node string.
    - end: Ending index to slice each node string. `None` processes till the end.
    - suff: Suffix to add to each node after processing.
    - types: Type of values stored in dictionaries (default: int).
    - net: True or False to fill network arrays
    Returns:
    Tuple containing three elements:
    1. Nodes dictionary with the count of occurrences for each node length.
    2. Edges dictionary with the count of edges between distinct nodes.
    3. Updated input dictionary (`indict`) with frequencies ('freq') of each processed node.

    Note:
    This function assumes that the 'filename' parameter is a DataFrame loaded via pandas.read_csv,
    and 'key' refers to a column in this DataFrame.
    """
    # Initialize dictionaries for nodes and edges with default integer values.
    nodes = defaultdict(types)
    edges = defaultdict(types)
    # Use the provided dictionary to update frequencies.
    out_dict = indict
    if net:
        # Iterate over each value in the specified column of the DataFrame.
        for val in filename[key]:
            # Split the value into nodes based on the provided delimiter.
            val = str(val).split(delim)
            # Update the node length frequency.
            nodes[len(val)] += 1

            # Iterate over each node after splitting.
            for i, node in enumerate(val):
                processed_node = node[start:end] + suff  # Process the node based on start, end, and suff.
                if node != nullcase:  # Check if the processed node is not the null case.
                    # Increment the frequency for the processed node.
                    out_dict[processed_node]['freq'] += 1
                    # Compare the current node with subsequent nodes to establish edges.
                    for nodeconn in val[i+1:]:
                        processed_conn = nodeconn[start:end] + suff  # Process the connection node.
                        if processed_node != processed_conn and nodeconn != nullcase:  # Ensure nodes are distinct.
                            # Increment the edge count between the two nodes.
                            edges[(processed_node, processed_conn)] += 1
    else:
        # Iterate over each value in the specified column of the DataFrame.
        for val in filename[key]:
            # Split the value into nodes based on the provided delimiter.
            val = str(val).split(delim)
            # Update the node length frequency.
            nodes[len(val)] += 1

            # Iterate over each node after splitting.
            for i, node in enumerate(val):
                processed_node = node[start:end] + suff  # Process the node based on start, end, and suff.
                if node != nullcase:  # Check if the processed node is not the null case.
                    # Increment the frequency for the processed node.
                    out_dict[processed_node]['freq'] += 1

    # Return the updated dictionaries.
    return nodes, edges, out_dict