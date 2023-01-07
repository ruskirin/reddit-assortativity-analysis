import networkx as nx
from pandas import concat, Series
from json import load
from collections import Counter


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


def print_iter_metrics(iterable, sample=False, pr=True):
    if isinstance(iterable, str):
        return

    if pr:
        # if level == 0:
        #     print(f'\n*** Level: {level}')
        print(f'Iterable type: {type(iterable)}, length: {len(iterable)}')

    if not (sample and pr):
        return

    print('Sample:')
    if isinstance(iterable, list):
        print(iterable[:5])
    elif isinstance(iterable, dict):
        print(list(iterable.items())[:4])


def get_strongly_conn_comps(graphs, largest=False):
    """
    Get strongly-connected components of a group of subreddit networks
    :param graphs: {subreddit: networkx graph} dictionary
    :param largest: if True return only largest strongly-connected component
    :return: dict of {subreddit: [strongly-connected components]
      OR largest strongly-connected component}
    """
    comps = {n: [sorted(nx.strongly_connected_components(g), key=len, reverse=True)]
             for n,g in graphs.items()}

    return comps if not largest else {n: g[0] for n, g in comps.items()}


def get_strong_comp_distrib(graphs):
    """
    Return the distribution of the nodes amongst strongly-connected components
    """
    strong_comps = get_strongly_conn_comps(graphs)

    # Keep track of amount of nodes by size of strongly-connected components
    strong_comp_distrib = {n: Counter() for n in strong_comps.keys()}
    for sr, comps in strong_comps.items():
        for comp in comps:
            comp_size = len(comp) # size of component
            strong_comp_distrib[sr][comp_size] += 1 # increment count

    return strong_comp_distrib


def count_strongest_comp(strongest_comps, node_count):
    """
    Return either number or percent of nodes inside the strongly-connected component with the most memebers

    :param strongest_comps: dictionary of {subreddit: nx.DiGraph} pairs
    :param node_count: dictionary of {subreddit: node count} pairs
    :return: DataFrame of {subreddit: (nodes in largest strongly-connected component
      , percent of nodes in largest strongly-connected component)}
    """
    count_strongest = {n: len(c) for n,c in strongest_comps.items()}
    pct_strongest = {n: count_strongest[n]/node_count[n] for n in strongest_comps.keys()}

    return concat([Series(count_strongest, name='nodes_largest_strong_comp'),
                   Series(pct_strongest, name='pct_nodes_largest_strong_comp')],
                  axis=1)


def count_deg_one_nodes(graphs, node_count, pct=True):
    """
    Return amount (or percentage of total) of nodes with in-degree + out-degree of 1
    """
    degrees = {n: nx.degree(g) for n, g in graphs.items()}

    # Counting amount of lowest degree nodes (1 in this case)
    singles = Counter()
    for sr, degs in degrees.items():
        for user, deg in degs:
            if deg == 1:
                singles[sr] += 1

    if pct:
        pct_singles = dict()
        for sr, count in node_count.items():
            pct_singles[sr] = singles[sr]/node_count[sr]

        return pct_singles

    return singles


def get_pagerank_max_avg(graphs):
    """
    Return a tuple of (PageRank max value, PageRank average value) for the network
    """
    pagerankings = {n: nx.pagerank(g) for n,g in graphs.items()}

    pr_max = {n: max(r.values()) for n,r in pagerankings.items()}
    pr_avg = {n: np.average(list(r.values())) for n,r in pagerankings.items()}

    return pr_max, pr_avg


def get_p_value(params, samples, field):
    p_vals = dict()

    for sr, stat in samples.items():
        portion_lt = params.loc[sr, field] > np.array(stat)
        portion_gt = params.loc[sr, field] < np.array(stat)

        # Use the smaller of the portion values as we're looking for min p-value
        portion = min(sum(portion_lt), sum(portion_gt))

        # 1000 was the size of the resamples -- shouldn't be hardcoded but done for sake of time
        p_vals[sr] = portion/1000

    return p_vals