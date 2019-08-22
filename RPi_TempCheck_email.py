#!/usr/bin/env python3.7

import sys
import smtplib
import socket
import os.path
import getopt

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

warnTemp = 0

MY_ADDRESS = 'SET YOUR EMAIL ADDRESS HERE' #Username
PASSWORD = 'SET THE PASSWORD FOR YOUR EMAIL ACCOUNT HERE' #Password
SMTPHost = 'SET YOUR SMTP HOST HERE' #SMTP Host i.e. for Outlook 365
SMTPPort = 587 #SMTP Port

def get_ip_address():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80)) #Google DNS IP for connection test
	ip_addr = s.getsockname()[0]
	s.close()
	return(ip_addr)

def getWarnTempArg(argv):
	global warnTemp
	if len(argv) != 1:
		print("usage: " + sys.argv[0] + " <inputTempC>")
		sys.exit(2)

	warnTemp = int(sys.argv[1])

	##### DEBUGGING
	#output_msg = "DEBUG: Warning Temp set to: " + str(warnTemp) + "°C"
	#print(output_msg)
	#####

def main():
	global warnTemp
	# set up the SMTP server connection
	try:
		s = smtplib.SMTP(SMTPHost,SMTPPort)
		s.starttls()
		s.login(MY_ADDRESS, PASSWORD)
	except:
		print("Unexpected error during SMTP Connection:", sys.exc_info())
		raise
	# create a MIMEMultipart message required for email
	msg = MIMEMultipart()

	osTempFilePath = '/sys/class/thermal/thermal_zone0/temp'

	if (os.path.exists(osTempFilePath)):
		osTempFile = open(osTempFilePath, 'r')
		cpuTempC = int(int(osTempFile.readline())/1000)
		cpuTempF = int(cpuTempC*9/5+32)
		###### DEBUGGING
		#print(cpuTempC)
		#print(cpuTempF)
		######

		if cpuTempC >= warnTemp:
			status_msg_short = "CPU TEMP WARNING, PLEASE CHECK"
			status_msg_long = "CPU TEMP MEETS OR EXCEEDS SET WARNING TEMP, CHECK ASAP!!!"
		else:
			status_msg_short = "CPU TEMP OK"
			status_msg_long = "CPU Temperature is OK"


		email_bdy_str = status_msg_long + "\n"
		email_bdy_str = email_bdy_str + "RPi CPU Temperature: " + str(cpuTempC) + "°C/" + str(cpuTempF) + "°F\n"

		# add IP address to email body
		email_bdy_str = email_bdy_str + "\nIP Address: " + get_ip_address() + "\n"

		# Add set Warning Temp at bottom of email body
		email_bdy_str = email_bdy_str + "\n(Set Warning Temp: " + str(warnTemp) + "°C)"

		###### DEBUGGING
		#print("DEBUG: "+ email_bdy_str)
		######

		# setup the parameters of the email message
		msg['From']=MY_ADDRESS
		msg['To']=MY_ADDRESS
		msg['Subject']="RPi CPU Temp Check Results for host " + socket.gethostbyaddr(socket.gethostname())[0] + " -> " + status_msg_short

		# add to message the the message body string
		msg.attach(MIMEText(email_bdy_str, 'plain'))

		# send the message via the SMTP connection set up earlier.
		s.send_message(msg)
		print("INFO: RPi CPU Temp Check Email sent successfully")
		# delete the message object now that the message has been sent
		del msg
		# Terminate the SMTP session and close the connection
	else:
		print("ERROR: Unable to locate OS Temp File: " + osTempFilePath)
		s.quit()
		sys.exit(1)
	s.quit()

if __name__ == '__main__':
	getWarnTempArg(sys.argv[1:])
	main()
	sys.exit(0)
