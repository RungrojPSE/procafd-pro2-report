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
    graph = adjacency_list(nodes, edges)

    # Remove cycles
    back_edges = remove_cycles(graph)
    # print("Back edges removed (causing cycles):", back_edges)
    # print("Graph after removing cycles:", graph)

    # back_edges

    # Find the longest path starting from node 1
    longest_chain = dfs_longest_path(graph, start_node)
    # print("Longest chain:", longest_chain)

    return longest_chain, back_edges, graph

def adjacency_list(nodes, edges):
    graph = {}
    for node in nodes:
        graph[node['id']] = []

    for edge in edges:
        graph[edge['from']].append(edge['to'])

    return graph


def assign_level(nodes, edges, remove_cycle=True):
    if remove_cycle:
        longest_chain, back_edges, graph = longest_path(nodes, edges, 1)
    else:
        graph = adjacency_list(nodes, edges)



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

    

    # Print the result
    return nodes


def reassign_ids(nodes, edges):
    # Create a mapping with new sequential IDs
    ids = {n['id']: i + 1 for i, n in enumerate(nodes)}

    # Update the 'id' in nodes
    for n in nodes:
        n['id'] = ids[n['id']]
    # Update the 'id' in edges
    for e in edges:
        e['from'] = ids[e['from']]
        e['to'] = ids[e['to']]

    return nodes, edges


def hypergraph_nodes_edges(nodes, edges):
    # Example
    # nodes = [
    #     {'id': 1, 'level': 0, 'label': '(iAB)'},
    #     {'id': 2, 'level': 1,  'label': '(dlA/B)'},
    #     {'id': 3, 'level': 2,  'label': '(oA)'},
    #     {'id': 4, 'level': 2,  'label': '(oB)'},
    # ]
    # edges = [
    #     {'from': 1, 'to': 2, 'label': 'AB'},
    #     {'from': 2, 'to': 3, 'label': 'A'},
    #     {'from': 2, 'to': 4, 'label': 'B'},
    # ]

    def get_node_prop(prop, byVal, byProp='id'):
        node = next((node for node in nodes if node[byProp] == byVal), None)
        if node:
            return node[prop]
        return None

    nodesH = []
    edgesH = []

    for edge in edges:
        idH = f"{edge['from']}-{edge['to']}"

        # classify role
        role = "Linked Components"
        
        level_from = get_node_prop('level', edge['from'])
        level_to = get_node_prop('level', edge['to'])
        recycle = False

        prop_from = get_node_prop('properties', edge['from'])
        prop_to = get_node_prop('properties', edge['to'])
        if prop_from['kind'] == 'START':
            role = "Input Components"
        
        if prop_to['kind'] == 'END':
            role = "Output Components"
            if prop_from['kind'] == 'SPLITTER':
                role = "Released Components"

        # Check this
        if level_from > level_to:
            role = "Recycled Components"
            recycle = True

        nodesH.append(
            {
            'id': idH,
            'label': edge['label'],
            'level': level_from,
            'properties': {
                    'role': role
                }
            }
        )

        edges_next = [e for e in edges if e['from'] == edge['to']]
        for e in edges_next:
            idH_next = f"{e['from']}-{e['to']}"
            edgesH.append(
                {
                    'from': idH,
                    'to': idH_next,
                    'label': get_node_prop('label', edge['to']),
                    'properties': {
                        'recycle': recycle
                    }
                }
            )

        # Sort the nodes by the 'level' key
        nodesH = sorted(nodesH, key=lambda x: x['level'])

    return nodesH, edgesH

# Hierarchical Topological Sorting: Reordering within each level to align with previous connections.
def hierarchical_topological_sort(nodes, edges):
    # Example
    # nodes = [
    # {"id": "zz", "level": 0},
    # {"id": "tt", "level": 0},
    # {"id": "gg", "level": 1},  
    # {"id": "aa", "level": 1},
    # {"id": "qq", "level": 2}, 
    # ]
    # edges = [
    # {"from": "zz", "to": "aa"},
    # {"from": "tt", "to": "gg"},
    # {"from": "gg", "to": "qq"},
    # {"from": "aa", "to": "qq"},  
    # ]

    def get_node(id):
        return next((n for n in nodes if n['id'] == id), None)

    graph = adjacency_list(nodes, edges)

    # Ensure that level 0 is found
    nodesO = [n for n in nodes if n['level'] == 0]  # Start with level 0 nodes
    if len(nodesO) == 0:
        raise ValueError("There are no root level!")

    for n in nodesO:  # Traverse and expand nodesO
        for idval in graph[n['id']]:
            if not any(existing['id'] == idval for existing in nodesO):
                if node := get_node(idval):  # Use walrus operator for brevity
                    nodesO.append(node)

    nodes, edges = reassign_ids(nodesO, edges)
    return nodes, edges