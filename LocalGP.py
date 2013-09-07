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

import wiringpi
import spidev

# RasPiConnectImports

import Config
import Validate
import BuildResponse 

board_type = sys.argv[-1]

def pi_rev_check():      # Function checks which Pi Board revision we have
    # make a dictionary of known Pi board revision IDs
    rev_dict={'0002':1,'0003':1,'0004':2,'0005':2,'0006':2,'000f':2}

    # search the cpuinfo file to get the board revision ID
    revcheck = open('/proc/cpuinfo')
    cpuinfo = revcheck.readlines()
    revcheck.close()

    # put Revision ID line in a variable called matching  
    matching = [s for s in cpuinfo if "Revision" in s]

    # extract the last four useful characters containing Rev ID
    rev_num = str(matching[-1])[-5:-1] 

    # look up rev_num in our dictionary and set board_rev (-1 if not found)
    board_rev = rev_dict.get(rev_num, -1) 
    return board_rev

def get_adc(channel):                     # read SPI data from MCP3002 chip
    if ((channel > 1) or (channel < 0)):  # Only channels 0 and 1 else return -1
        return -1
    r = spi.xfer2([1,(2+channel)<<6,0])   # these two lines explained at end
    ret = ((r[1]&31) << 6) + (r[2] >> 2)
    return ret 


board_revision = pi_rev_check() # check Pi Revision to set port 21/27 correctly
if board_revision == 1:
    # define ports list Rev 1
    ports = [25, 24, 23, 22, 21]
else:
    # define ports list all others
    ports = [25, 24, 23, 22, 27]

wiringpi.wiringPiSetupGpio()                        # initialise wiringpi
wiringpi.pinMode(18,2)                      # Set up GPIO 18 to PWM mode
wiringpi.pinMode(17,1)                      # GPIO 17 to output
wiringpi.digitalWrite(17, 0)                # port 17 off for rotation one way
wiringpi.pwmWrite(18,0)                     # set pwm to zero initially

for port_num in ports:
    wiringpi.pinMode(port_num, 1)                   # set up ports for output


port25 = False
port24 = False
FMOutput = 0
spi = spidev.SpiDev()
spi.open(0,0)         # The Gertboard ADC is on SPI channel 0 (CE0 - aka GPIO8)


def ExecuteUserObjects(objectType, element):

	# Example Objects
	global port25
	global port24
	global FMOutput

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
			output = board_revision
			FMOutput += 1000.0
			
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
			output = board_revision
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
			  wiringpi.digitalWrite(25, 0)      # switch on an led
			  port25=False
			  ledColour = 5
			  print "Led off"
			else:
			  wiringpi.digitalWrite(25, 1)      # switch on an led
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
			  wiringpi.digitalWrite(24,0)      # switch on an led
			  port24=False
			  responseData = "Port 24 Led off"
			else:
			  wiringpi.digitalWrite(24, 1)      # switch on an led
			  port24=True
			  responseData = "port 24 Led on"
			
	                outgoingXMLData += BuildResponse.buildResponse(responseData)
     			outgoingXMLData += BuildResponse.buildFooter()
                	return outgoingXMLData
	if( objectType ==VOLTMETER_UITYPE ):
        	        #check for validate request
                	if (validate == "YES"):
                        	outgoingXMLData += Validate.buildValidateResponse("YES")
                 	        outgoingXMLData += BuildResponse.buildFooter()
                        	return outgoingXMLData

			adc_value = (get_adc(0))  # read ADC voltage 
			if adc_value > 511:                 # above half-way on the pot
            			wiringpi.digitalWrite(17, 0)    # motor spins one way
		                pwm = (adc_value - 511) * 2 -1
        		else:                               # below half-way on the pot
            			wiringpi.digitalWrite(17, 1)    # motor spins the other way
            			pwm = adc_value * 2 + 1

        		wiringpi.pwmWrite(18, pwm)          # send PWM value to port 18

			responseData = "%i" % (adc_value)
	                outgoingXMLData += BuildResponse.buildResponse(responseData)
     			outgoingXMLData += BuildResponse.buildFooter()
                	return outgoingXMLData	
	
	else:
		return ""
	# returning a zero length string tells the server that you have not matched 
	# the object and server 
	return ""

