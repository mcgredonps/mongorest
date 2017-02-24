import json
import urllib2
import sys
import os
import calendar
import datetime
import exceptions

'''
    Script to ingest telemetry, create a JSON document, and do a POST
    operation to a nodejs web server that implements a REST API. The 
    node REST API writes the document to the Mongo database.
    
    As of this moment the error checking on the document is very light.
    In the future a json schema should be implemented to try to keep
    things kosher. 
    
    The inputs to the script are the directory that holds the JSON mission
    metadata document that describes the mission, the directory that holds 
    the video, and the directory that holds the other telemetry.
    
    Example metadata doc:
    
    { "fields":
    { "date": "2016-11-01",
    "exercise": "FX28",
    "mission": "9",
    "sortie": "1",
    "uavid": "17",
    "gopro": "83",
    "takeoff": "1511",
    "landing": "1515",
    "stack": "0",
    "comments": "pass mcf" } }
    
    This has the UAV ID and the gopro number, along with some other data. 
    The mission is the numeric id of the group of UAVs flying to accomplish
    some task, eg force on force.
    
    
'''

BASE_URL = "http://robodata.ern.nps.edu"

''' Help message
'''
def printHelpAndExit():
    print "Syntax: pythonPost.py metadataDirectoryName videoDirectoryName telemetryDirectoryName"
    exit()

'''
    Creates the document we insert into mongodb. Returns that.
'''
def createDocument(metadata, videoDirectory, telemetryDirectory):
    #print metadata
    #print videoDirectory
    #print telemetryDirectory
    
    # Open the document template
    with open('SortieFormat.json') as mission_data:
        documentTemplate = json.load(mission_data)
        mission_data.close()

    # Start filling it out
    
    # The sortie_description_format is OK
    
    # Exercise information
    documentTemplate['exercise_information']['exercise_name'] = metadata['fields']['exercise']
    documentTemplate['exercise_information']['location'] = "Camp Roberts"
    documentTemplate['exercise_information']['sponsor_organization'] = "Naval Postgraduate School"

    # Robot information about this specific robot. Should have version info on the software as well.
    documentTemplate['robot_information']['robot_type'] = "zephyr"
    documentTemplate['robot_information']['software'] = "ROS"
    documentTemplate['robot_information']['robot_owner'] ['name']= "Naval Postgraduate School, ARSENL"
    documentTemplate['robot_information']['robot_owner'] ['url']= "https://my.nps.edu/web/cruser"
    documentTemplate['robot_information']['uav_id'] = metadata['fields']['uavid']
    documentTemplate['robot_information']['gopro_id'] = metadata['fields']['gopro']

    # Telemetry information about one sortie.
    documentTemplate['sortie_data']['start_time'] = metadata['fields']['takeoff']
    documentTemplate['sortie_data']['end_time'] = metadata['fields']['landing']
    documentTemplate['sortie_data']['mission'] = metadata['fields']['mission']
    documentTemplate['sortie_data']['comment'] = metadata['fields']['comments']

    # Construct a date/time from the date and the time in the metadata file.. We have the date in
    # the metadata field, combine with landing and takeoff from other fields. Note this may
    # differ from telemetry times. The time in metadata is taken from the launch data forms,
    # which are filled out by hand.
    metadataDate = metadata['fields']['date']
    dateComponents = metadataDate.split('-')

    # launch time
    takeoffString = metadata['fields']['takeoff']
    takeoffInt = int(takeoffString)
    takeoffHour = takeoffInt / 100
    takeoffMin = takeoffInt % 100
    dateTime = datetime.datetime( int(dateComponents[0]), int(dateComponents[1]), int(dateComponents[2]), takeoffHour, takeoffMin )
    documentTemplate['sortie_data']['start_time'] = dateTime

    # landing time
    landingString = metadata['fields']['landing']
    landingInt = int(takeoffString)
    landingHour = takeoffInt / 100
    landingMin = takeoffInt % 100
    dateTime = datetime.datetime( int(dateComponents[0]), int(dateComponents[1]), int(dateComponents[2]), takeoffHour, takeoffMin )
    documentTemplate['sortie_data']['end_time'] = dateTime

    telemetryEntry = {}
    telemetryEntry['type'] = "mp4"
    telemetryEntry['url'] = "http://www.movesinstitute.org/movie.mp4"
    print "++++>Telementry entry is ", telemetryEntry
    documentTemplate['sortie_data']['telemetry'].append(telemetryEntry)
    documentTemplate['sortie_data']['telemetry'].append(telemetryEntry)

    print documentTemplate
    # Set the various telemetry entries.

    # Loop through the video directory, collecting the vid for a specific camera
    camDirectory = videoDirectory + "/CAM" + metadata['fields']['gopro']
    camDirectory = os.path.normpath(camDirectory)
    print "video directory is ", camDirectory

    try:
        for filename in os.listdir(camDirectory):
            filename = os.path.normpath(filename)
            if filename.endswith(".MP4") or filename.endswith(".mp4"):
                fullPath = camDirectory + "/" + filename
                tailPart = ""
                
                for idx in range(0,3):
                    dir, base = os.path.split(fullPath)
                    tailPart = base + "/" + tailPart
                    fullPath = dir
                tailPart = os.path.normpath(tailPart)
                print tailPart
                
                url = BASE_URL + "/" + tailPart
                
                telemetryEntry.type = "mp4"
                telemetryEntry.url = url
                
                telemetryArray = documentTemplate['sortie_data']['telemetry']
                print telemetryArray
                documentTemplate['sortie_data']['telemetry'].extend(telemetryEntry)
                continue
    except:
        print "No video found for camera ", camDirectory

    

    print documentTemplate

    return documentTemplate

# Arguments: first is name of the script, remainder any cmd line args

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)


if len(sys.argv) < 4:
    printHelpAndExit();

metadataDirectory = sys.argv[1]
videoDirectory = sys.argv[2]
telemetryDirectory = sys.argv[3]

print "relevant args are ", metadataDirectory, " ", videoDirectory, " ", telemetryDirectory

for filename in os.listdir('./FX28'):
    if filename.endswith(".json"):
        filename = "./FX28/" + filename
        #print "filename is:", filename
        with open(filename) as missionMetadata:
           metadata = json.load(missionMetadata)
           documentToInsert = createDocument(metadata, videoDirectory, telemetryDirectory)
           #print "metadata is ", data
           continue
    else:
        continue

# Build the HTTP post to send to the REST API

req = urllib2.Request('http://localhost:3000/REST/mission')
req.add_header('Content-Type', 'application/json')

with open('SortieFormat.json') as mission_data:
    data = json.load(mission_data)
    mission_data.close()

telemetryEntry = {};
telemetryEntry['telemetry_format'] = 'mp4'
telemetryEntry['url'] = 'http://www.apple.com'

data['sortie_data']['telemetry'].append(telemetryEntry)

#response = urllib2.urlopen(req, json.dumps(data))
