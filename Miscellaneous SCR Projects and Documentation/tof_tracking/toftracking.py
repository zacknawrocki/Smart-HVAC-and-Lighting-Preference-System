import sys, os, time,datetime, math, rospy, json
import numpy as np
from pytz import timezone, utc

for module in ['HVAC', 'time_of_flight', 'color_sensors', 'lights']:
	sys.path.append(os.environ["HOME"] + "/catkin_ws/src/scr_control/scripts/" + module)
import SCR_HVAC_client as hvac_control
import SCR_TOF_client  as tof_ros
import SCR_COS_client  as csensors_ros	
import SCR_OctaLight_client  as lights_ros

os.chdir("/home/arunas/catkin_ws/src/scr_control/scripts/zack/tof_tracking/AuxFiles_toftracking")
sys.path.append(os.getcwd())

import auxTracking as tof_aux 	# import needed tof processing functions

prevOccs = None


def local_time():
    # ignore day/month/year
    t = datetime.datetime.now().time()
    h, m, s, ms = t.hour, t.minute, t.second, t.microsecond//1000
    return "%02d:%02d:%02d.%02d" % (h, m, s, ms)



if __name__ == '__main__':
	##
	# LOAD BACKGROUNDS: TOF
	prevOccs_file = open('prevOccs.txt', 'w+')
	prevOccs_file.close()

	try:
		Bxy = np.loadtxt( "Bxy.txt", delimiter = ',' );
		# Bxy = Bxy * cos_comp_array;
	except:
		try:
			Bxy = np.loadtxt( "Bxy.txt", delimiter = ' ' );

		except:
			print('No Background Image Found: TOF')
			Bxy = np.zeros((75,160));

	##
	win_counter = np.zeros((2,1)); # 1. north, 2. east
	win_counter_thresh = 20;
	win_counter_bool = np.zeros((2,1));		

	pose_thresh = 1.35;
	prevOccs = []; 
	frame = 0; filesavetrig = 1;

	labels = list(range(1,50));

	##
	timestr = time.strftime("%Y%m%d-%H%M%S");
	#fname = 'OccLog_' + timestr + '.txt';
	fname = 'OccLog.txt';
	OccLog = open( fname, 'w' ); OccLog = open( fname, 'a' );

	OccLog.write(local_time()); OccLog.write('\n\n'); 

	print('ToF Tracking Active')

	while(1):
		##
		try:
			# Exy = np.zeros((75,160));
			Exy = (tof_ros.get_distances_all());
			Exy = np.flipud(np.fliplr(Exy));

		except:
			print('ToF Reading Error');
			Exy = np.zeros((75,160));

		##
		Fxy = tof_aux.compExy(Exy);

		Fxy = tof_aux.createFxy(Fxy,Bxy); 
		#print((Fxy));


		##
		num, OMapFeats, Fgm = tof_aux.getOMaps(Fxy, Debug = False); # occupancy mapping
		num_Morph, MorphFeats, Fgm_Morph = tof_aux.getOMaps(Fxy, Debug = True); # morph processing

		#numfalls, fall_locs, tFxy = tof_aux.fallDetect(Fxy); # fall detection

		##
		tempOccs, labels = tof_aux.Gobble(prevOccs, OMapFeats, MorphFeats, labels);
		prevOccs = tempOccs;

		prevOccs_file = open('prevOccs.txt', 'w')	
		prevOccs_file.write(str(prevOccs))
		prevOccs_file.close()

		numOcc = np.shape(prevOccs)[0];


		##
		numSit = 0; numStand = 0;
		occlocs = np.zeros((numOcc,2));
		for t in range (0,numOcc):
			occlocs[t,0] = prevOccs[t][0];
			occlocs[t,1] = prevOccs[t][1];

			if prevOccs[t][2] > pose_thresh:
				numStand += 1;
			else:
				numSit += 1;


		#print(num,num_Morph);
		#print(numSit+numStand);

		##
		if numOcc > 0:
			# print(prevOccs)
			OccFeats = [ item.tolist() for item in prevOccs];
			print(OccFeats)

			#OccFeats = tof_aux.getClosestLightFixture( OccFeats );	
			# print('OF:', OccFeats)



			try:
				# write to TOF log file
				OccLog.write(local_time()); OccLog.write('\n'); 
				OccLog.write(str(numOcc)); OccLog.write('\n');
				OccLog.write('{}\n\n'.format(OccFeats));
			except:
				print('Error Updating Occupant Log File')


			filesavetrig = 1;

		elif numOcc <= 0 and filesavetrig == 1:

			try:
				OccFeats = [ item.tolist() for item in np.zeros((0,8))];
				# print('OF:', OccFeats)
				# write to TOF log file
				OccLog.write(local_time()); OccLog.write('\n'); 
				OccLog.write(str(numOcc)); OccLog.write('\n');
				OccLog.write('{}\n\n'.format(OccFeats));
			except:
				print('Error Updating Occupant Log File')

			filesavetrig = 0;

		##
		try:
			tof_aux.transfer_to_Status_Screen('Status_Occupancy', {"Total": numSit+numStand, \
														"Standing": numSit, "Sitting": numStand, "Lying": 0});
		except:
			print('Error Updating to Status Screen')
