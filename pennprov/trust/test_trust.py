import unittest
from pennprov.trust.typehandlers import SetItem, TimeSeriesToSet
from pennprov.trust.measures import *

class TimeSeriesTestCase(unittest.TestCase):
    time_series_1 = [
        {'start': 1001, 'end': 1005, 'value': 'Sz'},
        {'start': 4001, 'end': 4004, 'value': 'hfo'},
        {'start': 4005, 'end': 4008, 'value': 'Sz'},
    ]
    time_series_2 = [
        {'start': 1001, 'end': 1005, 'value': 'Sz'},
        {'start': 2001, 'end': 2003, 'value': 'hfo'},
        {'start': 4005, 'end': 4008, 'value': 'Sz'},
    ]
    time_series_gold = [
        {'start': 1001, 'end': 1005, 'value': 'Sz'},
        {'start': 3001, 'end': 3005, 'value': 'Sz'},
    ]
    votes = {0: time_series_1, 1: time_series_2}

    def test_ts_conversion(self):
        print('Testing time series conversion to set')
        conv = TimeSeriesToSet(1, lambda x: x['start'],
                               lambda x: x['end'])

        print ('Sample rate: %d'%conv.sample_rate)
        ts_set = conv.get_set(self.time_series_1)

        print ('Expanded set: ')
        print(list(ts_set))
        self.assertTrue(4001 in ts_set)
        self.assertTrue(4003 in ts_set)
        self.assertTrue(1001 in ts_set)
        return True

    def test_ts_jaccard(self):
        conv = TimeSeriesToSet(1, lambda x: x['start'],
                               lambda x: x['end'])
        ts_set = conv.get_set(self.time_series_1)
        ts_set_2 = conv.get_set(self.time_series_2)

        print ('Jaccard: %f'%jaccard(ts_set, ts_set_2))

        return True

    def test_ts_pr(self):
        conv = TimeSeriesToSet(1, lambda x: x['start'],
                               lambda x: x['end'])
        ts_set = conv.get_set(self.time_series_1)
        ts_set_2 = conv.get_set(self.time_series_2)
        ts_set_g = conv.get_set(self.time_series_gold)

        print ('Jaccard 1 vs gold: %f'%jaccard(ts_set, ts_set_g))
        print ('Precision 1 vs gold: %f'%precision_vs_gold(ts_set, ts_set_g))
        print ('Recall 1 vs gold: %f'%recall_vs_gold(ts_set, ts_set_g))
        print ('Jaccard 2 vs gold: %f'%jaccard(ts_set_2, ts_set_g))
        print ('Precision 2 vs gold: %f'%precision_vs_gold(ts_set_2, ts_set_g))
        print ('Recall 2 vs gold: %f'%recall_vs_gold(ts_set_2, ts_set_g))

        return True


if __name__ == '__main__':
    unittest.main()
