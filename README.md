# VocPrez-theme-ogc
A VocPrez UI theme for the Open Geospatial Consortium

`apply.py` adds these elements - templates, style files and endpoints additions - to a VocPrez instance

This needs environment variables to be set:

export VP_HOME=/var/www/ogc
export VP_THEME_HOME=/var/www/VocPrez-theme-ogc
export SPARQL_ENDPOINT="http://defs-dev.opengis.net:8080/rdf4j-server/repositories/ogc-na"
export SPARQL_USERNAME=
export SPARQL_PASSWORD=
export API_KEY='r974wh46hgsdi767ghfnfy'

These are unchanged from VP 2.4 to VP 2.5 however you really do have to set the SPARQL_USERNAME & SPARQL_PASSWORD either to values or, as above, which will be interpreted as None. The API_KEY can be set to any string value but must be set.

