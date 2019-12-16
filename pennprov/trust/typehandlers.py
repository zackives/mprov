from typing import Set, Callable, Dict, List, Any


class SetItem:
    """
    Basic abstraction for a discrete item in a data range.
    This could be a sample in a time series, a string value,
    etc.
    """
    # The item, for purposes of ID and comparison
    item = None
    # The original data value from which this was
    # extracted
    original = None

    def __init__(self, item, orig):
        self.item = item
        self.original = orig

    def __str__(self):
        return str(self.item)

    def __repr__(self):
        return str(self.item)

    def get_id(self) -> int:
        if self.item:
            return hash(self.item)
        else:
            return 0

    def get_item(self):
        return self.item

    def get_original(self) -> Any:
        return self.original

    def __eq__(self, other):
        if isinstance(other,SetItem):
            return self.get_id() == other.get_id()
        else:
            return self.get_id() == other

    def __hash__(self):
        return hash(self.get_id())


class DomainToSet:
    """
    Base class:
    Convert from a given domain to a set of discrete values
    that we can reason about
    """
    def get_set(self, items):
        # type: (List) -> Set[SetItem]
        """
        Takes the set of items representing composite data,
        and returns a list of discrete and comparable items
        :param items:
        :return: Set of discrete items (eg with int IDs)
                 and a Dict from the items back to the originals
        """
        return set([])


class TimeSeriesToSet(DomainToSet):
    """
    Converts time down to a series of discrete ticks,
    based on sample_rate; creates a set item for each sample
    """
    tstart = lambda x: x['start']
    tend = lambda x: x['end']
    sample_rate = 1

    def __init__(self, sample_rate, tstart_getter = None, tend_getter = None):
        # type: (int, Callable, Callable)
        if tstart_getter:
            self.tstart = tstart_getter
        if tend_getter:
            self.tend = tend_getter
        self.sample_rate = sample_rate

    def get_set(self, items):
        # type: (List) -> Set[SetItem]
        ret = set([])

        for item in items:
            for tick in range(self.tstart(item), self.tend(item), self.sample_rate):
                ret.add(SetItem(tick, item))
        return ret


class DiscreteItemToSet(DomainToSet):
    """
    Converts a list of discrete items (strings, ints, etc)
    into a set of SetItems
    """

    def get_set(self, items):
        # type: (List) -> Set[SetItem]
        ret = set([])

        for item in items:
            ret.add(SetItem(item, item))
        return ret


# TODO: Explore other options, eg rectangle or polygon to set?
