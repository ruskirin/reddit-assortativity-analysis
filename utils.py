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


# A poor attempt at a recursive function -- been a while, so forgot that it
#   doesn't go well with loops
#
# def see_iter(iterable, sample=False, pr=True, depth=0, limit=-1, size=0):
#     """
#     Recursive function that iterates through an iterable and prints information
#       about its content. Returns the total children.
#     :param iterable: the iterable
#     :param size: current size of the iterable
#     :param depth: current "generation" into the iterable
#     :param limit: the last depth to examine
#       (def: -1 -> until no non-str iterables met)
#     :param sample: print samples of the iterables
#     :param pr: whether to print details about iterable
#     :return: cumulative size "lowest level" children
#     """
#     if isinstance(iterable, str):
#         return size
#
#     if size == 0:
#         size = len(iterable)
#
#     if (limit != -1) and (depth > limit):
#         # print(f'Reached desired depth')
#         return size
#
#     try:
#         print_iter_metrics(iterable, depth, sample, pr)
#
#         if isinstance(iterable, dict):
#             for k, v in iterable.items():
#                 see_iter(v, sample, pr, depth + 1, limit, size)
#
#         elif isinstance(iterable, list):
#             iterable = iter(iterable)
#             while True:
#                 see_iter(next(iterable), sample, pr, depth + 1, limit, size)
#
#         return size
#
#     except TypeError as te:
#         return size
#
#     except StopIteration as si:
#         print(si.args)
#         return size