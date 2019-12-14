from typing import Set, Callable, Dict, List, Any
from pennprov.trust.typehandlers import SetItem


def majority_vote(votes: Dict[int, Set[SetItem]]) -> Dict[int,bool]:
    """
    Given a dictionary of agent -> votes, figure out
    for each set item whether the majority vote positively or
    not
    """
    votes = {}

    for item_set in votes.values():
        for item in item_set:
            if item.get_id() in votes:
                votes[item.get_id()] = votes[item.get_id()] + 1
            else:
                votes[item.get_id()] = 1

    threshold = len(votes) / 2
    return [x >= threshold for x in votes]


def unanimous_vote(votes: Dict[int, Set[SetItem]]) -> Dict[int,bool]:
    """
    Given a dictionary of agent -> votes, figure out
    for each set item whether all vote positively
    """
    votes = {}

    for item_set in votes.values():
        for item in item_set:
            if item.get_id() in votes:
                votes[item.get_id()] = votes[item.get_id()] + 1
            else:
                votes[item.get_id()] = 1

    threshold = len(votes)
    return [x >= threshold for x in votes]


def precision_vs_gold(choice: Set[SetItem], gold: Set[SetItem]) -> float:
    tp = 0

    for item in choice:
        if item in gold:
            tp = tp + 1
    return float(tp) / len(choice)


def recall_vs_gold(choice: Set[SetItem], gold: Set[SetItem]) -> float:
    tp = 0

    for item in gold:
        if item in choice:
            tp = tp + 1
    return float(tp) / len(gold)


def jaccard(a: Set[SetItem], b: Set[SetItem]) -> float:
    return float(a.intersection(b)) / a.union(b)


