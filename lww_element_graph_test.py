import unittest
from lww_element_graph import Graph
import time


class TestGraph(unittest.TestCase):

    def test_add_vertices_and_edges(self):
        """
        This method tests CRDT for adding vertices and edges.
        This test case is also explained in the table in readme.md file.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_vertex(3, current_timestamp)
        graph.add_vertex(4, current_timestamp)
        graph.add_vertex(5, current_timestamp)
        graph.add_edge((1, 2), current_timestamp)
        graph.add_edge((2, 3), current_timestamp)
        graph.add_edge((3, 4), current_timestamp)
        graph.add_edge((4, 5), current_timestamp)
        graph.add_edge((5, 1), current_timestamp)
        graph.add_edge((1, 3), current_timestamp)
        graph.add_edge((2, 4), current_timestamp)
        graph.add_edge((3, 5), current_timestamp)
        graph.add_edge((4, 1), current_timestamp)
        graph.add_edge((5, 2), current_timestamp)
        expected_arr: list = [1, 2, 3, 4, 5]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)
        expected_arr: list = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (1, 3), (2, 4), (3, 5), (4, 1), (5, 2)]
        self.assertEqual(list(graph.add_edges_dict.keys()), expected_arr)

    def test_for_vertex_add_operation_idempotence(self):
        """
        This method tests idempotence of CRDT for vertex addition in the graph.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.vertex_exists(1))
        self.assertFalse(graph.add_vertex(1, current_timestamp - 1))
        self.assertFalse(graph.add_vertex(1, current_timestamp + 1))
        self.assertFalse(graph.add_vertex(1, current_timestamp + 2))
        expected_arr: list = [1]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)
        self.assertEqual(graph.add_vertices_dict[1], current_timestamp)

    def test_for_vertex_remove_operation_idempotence(self):
        """
        This method tests idempotence of CRDT for vertex removal from the graph.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.remove_vertex(1, current_timestamp)
        self.assertFalse(graph.remove_vertex(1, current_timestamp - 1))  # False because timestamp is less than current
        self.assertFalse(graph.remove_vertex(1, current_timestamp + 1))  # False because timestamp is already removed
        self.assertFalse(graph.remove_vertex(1, current_timestamp + 2))  # False because timestamp is already removed
        self.assertFalse(graph.add_vertex(1, current_timestamp))  # False because timestamp is already removed
        self.assertFalse(graph.vertex_exists(1))
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)
        self.assertEqual(graph.remove_vertices_dict[1], current_timestamp + 2)  # True because timestamp is the latest

    def test_for_vertex_commutativity(self):
        """
        This method tests commutativity of CRDT with vertex addition and removal
        using different timestamps.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        graph.remove_vertex(1, current_timestamp)
        expected_arr: list = [1]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)
        graph = Graph()
        graph.remove_vertex(1, current_timestamp)
        graph.add_vertex(1, current_timestamp)
        expected_arr: list = [1]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)
        graph = Graph()
        graph.add_vertex(1, current_timestamp + 1)
        graph.remove_vertex(1, current_timestamp - 1)
        expected_arr: list = [1]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)
        graph = Graph()
        graph.remove_vertex(1, current_timestamp - 1)
        graph.add_vertex(1, current_timestamp + 1)
        expected_arr: list = [1]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)
        graph = Graph()
        graph.add_vertex(1, current_timestamp + 1)
        graph.remove_vertex(1, current_timestamp + 2)
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)
        graph = Graph()
        graph.remove_vertex(1, current_timestamp + 2)
        graph.add_vertex(1, current_timestamp + 1)
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_add_remove_vertex(self):
        """
        This method tests add and remove operation of vertex in the graph.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.vertex_exists(1))
        self.assertFalse(graph.vertex_exists(2))
        graph.add_vertex(2, current_timestamp)
        graph.remove_vertex(1, current_timestamp + 10)
        self.assertTrue(graph.vertex_exists(2))
        self.assertFalse(graph.vertex_exists(1))
        expected_arr: list = [2]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_add_remove_edge(self):
        """
        This method tests add and remove operation of edge in the graph.
        """
        graph = Graph()
        current_timestamp = time.time()
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp + 10)
        graph.add_vertex(3, current_timestamp + 20)
        graph.add_edge((2, 3), current_timestamp)
        self.assertTrue(graph.edge_exists((2, 3)))
        graph.remove_edge((2, 3), current_timestamp + 10)
        self.assertFalse(graph.edge_exists((2, 3)))
        expected_arr: list = [(2, 3)]
        self.assertEqual(list(graph.remove_edges_dict.keys()), expected_arr)

    def test_merge_lww_graph(self):
        """
        This method tests merge operation of two lww element graphs.
        """
        graph_a = Graph()
        graph_b = Graph()
        graph_a.add_vertex(6, time.time())
        graph_a.add_vertex(2, time.time())
        graph_a.add_vertex(3, time.time())
        graph_a.add_edge((3, 2), time.time())
        graph_b.add_vertex(1, time.time())
        graph_b.add_vertex(0, time.time())
        graph_b.add_vertex(3, time.time())
        graph_b.add_edge((3, 0), time.time())
        merged = graph_a.merge(graph_b)
        assert {0, 1, 2, 3, 6}.issubset(merged.add_vertices_dict.keys())
        assert {(3, 2), (3, 0)}.issubset(merged.add_edges_dict.keys())

    def test_add_remove_add_vertex(self):
        """
        This method tests add->remove->add operations of vertex in the graph.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.vertex_exists(1))
        graph.remove_vertex(1, current_timestamp)
        self.assertTrue(graph.vertex_exists(1))
        graph.remove_vertex(1, current_timestamp + 100)
        self.assertFalse(graph.vertex_exists(1))
        graph.add_vertex(1, current_timestamp + 120)
        self.assertTrue(graph.vertex_exists(1))

    def test_remove_add_vertex(self):
        """
        This method tests remove->add operations of vertex in the graph.
        """
        current_timestamp = time.time()
        graph = Graph()
        self.assertFalse(graph.remove_vertex(1, current_timestamp))
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.vertex_exists(1))

    def test_add_edge_remove_vertex_bias(self):
        """
        This method tests concurrent operations of add_edge & remove_vertex
        this is a deadlock so this implementation is biased towards remove edge.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_edge((1, 2), current_timestamp + 10)
        self.assertTrue(graph.edge_exists((1, 2)))  # edge added
        graph.remove_vertex(2, current_timestamp + 10)  # remove vertex 2
        self.assertTrue(graph.vertex_exists(1))  # vertex 1 still exists
        self.assertFalse(graph.edge_exists((1, 2)))  # edge removed, since vertex 2 is removed

    def test_add_remove_add_edge(self):
        """
        This method tests add->remove->edge operations on edge in the graph.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_edge((1, 2), current_timestamp)
        self.assertTrue(graph.edge_exists((1, 2)))
        graph.remove_edge((1, 2), current_timestamp)
        self.assertTrue(graph.edge_exists((1, 2)))
        graph.remove_edge((1, 2), current_timestamp + 100)
        self.assertFalse(graph.edge_exists((1, 2)))
        graph.add_edge((1, 2), current_timestamp + 100)
        self.assertTrue(graph.edge_exists((1, 2)))

    def test_remove_vertex_twice_in_reverse_order(self):
        """
        This method tests applying remove operation twice on vertex
        in reverse order of timestamps means first bigger timestamp then small.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.vertex_exists(1))
        graph.remove_vertex(1, current_timestamp + 10)
        self.assertFalse(graph.vertex_exists(1))
        graph.remove_vertex(1, current_timestamp)
        self.assertFalse(graph.vertex_exists(1))
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_check_vertex_exists(self):
        """
        This method tests vertex_exists method of the graph.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.vertex_exists(1))
        self.assertFalse(graph.vertex_exists(2))
        graph.add_vertex(2, current_timestamp)
        self.assertTrue(graph.vertex_exists(2))
        expected_arr: list = [1, 2]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_get_vertices(self):
        """
        This method tests get_vertices method of the graph.
        It will check whether the return vertices are correct or not for a given vertex.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_vertex(3, current_timestamp)
        graph.add_edge((1, 2), current_timestamp)
        graph.add_edge((3, 1), current_timestamp)
        graph.add_edge((3, 2), current_timestamp)
        expected_arr: list = [2, 3]
        self.assertEqual(graph.get_vertices(1), expected_arr)
        expected_arr: list = [1, 3]
        self.assertEqual(graph.get_vertices(2), expected_arr)
        expected_arr: list = [1, 2]
        self.assertEqual(graph.get_vertices(3), expected_arr)

    def test_find_path(self):
        """
        This method will test the find_path function of the graph in which
        we are finding path between two vertices.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_vertex(3, current_timestamp)
        graph.add_vertex(3, current_timestamp)
        graph.add_vertex(4, current_timestamp)
        graph.add_vertex(5, current_timestamp)
        graph.add_vertex(6, current_timestamp)
        graph.add_vertex(7, current_timestamp)
        graph.remove_vertex(4, current_timestamp + 1)
        graph.add_edge((1, 2), current_timestamp)
        graph.add_edge((3, 2), current_timestamp)
        graph.add_edge((2, 4), current_timestamp)
        graph.add_edge((3, 5), current_timestamp)
        graph.add_edge((6, 1), current_timestamp)
        expected_arr: list = [1, 2, 3]
        self.assertEqual(graph.find_path(1, 3), expected_arr)
        expected_arr: list = [1, 2]
        self.assertEqual(graph.find_path(1, 2), expected_arr)
        expected_arr: list = []
        self.assertEqual(graph.find_path(1, 4), expected_arr)
        expected_arr: list = [1, 2, 3, 5]
        self.assertEqual(graph.find_path(1, 5), expected_arr)
        expected_arr: list = [6, 1, 2, 3, 5]
        self.assertEqual(graph.find_path(6, 5), expected_arr)

    def test_empty_lookup(self):
        """
        This method checks empty lookup of the graph.
        """
        graph = Graph()
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_vertex_already_exists(self):
        """
        This method tests if we add already existing vertex again to the graph.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        self.assertEqual(graph.add_vertex(1, current_timestamp + 10), False)
        expected_arr: list = [1]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_edge_already_exists(self):
        """
        This method tests if we add already existing
        EDGE again in the graph is it added or not.
        """
        current_timestamp = time.time()
        graph = Graph()
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_edge((1, 2), current_timestamp)
        self.assertEqual(graph.add_edge((1, 2), current_timestamp + 10), False)
        expected_arr: list = [1, 2]
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_add_vertex_exception(self):
        """
        This method tests the exception handling of unhashable type
        in add_vertex function.
        """
        current_timestamp = time.time()
        graph = Graph()
        self.assertEqual(graph.add_vertex([1, 2, 3], current_timestamp), None)
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_remove_vertex_exception(self):
        """
        This method tests the exception handling of unhashable type
        in remove_vertex function.
        """
        current_timestamp = time.time()
        graph = Graph()
        self.assertEqual(graph.remove_vertex([1, 2, 3], current_timestamp), None)
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_add_edge_exception(self):
        """
        This method tests the exception handling of unhashable type
        in add_edge function.
        """
        current_timestamp = time.time()
        graph = Graph()
        self.assertEqual(graph.add_edge([1, 2, 3], current_timestamp), None)
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)

    def test_remove_edge_exception(self):
        """
        This method tests the exception handling of unhashable type
        in remove_edge function.
        """
        current_timestamp = time.time()
        graph = Graph()
        self.assertEqual(graph.remove_edge([1, 2, 3], current_timestamp), None)
        expected_arr: list = []
        self.assertEqual(list(graph.add_vertices_dict.keys()), expected_arr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
