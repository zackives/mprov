import pandas as pd

from pennprov.sql.postgresql_provenance import PostgresqlProvenanceManager

prov_manager = PostgresqlProvenanceManager()
sr = prov_manager.get_schema_registry()

df = pd.DataFrame([{'x': 3, 'y': 2}, {'x': 4, 'z': 'str'}])
sr.add_pandas_dataframe('df', df)
sr.add_pandas_dataframe('b', df)
sr.set_key('b', ['x'], [str])

# spark = (pyspark.sql.SparkSession
#                      .builder
#                      .appName("PySpark unit test")
#                      .getOrCreate())

class FakeContext:
    def sql(self, sql):
        print('Spark statement: %s'%sql)

        return df

    def execute(self, sql):
        print ('Postgresql statement: %s'%sql)

        return df

context = FakeContext()

def print_query_results(query_list):
    print()
    if len(query_list[1]):
        print ('** Generating new tables:')
        for tab in query_list[1].keys():
            print(' %s: %s' %(tab,query_list[1][tab]))

    print(query_list[0])

def test_noresults():
    query_list = prov_manager.generate_prov_query_and_tables('select * from a where false')
    print_query_results(query_list)
    return True

def test_simple_select():
    query_list = prov_manager.generate_prov_query_and_tables('select * from a where x = 5')
    print_query_results(query_list)
    return True


def test_simple_join():
    query_list = prov_manager.generate_prov_query_and_tables('select a, d as coffee from a, b where a.x = b.y')
    print_query_results(query_list)
    return True

def test_join_udf_rename():
    query_list = prov_manager.generate_prov_query_and_tables('select a, d as coffee, monotonically_increasing_id() from a AS t, b, c where t.x = b.y and b.z = c.d')
    print_query_results(query_list)
    return True

def test_groupby():
    query_list = prov_manager.generate_prov_query_and_tables('select * from a AS t left join b AS G on a.x = b.y, c group by w')
    print_query_results(query_list)
    return True

def test_groupby_context():
    prov_manager.create_sql_with_provenance('mytable', 'select * from a AS t left join b AS G on a.x = b.y, c group by w', context)
    return True

def test_nested_select():
    try:
        prov_manager.generate_prov_query_and_tables('select *, (select * from c) from a where false')
        raise ('Unexpected: let a nested FROM query expression through')
    except:
        print('Successfully trapped nested SELECT clause')

def test_nested_for():
    try:
        prov_manager.generate_prov_query_and_tables('select * from a AS t join (select * from c) AS G on a.x = b.y, c group by w')
        raise ('Unexpected: let a nested FROM query expression through')
    except:
        print('Successfully trapped nested FROM clause')

