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

    with open(path/'subreddits-grouped-false.json', 'r') as f:
        sample = json.load(f)
    with open(path/'subreddits-grouped-true.json', 'r') as f:
        actual = json.load(f)
    with open(path/'subreddits-grouped-info.json', 'r') as f:
        info = json.load(f)

    # JSON can only save lists; convert to set for testing
    info['missing'] = set(info['missing'])
    info['added'] = set(info['added'])
    info['possible'] = {k: set(v) for k,v in info['possible'].items()}

    return sample, actual, info


def test_correct_subreddits_spelling(sample_actual_info):
    sample, actual, info = sample_actual_info

    orig = grouping.get_grouped_subreddits(actual)
    miss, add, change = grouping.get_missing_added_changed(orig, sample)

    actual_corr = grouping.remove_subreddits(actual, add)
    corrected = grouping.remove_subreddits(sample, add)
    corrected = grouping.correct_subreddits_spelling(corrected, change)

    corrected = {g: set(sr) for g, sr in corrected.items()}
    actual_corr = {g: set(sr) for g, sr in actual_corr.items()}

    assert corrected == actual_corr


def test_get_missing_added_changed(sample_actual_info):
    sample, actual, info = sample_actual_info
    orig = grouping.get_grouped_subreddits(actual)

    miss, add, changed = grouping.get_missing_added_changed(orig, sample)

    # print(f'Actual:'
    #       f'\nMissing: {info["missing"]}'
    #       f'\nAdded: {info["added"]}'
    #       f'\nChanged: {info["possible"]}')

    assert (miss == info['missing']) \
           and (add == info['added']) \
           and (changed == info['possible'])


def test_get_changed(sample_actual_info):
    sample, actual, info = sample_actual_info

    orig = grouping.get_grouped_subreddits(actual)
    proc = grouping.get_grouped_subreddits(sample)

    miss, false_miss = grouping.get_missing(orig, proc)
    add, false_add = grouping.get_added(orig, proc)
    changed = grouping.get_changed(orig, false_miss, false_add)

    assert changed == info['possible']


def test_get_missing(sample_actual_info):
    sample, actual, info = sample_actual_info
    orig = grouping.get_grouped_subreddits(actual)
    proc = grouping.get_grouped_subreddits(sample)

    miss, changed = grouping.get_missing(orig, proc)
    print(f'\nMissing: {miss}')
    print(f'Changed: {changed}')

    assert miss == set(info['missing'])


def test_get_added(sample_actual_info):
    sample, actual, info = sample_actual_info
    orig = grouping.get_grouped_subreddits(actual)
    proc = grouping.get_grouped_subreddits(sample)

    add, changed = grouping.get_added(orig, proc)
    print(f'\nAdded: {add}')
    print(f'Changed: {changed}')

    assert add == set(info['added'])


# if __name__ == '__main__':
#     import sys
#     print(sys.path)