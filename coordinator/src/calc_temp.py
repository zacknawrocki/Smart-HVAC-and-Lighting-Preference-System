#!/bin/python

import numpy as np
from queries import Queries
import sqlite3

class HvacDB(object):
    def __init__(self, database, users=None, nodes=None, sensors=None, ambient=None):
        self.Users = users
        self.Nodes = nodes
        self.Sensors = sensors
        self.Ambient = ambient
        self.database_str = database

    def get_data(self):

        # get the SQLite database
        try:
            conn = sqlite3.connect(self.database_str)
        except Exception as e:
            print(e)
        cur = conn.cursor()
        users = cur.execute(Queries.GET_USERS).fetchall()
        nodes = cur.execute(Queries.GET_NODES).fetchall()
        sensors = cur.execute(Queries.GET_SENSORS).fetchall()
        ambient = cur.execute(Queries.GET_AMBIENT).fetchall()
        conn.close()

        # populate the objects used to calculate the temperature
        users = [User(users[i][0], users[i][1], users[i][2])
            for i in range(len(users))]
        nodes = [Node(nodes[i][0], nodes[i][4],
            np.array((nodes[i][1], nodes[i][2])).T, nodes[i][5])
            for i in range(len(nodes))]
        sensors = [Sensor(sensors[i][0], sensors[i][3], 
            np.array((sensors[i][1], sensors[i][2])).T) 
            for i in range(len(sensors))]
        #ambient = [Ambient(ambient[i][0], ambient_temp[i][1])
            #for i in range(len(ambient))]

        # parse out the unused nodes, then match the nodes to the users
        active_users = []
        active_nodes = []
        print("[CALC_TEMP]  Active Users:")
        for node in nodes:
            if node.CurrentUserId >= 0:
                active_nodes.append(node)
                for user in users:
                    if user.Id is node.CurrentUserId:
                        active_users.append(user)
                        node.CurrentUser = user
                        print("[CALC_TEMP]  User %d: %s with preference %.2f degrees"
                            % (user.Id, user.Name, user.Preference))
        print("[CALC_TEMP]  End active users\n")

        # remove inactive sensors
        active_sensors = []
        for sensor in sensors:
            if sensor.Temperature > 0:
                active_sensors.append(sensor)
            else:
                print("[CALC_TEMP]  Sensor %d is not being used" % sensor.Id)

        # update database with the active objects
        self.Users = active_users
        self.Nodes = active_nodes
        self.Sensors = active_sensors
        self.Ambient = ambient

    def calc_temp(self, last_temp, default_temp):

        # if there are no users or no sensors revert to a default temperature
        if not self.Nodes:
            return default_temp

        node_num = len(self.Nodes)
        sensor_num = len(self.Sensors)
        node_pos = np.empty([2,node_num])
        sensor_pos = np.empty([2,sensor_num])

        # get the preference array from the database
        T_prefs = np.empty([1,node_num])
        for i in range(node_num):
            T_prefs[0,i] = self.Nodes[i].CurrentUser.Preference

        T_offsets = np.empty([1,node_num])
        for i in range(node_num):
            T_offsets[0,i] = self.Nodes[i].TempOffset

        # if no sensors are online, return average of preferences
        if not self.Sensors:
            return np.mean(T_prefs)

        # get the node positions, arrange in a matrix and reshape to column vector
        node_pos = np.matrix([n.Pos for n in self.Nodes]).reshape((2*node_num,1))

        # get sensor positions from the database
        sensor_pos = np.matrix([sensor.Pos for sensor in self.Sensors]).T
        sensor_pos = np.tile(sensor_pos, (node_num, 1))

        # distance matrix where each row is a node and column a sensor
        distances = np.square(sensor_pos - node_pos)
        distances = np.sum(distances.reshape((2, node_num*sensor_num)), axis=0)
        distances = np.reshape(np.sqrt(distances), (node_num, sensor_num))

        # get weight matrix. closer the sensor to the node, the larger the weight
        total_dist = np.power(np.matrix(np.sum(distances, axis=1)),-1)
        normalized_distances = np.multiply(total_dist, distances)
        weights = np.ones([node_num,sensor_num]) - normalized_distances
        weights = weights/(sensor_num-1) if sensor_num > 2 else weights

        print weights

        # get sensor temps from the database
        sensor_temps = [sensor.Temperature for sensor in self.Sensors]

        # update estimated node temperature in the node objects
        T_est = np.matrix(sensor_temps)*weights.T
        for i in range(node_num):
            self.Nodes[i].EstimatedTemp = T_est[0,i]

        for node in self.Nodes:
            print("[CALC_TEMP]  Estimated temperature at node %d with user %s is %.2f degrees"
                % (node.Id, node.CurrentUser.Name, node.EstimatedTemp))
            conn = sqlite3.connect(self.database_str)
            cur = conn.cursor()
            cur.execute(Queries.UPDATE_NODE_TEMP, [float(node.EstimatedTemp), int(node.Id)])
            cur.execute(Queries.INSERT_HISTORICAL_NODE, [int(node.Id), int(node.CurrentUserId), float(node.EstimatedTemp)])
            conn.commit()
            conn.close()

        # output_temp = np.mean(2*T_prefs - T_est)
        # output_temp = np.mean(T_prefs + (last_temp - T_est))
        output_temp = np.mean(T_prefs + T_offsets)
        print("[CALC_TEMP]  The output temperature is %.2f degrees" % output_temp)

        # make sure the temperature is within the bounds
        if output_temp < 61:
            output_temp = 61
        elif output_temp > 79:
            output_temp = 79

        return output_temp


class Node(object):
    def __init__(self, NODE_ID, USER_ID, POS, TEMP_OFFSET):
        self.Id = NODE_ID
        self.Pos = POS
        self.CurrentUserId = USER_ID
        self.CurrentUser = User()
        self.TempOffset = TEMP_OFFSET
        self.EstimatedTemp = -1.

class Sensor(object):
    def __init__(self, SENSOR_ID, TEMP, POS):
        self.Id = SENSOR_ID
        self.Pos = POS
        self.Temperature = TEMP

class Ambient(object):
    def __init__(self, ID, TEMP):
        self.Id = ID
        self.Temperature = TEMP

class User(object):
    def __init__(self, USER_ID=None, NAME=None, PREF=None):
        self.Id = USER_ID
        self.Name = NAME
        PREF.split(" ")
        self.Preference = float(PREF[0])

def main(db, last_temp, default_temp):

    # get sqlite database
    db = HvacDB(db)
    db.get_data()

    # calculate the output temperature
    return db.calc_temp(last_temp, default_temp)
