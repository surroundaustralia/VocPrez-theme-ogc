import logging
import dateutil.parser
from flask import g
from vocprez import _config as config
from vocprez.model.vocabulary import Vocabulary
from vocprez.model.property import Property
from vocprez.source._source import *
from vocprez.source.sparql import SPARQL
import vocprez.utils as u
from rdflib import Literal, URIRef, Graph


class OGCSPARQL(SPARQL):
    """Source for a generic SPARQL endpoint
    """

    def get_collection(self, collection_uri):
        print("OGC get_collection()")
        # get the collection's metadata and members
        q = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

            SELECT DISTINCT *            
            WHERE {
                <xxxx> a skos:Collection ;
                       ?p ?o .

                FILTER(!isLiteral(?o) || lang(?o) = "en" || lang(?o) = "")

                OPTIONAL {
                    ?p skos:prefLabel|rdfs:label ?ppl .
                    FILTER(!isLiteral(?o) || lang(?o) = "en" || lang(?o) = "")
                }

                OPTIONAL {
                    ?o skos:prefLabel|rdfs:label ?opl .
                    FILTER(!isLiteral(?o) || lang(?o) = "en" || lang(?o) = "")
                }
            }
            """.replace("xxxx", collection_uri)

        vocab_uri = None
        pl = None
        d = None
        c = None
        s = {
            "provenance": None,
            "source": None,
            "wasDerivedFrom": None,
        }
        m = []
        found = False
        for r in u.sparql_query(q, config.SPARQL_ENDPOINT, config.SPARQL_USERNAME, config.SPARQL_PASSWORD):
            prop = r["p"]["value"]
            val = r["o"]["value"]
            found = True
            if val == "http://www.w3.org/2004/02/skos/core#Concept":
                return None

            if prop == "http://www.w3.org/2004/02/skos/core#prefLabel":
                pl = val
            elif prop == "http://www.w3.org/2004/02/skos/core#definition":
                d = val
            elif prop == "http://www.w3.org/2000/01/rdf-schema#comment":
                c = val
            elif prop == "http://purl.org/dc/terms/provenance":
                s["provenance"] = val
            elif prop == "http://purl.org/dc/terms/source":
                s["source"] = val
            elif prop == "http://www.w3.org/2004/02/skos/core#inScheme":
                s["inScheme"] = val
                vocab_uri = val
            elif prop == "http://www.w3.org/ns/prov#wasDerivedFrom":
                s["wasDerivedFrom"] = val
            elif prop == "http://www.w3.org/2004/02/skos/core#member":
                m.append(Property(prop, "Member", val, r["opl"]["value"]))

        if not found:
            return None

        from vocprez.model.collection import Collection
        if not d:
            d = c
        return Collection(vocab_uri, collection_uri, pl, d, s, sorted(m, key=lambda x: x.value_label.lower()))
