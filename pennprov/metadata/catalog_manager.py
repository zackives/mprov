import pennprov.metadata.dataframe_schema
import pennprov.metadata.graph_template
import pennprov.models.graph_script
from pennprov.sql.schema_registry import SchemaRegistry

class Catalog:
    input_and_prov_tables: SchemaRegistry = SchemaRegistry()

    def __init__(self):
        self.load()

    def load(self):
        pass

    def persist(self):
        pass