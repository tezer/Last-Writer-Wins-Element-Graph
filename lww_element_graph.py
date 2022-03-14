"""
Graph class implements a basic structure state-based LWW-Element-Graph.
GraphOperation is a class with static methods for graph operations.
The graph contains functionalities to:
● add a vertex/edge,
● remove a vertex/edge,
● check if a vertex is in the graph,
● query for all vertices connected to a vertex,
● find any path between two vertices
● merge with concurrent changes from other graph/replica.
"""

import logging
from typing import Tuple, Dict, List, Any, Set

logging.basicConfig(format='%(filename)s - %(levelname)s - %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.ERROR)
logger = logging.getLogger(__name__)


class GraphOperations:
    """
    A class to provide static methods to Graph Class
    """

    @staticmethod
    def vertex_exists(graph, vertex: int) -> bool:
        """
        Check if a vertex exists in the graph.
        :param graph to check if vertex exists in.
        :param vertex: vertex to be checked.
        :return: True if vertex exists, False otherwise.
        """
        try:
            if vertex not in graph.add_vertices_dict:
                return False  # vertex does not exist
            elif vertex not in graph.remove_vertices_dict:
                return True  # vertex was added and not removed, so it exists
            elif graph.remove_vertices_dict[vertex] > graph.add_vertices_dict[vertex]:
                return False  # vertex was removed after it was added
            elif graph.remove_vertices_dict[vertex] == graph.add_vertices_dict[vertex]:
                return True  # it was added and removed at the same timestamp, it exists, because of the addition bias
            else:
                return True  # vertex was added before it was removed, it exists
        except TypeError:
            logger.error(f"TypeError in vertex_exists: {vertex}")
            return None

    @staticmethod
    def edge_exists(graph, vertex1: int, vertex2: int) -> bool:
        """
        Check if an edge exists in the graph.
        :param graph to check if edge exists in.
        :param vertex1: first vertex of the edge.
        :param vertex2: second vertex of the edge.
        :return: True if edge exists, False otherwise.
        """
        try:
            if vertex1 not in graph.vertices_dict or vertex2 not in graph.vertices_dict:
                return False  # edge does not exist, because at least one of the vertices does not exist
            elif (vertex1, vertex2) not in graph.add_edges_dict and (vertex2, vertex1) not in graph.add_edges_dict:
                return False  # edge does not exist
            elif (vertex1, vertex2) not in graph.remove_edges_dict or (vertex2, vertex1) not in graph.remove_edges_dict:
                return True  # edge was added and not removed, so it exists
            elif graph.remove_edges_dict[vertex1][vertex2] > graph.add_edges_dict[vertex1][vertex2]:
                return False  # edge was removed after it was added
            elif graph.remove_edges_dict[vertex1][vertex2] == graph.add_edges_dict[vertex1][vertex2]:
                return True  # edge was added and removed at the same timestamp, it exists, because of the addition bias
            else:
                return True  # edge was added before it was removed, it exists
        except TypeError:
            logger.error(f"TypeError in edge_exists: {vertex1}, {vertex2}")
            return None

    @staticmethod
    def add_vertex(graph, vertex: int, timestamp: int) -> bool:
        """
        Add a vertex to the graph.
        :param graph to add vertex to.
        :param vertex: vertex to be added.
        :param timestamp: timestamp of the operation.
        """
        try:
            if GraphOperations.vertex_exists(graph, vertex):
                logger.warning(f"Vertex {vertex} already exists in the graph.")
                return False  # vertex already exists
            if vertex in graph.remove_vertices_dict:
                if graph.remove_vertices_dict[vertex] <= timestamp:
                    logger.debug(f"Vertex {vertex} was removed before this timestamp.")
                    graph.remove_vertices_dict.pop(vertex)  # remove vertex from remove_vertices
                    graph.add_vertices_dict[vertex] = timestamp  # add vertex to add_vertices
                    graph.vertices_dict[vertex] = []  # add vertex to vertices
                    logger.info(f"Vertex {vertex} was added to the graph.")
                    return True  # vertex was removed before, but added now
                else:
                    logger.debug(f"Vertex {vertex} was removed after this timestamp.")
                    logger.info(f"Vertex {vertex} was not added to the graph.")
                    return False  # vertex was removed after this timestamp
            else:
                graph.add_vertices_dict[vertex] = timestamp
                graph.vertices_dict[vertex] = []
                logger.info(f"Vertex {vertex} was added to the graph.")
                return True  # vertex was added
        except TypeError:
            logger.error(f"TypeError in add_vertex: {vertex}")
            return None

    @staticmethod
    def add_edge(graph, edge: Tuple[int, int], timestamp: float) -> bool:
        """
        Add an edge to the graph.
        :param graph to add edge to.
        :param edge: edge to be added.
        :param timestamp: timestamp of the operation.
        """
        try:
            if GraphOperations.edge_exists(graph, edge[0], edge[1]):
                logger.warning("Edge {} already exists in the graph.".format(edge))
                return False  # edge already exists
            if edge in graph.remove_edges_dict:
                if graph.remove_edges_dict[edge] <= timestamp:
                    logger.debug(f"Edge {edge} was removed before.")
                    graph.remove_edges_dict.pop(edge)  # remove edge from remove_edges
                    graph.add_edges_dict[edge] = timestamp  # add edge to add_edges
                    graph.vertices_dict[edge[0]].append(edge[1])  # add edge to vertices
                    graph.vertices_dict[edge[1]].append(edge[0])  # add edge to vertices
                    logger.info(f"Edge {edge} was added.")
                    return True  # edge was removed before, but added now
                else:
                    logger.debug(f"Edge {edge} was removed after this timestamp.")
                    return False  # edge was removed after this timestamp
            else:
                graph.add_edges_dict[edge] = timestamp
                graph.vertices_dict[edge[0]].append(edge[1])  # add edge to vertices
                graph.vertices_dict[edge[1]].append(edge[0])  # add edge to vertices
                logger.info(f"Edge {edge} was added.")
                return True  # edge was added
        except TypeError:
            logger.error(f"Edge {edge} is not a tuple.")
            return None
        except KeyError:
            logger.warning(f"Edge {edge} is not in the graph.")
            return None

    @staticmethod
    def remove_vertex(graph, vertex: int, timestamp: int) -> bool:
        """
        Remove a vertex from the graph.
        :param graph to remove vertex from.
        :param vertex: vertex to be removed.
        :param timestamp: timestamp of the operation.
        """
        try:
            if not GraphOperations.vertex_exists(graph, vertex):
                logger.debug(f"Vertex {vertex} does not exist in the graph.")
                graph.remove_vertices_dict[vertex] = timestamp  # add vertex to remove_vertices
                return False  # vertex does not exist
            if vertex in graph.add_vertices_dict:
                if graph.add_vertices_dict[vertex] < timestamp:
                    logger.debug(f"Vertex {vertex} was added before.")
                    graph.add_vertices_dict.pop(vertex)  # remove vertex from add_vertices
                    graph.remove_vertices_dict[vertex] = timestamp  # add vertex to remove_vertices
                    graph.vertices_dict.pop(vertex)  # remove vertex from vertices
                    logger.info(f"Vertex {vertex} was removed.")
                    return True  # vertex was added before, but removed now
                else:
                    logger.debug(f"Vertex {vertex} was added after this timestamp.")
                    return False  # vertex was added after this timestamp
            else:
                graph.remove_vertices_dict[vertex] = timestamp
                graph.vertices_dict.pop(vertex)  # remove vertex from vertices
                logger.info(f"Vertex {vertex} was removed.")
                return True  # vertex was removed
        except TypeError:
            logger.error(f"Vertex {vertex} is not an integer.")
            return None

    @staticmethod
    def remove_edge(graph, edge: Tuple[int, int], timestamp: float) -> bool:
        """
        Remove an edge from the graph.
        :param graph to remove edge from.
        :param edge: edge to be removed.
        :param timestamp: timestamp of the operation.
        """
        if not graph.edge_exists(edge):
            logger.debug(f"Edge {edge} does not exist in the graph.")
            return False  # edge does not exist, so it cannot be removed
        if edge in graph.add_edges_dict:
            if graph.add_edges_dict[edge] < timestamp:
                logger.debug(f"Edge {edge} was added before.")
                graph.add_edges_dict.pop(edge)  # remove edge from add_edges
                graph.remove_edges_dict[edge] = timestamp  # add edge to remove_edges
                graph.vertices_dict[edge[0]].remove(edge[1])  # remove edge from vertices
                graph.vertices_dict[edge[1]].remove(edge[0])  # remove edge from vertices
                logger.info(f"Edge {edge} was removed.")
                return True  # edge was added before, but removed now
            else:
                logger.warning("Edge {} was added after this timestamp.".format(edge))
                return False  # edge was added after this timestamp
        else:
            graph.remove_edges_dict[edge] = timestamp
            graph.vertices_dict[edge[0]].remove(edge[1])  # remove edge from vertices
            graph.vertices_dict[edge[1]].remove(edge[0])  # remove edge from vertices
            logger.info(f"Edge {edge} was removed.")
            return True  # edge was removed

    @staticmethod
    def get_vertices(graph, vertex: int) -> list:
        """
        Get all vertices that are adjacent to a given vertex.
        :param graph to get vertices from.
        :param vertex: vertex to find adjacent vertices of.
        :return: list of adjacent vertices.
        """
        if not GraphOperations.vertex_exists(graph, vertex):
            logger.debug(f"Vertex {vertex} does not exist in the graph.")
            return []  # vertex does not exist, so it cannot have any adjacent vertices
        return graph.vertices_dict[vertex]

    @staticmethod
    def find_path(graph, start: int, end: int, visited: Set[int]) -> list:
        """
        Find a path between two vertices.
        :param graph to find path in.
        :param start: start vertex.
        :param end: end vertex.
        :param visited: set of visited vertices.
        :return: list of vertices in the path.
        """
        if not GraphOperations.vertex_exists(graph, start) or not GraphOperations.vertex_exists(graph, end):
            logger.debug("Start or end vertex does not exist in the graph.")
            return []  # start or end vertex does not exist, so there is no path
        if len(graph.vertices_dict[start]) == 0 or len(graph.vertices_dict[end]) == 0:
            logger.debug("Start or end vertex does not have any adjacent vertices.")
            return []  # start or end vertex does not have any adjacent vertices, so there is no path
        if start == end:
            return [start]  # start and end vertex are the same, so there is a path of length 1

        if start not in graph.vertices_dict or end not in graph.vertices_dict:
            logger.debug("Start or end vertex does not exist in the graph.")
            return []  # start or end vertex does not exist, so there is no path
        for node in graph.vertices_dict[start]:
            if node in visited:
                continue
            if node == end:
                return [start, end]  # start and end vertex are adjacent, so there is a path of length 2
            if node in graph.vertices_dict[end]:
                return [start, node, end]  # start and end vertex are adjacent, so there is a path of length 3
            visited.add(node)
            path = GraphOperations.find_path(graph, node, end, visited)
            if len(path) > 0:
                return [start] + path  # start and end vertex are not adjacent, but there is a path of length > 1
        return []  # start and end vertex are not adjacent, and there is no path

    @staticmethod
    def merge(one: Dict[int, Any], two: Dict[int, Any]) -> Dict[int, Any]:
        """
        Merge two dictionaries.
        :param one: first dictionary.
        :param two: second dictionary.
        :return: merged dictionary.
        """
        for item, timestamp in two.items():
            if item not in one:
                one[item] = timestamp
            else:
                if one[item] < timestamp:
                    one[item] = timestamp
        return one


class Graph:
    """ Graph class. """
    timestamp = float
    vertex = int
    edge = Tuple[vertex, vertex]

    def __init__(self):
        """
        Initialize the graph.
        """
        self.add_vertices_dict: Dict[int, int] = {}
        self.add_edges_dict: Dict[Graph.edge, int] = {}
        self.remove_vertices_dict: Dict[int, int] = {}
        self.remove_edges_dict: Dict[Graph.edge, int] = {}
        self.vertices_dict: Dict[int, List[int]] = {}

        self.op = GraphOperations()

    def vertex_exists(self, v: vertex) -> bool:
        """
        Check if a vertex exists in the graph.
        """
        return self.op.vertex_exists(self, v)

    def edge_exists(self, e: edge) -> bool:
        """
        Check if an edge exists in the graph.
        """
        return self.op.edge_exists(self, e[0], e[1])

    def add_vertex(self, v: vertex, t: timestamp) -> bool:
        """
        Add a vertex to the graph.
        """
        return self.op.add_vertex(self, v, t)

    def remove_vertex(self, v: vertex, t: timestamp) -> bool:
        """
        Remove a vertex from the graph.
        """
        return self.op.remove_vertex(self, v, t)

    def add_edge(self, e: edge, t: timestamp) -> bool:
        """
        Add an edge to the graph.
        """
        return self.op.add_edge(self, e, t)

    def remove_edge(self, e: edge, t: timestamp) -> None:
        """
        Remove an edge from the graph.
        """
        self.op.remove_edge(self, e, t)

    def get_vertices(self, v: vertex) -> List[vertex]:
        """
        Get all vertices connected to a vertex.
        """
        return self.op.get_vertices(self, v)

    def find_path(self, v1: vertex, v2: vertex) -> List[vertex]:
        """
        Find a path between two vertices.
        """
        return self.op.find_path(self, v1, v2, set())

    def merge(self, other_graph):
        """
        Merge with concurrent changes from other graph/replica.
        """
        try:
            self.add_vertices_dict = self.op.merge(self.add_vertices_dict, other_graph.add_vertices_dict)
            self.add_edges_dict = self.op.merge(self.add_edges_dict, other_graph.add_edges_dict)
            self.remove_vertices_dict = self.op.merge(self.remove_vertices_dict, other_graph.remove_vertices_dict)
            self.remove_edges_dict = self.op.merge(self.remove_edges_dict, other_graph.remove_edges_dict)
            self.vertices_dict = self.op.merge(self.vertices_dict, other_graph.vertices_dict)
            logger.debug(
                f"Merged graph: {self.add_vertices_dict}, {self.add_edges_dict}, {self.remove_vertices_dict}, {self.remove_edges_dict}, {self.vertices_dict}")
        except Exception as e:
            logger.error(f"Error merging graph: {e}")
        return self


