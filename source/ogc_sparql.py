import logging
import dateutil.parser
from flask import g
from markdown import markdown

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

    @staticmethod
    def collect(details):
        """
        For this source, one SPARQL endpoint is given for a series of vocabs which are all separate ConceptSchemes

        'ga-jena-fuseki': {
            'source': VocabSource.SPARQL,
            'sparql_endpoint': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
            'sparql_username': '<sparql_user>', # Optional username for SPARQL endpoint
            'sparql_password': '<sparql_password>', # Optional password for SPARQL endpoint
        },
        """
        logging.debug("SPARQL collect()...")

        # Get all the ConceptSchemes from the SPARQL endpoint
        # Interpret each CS as a Vocab
        q = """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dcterms: <http://purl.org/dc/terms/>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                SELECT * 
                WHERE {{
                    ?cs a skos:ConceptScheme .
                    OPTIONAL {{ ?cs skos:prefLabel ?title .
                        FILTER(lang(?title) = "{language}" || lang(?title) = "") }}
                    OPTIONAL {{ ?cs dcterms:created ?created }}
                    OPTIONAL {{ ?cs dcterms:issued ?issued }}
                    OPTIONAL {{ ?cs dcterms:modified ?modified }}
                    OPTIONAL {{ ?cs dcterms:creator ?creator }}
                    OPTIONAL {{ ?cs dcterms:source ?source }}
                    OPTIONAL {{ ?cs dcterms:publisher ?publisher }}
                    OPTIONAL {{ ?cs owl:versionInfo ?version }}
                    OPTIONAL {{ ?cs skos:definition ?description .
                        FILTER(lang(?description) = "{language}" || lang(?description) = "") }}
                    OPTIONAL {{ ?cs ?p ?pval .
                        FILTER( ! isBlank(?pval) )  }}    
                }} 
                ORDER BY ?title
                """.format(language=config.DEFAULT_LANGUAGE)
        # record just the IDs & title for the VocPrez in-memory vocabs list
        concept_schemes = u.sparql_query(
            q,
            details["sparql_endpoint"],  # must specify a SPARQL endpoint if this source is to be a SPARQL source
            details.get("sparql_username"),
            details.get("sparql_password"),
        )
        assert concept_schemes is not None, "Unable to query for ConceptSchemes"

        sparql_vocabs = {}
        vocab_ids = []
        for cs in concept_schemes:
            vocab_id = cs["cs"]["value"]
            part = cs["cs"]["value"].split("#")[-1].split("/")[-1]
            if len(part) < 1:
                part = cs["cs"]["value"].split("#")[-1].split("/")[-2]
            id = part.lower()
            if id in vocab_ids:
                if id[-1].isnumeric():
                    id = id[:-1] + str(int(id[-1]) + 1)
                else:
                    id = id + "1"

            prop = cs["p"]["value"]
            val = cs["pval"]["value"]
            showlist = [ "http://www.w3.org/ns/dx/prof/isProfileOf" ]
            if prop in show_list :
                other_properties.append(Property(prop, property_label, val, object_label))


            vocab_ids.append(id)

            sparql_vocabs[vocab_id] = Vocabulary(
                id,
                cs["cs"]["value"],
                cs["title"].get("value") or vocab_id if cs.get("title") else vocab_id,  # Need str for sorting, not None
                markdown(cs["description"].get("value")) if cs.get("description") is not None else None,
                cs["creator"].get("value") if cs.get("creator") is not None else None,
                dateutil.parser.parse(cs.get("created").get("value")) if cs.get("created") is not None else None,
                # dct:issued not in Vocabulary
                # dateutil.parser.parse(cs.get('issued').get('value')) if cs.get('issued') is not None else None,
                dateutil.parser.parse(cs.get("modified").get("value")) if cs.get("modified") is not None else None,
                cs["version"].get("value") if cs.get("version") is not None else None,  # versionInfo
                config.VocabSource.SPARQL,
                sparql_endpoint=details["sparql_endpoint"],
                sparql_username=details.get("sparql_username"),
                sparql_password=details.get("sparql_password"),
                other_properties= [ Property()]
            )
        g.VOCABS = {**g.VOCABS, **sparql_vocabs}
        logging.debug("SPARQL collect() complete.")

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
