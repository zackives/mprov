from pennprov.cypher.cypher import CypherInterface 
import pennprov.sql.sql_provenance

ci = CypherInterface()

def test_parser():
    ci.parse('MATCH (n) RETURN count(n)')