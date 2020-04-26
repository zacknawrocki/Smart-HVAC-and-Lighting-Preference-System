import sys, os, time,datetime, math, rospy, json
#os.chdir("/home/arunas/catkin_ws/src/scr_control/scripts/time_of_flight")
#sys.path.append(os.getcwd())
#import SCR_TOF_client as tof

for module in ['HVAC', 'time_of_flight', 'color_sensors', 'lights']:
	sys.path.append(os.environ["HOME"] + "/catkin_ws/src/scr_control/scripts/" + module)
import SCR_HVAC_client as hvac_control
import SCR_TOF_client  as tof_ros
import SCR_COS_client  as csensors_ros	
import SCR_OctaLight_client  as lights_ros
import numpy as np

os.chdir("/home/arunas/catkin_ws/src/scr_control/scripts/tk/tof_tracking/AuxFiles_Feb")
sys.path.append(os.getcwd())


time.sleep(15);
print('Capturing Sensor Data');

fid = "cos_comp_array.txt";
cos_comp_array = np.loadtxt( fid, delimiter =',' );

fid = "freq_comp_array.txt";
freq_comp_array = np.loadtxt( fid, delimiter =',' );

fid = "sensor2Exy_dims.txt";
sensor2Bxy_dims = np.loadtxt( fid, delimiter =',' );

hgt_SCR = 2820; #mm

def tofHgtComp( Bxy, freq_comp_array, sensor2Bxy_dims ):

	Bxy = hgt_SCR - Bxy;
	Bxy[ Bxy < 100 ] = 0;
	Bxy[ Bxy > 2300 ] = 0;

	# compensate diff sections Bxy = Bxy * freqHgt;
	for i in range(0,18,1):
		idx = sensor2Bxy_dims[i,:];
		idx1 = int(idx[1])-1; idx2 = int(idx[2]); 
		idx3 = int(idx[3])-1; idx4 = int(idx[4]);
		# print( idx1, idx2, idx3, idx4 )
		temp = Bxy[ idx1:idx2, idx3:idx4  ];
		# print(np.shape(temp))
		temp = np.polyval( freq_comp_array[i,:], temp);
		Bxy[ idx1:idx2, idx3:idx4  ] = temp;

	Bxy = 0.001 * Bxy; #m
	return Bxy

# begin detection
for i in range(0,20,1):
	if i==0 :
		Bxy = np.asarray(tof_ros.get_distances_all());
		Bxy = Bxy * cos_comp_array;
		Bxy = tofHgtComp( Bxy, freq_comp_array, sensor2Bxy_dims );
	else:
		tempBxy = np.asarray(tof_ros.get_distances_all());
		tempBxy = tempBxy * cos_comp_array;
		tempBxy = tofHgtComp( tempBxy, freq_comp_array, sensor2Bxy_dims );
		Bxy = 0.5 * ( Bxy + tempBxy );

	time.sleep(0.25);

np.savetxt("Bxy.txt", Bxy, delimiter = ',');

# np.savetxt("C:\\Users\\LESA\\AppData\\Local\\Packages\\CanonicalGroupLimited.Ubuntu16.04onWindows_79rhkp1fndgsc\\LocalState\\rootfs\\home\\lesa\\catkin_ws\\src\\scr_control\\scripts\\tk\\TRACKING_FEB\\AuxFiles_Feb\\Bxy.txt", Bxy, delimiter = ',');
