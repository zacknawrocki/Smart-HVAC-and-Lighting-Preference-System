import time, sys, requests, os
for module in ['HVAC', 'time_of_flight', 'color_sensors', 'lights']:
	sys.path.append(os.environ["HOME"] + "/catkin_ws/src/scr_control/scripts/" + module)
import SCR_HVAC_client as hvac_control
import SCR_TOF_client  as tof_control
import SCR_COS_client  as cos_control
import SCR_OctaLight_client  as light_control
import numpy as np

def post_request(name, data):
	requests.post('http://192.168.0.2:5000/' + name, json=data)