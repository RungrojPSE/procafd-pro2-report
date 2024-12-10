

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
