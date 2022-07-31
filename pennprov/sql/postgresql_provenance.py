from pennprov.sql.sql_provenance import SqlProvenanceManager
import psycopg2

class PostgresqlProvenanceManager(SqlProvenanceManager):
    def __init__(self):
        SqlProvenanceManager.__init__(self)

    def create_sql_with_provenance(self, name:str, sql: str, context):
        rewritten_sql, aux_tables = self.generate_prov_query_and_tables(sql)

        # Generate views first
        for view in aux_tables.keys():
            if view.endswith('_uid'):
                context.execute(aux_tables[view])

        # Generate provenance stored tables next
        for view in aux_tables.keys():
            if view.endswith('_tab'):
                context.execute(aux_tables[view])
        
        context.sql('CREATE MATERIALIZED VIEW ' + name + ' AS ' + rewritten_sql)

        # Return an intermediate result
        context.execute('select * from ' + name)

        return context

