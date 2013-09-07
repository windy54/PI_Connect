#!/usr/bin/python
# Filename: LocalExample.py
# MiloCreek JS MiloCreek
# Version 1.1 4/8/13
#
# Local Execute Objects for RasPiConnect  
# to add Execute objects, modify this file 
#
#
#
# RasPiConnectServer interface constants

REMOTE_WEBVIEW_UITYPE = 1
ACTION_BUTTON_UITYPE = 16
FEEDBACK_ACTION_BUTTON_UITYPE = 17
SINGLE_LED_DISPLAY = 32
SPEEDOMETER_UITYPE = 64
VOLTMETER_UITYPE = 128
SERVER_STATUS_UITYPE = 256
PICTURE_REMOTE_WEBVIEW_UITYPE = 512
LABEL_UITYPE = 1024
FM_BLINK_LED_UITYPE = 2048
TEXT_DISPLAY_UITYPE = 4096
TOGGLE_SWITCH_UITYPE = 33
SEND_TEXT_UITYPE = 34

# system imports
import sys
import subprocess

import RPi.GPIO as GPIO


# RasPiConnectImports

import Config
import Validate
import BuildResponse 


board_type = sys.argv[-1]

if GPIO.RPI_REVISION == 1:      # check Pi Revision to set port 21/27 correctly
    # define ports list for Revision 1 Pi
    ports = [25, 24, 23, 22, 21]
else:
    # define ports list all others
    ports = [25, 24, 23, 22, 27]   
ports_rev = ports[:]                            # make a copy of ports list
ports_rev.reverse()                             # and reverse it as we need both

GPIO.setmode(GPIO.BCM)                                  # initialise RPi.GPIO

for port_num in ports:
    GPIO.setup(port_num, GPIO.OUT)                  # set up ports for output

port25 = False
port24 = False

def ExecuteUserObjects(objectType, element):

	# Example Objects
	global port25
	global port24

	# fetch information from XML for use in user elements

	#objectServerID is the RasPiConnect ID from the RasPiConnect App

        objectServerID = element.find("./OBJECTSERVERID").text
        objectID = element.find("./OBJECTID").text

        if (Config.debug()):
        	print("objectServerID = %s" % objectServerID)
	# 
	# check to see if this is a Validate request
	#
        validate = Validate.checkForValidate(element)

        if (Config.debug()):
        	print "VALIDATE=%s" % validate

        
	# Build the header for the response

	outgoingXMLData = BuildResponse.buildHeader(element)


	# objects are split up by object types by Interface Constants
	#
	#
	#
	# search for matches to object Type 

	# object Type match
	print("+++++++++++OBJECTTYPE %i" % objectType)
	if (objectType == ACTION_BUTTON_UITYPE):

		if (Config.debug()):
			print "ACTION_BUTTON_UTYPE of %s found" % objectServerID

		# B-2 - play a beep on the Raspberry Pi
		if (objectServerID == "B-2"):	

                	#check for validate request
			# validate allows RasPiConnect to verify this object is here 
                	if (validate == "YES"):
                        	outgoingXMLData += Validate.buildValidateResponse("YES")
                        	outgoingXMLData += BuildResponse.buildFooter()
                        	return outgoingXMLData

			# not validate request, so execute

			# note that python is in the main directory for this call, not the local directory

			output = subprocess.call(["aplay", "sounds/match1.wav"])
			
			responseData = "OK"
                	outgoingXMLData += BuildResponse.buildResponse(responseData)
      			outgoingXMLData += BuildResponse.buildFooter()
                	return outgoingXMLData
	if (objectType == TEXT_DISPLAY_UITYPE):
		
        	if (objectServerID == "LT-1"):	

        	        #check for validate request
                	if (validate == "YES"):
                        	outgoingXMLData += Validate.buildValidateResponse("YES")
                 	        outgoingXMLData += BuildResponse.buildFooter()

                        	return outgoingXMLData

#			output = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
			output = GPIO.VERSION
			FMOutput = 1000.0
			
			print "VERSION++++++++++++++=%s" % output

			responseData = "%3.2f, %3.2f, %s" % (FMOutput,FMOutput, output,)

	                outgoingXMLData += BuildResponse.buildResponse(responseData)
     			outgoingXMLData += BuildResponse.buildFooter()
                	return outgoingXMLData
                	
        	if (objectServerID == "LT-2"):	

        	        #check for validate request
                	if (validate == "YES"):
                        	outgoingXMLData += Validate.buildValidateResponse("YES")
                 	        outgoingXMLData += BuildResponse.buildFooter()

                        	return outgoingXMLData

#			output = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
			output = GPIO.RPI_REVISION
			FMOutput = 2222.0

			
                        print "VERSION---------=%s" % output



			responseData = "%3.2f, %3.2f, %s" % (output,output, "RPI Version")

	                outgoingXMLData += BuildResponse.buildResponse(responseData)
     			outgoingXMLData += BuildResponse.buildFooter()
                	return outgoingXMLData

	if (objectType == SINGLE_LED_DISPLAY ):

        	        #check for validate request
                	if (validate == "YES"):
                        	outgoingXMLData += Validate.buildValidateResponse("YES")
                 	        outgoingXMLData += BuildResponse.buildFooter()
                        	return outgoingXMLData
			if(port25):
			  GPIO.output(25,0)
			  port25=False
			  ledColour = 5
			  print "Led off"
			else:
			  GPIO.output(25,1)
			  port25=True
			  ledColour=2
			  print "Led on"
			
			responseData = "%i" % (ledColour)


	                outgoingXMLData += BuildResponse.buildResponse(responseData)
     			outgoingXMLData += BuildResponse.buildFooter()
                	return outgoingXMLData	
	if (objectType == FEEDBACK_ACTION_BUTTON_UITYPE):
        	        #check for validate request
                	if (validate == "YES"):
                        	outgoingXMLData += Validate.buildValidateResponse("YES")
                 	        outgoingXMLData += BuildResponse.buildFooter()
                        	return outgoingXMLData
			if(port24):
			  GPIO.output(24,0)
			  port24=False
			  responseData = "Port 24 Led off"
			else:
			  GPIO.output(24,1)
			  port24=True
			  responseData = "port 24 Led on"
			
	                outgoingXMLData += BuildResponse.buildResponse(responseData)
     			outgoingXMLData += BuildResponse.buildFooter()
                	return outgoingXMLData
	else:
		return ""
	# returning a zero length string tells the server that you have not matched 
	# the object and server 
	return ""

