''' 
This file runs the preference coordinator server. It communicates with each preference client,
the SCR Schedule Website, the HVAC Server, and the HVAC database, to manage the preferences
of room occupants, using the CherryPy Python library. 
''' 

# Modules and frameworks
from queries import Queries
import cherrypy
import ConfigParser
import time
import sqlite3
import json
import calc_temp
from cherrypy.lib import static
import os
from HVACLib import HVAC
import cherrypy_cors
from datetime import datetime, date
import threading
import requests


SQLITE_DB = "hvac.db"  # File containing coordinator SQLITE database
CONFIG_FILE = "config.cfg"  # File containing coordinator configuration options
NODE_TIMEOUT = 40  # Heartbeat timeout before a preference client is labeled offline
TEMPERATURE_SET_DELAY = 20  # Minimum delay after thermostat temperature optimization
MYHVAC = HVAC() # HVAC Library, used to send commands to the HVAC Server in the SCR


class Coordinator(object):
    """
    This Coordinator object uses the CherryPy Python library to serve API calls
      over HTTP. The preference clients communicate with the coordinator using
      these API calls. HTTP port, sensor IDs and coordinates, and location ZIP
      code are all contained in the configuration file for the coordinator.

    The coordinator holds a database containing information
      about the system as a whole and updates the database as preference clients
      make requests. The database contains 8 tables, and the tables schemas are
      below.

        ambient
          id INTEGER PRIMARY KEY AUTOINCREMENT
          temperature REAL

        nodes
          id INTEGER PRIMARY KEY
          x_pos REAL
          y_pos REAL
          current_user_id INTEGER

        users
          id INTEGER PRIMARY KEY AUTOINCREMENT
          name TEXT
          preference REAL

        sensors
          id INTEGER PRIMARY KEY
          x_pos REAL
          y_pos REAL
          temperature REAL

        historical_nodes
          time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP
          id INTEGER
          current_user_id INTEGER

        historical_users
          time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP
          id INTEGER
          name TEXT
          preference REAL

        historical_sensors
          time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP
          id INTEGER
          temperature REAL

        historical_optimized
          time TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP
          temperature REAL

    """

    def __init__(self, config):
        """ Coordinator object initialization.
        :param config: ConfigParser object containing coordinator configuration
        """
        self.config = config
        self.last_temperature_update = None
        self.thermostat = None
        self.default_temp = 70
        self.temp_offset = 0
        self.nodes = {}
        self.sensors = {}
        self.init_db()
        self.init_sensors()

    @cherrypy.expose
    def start_node(self, node_id=None, pos_x=None, pos_y=None):
        """ CherryPy exposed API for preference client (node) initialization.
        This function is called by the preference client during startup in
          order to let the coordinator know that a new client is online and
          will begin sending heartbeat messages while it is online.
        :param node_id: unique integer ID for preference client
        :param pos_x: x-coordinate of client position in room
        :param pos_y: y-coordinate of client position in room
        :return: JSON object containing temperature sensor properties
        """
        if node_id is not None and pos_x is not None and pos_y is not None:
            node_id = int(node_id)
            pos_x = float(pos_x)
            pos_y = float(pos_y)
            self.nodes[node_id] = {
                'online': True,
                'last_heartbeat': time.time()
            }
            self.stop_node(node_id=node_id)
            self.execute_query(insert=Queries.INSERT_NODE,
                               args=[node_id, pos_x, pos_y, -1, 0])
            #self.execute_query(insert=Queries.INSERT_HISTORICAL_NODE,
                               #args=[node_id, -1])
            cherrypy.log("Started node %d" % node_id)
            self.print_db()
            return json.dumps(self.sensors)

    @cherrypy.expose
    def stop_node(self, node_id=None):
        """ CherryPy exposed API for preference client termination.
        This function is called by the preference client during shutdown in
          order to let the coordinator know that the client is offline.
        :param node_id: unique integer ID for preference client
        """
        if node_id is not None:
            node_id = int(node_id)
            self.nodes[node_id]['online'] = False
            self.execute_query(insert=Queries.DELETE_NODE,
                               args=[node_id])
            cherrypy.log("Stopped node %d" % node_id)
            self.print_db()

    @cherrypy.expose
    def add_user(self, username=None, preference=None):
        """ CherryPy exposed API for adding a new user.
        This function is called by the preference client when a new user is
          added using the GUI. The user name and preference are added to the
          coordinator database.
        :param username: unique username for the new user
        :param preference: string of user preferences
        """
        if username is not None and preference is not None:
            self.execute_query(insert=Queries.INSERT_USER,
                               args=[username, preference])
            user_id = int(self.get_user_id(username))
            self.execute_query(insert=Queries.INSERT_HISTORICAL_USER,
                               args=[user_id, username, preference])
            cherrypy.log("Added user %s" % username)
            self.print_db()

    @cherrypy.expose
    def remove_user(self, username=None):
        """ CherryPy exposed API for removing a new user.
        This function is called by the preference client when a new user is
          removed using the GUI. The user name and preference are removed to the
          coordinator database.
        :param username: unique username for the new user
        :param preference: string of user preferences
        """
        if username is not None:
            user_id = self.get_user_id(username)
            self.execute_query(insert=Queries.DELETE_USER,
                               args=[user_id])
            cherrypy.log("Removed user %s" % username)
            self.print_db()

    @cherrypy.expose
    def get_preference(self, username=None):
        """ CherryPy exposed API for retrieving a user preference.
        This function is called by the preference client when an existing
          user has logged in and the current preference needs to be displayed.
        :param username: unique username for the existing user
        :return: string preference for the user
        """
        if username is not None:
            users = self.execute_query(select=Queries.GET_USERS)
            for user in users:
                print(str(user[1]))
                print(str(username))
                print(user[2])
                if str(user[1]) == str(username):
                    preference = user[2]
                    # color_temperature = user[3]
                    # client_number = user[4]
                    # print("Color temperature: %s" % str(color_temperature))
                    # print("Client number: %s" % str(client_number))
                    print("Preference: %s" % str(preference))
                    return json.dumps(preference)

    @cherrypy.expose
    def get_user_names(self):
        """ CherryPy exposed API for retrieving a list of all user names.
        This function is called by the preference client in order to display a
          list of user names for an existing user to log in using the GUI.
        :return: JSON list of strings containing existing user names
        """
        users = self.execute_query(select=Queries.GET_USERS)
        usernames = []
        for user in users:
            usernames.append(str(user[1]))
        return json.dumps(usernames)

    @cherrypy.expose
    def add_user_to_node(self, username=None, node_id=None):
        """ CherryPy exposed API for adding a user to a preference client.
        This function is called by the preference client when a user logs in
          at that preference client. It tells the coordinator that a user
          is currently active at that node (preference client), as well as
          tags users, by sending their information to the TOF Tagging Server.
        :param username: unique user name for the existing user
        :param node_id: unique node ID for the preference client
        """
        if username is not None and node_id is not None:
            node_id = int(node_id)
            user_id = int(self.get_user_id(username))
            self.execute_query(insert=Queries.UPDATE_NODE,
                               args=[user_id, node_id])
            #self.execute_query(insert=Queries.INSERT_HISTORICAL_NODE,
                               #args=[node_id, user_id])
            cherrypy.log("Added user to node")
            self.print_db()
            preference = self.get_preference(username)
            data = {'username': username, 'preference': preference}
            '''
            Connects to tagging server, to match users, who have logged into preference
            clients in the SCR, to their TOF tracking coordinates
            '''
            try:
                response = requests.post(url="http://192.168.0.2:3001/tag_user", data=data, timeout=1.5)
                print(response)
                return response
            except Exception as e:
                return None

    @cherrypy.expose
    def remove_user_from_node(self, username=None, node_id=None):
        """ CherryPy exposed API for removing a user from a preference client.
        This function is called by the preference client when a user logs out
          at that preference client. It tells the coordinator that the user
          is no longer active.
        :param username: unique user name for the existing user
        :param node_id: unique node ID for the preference client
        """
        if username is not None and node_id is not None:
            node_id = int(node_id)
            self.execute_query(insert=Queries.UPDATE_NODE,
                               args=[-1, node_id])
            #self.execute_query(insert=Queries.INSERT_HISTORICAL_NODE,
                               #args=[node_id, -1])
            cherrypy.log("Removed user from node")
            self.print_db()

    @cherrypy.expose
    def update_preference(self, username=None, preference=None):
        """ CherryPy exposed API for updating an existing user's preference.
        This function is called by the preference client when a user changes
          his/her preference using the GUI.
        :param username: unique user name for the existing user
        :param preference: new string of preferences for the user
        """
        if username is not None and preference is not None:
            user_id = self.get_user_id(username)
            self.execute_query(insert=Queries.UPDATE_PREFERENCE,
                               args=[preference, user_id])
            self.execute_query(insert=Queries.INSERT_HISTORICAL_USER,
                               args=[user_id, username, preference])
            cherrypy.log("Updated preference")
            self.print_db()


    @cherrypy.expose
    @cherrypy.tools.json_in()
    def update_preference1(self):
        """ CherryPy exposed API for updating an existing user's preference.
        This function is called by the preference client when a user changes
          his/her preference using the GUI.
        """
        u_pr = cherrypy.request.json
        print("updating preference")
        print("print(u_pr)")
        print(u_pr)
        print(" ")
        print("print(type(u_pr))")
        print(type(u_pr))
        print(" ")
        print("print(u_pr[3])")
        print(u_pr[3])
        print(" ")
        print("print(u_pr[4])")
        print(u_pr[4])
        print(" ")
        print("u_pr = json.dumps(u_pr)")
        print(" ")
        print("print(type(u_pr))")
        print(type(u_pr))
        print(u_pr)
        print(" ")
        print("print(u_pr[3])")
        print(u_pr[3])
        print(" ")
        print("testing")
        print(type(u_pr[4]))
        # temp = u_pr[0]
        # colortemp = u_pr[1]
        # clientnumber = u_pr[2]
        # flag = u_pr[3]
        # username = u_pr[4]
        # preference = ""
        # for i in range(len(u_pr)):
        #   preference += u_pr[i]
        #   preference += " "

        # print(preference)

        # self.update_preference(self, username=u_pr[4], preference=u_pr)

        username = str(u_pr[4])
        print(username)
        d = [s.encode('ascii') for s in u_pr]
        print(type(d))
        print(d[3])
        preference = ""
        for i in range(len(d)):
          preference += d[i]
          preference += " "
        print(preference)
        # preference = str(u_pr)
        user_id = self.get_user_id(username)
        self.execute_query(insert=Queries.UPDATE_PREFERENCE,
                           args=[preference, user_id])
        self.execute_query(insert=Queries.INSERT_HISTORICAL_USER,
                           args=[user_id, username, preference])
        cherrypy.log("Updated preference")
        self.print_db()




    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def add_meeting(self):
        """ CherryPy exposed API for adding SCR meetings to the database.
        This function is called by the SCR Schedule Website, to provide
        awareness/satisfy the preferences for upcoming meetings.
        """
        data = None
        id = None
        start_time = None
        end_time = None
        title = None
        userlist = None
        
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
        
        result = {'operation': 'request', 'result': 'success'}
        if cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            id = data["id"]
            start_time = data["start_time"]
            end_time = data["end_time"]
            title = data["title"]
            userlist = data["userlist"]
            users = self.get_user_names()
            temp_pref = 0
            preference = None
            temp = None
            userstring= ""
            for user in userlist:
                if user not in users:
                    preference = "70 4000 1 1 " + user
                    self.add_user(user, preference)
                    temp_pref += 70
                else:
                    preference = json.loads(self.get_preference(user))
                    temp = int(float((preference.split()[0])))
                    temp_pref += temp
                userstring += user
                userstring += "__!__"
            avgtemp = temp_pref / len(userlist)
            # phpc_time hardcoded for now
            phpc_time = 30
            if id is not None and title is not None and start_time is not None and end_time is not None and userlist is not None and avgtemp is not None and phpc_time is not None:
                self.execute_query(insert=Queries.INSERT_MEETING, args=[id, title, start_time, end_time, userstring, avgtemp, phpc_time])
                cherrypy.log("Added meeting %s" % title)
                self.print_db()
            print("Added " + title)
            threading.Thread(target=self.setup_temperature(avgtemp, start_time, end_time)).start()
        return result


# =========================================================================================== #

    '''
    Much of this section of code will change (or be obsolete) once we implement our new smart temperature,
    pre-heating/pre-cooling, data-driven learning, control algorithm
    '''

    # Only used if SCR Schedule website is not in use (Relies on LESA's Google Calendar Account)
    def add_meeting_via_google_calendar(self):
        pass

    
    def setup_temperature(self, avgtemp, start_time, end_time):
        """ Threaded function, which sets an upcoming meeting's temperature to the average of
        the attendees' temperature preferences.
        :param avgtemp: temperature to set the SCR to, for the relevant meeting
        :param start_time: the time the meeting begins (when the target temperature should be reached)
        :param end_time: the time the meeting ends (time to hand control back to the BMS)
        """
        s = start_time.split("T")
        s1 = s[0].split("-")
        startyear = s1[0]
        startmonth = s1[1]
        startday = s1[2]
        starttime = s[1]

        e = end_time.split("T")
        e1 = e[0].split("-")
        e = end_time.split("T")
        e1 = e[0].split("-")
        endyear = e1[0]
        endmonth = e1[1]
        endday = e1[2]
        endtime = e[1]

        ctime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ctime = ctime.split()
        c = ctime[0].split("-")
        currentyear = c[0]
        currentmonth = c[1]
        currentday = c[2]
        currenttime = ctime[1]

        seconds = self.seconds_between(startyear, startmonth, startday, starttime, currentyear, currentmonth, currentday, currenttime)
        time_to_set_temp = 900
        if time_to_set_temp < seconds:
            print("Waiting to set temperature.")
            time.sleep(seconds - time_to_set_temp)
            print("READY")
            print("Before")
            MYHVAC.getTemp(4, True)
            avgtempc = int((avgtemp - 32) * 5/9)
            MYHVAC.setTemp(int((avgtempc)))
            print("Set temperature to " + str(avgtempc) + " C.")
            print("Sleeping for pre-heating/pre-cooling")
            time.sleep(time_to_set_temp)
            print("After")
            MYHVAC.getTemp(4, True)
            meeting_duration = self.seconds_between(startyear, startmonth, startday, starttime, endyear, endmonth, endday, endtime)
            print("Sleeping for meeting")
            time.sleep(meeting_duration)
            # Meeting is over
            myhvac.reset()
            myhvac.close()

    # Helper function for setup_temperature, to find the time between the next meeting, and the current date/time
    def seconds_between(self, syear, smonth, sday, stime, fyear, fmonth, fday, ftime):
        nstime = stime.split(":")
        nftime = ftime.split(":")
        start = datetime(year = int(syear), month = int(smonth), day = int(sday), hour = int(nstime[0]), minute = int(nstime[1]), second = int(nstime[2]))
        finish = datetime(year = int(fyear), month = int(fmonth), day = int(fday), hour = int(nftime[0]), minute = int(nftime[1]), second = int(nftime[2]))
        difference = start - finish
        print("DIFFERENCE IS: ")
        print(difference)
        return difference.seconds

# =========================================================================================== #

    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def remove_meeting(self):
        """ CherryPy exposed API for removing SCR meetings to the database.
        This function is called by the SCR Schedule Website, to cancel previously
        planned meetings.
        """
        data = None
        id = None
        if cherrypy.request.method == 'OPTIONS':
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST'])
        result = {'operation': 'request', 'result': 'success'}
        if cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            id = data["id"]
            if id is not None:
                self.execute_query(insert=Queries.DELETE_MEETING, args=[id])
                cherrypy.log("Removed meeting with an id of %s" % id)
                self.print_db()
        print("removed")
        return result

    @cherrypy.expose
    def get_default_temp(self):
        return json.dumps(self.default_temp)

    @cherrypy.expose
    def change_default_temp(self, temp=None):
        if temp is not None:
            try:
                temp = int(temp)
                self.default_temp = temp
                cherrypy.log('Changed default temp to %d' % temp)
            except Exception:
                cherrypy.log('Could not change default temp')
                cherrypy.response.headers['Status'] = "300"
                return False

    @cherrypy.expose
    def get_temp_offset(self, node_id):
        if node_id is not None:
            cherrypy.log('Getting temp offset for node %d' % int(node_id))
            offset = self.execute_query(select=Queries.GET_NODE_OFFSET,
                                        args=[node_id])
            if offset:
                return json.dumps(int(offset[0][0]))

    @cherrypy.expose
    def change_temp_offset(self, offset, node_id):
        if offset is not None and node_id is not None:
            try:
                offset = int(offset)
                self.execute_query(insert=Queries.UPDATE_OFFSET,
                                   args=[offset, node_id])
                cherrypy.log('Changed temp offset to %d' % offset)
                self.print_db()
            except Exception:
                cherrypy.log('Could not change temp offset')
                cherrypy.response.headers['Status'] = "300"
                return False

    @cherrypy.expose
    def update_sensors(self, sensor_data=None):
        """ CherryPy exposed API for sending updated sensor temperature data.
        This function is called by only one online preference client at a given
          time. This preference client retrieves temperatures for each sensor
          in the room and passes on the temperature data to the coordinator
          using this API.
        :param sensor_data: JSON object containing sensor IDs and temperatures
        """
        if sensor_data is not None:
            sensor_data = json.loads(sensor_data)
            print "SENSOR DATA: %s" % sensor_data
            for sensor_id, temp in sensor_data.iteritems():
                sensor_id = int(sensor_id)
                temp = float(temp)
                self.execute_query(insert=Queries.UPDATE_SENSOR,
                                   args=[temp, sensor_id])
                time.sleep(1)
                self.execute_query(insert=Queries.INSERT_HISTORICAL_SENSOR,
                                   args=[sensor_id, temp])
            self.print_db()

    @cherrypy.expose
    def query_temperature(self):
        """ CherryPy exposed API for retrieving the optimized temperature.
        This function is called by only one online preference client at a given
          time. This preference client periodically queries the coordinator
          using this API call in order to retrieve the optimized thermostat
          temperature for the room.
        :return: JSON object containing the optimized temperature, or "None"
                   if the optimized temperature is not ready
        """
        if self.last_temperature_update is None:
            self.last_temperature_update = time.time()
            last_temperature = self.thermostat
            temperature = int(calc_temp.main(
                db=SQLITE_DB,
                last_temp=last_temperature,
                default_temp=self.default_temp))
            self.thermostat = temperature
            self.execute_query(insert=Queries.INSERT_HISTORICAL_OPTIMIZED,
                               args=[temperature])
            self.print_db()
            return str(temperature)
        elif self.last_temperature_update < time.time() - TEMPERATURE_SET_DELAY:
            self.last_temperature_update = time.time()
            last_temperature = self.thermostat
            temperature = int(calc_temp.main(
                db=SQLITE_DB,
                last_temp=last_temperature,
                default_temp=self.default_temp))
            self.thermostat = temperature
            self.execute_query(insert=Queries.INSERT_HISTORICAL_OPTIMIZED,
                               args=[temperature])
            self.print_db()
            return str(temperature)
        else:
            return "None"

    @cherrypy.expose
    def get_state(self):
        """ CherryPy exposed API for retrieving the state of the system.
        This function is called by any preference client when a user uses the
          GUI to retrieve a string containing the overall state of the system.
        :return: a string containing the overall state of the system
        """
        return json.dumps(self.db_str())

    @cherrypy.expose
    def get_node_state(self, node_id=None):
        if node_id is not None:
            if node_id in self.nodes.keys():
                cherrypy.log("Heartbeat node %d" % node_id)
                self.nodes[node_id]['last_heartbeat'] = time.time()
            self.check_heartbeats()
            state = {
                'estimated_temp': self.execute_query(
                    select=Queries.GET_NODE_TEMPERATURE,
                    args=[node_id])[0][0],
                'thermostat_temp': self.thermostat,
                'sensors': self.execute_query(select=Queries.GET_SENSORS)
            }
            return json.dumps(state)
        return "None"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def Temperature_Sensors(self):
       
      sensor_data = cherrypy.request.json
      for sensor_id, temp in sensor_data.iteritems():
          sensor_id = int(sensor_id[1]) - 1
          temperature = self.ctof(float(temp))
          self.execute_query(insert=Queries.UPDATE_SENSOR,
                              args=[temperature, sensor_id])
          self.execute_query(insert=Queries.INSERT_HISTORICAL_SENSOR,
                              args=[sensor_id, temp])
      #temperature = int(calc_temp.main(
          #db=SQLITE_DB,
          #last_temp=self.thermostat,
          #default_temp=self.default_temp
      #))
      self.execute_query(insert=Queries.INSERT_HISTORICAL_OPTIMIZED,
                          args=[temperature])
      self.thermostat = temperature
      self.print_db()


            # Modified for Demo (4/11)

      users = self.execute_query(select=Queries.GET_USERS)
      print(users)
      preferences = []
      for user in users:
        p0 = self.get_preference(user[1])
        print("Printing p0")
        preference = json.loads(p0)
        preferences.append(preference)
        # p = preferences.split()
        # p[3] = str(0)
        # s = ""
        # s.join(p)
        # print(s)
        # self.update_preference(str(user[1]), s)
      return json.dumps(preferences)
   


    @cherrypy.expose
    def GetDB(self):
        localDir = os.path.dirname(__file__)
        absDir = os.path.join(os.getcwd(), localDir)
        path = os.path.join(absDir, 'hvac.db')
        return static.serve_file(path, 'application/x-download',
                                 'attachment', os.path.basename(path))

    def init_sensors(self):
        """ Initialize sensors in the coordinator database.
        This function initialized the sensors table in the coordinator database
          based on the configuration file, which contains sensor IDs and
          coordinates.
        """
        id_list = self.config.get('Sensors', 'ids').split()
        pos_x_list = self.config.get('Sensors', 'positions_x').split()
        pos_y_list = self.config.get('Sensors', 'positions_y').split()
        for i in range(len(id_list)):
            sensor_id = int(id_list[i])
            pos_x = float(pos_x_list[i])
            pos_y = float(pos_y_list[i])
            self.sensors[sensor_id] = (pos_x, pos_y)
            self.execute_query(insert=Queries.INSERT_SENSOR,
                               args=[sensor_id, pos_x, pos_y, -1])

    def init_db(self):
        """ Initialize the coordinator database.
        This function is called on coordinator initialization and initializes
          all tables in the database. If the database does not yet exist,
          a new database is created with needed tables. If the database
          exists, node and sensor tables are cleared.
        """
        if len(self.execute_query(select=Queries.GET_TABLES)) == 0:
            self.execute_query(insert=Queries.CREATE_TABLE_USERS)
            self.execute_query(insert=Queries.CREATE_TABLE_SENSORS)
            self.execute_query(insert=Queries.CREATE_TABLE_NODES)
            self.execute_query(insert=Queries.CREATE_TABLE_AMBIENT)
            self.execute_query(insert=Queries.CREATE_TABLE_HISTORICAL_NODES)
            self.execute_query(insert=Queries.CREATE_TABLE_HISTORICAL_OPTIMIZED)
            self.execute_query(insert=Queries.CREATE_TABLE_HISTORICAL_SENSORS)
            self.execute_query(insert=Queries.CREATE_TABLE_HISTORICAL_USERS)
            self.execute_query(insert=Queries.CREATE_TABLE_MEETINGS)
        else:
            self.execute_query(insert=Queries.DROP_TABLE_NODES)
            self.execute_query(insert=Queries.CREATE_TABLE_NODES)
            self.execute_query(insert=Queries.DROP_TABLE_SENSORS)
            self.execute_query(insert=Queries.CREATE_TABLE_SENSORS)

    def get_user_id(self, username):
        """ Retrieve a user ID based on the user's name.
        :param username: unique user name of the user
        :return: unique integer ID of the user
        """
        ids = self.execute_query(select=Queries.GET_USER_ID,
                                 args=[username])
        return ids[0][0]

    def check_heartbeats(self):
        """ Check heartbeat timestamps for each preference client.
        This function checks heartbeat timestamps and labels a preference
          client as offline if it has not provided a heartbeat within
          NODE_TIMEOUT seconds.
        """
        offline = []
        for node_id, info in self.nodes.iteritems():
            if info['last_heartbeat'] < time.time() - NODE_TIMEOUT:
                offline.append(node_id)
        for node_id in offline:
            self.nodes[node_id]['online'] = False

    def execute_query(self, insert=None, select=None, args=[]):
        """ Execute a SQLITE3 insert or select query.
        :param insert: insert query string (commits after execution)
        :param select: select query string (does not commit after execution)
        :param args: optional arguments for query string
        :return: True if insert query was successful, or queries data if
                 select query was successful
        """
        db = sqlite3.connect(SQLITE_DB)
        cur = db.cursor()
        if insert:
            cur.execute(insert, args)
            db.commit()
            db.close()
            return True
        elif select:
            cur.execute(select, args)
            data = cur.fetchall()
            db.close()
            return data

    def db_str(self):
        """ Get a string containing the current state of the system.
        :return: string containing system state
        """
        outstr = "Thermostat Temp: %d\n" % self.thermostat
        outstr += "Users: %s\n" % str(self.execute_query(select=Queries.GET_USERS))
        outstr += "Node: %s\n" % str(self.execute_query(select=Queries.GET_NODES))
        outstr += "Sensors: %s\n" % str(self.execute_query(select=Queries.GET_SENSORS))
        return outstr

    def print_db(self):
        """ Print the current state of the system. """
        users = self.execute_query(select=Queries.GET_USERS)
        nodes = self.execute_query(select=Queries.GET_NODES)
        sensors = self.execute_query(select=Queries.GET_SENSORS)
        print('+' * 100)
        print(" Users")
        if len(users) == 0:
            print("\t(none)")
        else:
            print("\t| %-14s | %-14s | %-14s |" % ("ID", "NAME", "PREFERENCE"))
            for user in users:
                print("\t| %-14s | %-14s | %-14s |" % user)
        print(" Nodes")
        if len(nodes) == 0:
            print("\t(none)")
        else:
            print("\t| %-14s | %-14s | %-14s | %-14s | %-14s | %-14s |" % ("ID", "POSX", "POSY", "ESTIMATED", "CURRENT_USER", "TEMP_OFFSET"))
            for node in nodes:
                print("\t| %-14s | %-14s | %-14s | %-14s | %-14s | %-14s |" % node)
        print(" Sensors")
        if len(sensors) == 0:
            print("\t(none")
        else:
            print("\t| %-14s | %-14s | %-14s | %-14s |" % ("ID", "POSX", "POSY", "TEMPERATURE"))
            for sensor in sensors:
                print("\t| %-14s | %-14s | %-14s | %-14s |" % sensor)
        print(" Thermostat Setting")
        print("\t%s" % str(self.thermostat))
        print('+' * 100)

    def ctof(self, temp_c):
        return temp_c * 1.8 + 32


    def ftoc(self, temp_f):
        return (temp_f - 32) / 1.8


def main():
    # Create the configuration file parser object and start the CherryPy server
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    port = config.getint('Meta', 'port')
    host = config.get('Meta', 'host')
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_port': port,
                            'server.socket_host': host,
                            'cors.expose.on': True})
    cherrypy.quickstart(Coordinator(config))


main()
