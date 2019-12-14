from typing import Set, Callable, Dict, List, Any
from pennprov.trust.typehandlers import SetItem


class GetAgentTrust:
    item_to_agent = lambda x: x['agent']

    def get_trust(self, discrete_items: Set[SetItem], \
                  discrete_to_orig: Dict) -> List[float]:
        return []


class VoteBasedTrust(GetAgentTrust):
    """
    Trust model based on simple votes
    """
