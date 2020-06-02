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

class BasicSchema:
    count = 0
    fields = []
    types = []

    def __init__(self, *args):
        if len(args) == 1:
            self.init1(args[0])
        elif len(args) == 2:
            self.init2(args[0], args[1])
        elif len(args) == 3:
            self.init3(args[0], args[1], args[2])
        else:
            raise TypeError('Illegal inputs')

    def init1(self, name):
        # type: (str) -> None
        self.name = name
        self.fields = []
        self.types = []

    def init2(self, name, fields_types):
        # type: (str, dict) -> None
        """ Initialize with a name and a dictionary of attributes to types """
        self.name = name
        self.fields = []
        self.types = []
        for k in fields_types.keys():
            self.fields.append(k)
            self.types.append(fields_types[k])

    def init3(self, name, fields, types):
        # type: (str, list, list) -> None
        """ Initialize with a name and a list of field-type pairs """
        self.name = name
        self.fields = fields
        self.types = types

    def add_field(self, k, v):
        # type: (str, Any) -> None
        self.fields.append(k)
        self.types.append(v)

    def get_field(self, k):
        # type: (str) -> Any
        i = self.fields.index(k)
        if i:
            return self.types[i]
        else:
            return None

    def get_name(self):
        return self.name

    def create_tuple(self, *args):
        if len(args) == 0:
            return self.create_tuple_blank()
        elif isinstance(args[0], list):
            return self.create_tuple_list(args[0])
        else:
            return self.create_tuple_dict(args[0])

    def create_tuple_blank(self):
        return BasicTuple(self)

    def create_tuple_dict(self, content):
        # type: (dict) -> BasicTuple
        return BasicTuple(self, content)

    def create_tuple_list(self, content):
        # type (list) -> BasicTuple
        dict2 = {}
        for i, k in enumerate(self.fields):
            dict2[k] = content[i]

        return BasicTuple(self, dict2)

    def __str__(self):
        ret = self.name + '('
        for i, f in enumerate(self.fields):
            if i > 0:
                ret = ret + ','
            ret = ret + f + ':' + self.types[i]

        return ret + ")"

class BasicTuple:
    schema = None
    data = {}

    def __init__(self, *args):
        if len(args) == 1:
            self.init1(args[0])
        elif len(args) == 2:
            self.init2(args[0], args[1])
        else:
            raise TypeError('Illegal inputs')

    def init1(self, schema):
        # type: (BasicSchema) -> None
        self.schema = schema
        for i, name in enumerate(schema.fields):
            self.data[name] = None

    def init2(self, schema, values):
        # type: (BasicSchema, dict) -> None
        self.schema = schema
        self.data = values

    def __str__(self):
        ret = self.schema.get_name() + '('
        for i, f in enumerate(self.schema.fields):
            if i > 0:
                ret = ret + ','
            if f is None:
                raise TypeError("Can't have a null key")
            elif self.data is None or self.data[f] is None:
                ret = ret + f
            else:
                ret = ret + f + ':' + str(self.data[f])

        return ret + ")"

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.data[self.schema.fields[item]]
        else:
            return self.data[item]

    def __setitem__(self, key, value):
        if key in self.schema.fields:
            self.data[key] = value
        elif isinstance(key, int):
            self.data[self.schema.fields[key]] = value
