import json

import matplotlib.pyplot as plt
import networkx as nx
import yaml


def parse_json(filename):
    # Load the JSON data
    with open(filename, "r") as f:
        data = json.load(f)

    # Initialize an empty list to store the nodes
    nodes = []

    # Create a dictionary to map the link to the ID of the node
    link_to_id = {}

    # Iterate over the nodes in the JSON data
    for node in data["nodes"]:
        # Create a new dictionary for the node
        new_node = {}

        # Set the ID of the node to its order value
        new_node["ID"] = node["order"]

        # Add the type of the node
        new_node["type"] = node["type"]

        # Check if the node has the 'widgets_values' key
        if "widgets_values" in node:
            # Parse the widgets_values to node attributes
            new_node["widgets_values"] = node["widgets_values"]
        else:
            # If the node doesn't have the 'widgets_values' key, set 'widgets_values' to None
            new_node["widgets_values"] = None

        # Initialize an empty list to store the inputs
        inputs = []

        # Iterate over the inputs of the node
        for input in node["inputs"]:
            # If the input has a link, add the ID of the node to which this link belongs to the inputs list
            if input["link"] is not None:
                # If the link is not in the link_to_id dictionary, add it
                if input["link"] not in link_to_id:
                    for n in data["nodes"]:
                        for o in n["outputs"]:
                            # Check if the output has the 'links' key and is not None
                            if "links" in o and o["links"] is not None:
                                if input["link"] in o["links"]:
                                    link_to_id[input["link"]] = n["order"]
                                    break
                inputs.append(link_to_id[input["link"]])

        # Add the inputs to the node
        new_node["inputs"] = inputs

        # Add the node to the nodes list
        nodes.append(new_node)

    return nodes


def create_graph(nodes):
    # Create a new directed graph
    G = nx.DiGraph()

    # Add the nodes to the graph
    for node in nodes:
        G.add_node(node["ID"], type=node["type"], widgets_values=node["widgets_values"])

    # Add the edges to the graph
    for node in nodes:
        for input in node["inputs"]:
            G.add_edge(input, node["ID"])

    return G


def contract_reroutes(G):
    # Find all nodes with type Reroute
    reroute_nodes = [n for n, d in G.nodes(data=True) if d["type"] == "Reroute"]

    # Iterate over reroute nodes
    for reroute_node in reroute_nodes:
        # Get predecessors and successors of the reroute node
        predecessors = list(G.predecessors(reroute_node))
        successors = list(G.successors(reroute_node))

        # For each predecessor, connect it to each successor
        for predecessor in predecessors:
            for successor in successors:
                # Add edge from predecessor to successor
                G.add_edge(predecessor, successor)

        # Remove the reroute node from the graph
        G.remove_node(reroute_node)

    return G


def flatten(x):
    if isinstance(x, list):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]


def reduce_groups(G):
    reduced = []
    replace_with = {}

    # Sort the nodes by ID
    nodes = sorted(G.nodes(data=True), key=lambda x: x[0])

    for node in nodes:
        id = node[0]
        from_nodes = list(G.predecessors(node[0]))
        type = node[1]["type"]
        widgets_values = node[1]["widgets_values"]

        if type == "NNGroup":
            for i, from_node in enumerate(from_nodes):
                if from_node in replace_with:
                    from_nodes[i] = replace_with[from_node]

            # Flatten from_nodes if it contains lists
            replace_with[id] = flatten(from_nodes)
            continue

        # Replace all from_nodes with the id of the node
        for i, from_node in enumerate(from_nodes):
            if from_node in replace_with:
                from_nodes = replace_with[from_node]

        # from_nodes = from_nodes[0] if len(from_nodes) == 1 else from_nodes
        reduced.append([id, from_nodes, type, widgets_values])

        # print(f"{id}, {from_nodes}, {type}, {widgets_values}")

    return reduced


def squeeze_ids(nodes):
    old2new = {}

    for node_new_id, node in enumerate(nodes):
        # Replace the old id with the new id
        node_old_id = node[0]
        old2new[node_old_id] = node_new_id
        node[0] = node_new_id

        # Replace ids in from_nodes with the new ids
        from_nodes = node[1]
        for i, from_node in enumerate(from_nodes):
            from_nodes[i] = old2new[from_node]

    return nodes


def parse_to_yaml(nodes):
    string = "network:"

    for node in nodes:
        id = node[0]
        from_nodes = node[1]
        module_name, repeats, args, *_ = node[3]

        if len(from_nodes) == 0:
            from_nodes = -1
        elif len(from_nodes) == 1:
            from_nodes = from_nodes[0]

        string += f"\n - [{str(from_nodes):>15}, {module_name:>15}, {repeats}, [{args}]]"

    with open("yolov8-comfyui.yaml", "w") as f:
        for line in string:
            f.write(line)


def print_nodes(nodes):
    for node in nodes:
        id = node[0]
        from_nodes = node[1]
        module_name, repeats, args, *_ = node[3]
        print(f"{id:>2}, {str(from_nodes):>15}, {module_name:>15}, {repeats}, {[args]}")


nodes = parse_json("yolov8.json")
G = create_graph(nodes)
G = contract_reroutes(G)
nodes = reduce_groups(G)
nodes = squeeze_ids(nodes)


parse_to_yaml(nodes)
print_nodes(nodes)
