import pandas as pd
import networkx as nx
import numpy as np
import json
from time import time
from collections import Counter


def nx_digraph_from_path(name, path):
    """Extract json data from @path and return its (name, nx.DiGraph) tuple"""
    try:
        with open(path) as f:
            js = json.load(f)

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


# def gt_digraph_from_path(path):
#     try:
#         with open(path) as f:
#             js = json.load(f)
#
#             # graph-tool and igraph do not take string nodes; using UniqueIdGenerator
#             #   from igraph to create a mapping of usernames to unique integers
#             id_map = UniqueIdGenerator()
#             data_dict = dict()
#             for j in js:
#                 data_dict.update(j)
#
#             edges = {(id_map[x], id_map[y]) for x in data_dict for y in
#                      data_dict[x]}
#             # Get dictionary of {node id: node name}
#             id_map = id_map.reverse_dict()
#
#             g = Graph(directed=True)
#             g.add_edge_list(edges)
#
#             return g
#
#     except ValueError as je:
#         print(je)
#         return None


def node_mean_cosine_similarity(graph, out=False):
    """
    Get a dataframe of mean in/out cosine similarities for each node of a
      directed graph
    :param graph: nx.DiGraph
    :param out: whether to get the out cosine similarity
    """
    adj = nx.adjacency_matrix(graph)
    # dot multiplication depends on whether to get common in- or out-nodes
    common_neighbors = (adj.dot(adj.T) if out else adj.T.dot(adj)).toarray()

    deg = list(
        dict(graph.out_degree() if out else graph.in_degree()).values()
    )
    deg = np.reshape(deg, (-1, 1))  # Is initially of shape [n, 0]
    geometric_distance = np.sqrt(deg.dot(deg.reshape(1, -1)))

    # @out specifies array on which to map the division
    # @where is a boolean array indexing where to apply output of division
    s = np.divide(common_neighbors,
                  geometric_distance,
                  out=np.zeros(common_neighbors.shape),
                  where=(geometric_distance != 0.0)
                  )
    np.fill_diagonal(s, 0)

    return pd.DataFrame(s, index=graph.nodes(), columns=graph.nodes()).mean()


def graph_mean_cosine_similarity(graphs, out=False):
    """Get the mean cosine similarity for each graph in graphs; graphs must be
    a dictionary of {graph name: networkx.DiGraph} pairs"""
    mean_csim = {n: node_mean_cosine_similarity(g, out).mean() for n,g in graphs.items()}
    return pd.Series(mean_csim, name='mean_cos_sim')


def z_normalize(network_params, sort_by, exclude=None):
    """
    Z-score normalize numeric values in dataframe
    :param network_params: DataFrame
    :param sort_by: features to sort the normalized dataframe by
    :param exclude: columns to exclude from normalizing
    :return: DataFrame
    """
    if exclude is None:
        exclude = set()

    # Non-numeric columns have dtype of 'object' -> 'O'; apply normalization
    #   to numeric columns, not labeled for exclusion
    of_interest = lambda x: (x.dtype != 'O') and (x.name not in exclude)

    normd = network_params.apply(
        lambda x: (x - x.mean())/x.std() if of_interest(x) else x,
        axis=0
    ).sort_values(by=sort_by, axis=0, ascending=False)

    return normd


def get_graph_nodes_edges(graphs):
    """
    Get amount of nodes and edges from dictionary of {graph_name: networkx_Graph}
    """
    nodes_edges = {n: (nx.number_of_nodes(g), nx.number_of_edges(g)) for n,g in graphs.items()}
    return pd.DataFrame.from_dict(nodes_edges, orient='index', columns=['nodes', 'edges'])


def get_graph_density(graphs, round_decimal=6):
    """
    Return a series of graph_name: density values
    :param graphs: dictionary of {subreddit: networkx Graph} values
    :param round_decimal: decimal to round density to
    :return: pandas.Series
    """
    density = {n: np.round(nx.density(g), round_decimal) for n,g in graphs.items()}
    return pd.Series(density, name='density')


def get_subset_strongly_conn_components(graphs, largest=False):
    """
    Get strongly-connected components of a group of subreddit networks
    :param graphs: {subreddit: networkx graph} dictionary
    :param largest: if True return only largest strongly-connected component
    :return: dict of {subreddit: [strongly-connected components]
      OR set(largest strongly-connected component)}
    """
    comps = {n: list(sorted(nx.strongly_connected_components(g), key=len, reverse=True))
             for n,g in graphs.items()}

    return comps if not largest else {n: g[0] for n, g in comps.items()}


def get_graph_amt_nodes_largest_strong_comp(strongest_comps, node_count):
    """
    Get amount and percent of nodes in largest strongly-connected component
    :param strongest_comps: dictionary of {subreddit: nx.DiGraph} pairs
    :param node_count: dictionary of {subreddit: node count} pairs
    :return: DataFrame of {subreddit: (nodes in largest strongly-connected
      component, percent of nodes in largest strongly-connected component)}
    """
    count_strongest = {n: len(c) for n,c in strongest_comps.items()}
    pct_strongest = {n: count_strongest[n]/node_count[n] for n in strongest_comps.keys()}

    return pd.concat(
        [pd.Series(count_strongest, name='nodes_largest_strong_comp'),
         pd.Series(pct_strongest, name='pct_nodes_largest_strong_comp')],
        axis=1)


def graph_strongest_vs_not_assortativity(graphs):
    group_nodes = {n: set(g.nodes()) for n, g in graphs.items()}
    group_strongest = get_subset_strongly_conn_components(graphs, True)
    group_outsiders = {
        sr: nodes.difference(group_strongest[sr]) for sr, nodes in
        group_nodes.items()
    }

    modularities = {
        n: nx.algorithms.community.quality.modularity(
            g, [group_strongest[n], group_outsiders[n]]) for n, g in graphs.items()
    }
    return pd.Series(modularities, name='modularity')


def get_digraph_deg_distrib(graphs):
    """
    Get in and out degree distributions of networkx DiGraphs
    :param graphs: dictionary of {graph_name: networkx_Graph}
    :return: dictionary of {graph_name: dict_in_distrib, dict_out_distrib}
    """
    distribs = dict()
    for name, graph in graphs.items():
        distribs[name]['in'] = [d[1] for d in graph.in_degree()]
        distribs[name]['out'] = [d[1] for d in graph.out_degree()]

    return distribs


def get_graph_amt_nodes_deg_one(graphs, node_count):
    """
    Get amount of degree-one nodes and percentage of degree-one nodes
    """
    degrees = {n: nx.degree(g) for n, g in graphs.items()}

    # Counting amount of lowest degree nodes (1 in this case)
    singles = Counter()
    for sr, degs in degrees.items():
        for user, deg in degs:
            if deg == 1:
                singles[sr] += 1

    pct_singles = {n: singles[n]/node_count[n] for n in node_count.keys()}

    return pd.concat([pd.Series(singles, name='nodes_deg_one'),
                   pd.Series(pct_singles, name='pct_nodes_deg_one')],
                  axis=1)


def get_pagerank_max_avg(graphs):
    """
    Return a DataFrame of (PageRank max value, PageRank average value) for the network
    """
    pagerankings = {n: nx.pagerank(g) for n,g in graphs.items()}

    max_avg = {n: (max(r.values()), np.average(list(r.values())))
              for n,r in pagerankings.items()}

    return pd.DataFrame.from_dict(max_avg, orient='index', columns=['pagerank_max', 'pagerank_avg'])


def get_graph_reciprocity(graphs):
    recip = {n: nx.reciprocity(g) for n,g in graphs.items()}
    return pd.Series(recip, name='reciprocity')


def get_graph_base_stats(graphs, cos_sim_out=False):
    strongest_comps = get_subset_strongly_conn_components(graphs, True)

    nodes_edges = get_graph_nodes_edges(graphs)
    density = get_graph_density(graphs)
    num_pct_strongest = get_graph_amt_nodes_largest_strong_comp(strongest_comps, nodes_edges['nodes'])
    num_pct_deg_one = get_graph_amt_nodes_deg_one(graphs, nodes_edges['nodes'])
    pagerank_max_avg = get_pagerank_max_avg(graphs)
    recip = get_graph_reciprocity(graphs)
    similarity = graph_mean_cosine_similarity(graphs, cos_sim_out)
    modularity = graph_strongest_vs_not_assortativity(graphs)

    return pd.concat(
        [nodes_edges, density, num_pct_strongest, num_pct_deg_one,
         pagerank_max_avg, recip, similarity, modularity],
        axis=1)


def get_strong_comp_distrib(graphs):
    """
    Return the distribution of the nodes amongst strongly-connected components
    """
    strong_comps = get_subset_strongly_conn_components(graphs)

    # Keep track of amount of nodes by size of strongly-connected components
    strong_comp_distrib = {n: Counter() for n in strong_comps.keys()}
    for sr, comps in strong_comps.items():
        for comp in comps:
            comp_size = len(comp) # size of component
            strong_comp_distrib[sr][comp_size] += 1 # increment count

    return strong_comp_distrib


def get_p_value(params, samples, field):
    p_vals = dict()

    for sr, stat in samples.items():
        portion_lt = params.loc[sr, field] > np.array(stat)
        portion_gt = params.loc[sr, field] < np.array(stat)

        # Use the smallest of the portion values as we're looking for min p-value
        portion = min(sum(portion_lt), sum(portion_gt))

        # 1000 was the size of the resamples -- shouldn't be hardcoded but done for sake of time
        p_vals[sr] = portion/1000

    return p_vals



# def cosine_similarity_alt(graph, out=False):
#     """
#     TODO: GIVES INACCURATE MEASUREMENTS!
#       Removing nodes with in/out degree 0 => removing out/in edges that do
#       come from/to them, meaning that similarity measures of other nodes are also
#       affected. Instead of creating a new graph with those nodes removed,
#       specifically give a similarity score of 0 to the appropriate nodes without
#       modifying the graph structure itself.
#
#     Alternative calculation of cosine similarity, returning dataframe of nodes
#       with non-zero similarity values. Should be faster since there is a condition
#       check for zero degree before computing the adjacency dot product.
#     """
#     # dropping nodes of degree 0 but passed graph is mutable so need a deepcopy
#     g = graph.copy()
#     deg_zero = [n for n,d in g.out_degree() if d == 0] if out \
#         else [n for n,d in g.in_degree() if d == 0]
#     g.remove_nodes_from(deg_zero)
#
#     print(f'Dropping nodes: {deg_zero}')
#
#     adj = nx.adjacency_matrix(g).toarray()
#     # dot multiplication depends on whether to get common in- or out-nodes
#     common_neighbors = adj.dot(adj.T) if out else adj.T.dot(adj)
#
#     deg = list(dict(g.out_degree() if out else g.in_degree()).values())
#     deg = np.reshape(deg, (-1, 1)) # Is initially of shape [n, 0]
#     geometric_distance = np.sqrt(deg.dot(deg.reshape(1, -1)))
#
#     s = np.nan_to_num(np.divide(common_neighbors, geometric_distance))
#     np.fill_diagonal(s, 0.0)
#
#     df = pd.DataFrame(0.0, index=graph.nodes(), columns=graph.nodes())
#     df.update(pd.DataFrame(s, index=g.nodes(), columns=g.nodes()))
#
#     return df