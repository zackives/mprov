from pennprov.sql.mprov import SqlProvenance
import logging

from pennprov.connection.mprov_connection_cache import MProvConnectionCache
from pennprov.api.decorators import MProvAgg

import pandas as pd

logging.basicConfig(level=logging.DEBUG)
connection_key = MProvConnectionCache.Key()
mprov_conn = MProvConnectionCache.get_connection(connection_key)
if mprov_conn:
    mprov_conn.create_or_reset_graph()


def simple_query():
    query = 'select * from test'
    parsed = """
== Parsed Logical Plan ==
'Project [*]
+- 'UnresolvedRelation [test]

== Analyzed Logical Plan ==
x: bigint, y: bigint, name: string
Project [x#0L, y#1L, name#2]
+- SubqueryAlias test
   +- LogicalRDD [x#0L, y#1L, name#2], false

== Optimized Logical Plan ==
LogicalRDD [x#0L, y#1L, name#2], false

== Physical Plan ==
*(1) Scan ExistingRDD[x#0L,y#1L,name#2]
    """
    print(parsed)


def join_query():
    query = 'select t1.x, count(*) from test t1 join test t2 on t1.x = t2.y group by t1.x'
    parsed = """
== Parsed Logical Plan ==
'Aggregate ['t1.x], ['t1.x, unresolvedalias('count(1), None)]
+- 'Join Inner, ('t1.x = 't2.y)
   :- 'SubqueryAlias t1
   :  +- 'UnresolvedRelation [test]
   +- 'SubqueryAlias t2
      +- 'UnresolvedRelation [test]

== Analyzed Logical Plan ==
x: bigint, count(1): bigint
Aggregate [x#0L], [x#0L, count(1) AS count(1)#32L]
+- Join Inner, (x#0L = y#29L)
   :- SubqueryAlias t1
   :  +- SubqueryAlias test
   :     +- LogicalRDD [x#0L, y#1L, name#2], false
   +- SubqueryAlias t2
      +- SubqueryAlias test
         +- LogicalRDD [x#28L, y#29L, name#30], false

== Optimized Logical Plan ==
Aggregate [x#0L], [x#0L, count(1) AS count(1)#32L]
+- Project [x#0L]
   +- Join Inner, (x#0L = y#29L)
      :- Project [x#0L]
      :  +- Filter isnotnull(x#0L)
      :     +- LogicalRDD [x#0L, y#1L, name#2], false
      +- Project [y#29L]
         +- Filter isnotnull(y#29L)
            +- LogicalRDD [x#28L, y#29L, name#30], false

== Physical Plan ==
*(5) HashAggregate(keys=[x#0L], functions=[count(1)], output=[x#0L, count(1)#32L])
+- *(5) HashAggregate(keys=[x#0L], functions=[partial_count(1)], output=[x#0L, count#36L])
   +- *(5) Project [x#0L]
      +- *(5) SortMergeJoin [x#0L], [y#29L], Inner
         :- *(2) Sort [x#0L ASC NULLS FIRST], false, 0
         :  +- Exchange hashpartitioning(x#0L, 200), true, [id=#67]
         :     +- *(1) Project [x#0L]
         :        +- *(1) Filter isnotnull(x#0L)
         :           +- *(1) Scan ExistingRDD[x#0L,y#1L,name#2]
         +- *(4) Sort [y#29L ASC NULLS FIRST], false, 0
            +- Exchange hashpartitioning(y#29L, 200), true, [id=#73]
               +- *(3) Project [y#29L]
                  +- *(3) Filter isnotnull(y#29L)
                     +- *(3) Scan ExistingRDD[x#28L,y#29L,name#30]
    """
    print(parsed)


sql = SqlProvenance(mprov_conn)

print(sql.query_to_entity("test"))

simple_query()
join_query()
