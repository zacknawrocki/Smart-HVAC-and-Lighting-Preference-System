import sys, os, time, math, json
import numpy as np
import scipy
print(scipy.__version__)
from requests import post
from scipy.spatial.distance import cdist
import scipy.stats
import scipy.ndimage
from scipy.ndimage.filters import maximum_filter
from scipy.misc import toimage
from skimage.measure import label, regionprops
from skimage import morphology
import matplotlib.pyplot as plt
from skimage.io import imread, imsave

freq_comp_array = np.loadtxt( "freq_comp_array.txt", delimiter =',' );
sensor2Exy_dims = np.loadtxt( "sensor2Exy_dims.txt", delimiter =',' );
cos_comp_array = np.loadtxt( "cos_comp_array.txt", delimiter =',' );
tof_occ_zones = np.loadtxt("tof_occ_zones.txt", delimiter = ',');
rgb_occ_zones = np.loadtxt("rgb_occ_zones_rosconfig_final.txt", delimiter = ',');
zones_rgb2tof = np.loadtxt("zones_rgb2tof.txt", delimiter = ',');
zones_tof2rgb = np.loadtxt("zones_tof2rgb.txt", delimiter = ',');
light_tofzones = np.loadtxt("light_tofzones_nomiddle.txt", delimiter = ',');

# fid = "east_window_tof_locations.txt";
# east_win_locs = np.loadtxt( fid, delimiter =',' );
# fid = "north_window_tof_locations.txt";
# north_win_locs = np.loadtxt( fid, delimiter =',' );

fidOcc = "/home/arunas/catkin_ws/src/scr_control/scripts/Toufiq/Occupancy_info.txt";


pose_thresh = 1.3; light_thresh = 2000;
zones2Locs = tof_occ_zones[:,0:2]; zones2Grid = tof_occ_zones[:,2:4];
tau_door = 15;  tau_occs = 30; tau_neigh = 13;
#door_loc = [[73,3]]; # door_loc = [[65,1]];
door_loc = [[0,155]];
win_counter_thresh = 20;


def getClosestLightFixture( occFeats ):
	for n in range(0,np.shape(occFeats)[0]):
		# loc = occFeats[n,0:2]; loc = np.asarray(loc); loc = loc[np.newaxis,:]; 
		# print(occFeats)
		loc = np.zeros((1,2)); loc[0,0] = occFeats[n][0]; loc[0,1] = occFeats[n][1]; 
		idx = np.argmin(cdist(loc, light_tofzones));
		occFeats[n][6] = idx;

	return occFeats

def respondOccActivities( num, occlocs, numSit, numStand, win_counter, win_counter_bool):
	# print(num)
	occsActs = np.zeros((4,1));

	# if num != 0:
	occsActs[0,0] = num; # total occupants
	# occsActs[1,0] = numStand;
	# occsActs[2,0] = numSit;

	occsActs[3,0] = 0; # fall detection

	for i in range( 0, np.shape(occlocs)[0]):
		# print('WLoc:', occlocs[i,:]);

		# north window
		if occlocs[i,0] <= 7 and occlocs[i,1] <= 40:
			print('NorthWinOccupied', win_counter[0,0], 'Location: ', occlocs[i,:] )
			if win_counter[0,0] <= win_counter_thresh + 2:
				win_counter[0,0] += 1;

		else:
			if win_counter[0,0] > 0:
				win_counter[0,0] -= .025;


		# east window
		if (10 <= occlocs[i,0] <= 70) and (152 <= occlocs[i,1] <= 160): 
			print('EastWinOccupied', win_counter[1,0], 'Location: ', occlocs[i,:] );
			if win_counter[1,0] <= win_counter_thresh + 2:
				win_counter[1,0] += 1;

		else:
			if win_counter[1,0] > 0:
				win_counter[1,0] -= .05;


		# above threshold count
		for i in range(0,2):
			if win_counter[i,0] >= win_counter_thresh:
				win_counter_bool[i,0] = 1;
			else:
				win_counter_bool[i,0] = 0;

		occsActs[1,0] = win_counter_bool[0,0];
		occsActs[2,0] = win_counter_bool[1,0];

		# print('Counter', win_counter);
	
	# print('Bool', win_counter_bool);
	np.savetxt( fidOcc, occsActs );

	return win_counter, win_counter_bool


thingSpeakURL = 'http://192.168.0.2:5000/'

def transfer_to_Status_Screen(name, data):
	post('http://192.168.0.2:5000/' + name, json=data)



def compExy( Exy ):
	Exy = Exy * cos_comp_array;
	hgt_SCR = 2820; #mm
	Exy = hgt_SCR - Exy; # invert height - floor
	Exy[ Exy < 200 ] = 0; Exy[ Exy > 2300 ] = 0;
	# # print('Exy_beforecomp:', np.sum(Exy))

	# compensate diff sections Exy = Exy * freqHgt;
	for i in range(0,18,1):
		idx = sensor2Exy_dims[i,:];
		idx1 = int(idx[1])-1; idx2 = int(idx[2]); 
		idx3 = int(idx[3])-1; idx4 = int(idx[4]);
		temp = Exy[ idx1:idx2, idx3:idx4  ];
		temp = np.polyval( freq_comp_array[i,:], temp);
		Exy[ idx1:idx2, idx3:idx4  ] = temp;

	Exy = 0.001 * Exy; #m

	return Exy

def createFxy( Exy, Bxy ):
	tempBxy = Bxy.copy();
	tempBxy[ (Exy - tempBxy ) >= 0.2] = 0;
	Fxy = Exy - tempBxy;
	Fxy[Fxy<0.1] = 0; Fxy[Fxy>2.3] = 0;

	return Fxy

# Occupancy Mapping Function 
def getOMaps( Fxy, Debug ):    
	bw = Fxy > 0.1
	bw = morphology.remove_small_objects( bw, 8 )     # Fxy[ (bw==0) ] = 0;
	Fxy = scipy.signal.medfilt2d(Fxy, kernel_size=3)

	# Fxy = np.delete( Fxy, [26,27,28,29,48,49,50], 0)
	# Fxy = np.delete( Fxy, [26,27,28,29,48,49,50], 0);	
	Fxy = np.delete( Fxy, [20,21], 1)

	H = 0.2 * np.matrix(' 0 1 0; 1 1 1; 0 1 0 ')
	tFxy = scipy.ndimage.correlate(Fxy, H, mode='constant')

	# tFxy = Fxy; ##########################

	rng =  np.linspace(0, 3.0, num=100)

	psit = [0.94,0.17]; pstand = [1.58, 0.38]; # pstand = [1.6, 0.26];

	alpha = scipy.stats.norm( psit[0], psit[1] ).pdf(rng)
	alpha = np.max(alpha)
	
	sit = scipy.stats.norm( psit[0], psit[1] ).pdf(tFxy)
	sit = sit / alpha

	beta = scipy.stats.norm( pstand[0], pstand[1] ).pdf(rng)
	beta = np.max(beta)

	stand = scipy.stats.norm( pstand[0], pstand[1] ).pdf(tFxy)
	stand = stand / beta

	tFxy[ (sit<0.5) & (stand<0.5)] = 0;
	bw = tFxy > 0.1; bw = morphology.remove_small_objects( bw, 8 )
	tFxy[ (bw==0) ] = 0;

	if Debug:
		tFxy = Fxy;

	labels = label(tFxy, neighbors = 8);
	regions = regionprops(labels, coordinates='rc');

	num = len( regions );

	occlocs = []; occarea = []; occMAL = []; occhgt = []; occpose = []; 
	occFeats = [];
	Iobr = np.zeros((75,160));

	if num > 0:
		I = toimage(tFxy)
		strel = morphology.disk( 1 )
		Ie = morphology.erosion( I, strel)
		Id = morphology.dilation( I, strel)

		Iobr = morphology.reconstruction( Ie, Id )
		Fgm = morphology.local_maxima( Iobr )
		# # print( "Fgm = ", Fgm)
		Iobr[ (Fgm ==0 ) ] = 0

		labels = label(Fgm)	
		regions = regionprops(labels, tFxy, coordinates='rc')

		num = len( regions )
		occFeats = np.zeros((num,8)); # current location(2), hgt, pose, previous location(2), light, label

		if num > 0:
			for props in regions:
				occlocs.append(props.centroid)
				occarea.append( props.mean_intensity )
				# occMAL.append( props.major_axis_length )
				occhgt.append( props.max_intensity)

			occpose = np.asarray(occhgt);
			occpose = np.asarray([occpose > pose_thresh]);
			occpose = occpose * 1.0;

			locs = np.asarray(occlocs); locs = locs[np.newaxis,:];
			hgts = np.asarray(occhgt); hgts = hgts[np.newaxis,:]; 
			occFeats[:,0:2] = np.round(locs); # location
			occFeats[:,2] = np.round(hgts,2);
			occFeats[:,3] = occpose;

	return num, occFeats, Iobr


def fallDetect( Fxy ):
	bw = Fxy > 0.1
	bw = morphology.remove_small_objects( bw, 8 )
	Fxy[ (bw==0) ] = 0;
	Fxy = scipy.signal.medfilt2d(Fxy, kernel_size=3)

	# Fxy = np.delete( Fxy, [26,27,28,29,48,49,50], 0)
	Fxy = np.delete( Fxy, [26,27,28,29,48,49,50], 0)
	Fxy = np.delete( Fxy, [20,21], 1)

	H = (1/9) * np.ones((3,3))
	tFxy = scipy.ndimage.correlate(Fxy, H, mode='constant')

	tFxy = Fxy;

	rng =  np.linspace(0, 3.0, num=100)

	pfall = [0.3, 0.08];

	eta = scipy.stats.norm( pfall[0], pfall[1] ).pdf(rng)
	eta = np.max(eta)
	
	fall = scipy.stats.norm( pfall[0], pfall[1] ).pdf(tFxy)
	fall = fall / eta

	tFxy[ (fall>=0.5) ] = 255;
	tFxy[ (fall<0.5) ] = 0;
	bw = tFxy > 0.1
	bw = morphology.remove_small_objects( bw, 16 )
	tFxy[ (bw==0) ] = 0; 

	labels = label(tFxy, neighbors = 8)
	regions = regionprops(labels, coordinates='rc')

	num = len( regions );
	fall_locs = [];

	if num > 0:
		for props in regions:
			fall_locs.append( props.centroid)
			# fall_hgt.append( props.max_intensity)

	return num, fall_locs, tFxy


def rgbZones( magRGB ):
	# check if magnitude >= light thresh == occupied zone
	# magRGB = bRGB[:,3];
	currRGBgrid = np.zeros((5,14));
	zones_rgb = np.asarray(magRGB);
	zones_rgb = np.asarray([zones_rgb > 0.8]);
	zones_rgb = zones_rgb * 1.0;

	for sensor in range(0,53):
		if zones_rgb[0,sensor] == 1:
			currRGBgrid[int(rgb_occ_zones[sensor, 2]), int(rgb_occ_zones[sensor, 3])] = 1;

	return zones_rgb, currRGBgrid


def nearestRGB(MorphFeats, bRGB):
	bRGB = bRGB[0:53,3];
	bRGB = abs(bRGB);
	numlocs = np.shape(MorphFeats)[0];
	newMorphFeats = np.zeros((numlocs, 10));
	newMorphFeats[:,0:4] = MorphFeats[:,0:4];

	for l in range(0,numlocs):
		loc = newMorphFeats[l,0:2]; loc = np.asarray(loc); loc = loc[np.newaxis,:]; 
		distRGB = cdist(loc, rgb_occ_zones[:,0:2]);
		# # print(np.shape(distRGB), np.shape(bRGB));
		newMorphFeats[l,4] = bRGB[np.argmin(distRGB)];
		newMorphFeats[l,5] = np.amin(distRGB);
	

	# # print( 'nMF:', newMorphFeats)
	return newMorphFeats


def createCorrMatrix( Feats_1, Feats_2):
	num1 = np.shape(Feats_1)[0]; num2 = np.shape(Feats_2)[0]; corrM = np.zeros((num1, num2));

	for a in range(0,num1):
		loc = Feats_1[a][0:2]; loc = np.asarray(loc); loc = loc[np.newaxis,:]; 
		hgt = Feats_1[a][2]; pose = Feats_1[a][3];

		if cdist( loc, door_loc ) <= 5:
			corrM[a,:] = 1000;

		for b in range(0,num2):
			temp = Feats_2[b,:]; temp = temp[np.newaxis,:]
			loc2 = Feats_2[b,0:2]; loc2 = loc2[np.newaxis,:]; 
			hgt2 = Feats_2[b,2]; pose2 = Feats_2[b,3];

			# corrM[a,b] = 0.5 * ( abs(loc[0] - loc2[0]) + abs(loc[1] - loc2[1]) ) + 0.3 * abs(hgt-hgt2);
			# corrM[a,b] = cdist(loc,loc2) + 0.3 * abs(hgt-hgt2) + 0.5 * abs(pose-pose2);
			corrM[a,b] = cdist(loc,loc2) + 0.3 * abs(hgt-hgt2);

			if cdist( loc2, door_loc ) <= 5:
				corrM[:,b] = 1000;

	return corrM


def Gobble( prevOccs, currOMapOccs, currMorphOccs, labels ):
	numprev = np.shape(prevOccs)[0]; numOMap = np.shape(currOMapOccs)[0];
	numMorph = np.shape(currMorphOccs)[0];

	trackOccs = []; possOccs = []; missOccs = [];

	if numprev == 0 and numOMap > 0:
		for o in range(0,numOMap):
			loc = currOMapOccs[o,0:2]; loc = loc[np.newaxis,:];
			hgt = currOMapOccs[o,2];

			if cdist( loc, door_loc ) > 5 and cdist( loc, door_loc ) <= tau_door and hgt > 1.4 :
				currOMapOccs[o,4:6] = -1 * np.ones((1,2));

				# ASSIGN LABEL
				currOMapOccs[o,7] = np.amin(labels);
				del labels[np.argmin(labels)]; # remove label from consideration

				# Update occupant information
				trackOccs.append(currOMapOccs[o]);
				# print('New: empty', currOMapOccs[o])
			else:
				possOccs.append(currOMapOccs[o]);
				# print('Possible: empty', currOMapOccs[o])

	elif numprev > 0:
		statusPrev = np.zeros((numprev,1));

		if numOMap > 0:
			statusOMap = np.zeros((numOMap,1)); # check for matches and new entries
			corrOMap = createCorrMatrix( prevOccs, currOMapOccs );
		else:
			corrOMap = 1000 * np.ones((numprev, numprev));

		if numMorph > 0:
			corrMorph = createCorrMatrix( prevOccs, currMorphOccs );
		else:
			corrMorph = 1000 * np.ones((numprev, numprev));

		if numMorph > 0 and numOMap > 0:
			corrMorphOMap = createCorrMatrix( currOMapOccs, currMorphOccs );
			# # print('\n CMO: ', corrMorphOMap);

			for o in range(0, numMorph):
				if np.amin(corrMorphOMap[:,o]) < 6: ## similar morph and omap
					corrMorph[:,o] = 1000;
		else:
			corrMorphOMap = 1000 * np.ones((numMorph, numMorph));



		for p in range(0,numprev):
			loc = prevOccs[p][0:2]; loc = np.asarray(loc); loc = loc[np.newaxis,:]; 
			hgt = prevOccs[p][2]; pose = prevOccs[p][3]; occlbl = prevOccs[p][7];
			# print('pOcss', prevOccs[p])

			minval_OMap = np.amin(corrOMap[p,:]); minidx_OMap = np.argmin(corrOMap[p,:]) ;
			minval_Morph = np.amin(corrMorph[p,:]); minidx_Morph = np.argmin(corrMorph[p,:]);

			# # print('MINVAL: ', minval_OMap, minval_Morph)

			if (minval_OMap < tau_occs) and (minval_OMap ==  np.amin(corrOMap[:, minidx_OMap])):	
				currOMapOccs[minidx_OMap,4:6] = prevOccs[p][0:2];

				currOMapOccs[minidx_OMap, 7] = prevOccs[p][7]; # label 

				trackOccs.append(currOMapOccs[minidx_OMap]);
				statusOMap[minidx_OMap] = 1; corrOMap[:,minidx_OMap] = 1000;
				# print('Tracked: OMap', currOMapOccs[minidx_OMap] );

			elif (minval_Morph < tau_occs ) and (minval_Morph ==  np.amin(corrMorph[:, minidx_Morph])) \
						and currMorphOccs[minidx_Morph,2] > 0.8:	
				if cdist( loc, door_loc ) > tau_door or ( cdist( loc, door_loc ) < tau_door and pose == 0 ):	
					currMorphOccs[minidx_Morph,4:6] = prevOccs[p][0:2];	
					
					currMorphOccs[minidx_Morph,7] = prevOccs[p][7];
					trackOccs.append(currMorphOccs[minidx_Morph]);
					corrMorph[:,minidx_Morph] = 1000;
					# print('Tracked: Morph', currMorphOccs[minidx_Morph]);

				else:
					# EXIT : return label for selection
					labels.append(prevOccs[p][7]);
					continue;					
					# print('Exit w/ door', prevOccs[p]);

			# elif pose == 0  and ( abs(loc[0,0] - 20) < 2 or abs(loc[0,0] - 45) < 2) and mag > 3000:
			# 	trackOccs.append(prevOccs[p]);
			# 	# print('Missing: near table', prevOccs[p]);

				
			else:
				if cdist( loc, door_loc ) <= tau_door:
					# EXIT : return label for selection
					labels.append(prevOccs[p][7]);
					continue;
					# print('Exit', prevOccs[p] );
				else:					
					missOccs.append(prevOccs[p]);
					# print('Missing', prevOccs[p])

		
		numMiss = np.shape(missOccs)[0]; missStatus = np.zeros((numMiss,1));
		numTrack = np.shape(trackOccs)[0];

		# print('numMiss:', numMiss);

		for o in range(0,numOMap):
			if statusOMap[o] == 0:
				loc = currOMapOccs[o,0:2]; loc = loc[np.newaxis,:];
				hgt = currOMapOccs[o,2]; # mag = currOMapOccs[o,5]; drgb = currOMapOccs[o,6];

				for t in range (0,numTrack):
					locT = trackOccs[t][0:2]; locT = locT[np.newaxis,:];
					hgtT = trackOccs[t][2]; 

					if cdist( loc, locT ) <= 13:
						if hgt > hgtT:
							currOMapOccs[o,7] = trackOccs[t][7]; # update label
							trackOccs[t] = currOMapOccs[o];

						statusOMap[o] = 1;
						# print('too close: poss and tracked', loc, locT)

				for m in range(0,numMiss):
					if missStatus[m] == 0 and statusOMap[o] == 0:
						locM = missOccs[m][0:2]; locM = locM[np.newaxis,:];
						hgtM = missOccs[m][2]; 

						if cdist( loc, locM ) <= 50 and cdist( loc, door_loc ) > 5:
							currOMapOccs[o,4:6] = missOccs[m][0:2];

							# ASSIGN LABEL
							currOMapOccs[o,7] = missOccs[m][7];
							# del labels[np.argmin(labels)]; # remove label from consideration

							# UPDATE OCCUPANT INFORMATION
							trackOccs.append(currOMapOccs[o]);
							# print('Prev. Missing:', currOMapOccs[o]);
							missStatus[m] = 1;	statusOMap[o] = 1;

						# else:
						# 	trackOccs.append(missOccs[m]);
						# 	# print('Missing:', missOccs[m] );

			if statusOMap[o] == 0: # no matches: new occupant?
				if cdist( loc, door_loc ) > 5 and cdist( loc, door_loc ) <= 2 * tau_door and hgt > 1.35:
					currOMapOccs[o,4:6] = -1 * np.ones((1,2));
					
					# ASSIGN LABEL
					currOMapOccs[o,7] = np.amin(labels);
					del labels[np.argmin(labels)]; # remove label from consideration

					# UPDATE OCCUPANT INFORMATION
					trackOccs.append(currOMapOccs[o]);
					# print('New: Door Poss', currOMapOccs[o]);
				# elif mag > 6000 and drgb < 5:
				# 	trackOccs.append(currOMapOccs[o]);
				# 	# print('New: RGB Poss', currOMapOccs[o]);

				elif cdist( loc, door_loc ) > 5:
					possOccs.append(currOMapOccs[o]);
					# print('Possible', currOMapOccs[o])


		for m in range(0,numMiss):
			if missStatus[m] == 0:
				locM = missOccs[m][0:2]; locM = locM[np.newaxis,:];
				hgtM = missOccs[m][2]; 

			# 	for t in range (0,numTrack):
			# 		locT = trackOccs[t][0:2]; locT = locT[np.newaxis,:];
			# 		hgtT = trackOccs[t][2]; 

			# 		if cdist( locM, locT ) <= tau_neigh:
			# 			if hgtM > hgtT:
			# 				trackOccs[t] = missOccs[m];
			# 			missStatus[m] = 1;
			# 			# print('too close: miss and tracked', locM, locT)


			# if missStatus[m] == 0:
				missOccs[m][4:6] = -1 * np.ones((1,2));
				trackOccs.append(missOccs[m]);
				# print('Missing, no matches:', missOccs[m] );

	return trackOccs, labels


