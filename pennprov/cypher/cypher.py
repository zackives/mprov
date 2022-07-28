from re import template
import pennprov.metadata.graph_template
import pennprov.models.graph_script

import pennprov.sql.sql_provenance
from pennprov.metadata.catalog_manager import Catalog

class CypherInterface:
    catalog: Catalog = Catalog()

    def execute(self, cyper_query: str):
        return []