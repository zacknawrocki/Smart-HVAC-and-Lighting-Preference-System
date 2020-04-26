import socket
import time
import random
import datetime
import re

class HVAC:
    # minimum = 18.0
    # maximum = 23.5
    # maxtime =.02 #Number of Hours
    # tempval = 18.0 #initial temperature value
    # timeinterval = 1 #5 minute intervals
    # datalogging = False

    def __init__(self, host = '192.168.0.36', port = 60606):
        self.s = socket.socket()
        self.s.settimeout(8)
        self.host = host
        self.port = port
        self.s.connect((self.host,self.port))
        # self.sendMessage("read t1")				#test message to raise exception if not connected

    def changeHostPort(self, host, port):
        self.s.close()
        self.s.connect((host,port))
        self.host = host
        self.port = port

    def sendMessage(self, message):
        self.s.send(message.encode())	#send the message (thermostat value)
        data = self.s.recv(1024).decode()
        print ('Received from server: ' + data)
        return data

    def close(self):
        self.sendMessage("quit")
        self.s.close()

    def force_close(self):
        self.s.close()

    def writeToFile(self, item):
        file = open(str(time.strftime("%m.%d.%Y"))+".txt", 'a')		#open a file with the current date in case code randomly stops
        file.write("%s\n" % item)
        file.close()

    def reset(self): # Hand over to BMS control
        self.sendmessage("bms")

    def setTemp(self, temp):
        self.tempval = temp
        message = "set temp " + str(temp)	#set the message to be a certain temperature
        self.sendMessage(message)	#set temperature value

    def setFan(self, speed):
        self.sendMessage("set fan " + str(speed))

    def setEP(self, number, level):
        voltage = 5.0*level/100
        print(voltage)
        self.sendMessage("set ep" + str(number) + " " + str(voltage))

    def setFeedbackTemp(self, temp):
        self.sendMessage("set feed " + str(temp))

    def getTemp(self, number):
        data = self.sendMessage("read t" + str(number))
        temp = [float(s) for s in re.findall("\d+\.\d+", data)]
        return temp[0]

    def getC02(self):
        data = self.sendMessage("read co2")	#read co2 value
        co2 = [float(s) for s in re.findall("\d+\.\d+", data)]
        if self.datalogging:
            self.writeToFile(data)		#write the value to the file
        return co2[0]

    def getHumid(self):
        data = self.sendMessage("read rh")	#read humidity value
        hum = [float(s) for s in re.findall("\d+\.\d+", data)]
        if self.datalogging:
            self.writeToFile(data)		#write the value to the file
        return hum[0]

    # def configureExperiment(self):
    # 	self.minimum = input("Enter Minimum Temperature Value (c): ")
    # 	self.maximum = input("Enter Maximum Temperature Value (c): ")
    # 	self.maxtime = input("Enter Length of Experiment (hours): ")
    # 	self.tempval = input("Enter initial temperature value (c): ")
    # 	self.timeinterval = input("Enter Time Interval (minutes): ")

    # def runExperiment(self):
    # 	self.datalogging = True
    # 	carbon = []
    # 	humid = []
    # 	desiredtemp = []
    # 	myinput = raw_input("Time to start experiment (ex: 18:00) (or enter \"now\") ")
    # 	if myinput == "now":
    # 		starttime=time.time()
    # 	else:
    # 		starttime = myinput.split(":")
    # 		while datetime.datetime.now().hour != int(starttime[0]):		#check every minute for the hour
    # 			time.sleep(60)
    # 		while datetime.datetime.now().minute != int(starttime[1]):	#check every minute for the minute
    # 			time.sleep(60)
    # 		starttime = time.time()

    # 	myrange = self.maximum - self.minimum
    # 	midpoint = (self.maximum + self.minimum)/2.0


    # 	for i in range(int(self.maxtime*60)):
    # 		if i/self.timeinterval == int(i/self.timeinterval):	#change temperature set point at every time interval
    # 			randnum = random.randrange(6,2*myrange+1,1)/2.0  #choose a value between 3 and myrange in steps of 0.5
    # 			if self.tempval > midpoint:	#adjust up or down
    # 				self.tempval -= randnum
    # 			else:
    # 				self.tempval += randnum
    # 			if self.tempval > self.maximum:	#correct for out of bounds
    # 				self.tempval = self.maximum
    # 			if self.tempval < self.minimum:
    # 				self.tempval = self.minimum
    # 			self.setTemp(self.tempval)

    # 		humid.append(self.getHumid())
    # 		carbon.append(self.getC02())
    # 		time.sleep(60.0 - ((time.time() - starttime) % 60.0))	#iterating time like this removes error by using the system clock

    # 	self.sendMessage("bms")		#set room back to thermostat control
    # 	self.sendMessage("quit")	#stop sending messages

    # 	self.close()

    # 	file = open(str(time.strftime("%d.%m.%Y"))+"final.txt", 'w')		#remake entire file for last date
    # 	file.write('Desired Temperature:\n')
    # 	for item in desiredtemp:		#write all desiredtemp values to a file
    # 	  file.write("%s\n" % item)
    # 	file.write('Co2:\n')
    # 	for item in carbon:				#write all carbon values to a file
    # 	  file.write("%s\n" % item)
    # 	file.write('Humidity:\n')
    # 	for item in humid:				#write all humidity values to a file
    # 	  file.write("%s\n" % item)
    # 	file.close()

    # 	self.datalogging = False



