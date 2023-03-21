import json
import pytest
from pathlib import Path
import grouping
import os


@pytest.fixture
def sample_actual_info() -> tuple[dict, dict, dict]:
    """Get a verified false and true sample of grouped subreddits"""
    path = Path('tests/samples')

    if not path.exists():
        print(f'Current path is: {os.getcwd()}')
        raise NotADirectoryError

    with open(path/'subreddits_grouped_false.json', 'r') as f:
        sample = json.load(f)
    with open(path/'subreddits_grouped_true.json', 'r') as f:
        actual = json.load(f)
    with open(path/'subreddits_grouped_info.json', 'r') as f:
        info = json.load(f)

    return sample, actual, info


def test_get_missing(sample_actual_info):
    sample, actual, info = sample_actual_info
    orig = grouping.get_grouped_subreddits(actual)

    miss, changed = grouping.get_missing(orig, sample)
    print(miss)
    print(changed)

    assert miss == set(info['missing'])


def test_get_added(sample_actual_info):
    sample, actual, info = sample_actual_info
    orig = grouping.get_grouped_subreddits(actual)

    add, changed = grouping.get_added(orig, sample)
    print(add)
    print(changed)

    assert add == set(info['added'])


def test_missing_added_changed(sample_actual_info):
    sample, actual, info = sample_actual_info

    miss, add, change = grouping.get_missing_added_changed(
        set(actual.keys()), sample
    )

    assert (miss == info['missing']) and (add == info['added']) and (change == info['possible'])


# if __name__ == '__main__':
#     import sys
#     print(sys.path)