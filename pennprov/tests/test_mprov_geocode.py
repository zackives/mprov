######################
## mProv Copyright (C) 2017-22 by Trustees of the University of Pennsylvania
## All Rights Reserved.
## 
##
# ## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
######################

import pandas as pd
import numpy as np
import geopy

import pennprov.connection.mprov as mprov
from pennprov.metadata.stream_metadata import BasicSchema, BasicTuple
from datetime import datetime, timezone
from geopy.geocoders import Nominatim
from datetime import datetime

class TestMProv2:
    conn = None

    def __init__(self):
        self.conn = mprov.MProvConnection()
        assert self.conn is not None

        self.conn.create_or_reset_graph()
        self.locator = Nominatim(user_agent='myGeocoder')

    def create_raw(self):
        data = pd.read_csv('sample_data/california_housing_test.csv')

        data = data[data['housing_median_age'] < 5]

        # Let's rework this so (lat, long) is a key...
        data['loc'] = data.apply(lambda x: str('(' + str(x['longitude']) +',' + str(x['latitude']) + ')'), axis=1)

        self.tuple_uuids = self.conn.store_df_rows_with_provenance('source', data, 'loc')

        self.conn.store_annotations(self.tuple_uuids['(-116.95,33.86)'], {'annotation': 3})
        self.conn.flush()

        return data
        
    def geo_lookup(self, row, dest_name):
        coordinates = str(row.loc['latitude']) + ',' + str(row.loc['longitude'])
        location = self.locator.reverse(coordinates)
        row2 = row.copy()
        row2['geo'] = str(location)
        self.conn.set_relation_key('geo_lookup', 'geo')

        derivation = self.conn.record_provenance('source', row, 'geo_lookup', dest_name, row2)
        self.conn.store_annotations(derivation, {'geocoder': 'myGeocoder'})
        return location

def test_prov():
    work = TestMProv2()
    data = work.create_raw()
    data2 = data.apply(lambda x: TestMProv2.geo_lookup(work, x, 'geo_lookup'), axis=1)

