import csv
import networkx as nx
import matplotlib.pyplot as plt

"""
This script reads a CSV file containing a list of URLs and their connections, and creates a network graph
showing the connections between the links.

The CSV file should have the following structure:
    - Column 1: Source URL
    - Column 2: Target URL

The network graph will be saved as a PNG file.

Make sure to install the required libraries: networkx and matplotlib.
"""

# Step 1: Open CSV file containing URLs and connections
def open_csv(filename):
    urls = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row if present
        for row in reader:
            urls.append((row[0], row[1]))  # Assuming URLs and connections are in the first two columns
    return urls

# Step 2: Create network graph
def create_network_graph(urls):
    graph = nx.DiGraph()
    incoming_links = {}

    for source, target in urls:
        graph.add_edge(source, target)

        if target in incoming_links:
            incoming_links[target] += 1
        else:
            incoming_links[target] = 1

        if source not in incoming_links:
            incoming_links[source] = 1

    nx.set_node_attributes(graph, incoming_links, "incoming_links")
    return graph

# Step 3: Save network graph as PNG file
def save_network_graph(graph, filename):
    plt.figure(figsize=(30, 20))
    pos = nx.spring_layout(graph, seed=47, k=0.5, iterations=50)

    # Customize node color, edge color, and font style
    node_color = "#777777"  # Blue
    edge_color = "#999999"  # Gray
    font_color = "#232323"  # Dark gray
    font_weight = "bold"

    # Get the node sizes based on incoming link count

    multiplier = 1000 * (1 / len(graph.nodes))

    node_sizes = [links * multiplier for node, links in graph.nodes(data="incoming_links")]

    nx.draw_networkx(
        graph,
        pos,
        with_labels=True,
        node_color=node_color,
        node_size=node_sizes,
        font_color=font_color,
        font_size=4,
        font_weight=font_weight,
        edge_color=edge_color,
        width=0.25,
    )

    plt.box(False)
    plt.axis("off")
    plt.savefig(filename, dpi=300, bbox_inches="tight")

# Usage 
csv_filename = "links.csv"
output_filename = "network_graph.png"

urls = open_csv(csv_filename)
graph = create_network_graph(urls)
save_network_graph(graph, output_filename)