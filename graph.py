import json

def dfs(node, graph, visited, stack, back_edges):
    visited.add(node)
    stack.add(node)

    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(neighbor, graph, visited, stack, back_edges)
        elif neighbor in stack:  # Cycle detected
            back_edges.append((node, neighbor))  # Store the edge causing the cycle

    stack.remove(node)

def remove_cycles(graph):
    visited = set()
    stack = set()
    back_edges = []

    for node in graph:
        if node not in visited:
            dfs(node, graph, visited, stack, back_edges)

    # Remove back edges
    for from_node, to_node in back_edges:
        graph[from_node].remove(to_node)

    return back_edges

# Depth-First Search function to find the longest chain
def dfs_longest_path(graph, start, path=None):
    if path is None:
        path = []

    path.append(start)  # Add the current node to the path
    longest_path = path.copy()  # Assume current path is the longest for now

    for neighbor in graph[start]:
        new_path = dfs_longest_path(graph, neighbor, path)
        if len(new_path) > len(longest_path):
            longest_path = new_path

    path.pop()  # Backtrack
    return longest_path



def longest_path(nodes, edges, start_node):
    # nodes = [
    #     {'id': 1},
    #     {'id': 2},
    #     {'id': 3},
    #     {'id': 4},
    #     {'id': 5},
    # ]
    # edges = [
    #     {'from': 1, 'to': 2},
    #     {'from': 2, 'to': 3},
    #     {'from': 3, 'to': 4},
    #     {'from': 4, 'to': 2},
    #     {'from': 4, 'to': 5},
    # ]

    # Create an adjacency list
    graph = {}
    for node in nodes:
        graph[node['id']] = []

    for edge in edges:
        graph[edge['from']].append(edge['to'])

    # Remove cycles
    back_edges = remove_cycles(graph)
    # print("Back edges removed (causing cycles):", back_edges)
    # print("Graph after removing cycles:", graph)

    # back_edges

    # Find the longest path starting from node 1
    longest_chain = dfs_longest_path(graph, start_node)
    # print("Longest chain:", longest_chain)

    return longest_chain, back_edges, graph


def assign_level(nodes, edges, remove_cycle=0):
    if remove_cycle == 0:
        longest_chain, back_edges, graph = longest_path(nodes, edges, 1)
        print(graph)
    else:
        graph = {}
        for node in nodes:
            graph[node['id']] = []

        for edge in edges:
            graph[edge['from']].append(edge['to'])



    for node in nodes:
        node['level'] = None
    # nodes = []

    # Initialize nodes with 'id' and 'level'
    # for node_id in graph.keys():
    #     nodes.append({'id': node_id, 'level': None})

    # Helper functions to set and get levels
    def set_level(id, level):
        node = next((node for node in nodes if node['id'] == id), None)
        if node:
            node['level'] = level

    def get_level(id):
        node = next((node for node in nodes if node['id'] == id), None)
        if node:
            return node['level']
        return None

    # graph = {1: [2], 2: [3, 5], 3: [4], 4: [], 5: [], 6: [2]}
    # longest_path = [1, 2, 3, 4] # will not used

    # Traverse the graph and set levels
    def traverse_and_set_levels(node_id, current_level):
        set_level(node_id, current_level)
        for neighbor in graph[node_id]:
            # Only set the level if it's not already set to avoid overwriting
            if get_level(neighbor) is None:
                traverse_and_set_levels(neighbor, current_level + 1)

    # Find root nodes (nodes with no incoming edges)
    all_nodes = set(graph.keys())
    non_root_nodes = {node for neighbors in graph.values() for node in neighbors} # like union of [2], [3,5], [4], [2] = {2, 3, 4, 5} 
    root_nodes = all_nodes - non_root_nodes

    # Start traversal from all root nodes
    for root in root_nodes:
        traverse_and_set_levels(root, 0)

    create_graph_data(nodes, edges)

    # Print the result
    return nodes



def create_graph_data(nodes, edges):
    
    # Define nodes and edges
    data = {
        "nodes": nodes,
        "edges": edges
    }

    # Write the data to a JSON file
    with open("test/data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("data.json created successfully!")