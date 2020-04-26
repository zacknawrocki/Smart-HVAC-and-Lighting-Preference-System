from kivy.logger import Logger
import threading
import requests
import time

THREAD_DELAY = 5  # One-time delay before threads are started (seconds)
HEARTBEAT_DELAY = 10  # Delay between heartbeat messages (seconds)
UPDATE_SENSORS_DELAY = 10  # Delay between temperature sensor queries (seconds)
QUERY_TEMPERATURE_DELAY = 40  # Delay between optimized thermostat temp queries (seconds)


class Coordinator(object):
    """
    This class acts as a proxy for the coordinator server. The preference client
      uses this class to communicate with the coordinator server.

    This Coordinator class initializes either 1 or 3 threads, depending on its ID.
      If the preference client is assigned ID 1 in its configuration file, it is
      considered the primary preference client and will communicate with the
      coordinator server to provide temperature sensor data and query for the
      optimized thermostat temperature. These operations are performed in
      the update_sensors_thread and query_temperature_thread threads. Every
      preference client, regardless of ID, will also run a heartbeat thread to
      let the coordinator server that it is still online.
    """

    def __init__(self, app, host, port, node_id, pos_x, pos_y):
        """  Initialize the coordinator proxy based on configuration settings.
        :param host: IP address of the coordinator server
        :param port: port of the coordinator server
        :param node_id: unique ID of the preference client
        :param pos_x: x-coordinate of the preference client in the room
        :param pos_y: y-coordinate of the preference client in the room
        :param use_hvac: boolean specifying whether or not the preference client
                         should communicate with the HVAC server (set to false for
                         off-site testing)
        """
        self.app = app
        self.host = host
        self.port = port
        self.node_id = node_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.sensors = {}
        self.admin_system_on = True
        self.running = True
        self.connected = True
        self.thermostat_setting = None
        self.estimated_temperature = float(70)
        self.node_state_thread = None
        self.update_sensors_thread = None
        self.query_temperature_thread = None
        self.initialize_threads()

    def initialize_threads(self):
        """ Initialize threads, depending on preference client ID.
        This function starts the heartbeat thread regardless of ID, but only
          starts the sensor update and temperature query threads for the
          primary preference client, which has ID 1.
        """
        self.node_state_thread = threading.Thread(target=self.get_node_state)
        self.node_state_thread.start()

    def start_node(self):
        """ Make an HTTP request to the coordinator server for start_node.
        :return: JSON data returned from the coordinator server
        """
        response = self.request("start_node", {
            'node_id': self.node_id,
            'pos_x': self.pos_x,
            'pos_y': self.pos_y
        })
        if response:
            self.sensors = response.json()

    def stop_node(self):
        """ Make an HTTP request to the coordinator server for stop_node.
        :return: True if request was successful or False otherwise
        """
        self.running = False
        response = self.request("stop_node", {'node_id': self.node_id})
        if response:
            return True if response.status_code is 200 else False
        return False

    def add_user(self, username, preference):
        """ Make an HTTP request to the coordinator server for add_user.
        :param username: unique username for the new user
        :param preference: integer temperature preference for the user
        :return: True if request was successful or False otherwise
        """
        response = self.request("add_user", {
            'username': username,
            'preference': preference
        })

        print("Client Coordinator")
        print(preference)
        
        if response:
            return True if response.status_code is 200 else False
        return False

    def get_user_preference(self, username):
        """ Make an HTTP request to the coordinator for get_preference.
        :param username: unique username for the new user
        :return: JSON response from coordinator containing user preference
        """
        response = self.request("get_preference", {
            'username': username
        })
        if response:
            return response.json()
        return None

    def get_user_names(self):
        """ Make an HTTP request to the coordinator for get_user_names.
        :return: list containing all user names returned from coordinator
        """
        response = self.request("get_user_names", None)
        if response:
            usernames = []
            for username in response.json():
                usernames.append(str(username))
            print usernames
            return usernames
        return None

    def add_user_to_node(self, username):
        """ Make an HTTP request to the coordinator for add_user_to_node.
        :param username:
        :return:
        """
        response = self.request("add_user_to_node", {
            'username': username,
            'node_id': self.node_id
        })
        if response:
            return True if response.status_code is 200 else False
        return False

    def remove_user_from_node(self, username):
        """ Make an HTTP request to the coordinator for remove_user_from_node.
        :param username: unique username for the user
        :return: True if the request was successful or False otherwise
        """
        response = self.request("remove_user_from_node", {
            'username': username,
            'node_id': self.node_id
        })
        if response:
            return True if response.status_code is 200 else False
        return False

    def update_preference(self, username, preference):
        """ Make an HTTP request to the coordinator for update_preference.
        :param username: unique username for the user
        :param preference: new integer temperature preference
        :return: True if the request was successful or False otherwise
        """
        response = self.request("update_preference", {
            'username': username,
            'preference': preference
        })
        if response:
            return True if response.status_code is 200 else False
        return False

    def remove_user(self, username):
        Logger.info('Removing user %s' % username)
        response = self.request("remove_user", {
            'username': username
        })
        if response:
            return True if response.status_code is 200 else False
        return False

    def get_default_temp(self):
        response = self.request('get_default_temp', {})
        if response:
            return int(response.text)
        return False

    def change_default_temp(self, temp):
        Logger.info('Changing default temp to %d' % temp)
        response = self.request('change_default_temp', {
            'temp': temp
        })
        if response:
            return True if response.status_code is 200 else False
        return False

    def get_temp_offset(self):
        response = self.request('get_temp_offset', {
            'node_id': self.node_id
        })
        if response:
            return int(response.text)
        return False

    def change_temp_offset(self, offset):
        Logger.info('Changing temp offset to %d' % offset)
        response = self.request('change_temp_offset', {
            'offset': offset,
            'node_id': self.node_id
        })
        if response:
            return True if response.status_code is 200 else False
        return False

    def get_state(self):
        """ Make an HTTP request to the coordinator for get_state.
        :return: system state string returned by the coordinator
        """
        response = self.request("get_state", {})
        if response:
            return response
        return None

    def get_node_state(self):
        """ Periodically make an HTTP request to the coordinator to get the
        current state.
        """
        time.sleep(THREAD_DELAY+1)
        timer_counter = 0
        while True:
            if not self.running:
                return
            if timer_counter % HEARTBEAT_DELAY == 0:
                Logger.info('Requesting node state')
                data = self.request("get_node_state", {'node_id': self.node_id})
                if data:
                    Logger.info('Successfully received node state')
                    data = data.json()
                    
                    self.estimated_temperature = data['estimated_temp']

                    self.thermostat_setting = data['thermostat_temp']
                    self.app.sm.get_screen('UserMenu').update(self.thermostat_setting,
                                                              self.estimated_temperature)
                    self.app.sm.get_screen('Status').update(self.thermostat_setting,
                                                            self.estimated_temperature,
                                                            data['sensors'])
                else:
                    Logger.error('Unable to receive node state')
                timer_counter = 0
            time.sleep(1)
            timer_counter += 1

    def request(self, path, data):
        """ Send a request to the coordinator server.
        :param path: API path for the request
        :param data: data to be contained in the request
        :return: response from the coordinator server
        """
        url_str = 'http://' + self.host + ':' + str(self.port) + '/' + path
        try:
            response = requests.post(url=url_str, data=data, timeout=1.5)
            self.connected = True
            return response
        except Exception as e:
            Logger.error(str(e))
            self.connected = False
            return None

    def c_to_f(self, c):
        """ Convert celsius to fahrenheit
        :param c: temperature in celsius
        :return: temperature in fahrenheit
        """
        return (c*1.8) + 32

    def f_to_c(self, f):
        """ Convert fahrenheit to celsius
        :param f: temperature in fahrenheit
        :return: temperature in celsius
        """
        return (f-32.0) / 1.8
