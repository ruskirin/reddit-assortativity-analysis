import networkx as nx
from igraph.datatypes import UniqueIdGenerator
from graph_tool import Graph
from json import load


def nx_digraph_from_path(name, path):
    """Extract json data from @path and return its (name, nx.DiGraph) tuple"""
    try:
        with open(path) as f:
            js = load(f)

            # Merge the dictionaries representing a single subreddit
            data_dict = dict()
            for j in js:
                data_dict.update(j)

            graph = nx.DiGraph(data_dict)
            return name, graph
    except nx.NetworkXError as ne:
        print(ne)
        return None

    except ValueError as je:
        print(je)
        return None


def gt_digraph_from_path(path):
    try:
        with open(path) as f:
            js = load(f)

            # graph-tool and igraph do not take string nodes; using UniqueIdGenerator
            #   from igraph to create a mapping of usernames to unique integers
            id_map = UniqueIdGenerator()
            data_dict = dict()
            for j in js:
                data_dict.update(j)

            edges = {(id_map[x], id_map[y]) for x in data_dict for y in
                     data_dict[x]}
            # Get dictionary of {node id: node name}
            id_map = id_map.reverse_dict()

            g = Graph(directed=True)
            g.add_edge_list(edges)

            return g

    except ValueError as je:
        print(je)
        return None