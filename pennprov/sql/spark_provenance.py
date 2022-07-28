from pyspark.sql import SparkSession, DataFrame

from pennprov.sql.sql_provenance import SqlProvenanceManager

class SparkSqlProvenanceManager(SqlProvenanceManager):
    def __init__(self):
        SqlProvenanceManager.__init__(self)

    def _table_storage(self):
        return super()._table_storage() + 'STORED AS PARQUET'

    def _list_agg(self, items: str) -> str:
        return 'collect_list(' + items + ')'

    def _const_agg(self, items: str):
        select_str = ', '.join([self.prune(item) for item in items])
        return 'array(' + select_str + ')'

    def create_sql_with_provenance(self, name:str, sql: str, context: SparkSession) -> DataFrame:
        rewritten_sql, aux_tables = self.generate_prov_query_and_tables(sql)

        # Generate views first
        for view in aux_tables.keys():
            if view.endswith('_uid'):
                context.sql(aux_tables[view])

        # Generate provenance stored tables next
        for view in aux_tables.keys():
            if view.endswith('_tab'):
                context.sql(aux_tables[view])
        
        context.sql('CREATE VIEW ' + name + '_prov AS ' + rewritten_sql)

        context.sql('CREATE TABLE ' + name + ' LIKE ' + name + '_prov STORED PARQUET')

        # Return an intermediate result
        return context.sql('select * from ' + name)

    