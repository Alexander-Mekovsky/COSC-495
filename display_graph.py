from matplotlib import pyplot as plt
from pyvis.network import Network
import random
import math

def barchart(keys, vals, x, y, title, tight=False, xscale=10, yscale=6, xrot=45, rf='right'):
    """
    Displays a bar chart.

    Parameters:
    - keys: List of categories (x-axis).
    - vals: Corresponding values for each category (y-axis).
    - x: Label for the x-axis.
    - y: Label for the y-axis.
    - title: Chart title.
    - tight: If True, adjust subplot parameters to give specified padding.
    - xscale: Width of the chart.
    - yscale: Height of the chart.
    - xrot: Rotation of x-axis labels.
    - rf: Alignment of x-axis labels.
    """
    try:
        plt.figure(figsize=(xscale, yscale))
        plt.bar(keys, vals)
        plt.xticks(rotation=xrot, ha=rf)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(title)
        if tight:
            plt.tight_layout()
        plt.show()
    except Exception as e:
        return "Failure to display graph: " + str(e)
    return "Success"

def closeplot():
    """
    Closes the current pyplot plot to free up memory.
    """
    plt.close()

def random_color():
    """
    Generates a random hex color.

    Returns:
    A string representing a random hex color.
    """
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def average_color(color1, color2):
    """
    Calculates the average color between two hex colors.

    Parameters:
    - color1: First color as a hex string.
    - color2: Second color as a hex string.

    Returns:
    A hex string representing the average color.
    """
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:], 16)
    avg_r = (r1 + r2) // 2
    avg_g = (g1 + g2) // 2
    avg_b = (b1 + b2) // 2
    return "#{:02x}{:02x}{:02x}".format(avg_r, avg_g, avg_b)

def freq_network(nodes, edges, selnodes=None, start=0, end=None,suff='', h="1200px", w="100%", minsz=1, minw=0.1, maxw=10.0, bg="#222222", fontcol="white", graphtitle='network.html',physics=False):
    """
    Creates and displays an interactive network graph.

    Parameters:
    - nodes: List of nodes in the network.
    - edges: Dictionary of edges between nodes and their weights.
    - selnodes: Nodes to highlight in the graph.
    - start: Starting index to slice each node string.
    - end: Ending index to slice each node string. `None` processes till the end.
    - suff: Suffix to add to each node after processing.
    - h: Height of the graph.
    - w: Width of the graph.
    - minsz: Minimum size of nodes.
    - minw: Minimum width of edges.
    - maxw: Maximum width of edges.
    - bg: Background color of the graph.
    - fontcol: Font color for node labels.
    - graphtitle: Filename for the output HTML file.
    - physics: Enables or Disables physics
    """
    # try:
    net = Network(height=h, width=w, bgcolor=bg, font_color=fontcol)
    nodeColors = {}
    selNodes = selnodes if selnodes else nodes
    for node in selNodes:
        if node in nodes:
            nodeColors[node] = random_color()
            net.add_node(nodes[node]['desc'], size=minsz + math.log(nodes[node]['freq'] + 1), color=nodeColors[node], title=str(nodes[node]['freq']))
    
    max_weight = max(edges.values())
    
    for (source, target), count in edges.items():
        source = source[start:end] +suff
        target = target[start:end] +suff
        
        if source in selNodes and target in selNodes and source != target:
            scaledw = minw + (maxw - minw) * (math.log(count + 1) / math.log(max_weight + 1))
            edge_color = average_color(nodeColors.get(source, '#ffffff'), nodeColors.get(target, '#ffffff'))

            net.add_edge(nodes[source]['desc'], nodes[target]['desc'], width=scaledw, color=edge_color, title=str(count))
    
    net.toggle_physics(True)
    net.show(graphtitle, notebook=False)
    
    # except Exception as e:
    #     return "Failed to create network: " + str(e)

    return "Success"
