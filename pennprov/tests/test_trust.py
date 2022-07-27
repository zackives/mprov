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

from __future__ import print_function

import unittest

from pennprov.trust.trust import HybridDawidSkeneTrust
from pennprov.trust.typehandlers import SetItem, TimeSeriesToSet
from pennprov.trust.measures import *
from pennprov.trust.trust import *

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
    time_series_3 = [
        {'start': 1001, 'end': 1005, 'value': 'Sz'},
        {'start': 2003, 'end': 4004, 'value': 'Sz'}
    ]
    time_series_gold = [
        {'start': 1001, 'end': 1005, 'value': 'Sz'},
        {'start': 3001, 'end': 3005, 'value': 'Sz'},
    ]
    votes = {0: time_series_1, 1: time_series_2, 2: time_series_3}

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

    def test_time_series_scores(self):
        print('Testing time series similarity measures')
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

        # TS2 should have better precision because of fewer samples
        self.assertGreater(precision_vs_gold(ts_set_2, ts_set_g), precision_vs_gold(ts_set, ts_set_g))
        self.assertGreater(jaccard(ts_set_2, ts_set_g), jaccard(ts_set, ts_set_g))
        self.assertEqual(recall_vs_gold(ts_set_2, ts_set_g), recall_vs_gold(ts_set, ts_set_g))

        return True

    def test_time_series_fds_trust(self):
        fdst = FastDawidSkeneTrust()
        return self.algo(fdst)

    def test_time_series_ds_trust(self):
        fdst = DawidSkeneTrust()
        return self.algo(fdst)

    def test_time_series_mv_trust(self):
        fdst = MajorityVoteTrust()
        return self.algo(fdst)

    def test_time_series_h_trust(self):
        fdst = HybridDawidSkeneTrust()
        return self.algo(fdst)

    def algo(self,fdst):
        print ('** Trust algorithm: %s **'%fdst)
        conv = TimeSeriesToSet(1, lambda x: x['start'],
                               lambda x: x['end'])

        votes_enumerated = {}
        for i in self.votes.keys():
            v = self.votes[i]

            votes_enumerated[i] = conv.get_set(v)
        print (votes_enumerated)
        trusted, untrusted = fdst.get_trust(votes_enumerated)

        print ('Trusted:', trusted)
        print ('Untrusted:', untrusted)

        for i in votes_enumerated:
            print ('>> Trustworthiness by f-measure of Agent %d = %f' %(i,AgentTrust.get_agent_f1(votes_enumerated[i], \
                                                                                                  trusted)))

        return True


if __name__ == '__main__':
    unittest.main()
