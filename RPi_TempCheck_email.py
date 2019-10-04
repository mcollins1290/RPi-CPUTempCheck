#!/usr/bin/env python3.7

import sys
import smtplib
import socket
import os.path
import getopt
import configparser

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_SETTINGS = []
TEMP_THRESHOLDS = []

warnTemp = 0
critTemp = 0
sendEmail = True
sendEmailonOK = True

usage_msg = "usage: " + sys.argv[0] + " <SendEmailOnOK? (T/F)>"

def getSettings():

	global EMAIL_SETTINGS
	global TEMP_THRESHOLDS
	global warnTemp
	global critTemp
	##### DEBUGGING
	#currentDirectory = os.getcwd()
	#print(currentDirectory)
	#####
	settings_filename = './settings.ini'
	config = configparser.ConfigParser()
	config.read(settings_filename)
	# If settings file is missing, print error to CLI and Exit
	if not config.sections():
		print("ERROR: "+ settings_filename + " is missing. Exiting...")
		sys.exit(1)
	# File exists, check sections and options are present. If not, print error to CLI and Exit.
	for section in [ 'Email_Settings', 'Temp_Thresholds' ]:

		if not config.has_section(section):
			print("ERROR: Missing settings section: " + section +". Please check " + settings_filename + ". Exiting...")
			sys.exit(1)

	if section == 'Email_Settings':
		for option in [ 'FromEmail', 'ToEmail', 'Password', 'SMTPHost', 'SMTPPort' ]:
			if not config.has_option(section, option):
				print("ERROR: Missing Email Settings option: " + option +". Please check " + settings_filename + ". Exiting...")
				sys.exit(1)

	if section == 'Temp_Thresholds':
		for option in [ 'WarnTempinC', 'CritTempinC' ]:
			if not config.has_option(section, option):
				print("ERROR: Missing Temp. Threshold option: " + option +". Please check " + settings_filename + ". Exiting...")
				sys.exit(1)

	# Settings file sections and options valid. Now retrieve/parse values and store in global dicts
	try:
		EMAIL_SETTINGS = {
			'FROM_EMAIL':config.get('Email_Settings', 'FromEmail'),
			'TO_EMAIL':config.get('Email_Settings', 'ToEmail'),
			'PASSWORD':config.get('Email_Settings', 'Password'),
			'SMTP_HOST':config.get('Email_Settings', 'SMTPHost'),
			'SMTP_PORT':config.getint('Email_Settings', 'SMTPPort')}

		TEMP_THRESHOLDS = {
			'WARNTEMPINC':config.getint('Temp_Thresholds', 'WarnTempinC'),
			'CRITTEMPINC':config.getint('Temp_Thresholds', 'CritTempinC')}

	except ValueError as e:
		print("ERROR: Unable to parse values from settings file: \n" + str(e))
		sys.exit(1)

	# Retrieve Temp. Thresholds from THRESHOLDS dict and override global variable defaults
	warnTemp = TEMP_THRESHOLDS['WARNTEMPINC']
	critTemp = TEMP_THRESHOLDS['CRITTEMPINC']

	##### DEBUGGING #####
	#print("Warning Temp. Threshold set to " + str(warnTemp) + "°C")
	#print("Critical Temp. Threshold set to " + str(critTemp) + "°C")
	#####################

def str2bool(str):
	return str == "T"

def get_ip_address():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80)) #Google DNS IP for connection test
	ip_addr = s.getsockname()[0]
	s.close()
	return(ip_addr)

def chkArgs(argv):
	global sendEmailonOK

	if len(argv) != 1:
		print(usage_msg)
		sys.exit(2)

	if argv[0] != 'T' and argv[0] != 'F':
		print(usage_msg)
		sys.exit(2)

	sendEmailonOK = str2bool(argv[0])

def main():
	global EMAIL_SETTINGS
	global warnTemp
	global critTemp
	global sendEmailonOK
	global sendEmail

	osTempFilePath = '/sys/class/thermal/thermal_zone0/temp'

	if (os.path.exists(osTempFilePath)):
		osTempFile = open(osTempFilePath, 'r')
		cpuTempC = int(int(osTempFile.readline())/1000)
		cpuTempF = int(cpuTempC*9/5+32)
		###### DEBUGGING
		#print(cpuTempC)
		#print(cpuTempF)
		#cpuTempC = 100
		######

		if cpuTempC >= critTemp:
                        status_code = 'CRITICAL'
                        status_msg_short = "CPU TEMP CRITICAL, PLEASE CHECK"
                        status_msg_long = "CPU TEMP MEETS OR EXCEEDS SET CRITICAL TEMP, CHECK ASAP!!!"
		elif cpuTempC >= warnTemp:
			status_code = 'WARNING'
			status_msg_short = "CPU TEMP WARNING, PLEASE CHECK"
			status_msg_long = "CPU TEMP MEETS OR EXCEEDS SET WARNING TEMP, CHECK ASAP!!!"
		else:
			status_code = 'OK'
			status_msg_short = "CPU TEMP OK"
			status_msg_long = "CPU Temperature is OK"

			if sendEmailonOK == False:
				sendEmail = False

		if (sendEmail):
			email_bdy_str = status_msg_long + "\n"
			email_bdy_str = email_bdy_str + "RPi CPU Temperature: " + str(cpuTempC) + "°C/" + str(cpuTempF) + "°F"

			# add IP address to email body
			email_bdy_str = email_bdy_str + "\nIP Address: " + get_ip_address() + "\n"

			# Add set Warning and Critical Temp. Thresholds at bottom of email body
			email_bdy_str = email_bdy_str + "\n(Set Warning Temp: " + str(warnTemp) + "°C)"
			email_bdy_str = email_bdy_str + "\n(Set Critical Temp: " + str(critTemp) + "°C)"

			###### DEBUGGING
			#print("DEBUG: "+ email_bdy_str)
			######
			try:
				s = smtplib.SMTP(EMAIL_SETTINGS['SMTP_HOST'],EMAIL_SETTINGS['SMTP_PORT'])
				s.starttls()
				s.login(EMAIL_SETTINGS['FROM_EMAIL'],EMAIL_SETTINGS['PASSWORD'])
			except:
				print("Unexpected error during SMTP Connection:", sys.exc_info())
				raise
			# create a MIMEMultipart message required for email
			msg = MIMEMultipart()

			# setup the parameters of the email message
			msg['From']=EMAIL_SETTINGS['FROM_EMAIL']
			msg['To']=EMAIL_SETTINGS['TO_EMAIL']
			msg['Subject']="RPi CPU Temp Check Results for host " + socket.gethostbyaddr(socket.gethostname())[0] + ". Status Code: " + str(status_code)

			# add to message the the message body string
			msg.attach(MIMEText(email_bdy_str, 'plain'))

			# send the message via the SMTP connection set up earlier.
			s.send_message(msg)
			print("INFO: RPi CPU Temp Check Email sent successfully")
			# delete the message object now that the message has been sent
			del msg
			# Terminate the SMTP session and close the connection
			s.quit()
		print("INFO: RPi CPU Temp Check Completed successfully. Status Code: " + str(status_code))
	else:
		print("ERROR: Unable to locate OS Temp File: " + osTempFilePath)
		s.quit()
		sys.exit(1)

if __name__ == '__main__':
	chkArgs(sys.argv[1:])
	getSettings()
	main()
	sys.exit(0)
