import json
import urllib2
import sys

'''
    Script to ingest telemetry, create a JSON document, and do a POST
    operation to a nodejs web server that implements a REST API. The 
    node REST API writes the document to the Mongo database.
    
    As of this moment the error checking on the document is very light.
    In the future a json schema should be implemented to try to keep
    things kosher. 
    
    The inputs to the script are the JSON document 
'''

req = urllib2.Request('http://localhost:3000/REST/mission')
req.add_header('Content-Type', 'application/json')

with open('SortieFormat.json') as mission_data:
    data = json.load(mission_data)
    mission_data.close()

telemetryEntry = {};
telemetryEntry['telemetry_format'] = 'mp4'
telemetryEntry['url'] = 'http://www.apple.com'

data['sortie_data']['telemetry'].append(telemetryEntry)

response = urllib2.urlopen(req, json.dumps(data))
