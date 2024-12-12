To assign levels along all branches of a graph, you need to traverse the entire graph and set the levels for all nodes. The current code calculates levels only for nodes in the `longest_path`, so nodes outside the `longest_path` remain unprocessed. 

You can achieve your goal by using a graph traversal algorithm like Depth-First Search (DFS) or Breadth-First Search (BFS). Here's an updated version of your code that calculates levels for all nodes starting from the root nodes:

### Updated Code:
```python
graph = {1: [2], 2: [3, 5], 3: [4], 4: [], 5: [], 6: [2]}

nodes = []

# Initialize nodes with 'id' and 'level'
for node_id in graph.keys():
    nodes.append({'id': node_id, 'level': None})

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

# Traverse the graph and set levels
def traverse_and_set_levels(node_id, current_level):
    set_level(node_id, current_level)
    for neighbor in graph[node_id]:
        # Only set the level if it's not already set to avoid overwriting
        if get_level(neighbor) is None:
            traverse_and_set_levels(neighbor, current_level + 1)

# Find root nodes (nodes with no incoming edges)
all_nodes = set(graph.keys())
non_root_nodes = {node for neighbors in graph.values() for node in neighbors}
root_nodes = all_nodes - non_root_nodes

# Start traversal from all root nodes
for root in root_nodes:
    traverse_and_set_levels(root, 0)

# Print the result
print(nodes)
```

### Explanation:
1. **Graph Initialization**:
   - Each node is initialized with `id` and `level=None`.

2. **Traverse and Set Levels**:
   - A recursive function, `traverse_and_set_levels`, is defined to assign levels starting from a given node and its neighbors.

3. **Root Nodes**:
   - Nodes with no incoming edges are identified as root nodes. Traversal starts from these nodes.

4. **Level Assignment**:
   - During traversal, levels are assigned incrementally (`current_level + 1`) for each neighbor.

5. **Avoid Overwriting**:
   - Levels are set only for nodes with `None` level to prevent overwriting already calculated levels.

### Example Output:
For the given graph:
```plaintext
[{'id': 1, 'level': 0}, {'id': 2, 'level': 1}, {'id': 3, 'level': 2}, {'id': 4, 'level': 3}, {'id': 5, 'level': 2}, {'id': 6, 'level': 0}]
```

Here:
- Node 1 and 6 are root nodes (`level=0`).
- Other nodes are assigned levels based on their distances from the nearest root node.