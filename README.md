## What is a CRDT?

Conflict-Free Replicated Data Types (CRDTs) are data structures that power real-time collaborative applications in
distributed systems. CRDTs can be replicated across systems, they can be updated independently and concurrently
without coordination between the replicas, and it is always mathematically possible to resolve inconsistencies that
might result.

## LWW-Element-Graph (Last-Writer-Wins-Element-Graph):
LWW-Element-Graph is a CRDT that is a graph consisting of vertices and edges. Each vertex or edge has a timestamp that is
updated when the vertex or edge is added or removed.

## Implementation
### Classes
* `Graph`: A graph consisting of vertices and edges.
* `GraphOperations`: A set of operations on graphs.

### Methods
* `Graph.vertex_exists`: Returns true if the vertex exists in the graph.
* `Graph.edge_exists`: Returns true if the edge exists in the graph.
* `Graph.add_vertex`: Add a vertex to the graph.
* `Graph.add_edge`: Add an edge to the graph.
* `Graph.remove_vertex`: Remove a vertex from the graph.
* `Graph.remove_edge`: Remove an edge from the graph.
* `Graph.get_vertices`: Get all vertices that are adjacent to a given vertex.
* `Graph.find_path`: Find a path between two vertices.
* `Graph.merge`: Merge two graphs.

### Testing
The following tests were mage to ensure that the implementation of the CRDT is correct.

* `test_add_vertices_and_edges`: Test that adding vertices and edges to the graph works.
* `test_for_vertex_add_operation_idempotence`: Test that adding a vertex to the graph is idempotent.
* `test_for_vertex_remove_operation_idempotence`: Test that removing a vertex from the graph is idempotent.
* `test_for_vertex_commutativity`: Tests commutativity of CRDT with vertex addition and removal: e.g. adding a vertex to the graph and then removing it is the same as removing
* `test_add_remove_vertex`: Test adding and removing a vertex from the graph.
* `test_add_remove_edge`: Test adding and removing an edge from the graph.
* `test_merge_lww_graphs`: Test merging two graphs.
* `test_add_remove_add_vertex`: Test adding and removing a vertex from the graph and then adding it again.
* `test_remove_add_vertex`: Test removing a vertex from the graph and then adding it again.
* `test_add_edge_remove_vertex_bias`: Test that adding an edge to the graph and then removing a vertex from the graph is biased towards removing the edge.
* `test_add_remove_add_edge`: Test adding and removing an edge from the graph and then adding it again.
* `test_remove_vertex_twice_in_reverse_order`: Test removing a vertex from the graph twice in reverse order of the timestamps.
* `test_check_vertex_exists`: Test that the `vertex_exists` method works.
* `test_get_vertices`: Test that the `get_vertices` method works, and that it returns the correct vertices.
* `test_find_path`: Test that the `find_path` method works, finding a path between two vertices.
* `test_empty_lookup`: Test empty lookup of the graph.
* `test_vertex_already_exists`: Test a case when a vertex already exists in the graph.
* `test_edge_already_exists`: Test that an edge already exists in the graph.
* `test_add_vertex_exception`: Test that an exception is thrown when adding an unhashable vertex to the graph.
* `test_add_edge_exception`: Test that an exception is thrown when adding an unhashable edge to the graph.
* `test_remove_vertex_exception`: Test that an exception is thrown when removing an unhashable vertex from the graph.
* `test_remove_edge_exception`: Test that an exception is thrown when removing an unhashable edge from the graph.


### To run the tests:

Follow these steps to run the code in **local environment**:

 1. Ensure python 3.8+ is installed
 2. Open terminal
 3. Go to project root directory
 4. Run the following command: `python3 -m pip -q install -r requirements.txt`
 5. Run the following command: `python3 -m unittest lww_element_graph_test.py`

## Limitations

- This implementation can only handle hashable types.
- Garbage collection: elements should be removed from the sets from time to time when they are no longer useful. In fact, only the most-recent operation (add/remove) is needed.

## References
- https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type#LWW-Element-Set_(Last-Write-Wins-Element-Set)
- https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type
- https://github.com/pfrazee/crdt_notes
- https://hal.inria.fr/inria-00555588/PDF/techreport.pdf
- https://github.com/hammadkhann/State-based-LWW-Element-Graph
- https://github.com/alireza12t/State-Based-LWW-Element-Graph
- https://github.com/anshulahuja98/python3-crdt
