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

# RasPiConnectImports

import Config
import Validate
import BuildResponse 

# build standard header for image responce
def buildImageResponse(image):
	responseData = "<html><head>"
	responseData += "<title></title><style>body,html,iframe{margin:0;padding:0;}</style>"
	responseData += "</head>"
	responseData += "<body><img src=\""
	responseData += Config.localURL() 
	responseData += "static/"
	responseData += image
	responseData += "\" type=\"jpg\" width=\"300\" height=\"300\">"
	responseData += "<BR>Picture<BR>"
	responseData +="</body>"
	responseData += "</html>"
	
	return responseData
		
def ExecuteUserObjects(objectType, element):

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
	# search for matches to object Type 

	# object Type match
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
		# B-8 Shutdown
		if (objectServerID == "B-8"):	
              		#check for validate request
			# validate allows RasPiConnect to verify this object is here 
        	       	if (validate == "YES"):
                	       	outgoingXMLData += Validate.buildValidateResponse("YES")
                       		outgoingXMLData += BuildResponse.buildFooter()
	                       	return outgoingXMLData

			# not validate request, so execute
			# note that python is in the main directory for this call, not the local directory
                      	output = subprocess.call(["sudo","shutdown","-a","now"])
			responseData = "OK"
                	outgoingXMLData += BuildResponse.buildResponse(responseData)
      			outgoingXMLData += BuildResponse.buildFooter()
	                return outgoingXMLData			



	# camera status
	elif (objectServerID == "W-1"):
		#check for validate request
		if (validate == "YES"):
			outgoingXMLData += Validate.buildValidateResponse("YES")
			outgoingXMLData += BuildResponse.buildFooter()
			return outgoingXMLData

		tempData = "xx.x C (no i2c enabled)" 
		pressureData = "xxxx.x hPa (no i2c enabled)" 

				

		# read an HTML template into aw string		
		with open ("./Templates/camera.html", "r") as myfile:
    			responseData += myfile.read().replace('\n', '')
	
		# replace the URL so it will point to static
		responseData = responseData.replace("XXX", Config.localURL() ) 
	

		# now replace the AAA, BBB, etc with the right data
		responseData = responseData.replace("AAA", subprocess.check_output(["date", ""], shell=True))	

		# split uptime at first blank, then at first ,
		uptimeString = subprocess.check_output(["uptime", ""])	
	
		uptimeType = uptimeString.split(",")
		uptimeCount = len(uptimeType)

		if (uptimeCount == 6):
			# over 24 hours
			uptimeSplit = uptimeString.split(",")
			uptimeSplit = uptimeSplit[0]+uptimeSplit[1]
			uptimeSplit = uptimeSplit.split(" ", 1)
			uptimeData = uptimeSplit[1]
		else:	
			# under 24 hours
			uptimeSplit = uptimeString.split(" ", 2)
			uptimeSplit = uptimeSplit[2].split(",", 1)
			uptimeData = uptimeSplit[0]

		responseData = responseData.replace("BBB", uptimeData)	

		usersString = subprocess.check_output(["who", "-q"], shell=False, stderr=subprocess.STDOUT,)	
		responseData = responseData.replace("CCC", usersString)	

		freeString = subprocess.check_output(["free", "-mh"])	
		freeSplit = freeString.split("cache: ", 1)
		freeSplit = freeSplit[1].split("       ", 2)
		freeSplit = freeSplit[2].split("\nSwap:", 1)
		freeData = freeSplit[0]
		responseData = responseData.replace("DDD", freeData)	
			
		responseData = responseData.replace("EEE", tempData)	
		responseData = responseData.replace("FFF", pressureData)	


		output = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
		cpuTemp = "%3.2f C" % (float(output)/1000.0)
			
		responseData = responseData.replace("GGG", cpuTemp)	
		
		freeString = subprocess.check_output(["ifconfig", "eth0"])	
		freeSplit = freeString.split("inet addr:", 1)
		freeSplit = freeSplit[1].split(" ", 1)
		freeData = freeSplit[0]

		responseData = responseData.replace("HHH", freeData)	
			
		responseData = responseData.replace("III", Config.localURL())
		# responseData = responseData.replace("III", "'your external address here'")

		responseData = responseData.replace("JJJ", Config.version_number())

		# read latest data from ST-1 SendText control on RasPiConnect 

		try:
			with open ("./local/ST-1.txt", "r") as myfile:
    				sendTextData = myfile.read().replace('\n', '')
   		except IOError:
			sendTextData = ""

		responseData = responseData.replace("KKK", sendTextData)
		outgoingXMLData += BuildResponse.buildResponse(responseData)

        	if (Config.debug()):
			print outgoingXMLData			

		
	# previous camera image
	elif (objectServerID == "W-2"):
	
		#check for validate request
		if (validate == "YES"):
			outgoingXMLData += Validate.buildValidateResponse("YES")
			outgoingXMLData += BuildResponse.buildFooter()
			return outgoingXMLData

		imageName = "previous.jpg"	
		responseData =buildImageResponse(imageName)
		outgoingXMLData += BuildResponse.buildResponse(responseData)
		outgoingXMLData += BuildResponse.buildFooter()
		
        	if (Config.debug()):
			print outgoingXMLData	

	# latest camera image
	elif (objectServerID == "W-3"):
	
		#check for validate request
		if (validate == "YES"):
			outgoingXMLData += Validate.buildValidateResponse("YES")
			outgoingXMLData += BuildResponse.buildFooter()
			return outgoingXMLData
			
		imageName = "latest.jpg"
		responseData =buildImageResponse(imageName)	
		outgoingXMLData += BuildResponse.buildResponse(responseData)
		outgoingXMLData += BuildResponse.buildFooter()
		
        	if (Config.debug()):
			print outgoingXMLData	

	        return outgoingXMLData	
	else:
	
		# returning a zero length string tells the server that you have not matched 
		# the object and server 
		return ""

