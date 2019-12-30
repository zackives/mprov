"""
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
"""

from typing import Set, Dict, List, Tuple
from types import SimpleNamespace
from pennprov.trust.typehandlers import SetItem
from pennprov.trust.fast_dawid_skene import algorithms


class GetAgentTrust:
    item_to_agent = lambda x: x['agent']

    def get_trust(self, discrete_items, gold_standard = None):
        # type: (Dict[int, Set[SetItem], int]) -> Tuple[List,List]
        return []


class CoreTrust(GetAgentTrust):
    """
    Trust model, core algorithm
    """

    def get_trust_core(self, discrete_items, arg, gold_standard = None):
        # type: (Dict[int, str, Set[SetItem], int]) -> Tuple[List,List]

        responses = {}
        for agent in discrete_items.keys():
            for set_item in discrete_items[agent]:
                if set_item.get_id() not in responses.keys():
                    responses[set_item.get_id()] = {}
                responses[set_item.get_id()][agent] = [True]
        for item in responses.keys():
            for agent in discrete_items.keys():
                if agent not in responses[item]:
                    responses[item][agent] = [False]

        d = {'algorithm': arg, 'verbose': 'False'}
        args = SimpleNamespace(**d)
        print (responses)
        results = algorithms.run(responses, args)

        questions = responses.keys()
        questions = sorted(questions)
        trusted = [questions[i] for i,v in enumerate(results) if v]
        untrusted = [questions[i] for i,v in enumerate(results) if not v]
        return (trusted, untrusted)


class FastDawidSkeneTrust(CoreTrust):
    def get_trust(self, discrete_items, gold_standard = None):
        # type: (Dict[int, str, Set[SetItem], int]) -> Tuple[List,List]
        return super().get_trust_core(discrete_items, 'FDS', gold_standard)


class DawidSkeneTrust(CoreTrust):
    def get_trust(self, discrete_items, gold_standard = None):
        # type: (Dict[int, str, Set[SetItem], int]) -> Tuple[List,List]
        return super().get_trust_core(discrete_items, 'DS', gold_standard)


class MajorityVoteTrust(CoreTrust):
    def get_trust(self, discrete_items, gold_standard = None):
        # type: (Dict[int, str, Set[SetItem], int]) -> Tuple[List,List]
        return super().get_trust_core(discrete_items, 'MV', gold_standard)


class HybridDawidSkeneTrust(CoreTrust):
    def get_trust(self, discrete_items, gold_standard = None):
        # type: (Dict[int, str, Set[SetItem], int]) -> Tuple[List,List]
        return super().get_trust_core(discrete_items, 'H', gold_standard)