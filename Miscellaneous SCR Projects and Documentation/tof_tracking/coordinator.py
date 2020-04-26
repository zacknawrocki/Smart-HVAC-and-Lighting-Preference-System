import cherrypy
import ConfigParser
import time
from cherrypy.lib import static
import math
import os
import sys


# Location of preference clients in TOF units, from Preference Client 1 (index 0)
# to Preference Client 6 (index 5).
CLIENT_LOCATIONS = [(54, 115), (23, 115), (54, 73), (23, 73), (54, 35), (23, 35)]
CONFIG_FILE = "config.cfg"  # File containing coordinator configuration options

class OccupantTracking(object):
    def __init__(self, config):
        self.config = config
        self.tagged_occupants = dict()

    @cherrypy.expose
    def tag_user(self, username=None, preference=None):
        if username is not None and preference is not None:
            print("TAGGING")
            prevOccsfile = open("AuxFiles_toftracking/prevOccs.txt", "r")
            line = prevOccsfile.readline()
            if line.strip() != "[]":
                line = line.split("array(")
                locations = []
                for l in range(1, len(line)):
                    parsedline = line[l].split("[")[1].split(",")
                    x = float(parsedline[0])
                    y = float(parsedline[1])
                    name = int(parsedline[7].split(".")[0])
                    locations.append((x, y, name))
                print("Current locations of tracked occupants: " + str(locations))
                if locations is not None:
                    print(preference)
                    print(preference.split())
                    client_number = int(preference.split()[3])
                    occupant = self.closest_occupant(locations, client_number)
                    print("User " + username + " is occupant " + str(occupant[2]) + " from TOF data.")
                    self.tagged_occupants[occupant[2]] = (username, preference)
                    print("We have now tagged the occupant from client number " + str(client_number) + ".")
                    print("From here, we can now retieve the preferences and locations of")
                    print("a given user to provide them with the optimal temperature.")
                    print(self.tagged_occupants)
            else:
                print("No occupants are currently being tracked, therefore no occupants can be tagged")
                print("Refer to the SCR Status Screen (television screen) for more info.")
            prevOccsfile.close()

    # Returns an integer that represents the closest occupant to the preference client that was just logged onto
    def closest_occupant(self, occs, client_number):
        x = []
        y = []
        min_distance = sys.maxint
        closest = 0
        client_location = CLIENT_LOCATIONS[client_number - 1]

        for occ in range(len(occs)):
            # Euclidean distance
            distance = math.sqrt((occs[occ][0] - client_location[0]) ** 2 + (occs[occ][1] - client_location[1]) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest = occ
        return occs[closest]










def main():
    # Create the configuration file parser object and start the CherryPy server
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    port = config.getint('Meta', 'port')
    host = config.get('Meta', 'host')
    cherrypy.config.update({'server.socket_port': port,
                            'server.socket_host': host})
    cherrypy.quickstart(OccupantTracking(config))


main()
