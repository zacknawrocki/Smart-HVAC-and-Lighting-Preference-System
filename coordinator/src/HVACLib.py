''' 
This file serves as a library, that can process HVAC commands in the Smart Conference Room. The HVAC
Object communicates with the HVAC Server, to control the SCR and/or receive information about it, in
terms of heating, ventilation, and air conditioning.
''' 

# Modules
import socket
import time
import datetime
import re

# HVAC Object
class HVAC:
	def __init__(self, host = '192.168.0.36', port = 60606): # Connection between server and client is established during this initialisation
		self.s = socket.socket()
		self.host = host
		self.port = port
		try:
			self.s.connect((self.host,self.port))
			# self.sendMessage("read t1")				#test message to raise exception if not connected
		except:
			print("Connect using changeHostPort(host, port)")

	def changeHostPort(self, host, port):
		self.s.close()
		self.s.connect((host,port))
		self.host = host
		self.port = port

	def sendMessage(self, message):
		self.s.send(message.encode())	#send the message
		data = self.s.recv(1024).decode()
		print ('Received from server: ' + data)
		return data

	def close(self): # Closes the connection between server and current client 
		self.sendMessage("quit")
		self.s.close()

	def reset(self): # Hands over to BMS control
		self.sendMessage("bms")

	def setTemp(self, temp): # Sets desired temperature in the thermostat
		self.tempval = temp
		message = "set temp " + str(temp)	# set the message to be a certain temperature
		self.sendMessage(message)	# set temperature value

	def setFan(self, speed): # Sets fan speed level to : low, medium or high
		self.sendMessage("set fan " + str(speed))
		
	# Sets the opening level (0 to 100%) of a valve mentioned by number.
	# number 1 : North Radiator, 2: East Radiator, 3: Heating coil in the ceiling, 4: Cooling coil in the ceiling
	def setEP(self, number, level): 
		voltage = 5.0*level/100
		print(voltage)
		self.sendMessage("set ep" + str(number) + " " + str(voltage))
		
	# Sets the feedback temperature value for set point control, by default (if not set) the system takes feedback temperature 
	# from zone 4 (thermostat) temperature sensor
	def setFeedbackTemp(self, temp): 
		self.sendMessage("set feed " + str(temp))

	def writeToFile(self, item): # Stores the collected data to a file if datalogging is true
		file = open(str(time.strftime("%m.%d.%Y"))+".txt", 'a')		#open a file with the current date in case code randomly stops
		file.write(str(time.strftime("%m.%d.%Y.%H.%M.%S\n")))
		file.write("%s\n" % item)
		file.close()

	def getTemp(self, number, datalogging): # Receives tempearature data from five temp sensors, mentioned through number
		data = self.sendMessage("read t" + str(number))
		temp = [float(s) for s in re.findall("\d+\.\d+", data)]
		if datalogging:
			self.writeToFile(data)		# write the value to the file
		print("TEMP FROM HVAC LIB IS" + str(temp))
		return temp[0]

	def getC02(self, datalogging): # Receives Co2 value from sensor
		data = self.sendMessage("read co2")	#read co2 value
		co2 = [float(s) for s in re.findall("\d+\.\d+", data)]
		if datalogging:
			self.writeToFile(data)		#write the value to the file
		return co2[0]

	def getHumid(self, datalogging): # Receives humidity value from sensor
		data = self.sendMessage("read rh")	#read humidity value
		hum = [float(s) for s in re.findall("\d+\.\d+", data)]
		if datalogging:
			self.writeToFile(data)		#write the value to the file
		return hum[0]

	def getTime(self, datalogging): # Gets current system time
		data = str(time.strftime("%M.%H.%d.%m"))
		if datalogging:
			self.writeToFile(str(data))		#write the value to the file
		return data

	def getEP(self, val, datalogging): # Gets EP of SCR
		if val == 1:
			data = self.sendMessage("read ep1")
		elif val == 2:
			data = self.sendMessage("read ep2")
		elif val == 3:
			data = self.sendMessage("read ep3")
		elif val == 4:
			data = self.sendMessage("read ep4")

		print(data)
		datalist = data.split()
		datafloat = float(datalist[3])
		print(datafloat)
		if datalogging:
			self.writeToFile(str(data))		#write the value to the file
		return datafloat



		