import networkx as nx
from json import load


def digraph_from_path(name, path):
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