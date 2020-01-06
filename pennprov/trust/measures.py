'''
 Copyright 2019 Trustees of the University of Pennsylvania
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
'''

from typing import Set, Callable, Dict, List, Any
from pennprov.trust.typehandlers import SetItem


def majority_vote(votes: Dict[int, Set[SetItem]]) -> Dict[int,bool]:
    # type: (Dict[int, Set[SetItem]]) -> Dict[int,bool]
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


def unanimous_vote(votes):
    # type: (Dict[int, Set[SetItem]]) -> Dict[int,bool]
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


def precision_vs_gold(choice, gold):
    # type: (Set[SetItem], Set[SetItem]) -> float
    tp = 0

    for item in choice:
        if item in gold:
            tp = tp + 1
    return float(tp) / len(choice)


def recall_vs_gold(choice, gold):
    # type: (Set[SetItem], Set[SetItem]) -> float
    tp = 0

    for item in gold:
        if item in choice:
            tp = tp + 1
    return float(tp) / len(gold)


def jaccard(a, b):
    # type: (Set[SetItem], Set[SetItem]) -> float
    return float(len(a.intersection(b))) / len(a.union(b))


