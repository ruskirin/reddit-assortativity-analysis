from pathlib import Path
import json


PATH_DATA = Path('data')
PATH_NET = PATH_DATA/'chain-networks'
PATH_GROUPS = PATH_DATA/'subreddits_grouped.json'


def get_network_paths_grouped() -> dict:
    groups = get_groups()
    paths = get_network_paths()
    ns = dict()

    for g, subreddits in groups.items():
        srs = set()
        for sr in subreddits:
            srs.add((sr, paths[sr]))

        ns[g] = srs

    return ns


def get_network_paths() -> dict:
    """Get a dict of {subreddit: subreddit network path} pairs"""
    sr = {p.stem: p for p in PATH_NET.iterdir()}
    return sr


def get_groups() -> dict:
    """Get the json file with dict of subreddit groupings"""
    with open(PATH_GROUPS, 'r') as f:
        groups = json.load(f)

    return groups


